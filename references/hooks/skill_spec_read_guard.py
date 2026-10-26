#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version: v1.2b（2026-10-23 夹具逮出 Read 通道漏检：读事件未命中规范不再早退，落入追朔 | v1.2（2026-10-23 根治Bash敞口·皮叔令"该彻底根治就根治"：Bash高置信写形态前置拦+任意通道mtime追朔审计（脚本内写入下一事件现形）；v1.1（2026-10-23 证据换芯：空标记→记名读事件；过闸收紧为核心规范之一；GATE_DIR 可 env 覆盖+--self-test 三态夹具）
# 已知覆盖边界(如实·v1.1)：只拦 Write/Edit/MultiEdit 工具的 SKILL.md 改动；Bash 内 python/cp 改 SKILL.md 不在观测面（解析命令串误报半径大·守保守判定宁漏勿误·留待 payload 演进）
"""
skill_spec_read_guard.py —— 改 Skill 前必读规范守卫（PreToolUse·公共·硬拦）

病（2026-09-19 皮叔亲问「改 Skill 前必须先看规范，可以设 hook 吗」）：
  AI 改 SKILL.md 时**不读**《Skill架构规范》《指令编写规范》→ 违规落地（规范写在文件里，无人读）。
  = 典型"只写正面规则、缺反向校验"（执规-008 判据：不读文档也被拦才算机制化）。

判（机械·零 AI 判断）：
  · 见 Read/Grep/Glob 命中**规范文件** → 记标记 `~/.cache/skill_gate/spec_read.active`（mtime<4h）
  · 见 Edit/Write/MultiEdit 命中 **SKILL.md**（技能配置/*/SKILL.md 或 */skills/*/SKILL.md）
      → 有标记 → exit 0 放行；无标记 → exit 2 物理阻断 + 引导语

真相所有权（守卫规范§二）：规范文件清单=SPECS 常量（唯一住所·本文件）；⛔不在守卫里内联规范内容。
端中立（公共件）：不绑端；各端 settings.json PreToolUse 接入即可用。@0/scripts 豁免。
契约：exit 2=拦 / exit 0=放行；失败放行（守卫规范§三 Hook 三纪律）。
"""
# Win console UTF-8 guard (auto by clock-loop 1.7.2)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
import sys
import os
import json
import re
import time
import glob as _glob

GUARD_NAME = "skill_spec_read_guard.py"
GATE_DIR = os.environ.get("SKILL_GATE_DIR") or os.path.expanduser("~/.cache/skill_gate")
SPEC_MARKER = os.path.join(GATE_DIR, "spec_read.active")
TTL = 4 * 3600

# 规范文件（名字特征）——命中任一即视为"已读规范"
SPECS = ("Skill架构规范", "指令编写规范", "守卫编写规范", "文件格式规范", "脚本架构设计通用规范")
# v1.1：过闸只认核心规范——读外围规范记名但不放行（防"读文件格式规范凑闸"）
CORE_SPECS = ("Skill架构规范", "指令编写规范")
# 受管目标：SKILL.md（改 Skill 本体）
SKILL_RE = re.compile(r"(?:技能配置|skills)/[^/]+/SKILL\.md$")
BASELINE_TS = os.path.join(GATE_DIR, "postcheck_baseline")
RE_WRITEY = re.compile(r"(?:sed\s+-i[^\n]*(?:SKILL\.md|技能配置)|cp\s[^\n]*\s\S*(?:技能配置|/skills/)[^\n]*SKILL\.md|mv\s[^\n]*SKILL\.md|tee[^\n]*SKILL\.md)")
RE_REDIR  = re.compile(r">>?!?\s*\S*(?:技能配置|/skills/)[^\n]*SKILL\.md")
EXEMPT = (GUARD_NAME, "append_log_entry.py", "/growth-box/scripts/", "/数字分身/scripts/")


def _paths(tool, inp):
    out = []
    for k in ("file_path", "path", "pattern", "glob"):
        v = inp.get(k)
        if isinstance(v, str) and v:
            out.append(v)
    if tool in ("Bash", "bash"):
        out.append(str(inp.get("command", "")))
    return out


def _touch_spec(tag):
    # v1.1 记名读事件：每行 "规范名|epoch"，保留最近 20 行
    try:
        os.makedirs(GATE_DIR, exist_ok=True)
        lines = []
        if os.path.exists(SPEC_MARKER):
            lines = [l for l in open(SPEC_MARKER).read().splitlines() if "|" in l][-19:]
        lines.append(f"{tag}|{int(time.time())}")
        open(SPEC_MARKER, "w").write("\n".join(lines) + "\n")
    except Exception:
        pass

