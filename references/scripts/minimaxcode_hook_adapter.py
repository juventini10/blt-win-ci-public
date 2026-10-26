#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""minimaxcode_hook_adapter.py v1.0 — MiniMax Code 端 Stop 钩子 JSON 契约适配器

## 病形（2026-10-25 宿主观测日志实证）

MiniMax Code Desktop v3.1.3 的 Plugin Hook 契约：stdout 必须是**单个 JSON 对象**
（`hookSpecificOutput.additionalContext` / `decision:"block"` + `reason`）。
母本共享守卫多打印**纯文本巡检输出** ⇒ 宿主判 `HOOK_INVALID_OUTPUT` ⇒ **产出被丢弃**。

实证：`~/.minimax/v2/observability/logs/runtime-2026102512.log`
  `[12:22:05.250] WARN: [] Plugin hook command failed open
   {"code":"HOOK_INVALID_OUTPUT","pluginName":"bulutuo-guards","event":"Stop","declarationOrder":3}`
⇒ 钩子**跑了**、产出**没到对话** = 假绿（挂载在、机制不生效）。

## 修法（端中立·零共享件改动·本端适配器）

挂载命令改为 `python3 minimaxcode_hook_adapter.py -- <原命令…>`：
  1. stdin **直通**原命令（不吞载荷）
  2. 原命令 stdout 已是合法 JSON → **原样透传**（不干预已合规者）
  3. stdout 是纯文本 →
       · 命中告警行 → 包成 `{"hookSpecificOutput":{"additionalContext":"…"}}`（截断 1500 字）
       · 未命中   → **输出空**（静默通过·与「被宿主丢弃」等效，但零告警噪音）
  4. stderr 一律丢弃（宿主对 stderr 无契约）
  5. rc：原命令 rc 透传；适配器自身任何异常 → 输出空 + rc 0（**fail-safe**：适配器故障不得拖垮钩子）

## 口径边界（诚实声明）

- 本适配器只包 **Stop** 8 条。SessionStart/UserPromptSubmit 侧**未包**：宿主观测日志中
  UPS/SessionStart 零 `HOOK_INVALID_OUTPUT`，且 SessionStart 纯文本输出实测**可投递**
  （`<plugin-hook-context>` 实收 memory_pointer_reachability_guard 的纯文本巡检行）⇒ 不做无证据改动。
- 只在**真告警**时注入 ⇒ 静默通过仍静默（防「事后反馈注入打乱回复节奏」·reply_format_guard 退役前例）。

用法：
  python3 minimaxcode_hook_adapter.py -- <原命令…>
  python3 minimaxcode_hook_adapter.py --selftest
