#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""minimaxcode_health_aggregator.py v1.0 — MiniMax Code 端 SessionStart 健康巡检聚合器

## 为什么建它（2026-10-25·遗留 #6 + #8 联合根治）

宿主 Plugin runtime「最多并发 8 条」是**同一事件**的并发上限。本端 Stop 已挂 8 条（=上限值·
余量 0）⇒ 任何新增 Stop 钩子都有排队/超时风险（事件总预算 15s）。
而母本 WB 那 25 件额外挂载里有 ≈14 件**通用治理件**（端中立·路径已中立），本端此前一件未挂
⇒ ①覆盖不足 ②若直接加挂 Stop 则撞并发上限。

**最优解 = 聚合器**（端中立 §二·五「接入=调用·不=改写共享件」）：
把 N 件通用治理件收进**本端专属聚合器**（1 条 SessionStart 钩子内串行跑 N 件），
既补上覆盖，又把并发条数从「2+N」压到「3」⇒ 并发余量 5。

## 本端收编清单（**5 件**·全部经本轮实跑验证有判域）

| 件 | 判据 | 本轮实跑读数 |
|:--|:--|:--|
| design_family_guard | 设计哲学家族 INDEX/看板一致性 | ✅ 无漂移 |
| systemlog_stophook_check | 当日系统日志收口 | ✅ 通过 |
| guard_registry_check | 守卫登记一致性 | ✅ 通过 |
| triwich_closeout_guard | 三明智收尾三登记（seal/台账/FU） | ⚠ S1 真告警（台账缺 seal 凭据·根因已治） |
| reply_tail_guard | 回复尾部三明治签名 | 静默通过（无签名则报警） |

**⛔ 不收编（及原因·避免造假绿/噪音）**：
- `twin_changelog_guard`：判据对象＝童灵规格书 ↔ 数字分身 CHANGELOG（数字分身域）⇒ 本端挂 = 查他端账；
  且本轮实测其告警为 **mtime 假漂移**（`sha_changed=false`·内容未变）⇒ 补 CHANGELOG 记录＝造假账 ⛔
- `change_closedloop_guard`：全局欠账口径 ⇒ 本端挂 = 每轮报他端未登记文件（实测报 9 项他端件）⇒ 母本端已在守
- `post_change_guard`：实测 **15.86s** ⇒ 撞 Stop 15s 事件预算 ⇒ ⛔不挂
- `manifest_registrar`：无孤儿（无输出）+ 有写副作用 ⇒ 本端已用官方 registrar 手动登记
- `workbuddy_config_guard` / `workbuddy_inject_chain_guard` / `workbuddy_skill_health_guard`：判据对象是**母本**配置/技能目录 ⇒ 本端挂 = 查母本的账
- `ups_aggregator`：母本 UPS 单出口（11 provider）⇒ 本端 UPS 6 条共 1.56s 在预算内 ⇒ 不引入
- `tsl_closeout_guard` / `tsl_tree_hook`：TSL 树义务仅 D3 档 ⇒ 本档无判域

## 行为

1. 读宿主 stdin（一次）⇒ **原样转发**给每个子件（各子件独立 stdin）
2. 逐件串行执行，**每件独立 timeout**（单件卡住不拖累其他）
3. 已是合法 JSON 的子件输出 ⇒ 原样透传
4. 纯文本 ⇒ 按强弱告警词元判定（复用 `minimaxcode_hook_adapter.wrap_alert`）：
   命中真告警才包成宿主 JSON `additionalContext`；绿态 ⇒ 静默（防噪音）
5. **每件写一行台账**到 `~/.minimax/minimaxcode_health_state.jsonl`
   （件名·rc·耗时·输出摘要·ts）⇒ 补上「②在跑」环缺的状态面
6. fail-safe：任一件异常只记台账、不阻断其他件、不阻断对话

用法：python3 minimaxcode_health_aggregator.py
自测：python3 minimaxcode_health_aggregator.py --selftest
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    from minimaxcode_hook_adapter import wrap_alert, alert_lines
except Exception:  # pragma: no cover - 适配器缺失时降级为静默
    def wrap_alert(_text):
        return ""

    def alert_lines(_text):
        return []