def _spec_hit(text):
    return next((x for x in SPECS if x in text), None)

def _core_fresh():
    """TTL 窗口内存在任一核心规范的记名读事件 → True（v1.1 判据·同源：记的是被观测到的 Read 事件本身）"""
    try:
        now = time.time()
        for l in open(SPEC_MARKER).read().splitlines():
            if "|" not in l: continue
            tag, _, ts = l.rpartition("|")
            if tag in CORE_SPECS and now - float(ts) < TTL:
                return True
    except (OSError, ValueError):
        pass
    return False


def _mark_ts():
    try:
        vals = [float(l.rpartition("|")[2]) for l in open(SPEC_MARKER).read().splitlines() if "|" in l]
        return max(vals) if vals else 0.0
    except OSError:
        return 0.0

def _postcheck(viol_out):
    """层3：任意通道改动过 SKILL.md 而无闸事件（记名读或拦截尝试）→ 追朔红。
    基线：首跑只记快照不追（祖父化·防上线即冤红历史存量）；读失败=静默放行（Hook纪律）。"""
    try:
        now = time.time()
        files = [f for pat in ("技能配置/*/SKILL.md", "发布库/*/*/references/skills/*/SKILL.md")
                 for f in _glob.glob(os.path.expanduser("[记忆共享中心]/") + pat)]
        changed = [(f, os.path.getmtime(f)) for f in files if os.path.exists(f)]
        if not os.path.exists(BASELINE_TS):
            os.makedirs(GATE_DIR, exist_ok=True)
            open(BASELINE_TS, "w").write(str(int(now)))
            return
        base = float(open(BASELINE_TS).read() or "0")
        # 违规=基线后有改动且未经任何闸观测（读规范事件即合法信号·过闸/读规范均刷新基线）
        viol = [f for f, mt in changed if mt > base and mt > now - 3600]
        if viol:
            viol_out.extend(viol)
            open(BASELINE_TS, "w").write(str(int(now)))
    except Exception:
        pass

def main():
    try:
        obj = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(obj, dict):
        return
    tool = obj.get("toolName") or obj.get("tool_name") or ""
    inp = obj.get("input") or obj.get("tool_input") or {}
    if not isinstance(inp, dict):
        return
    full = json.dumps(inp, ensure_ascii=False)
    if any(x in full for x in EXEMPT):
        return
    paths = _paths(tool, inp)
    joined = " ".join(paths)
    # ① 读规范 → 记标记
    if tool in ("Read", "Grep", "Glob"):
        hit = _spec_hit(joined)
        if hit:
            _touch_spec(hit)
            if hit in CORE_SPECS:
                try:
                    open(BASELINE_TS, "w").write(str(int(time.time())))
                except Exception:
                    pass
            return
        # v1.2b：未命中规范的读事件落入追朔（原无条件 return=Read 通道盲区）
    # ② 改 Skill → 查标记
    _post_viol = []
    _postcheck(_post_viol)
    if _post_viol and not _core_fresh():
        print("⛔ v1.2 追朔审计：下列 SKILL.md 近 1h 被改过但无闸事件（记名读/拦截尝试）: "
              + "，".join(os.path.basename(os.path.dirname(x)) for x in _post_viol)
              + " → 疑似脚本/Bash 旁路。先读核心规范留名再重试；确属他端合法改动，Read 一次规范即自解。",
              file=sys.stderr)
        sys.exit(2)
    if tool in ("Bash", "bash") and _core_fresh() is False:
        cmd = str(inp.get("command", ""))
        if (RE_WRITEY.search(cmd) or RE_REDIR.search(cmd)) and "SKILL.md" in cmd:
            print("⛔ v1.2 Bash写形态门卫：命令含对 SKILL.md 的高置信写动作（sed -i/cp/mv/tee/重定向）且无核心规范记名读。"
                  "→ 先 Read《Skill架构规范》或《指令编写规范》任一，再执行。",
                  file=sys.stderr)
            sys.exit(2)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        if any(SKILL_RE.search(p) for p in paths):
            if _core_fresh():
                try:
                    os.makedirs(GATE_DIR, exist_ok=True)
                    open(BASELINE_TS, "w").write(str(int(time.time())))
                except Exception:
                    pass
                return
            print("⛔ Skill规范读取门卫 v1.1：本次将改 SKILL.md，但 4h 窗口内未见【核心规范】的记名读事件。"
                  "→ 请先 Read《Skill架构规范》或《指令编写规范》任一（记名留痕·外围规范不再免检放行），再改。",
                  file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