"""

import json
import os
import re
import subprocess
import sys

MAX_INJECT_CHARS = 1500

# 告警词元（**行内命中**才算）。
# ⛔ 不用「行首匹配」：守卫的告警行形如 `   - 铁律上界不一致`（缩进短横线开头），
#   行首判定会漏掉真漂移 ⇒ 门禁有洞。实证：rule_three_layer_guard 的漂移行即此形态。
ALERT_TOKENS = (
    "🔴", "❌", "告警", "报警", "违规", "失败", "FAIL", "ERROR", "CRITICAL",
    "漂移", "不一致", "缺失", "未布线", "越界", "撞号",
)
# 弱词元：单独命中不算告警（warn-only 残留不算红），须与强词元同现才算。
# 实证：绿态报告 `⑥ 触发规格覆盖：… ✅｜⚠️ match 留空 4 条（有法无触发器·有意取舍非漂移）`
#      —— 单独命中 ⚠ 但无强词元 ⇒ 静默（防每轮注入噪音 = reply_format_guard 退役前例）。
WEAK_TOKENS = ("⚠",)

# 否定形归一：良性表述里含强词元子串会误命中（实证：`有意取舍非漂移` 含「漂移」）。
# 命中前先抹掉否定形，避免「说没漂移」被当成「有漂移」。
NEGATED_FORMS = ("非漂移", "无漂移", "不漂移", "无告警", "未告警", "无缺失", "未缺失")


def _normalize(line):
    s = line
    for n in NEGATED_FORMS:
        s = s.replace(n, "")
    return s


def _is_alert_line(line):
    s = _normalize(line)
    if any(tok in s for tok in ALERT_TOKENS):
        return True
    return any(tok in s for tok in WEAK_TOKENS) and \
        any(tok in s for tok in ALERT_TOKENS)


def _looks_alert(text):
    """逐行判定：是否有行命中告警词元。"""
    return any(_is_alert_line(l) for l in (text or "").splitlines() if l.strip())


def _extract_alert_lines(text):
    out = []
    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            continue
        if _is_alert_line(s):
            out.append(s)
    return out


def _wrap(text):
    """纯文本 → 宿主 JSON 契约。无告警则返回空串（静默）。"""
    if not text or not text.strip():
        return ""
    if not _looks_alert(text):
        return ""
    lines = _extract_alert_lines(text)
    payload = "\n".join(lines) if lines else text.strip()
    if len(payload) > MAX_INJECT_CHARS:
        payload = payload[:MAX_INJECT_CHARS] + "\n…（适配器截断·原输出更长）"
    return json.dumps(
        {"hookSpecificOutput": {"additionalContext": payload}},
        ensure_ascii=False,
    )


def wrap_alert(text):
    """公开入口：纯文本 → 宿主 JSON 契约（无告警返回空串）。
    供本端聚合器复用（避免强弱词元判据两处维护）。"""
    return _wrap(text)


def alert_lines(text):
    """公开入口：抽取告警行。"""
    return _extract_alert_lines(text)


def _split_env(argv):
    """剥离命令前缀的 `VAR=VAL` 环境赋值（实证：card_id_guard 挂载带
    `CARD_GUARD_HOST=minimaxcode` 前缀·原样传给子进程会当成可执行名而失败）。"""
    env = {}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if "=" in tok and not tok.startswith("-") and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            k, v = tok.split("=", 1)
            env[k] = v
            i += 1
        else:
            break
    return env, argv[i:]


def run_adapter(argv):
    """argv = 原命令参数列表（不含本脚本自身）。返回 (rc, stdout)。"""
    env_extra, cmd = _split_env(argv)
    if not cmd:
        return 0, ""
    child_env = dict(os.environ)
    child_env.update(env_extra)
    try:
        proc = subprocess.run(
            cmd,
            stdin=sys.stdin.buffer,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=child_env,
        )
    except Exception:
        # fail-safe：原命令起不来 → 静默放行（宿主契约：钩子异常不阻断对话）
        return 0, ""
    out = proc.stdout.decode("utf-8", errors="replace")
    stripped = out.strip()
    if stripped:
        try:
            json.loads(stripped)  # 已是合法 JSON → 原样透传
            return proc.returncode, out
        except Exception:
            pass
    return proc.returncode, _wrap(out)


def _selftest():
    """自测：4 个用例（正/负夹具·双向可杀）。"""
    cases = [
        ("纯文本·有告警 → 包 JSON", "🔴 铁律上界不一致\n普通行", True),
        ("纯文本·缩进漂移行 → 包 JSON", "   - 铁律上界不一致", True),
        ("纯文本·无告警 → 输出空", "✅ 全部正常\n三层一致", False),
        ("纯文本·全绿巡检报告 → 输出空", "记忆规则三层一致性巡检：\n  铁律版: 版本 v8.44\n  铁律上界 40\n  ✅ 铁律集合上界一致", False),
        ("空输出 → 输出空", "", False),
    ]
    ok = True
    for name, src, expect_wrap in cases:
        got = _wrap(src)
        wrapped = bool(got)
        passed = (wrapped == expect_wrap)
        if passed and wrapped:
            try:
                d = json.loads(got)
                passed = "hookSpecificOutput" in d and "additionalContext" in d["hookSpecificOutput"]
            except Exception:
                passed = False
        ok = ok and passed
        print(f"  [{'OK' if passed else 'FAIL'}] {name} → {got[:80]!r}")
    # 用例4：合法 JSON 原样透传（由 run_adapter 承担·此处只验判定逻辑不误包）
    print(f"  [{'OK' if ok else 'FAIL'}] 自测合计")
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--selftest":
        return _selftest()
    if not argv or argv[0] != "--":
        sys.stderr.write("usage: minimaxcode_hook_adapter.py -- <command...>\n")
        return 2
    cmd = argv[1:]
    if not cmd:
        sys.stderr.write("no command given\n")
        return 2
    rc, out = run_adapter(cmd)
    if out:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