def _resolve_script_center():
    """脚本中心路径解析（2026-10-25·入包去作者机化）。

    病根：原写死作者机绝对路径 `/Users/<作者>/[记忆共享中心]/脚本中心` ⇒ 入包后所有用户机器
    指向不存在路径 ⇒ 聚合器 5 件全部 rc≠0 ⇒ 健康聚合器恒红（假红族·判据面≠落点面）。

    修法：**端中立推导**（三级降级，⛔不改判据只搬读取面）——
      ① `runtime_paths.rp("script_center")`（装机期逐机生成的声明面·单一真源）
      ② 环境变量 `BULUOTUO_SCRIPT_CENTER`（显式覆盖）
      ③ `Path.home()/[记忆共享中心]/脚本中心`（标准记忆共享中心默认布局）
    ④ 兜底：与本件同目录的父目录（安装器 ② 落 `<MC>/脚本中心/` 时的实际落点）
    """
    # ① 声明面（runtime_paths 与本件同目录或脚本中心根）
    for _cand in (HERE, os.path.dirname(HERE)):
        if os.path.isdir(_cand):
            try:
                if _cand not in sys.path:
                    sys.path.insert(0, _cand)
                import runtime_paths as _rp  # noqa: E402
                _v = _rp.rp("script_center", optional=True)
                if _v and os.path.isdir(_v):
                    return _v
            except Exception:
                pass
    # ② 显式环境覆盖
    _env = os.environ.get("BULUOTUO_SCRIPT_CENTER", "")
    if _env and os.path.isdir(_env):
        return _env
    # ③ 标准记忆共享中心布局
    _home = os.path.join(os.path.expanduser("~"), "[记忆共享中心]", "脚本中心")
    if os.path.isdir(_home):
        return _home
    # ④ 安装落点兜底：<部署根>/脚本中心/（安装器 ② 把本件落在脚本中心内）
    return os.path.dirname(HERE)


MC = _resolve_script_center()
STATE_PATH = os.path.expanduser("~/.minimax/minimaxcode_health_state.jsonl")

# 全局预算闸（2026-10-25）：单件 timeout 之和 = 5×20 = 100s ⇒ 撞宿主事件上限风险。
# 治法＝**总预算封顶**：逐件 timeout 取 min(单件上限, 剩余预算)；预算耗尽 ⇒ 余下件标 skipped
# （不是失败：没跑 ≠ 跑了判红 ⇒ 台账显形"未覆盖"而不是造假绿）。
TOTAL_BUDGET_SEC = 45.0

# (件名, argv, timeout 秒)
HEALTH_ITEMS = [
    ("design_family_guard", [sys.executable, MC + "/守卫/design_family_guard.py"], 20),
    ("systemlog_stophook_check", [sys.executable, MC + "/守卫/systemlog_stophook_check.py"], 20),
    ("guard_registry_check", [sys.executable, MC + "/守卫/guard_registry_check.py", "Stop"], 20),
    ("triwich_closeout_guard", [sys.executable, MC + "/守卫/triwich_closeout_guard.py", "--report"], 20),
    ("reply_tail_guard", [sys.executable, MC + "/守卫/reply_tail_guard.py"], 20),
]


def _write_state(rec):
    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _run_one(name, argv, timeout, stdin_bytes):
    t0 = time.time()
    try:
        p = subprocess.run(
            argv,
            input=stdin_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        rc = p.returncode
        out = p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc = -1
        out = ""
    except Exception as exc:  # noqa: BLE001
        rc = -2
        out = "EXC:%s" % exc
    dt = round(time.time() - t0, 3)
    return rc, out, dt


def _classify(out):
    """⇒ (kind, payload) kind ∈ silent|json|alert

    ⚠ 关键：子件的「内部 JSON」（自报状态）**不是**宿主契约形态 ⇒ 绝不可原样透传
    （原样透传会被宿主判 HOOK_INVALID_OUTPUT ⇒ 产出被丢——本轮实测的病）。
    仅当 JSON 本身含 `hookSpecificOutput`/`decision` 时才是宿主契约 ⇒ 才透传。
    """
    s = (out or "").strip()
    if not s:
        return "silent", ""
    try:
        d = json.loads(s)
    except Exception:
        wrapped = wrap_alert(s)
        return ("alert", wrapped) if wrapped else ("silent", "")
    # 合法 JSON：先判是不是宿主契约形态
    if isinstance(d, dict) and ("hookSpecificOutput" in d or "decision" in d):
        return "json", s
    # 子件内部 JSON ⇒ 当作子件自报状态判定：**尊重子件自己的 alarm 字段**
    # （alarm=false = 提示级·提醒不阻断 ⇒ 不注入；alarm=true = 真红项 ⇒ 注入）
    if isinstance(d, dict) and d.get("alarm") is True:
        wrapped = wrap_alert(json.dumps(d, ensure_ascii=False))
        if wrapped:
            return "alert", wrapped
        return "silent", ""
    # 非布尔 alarm（或无 alarm 字段）⇒ 退回复合词元判定
    wrapped = wrap_alert(json.dumps(d, ensure_ascii=False))
    if wrapped:
        return "alert", wrapped
    return "silent", ""


def aggregate(stdin_bytes):
    results = []
    payloads = []
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    t_start = time.time()
    for name, argv, timeout in HEALTH_ITEMS:
        remain = TOTAL_BUDGET_SEC - (time.time() - t_start)
        if remain <= 1.0:
            # 预算耗尽 ⇒ 标 skipped（显形"未覆盖"·⛔不记绿也不记红）
            results.append({"ts": ts, "item": name, "rc": -3, "sec": 0.0,
                            "kind": "skipped", "out_head": "总预算 %.0fs 耗尽·未跑" % TOTAL_BUDGET_SEC})
            continue
        rc, out, dt = _run_one(name, argv, min(timeout, remain), stdin_bytes)
        kind, payload = _classify(out)
        results.append({
            "ts": ts, "item": name, "rc": rc, "sec": dt, "kind": kind,
            "out_head": " ".join((out or "").split())[:180],
        })
        if payload:
            payloads.append(payload)
    for rec in results:
        _write_state(rec)
    return results, payloads


def _selftest():
    """对偶夹具：6 例（宿主契约透传 / 内部 JSON 不透传 / 告警注入 / 绿态静默 / 空 ⇒ 静默）。

    ⛔ 2026-10-25 自纠：原第 3 例断言「合法 JSON → 透传」**与设计契约矛盾**——
    子件内部 JSON（如 `{"alarm": false}`）原样透传会被宿主判 HOOK_INVALID_OUTPUT ⇒ 产出被丢。
    真正透传的条件是**宿主契约形态**（含 `hookSpecificOutput`/`decision`）⇒ 夹具按契约重写。
    """
    ok = True

    def case(name, src, expect_kind, expect_substr=None):
        nonlocal ok
        r = _classify(src)
        passed = r[0] == expect_kind
        if passed and expect_substr is not None:
            passed = expect_substr in r[1]
        ok = ok and passed
        print(f"  [{'OK' if passed else 'FAIL'}] {name} → {r[0]}")

    # ① 宿主契约形态 JSON ⇒ 原样透传（不改写已合规者）
    case("宿主契约 JSON（hookSpecificOutput）→ 透传",
         '{"hookSpecificOutput":{"additionalContext":"x"}}', "json", "hookSpecificOutput")
    # ② 宿主契约形态 JSON（decision）⇒ 原样透传
    case("宿主契约 JSON（decision）→ 透传",
         '{"decision":"block","reason":"r"}', "json", "decision")
    # ③ 子件内部 JSON（alarm=false）⇒ **不**透传 ⇒ 静默（防 HOOK_INVALID_OUTPUT）
    case("内部 JSON（alarm=false）→ 不透传·静默", '{"alarm": false}', "silent", "")
    # ④ 纯文本真告警 ⇒ 包宿主 JSON
    case("纯文本告警 → 包 JSON", "🔴 真红：铁律上界不一致", "alert", "hookSpecificOutput")
    # ⑤ 纯文本绿态 ⇒ 静默
    case("绿态纯文本 → 静默", "✅ 全部正常 三层一致", "silent", "")
    # ⑥ 空输出 ⇒ 静默
    case("空输出 → 静默", "", "silent", "")
    print(f"  [{'OK' if ok else 'FAIL'}] 分类自测合计")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    stdin_bytes = sys.stdin.buffer.read() if not sys.stdin.isatty() else b""
    results, payloads = aggregate(stdin_bytes)
    for p in payloads:
        sys.stdout.write(p + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
