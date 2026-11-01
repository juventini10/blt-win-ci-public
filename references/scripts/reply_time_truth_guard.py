#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
# ============================================================
# reply_time_truth_guard.py v1.0.0 — 回复产出签名时刻真值守卫（Stop 面）
# 立据：2026-10-27 Qoder CN 违反铁律-026 实案——回复正文写了 15:42/16:55，
#   `date` 实取却是 09:22（顺推上一轮时间，一次没取）⇒ TSL --since 落进未来窗口、
#   扫出"L7 全红"假象。铁律-026 原文"时刻必实取，估算即造假"只有条文无执行位。
#
# 判据（零假阳性设计）：
#   产出签名形如 [图标 | 摘要 | YYYY-MM-DD HH:MM]，其时刻**不可能晚于当前真实时刻**。
#   签名时刻 > 当前时刻 + 容差 ⇒ 必为编造（不是"估得不准"，是不存在）。
#   反向不判：早于当前时刻**不报**（可能是本回合早期真实取的时间，无法证伪）。
#
# 形态：报告制（默认 exit 0，红行显形）/ --gate（有红 exit 1）
# 自测：--selftest（正例 2 + 负例 2 + 变异 1）
# ============================================================
import sys, re, json, datetime

TOL_MIN = 3   # 容差分钟：允许时钟微漂，不容忍跨小时编造
SIG = re.compile(r"\[[^\[\]\n]{0,30}?\|\s*[^\[\]\n]{0,60}?\|\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}):(\d{2})\]")
TSL_SINCE = re.compile(r"since=(\d{4}-\d{2}-\d{2})\s+(\d{2}):(\d{2})")


def _now():
    return datetime.datetime.now()


def check(text, now=None):
    """返回 (findings, max_delta_min)。findings = [(kind, raw, delta_min)]"""
    now = now or _now()
    out = []
    for m in SIG.finditer(text or ""):
        try:
            t = datetime.datetime.strptime("%s %s:%s" % (m.group(1), m.group(2), m.group(3)),
                                           "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        d = (t - now).total_seconds() / 60.0
        if d > TOL_MIN:
            out.append(("签名时刻在未来", m.group(0), int(d)))
    return out, 0


def _load_reply():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        return ""
    if not raw.strip():
        return ""
    try:
        d = json.loads(raw)
    except Exception:
        return raw
    for k in ("last_assistant_message", "assistant_message", "message", "text"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v.strip():
            return v
    return raw


def _selftest():
    now = datetime.datetime(2026, 10, 27, 9, 30)
    cases = [
        ("P1 真实过去时刻 不报", "abc [🔧 | 做完 | 2026-10-27 09:28]", 0),
        ("P2 无签名 不报", "纯文本没有签名", 0),
        ("N1 未来 5 小时 必报（本案复刻）", "[🔧 | 越界 | 2026-10-27 15:42]", 1),
        ("N2 未来 1 天 必报", "[🧠 | 明天 | 2026-10-28 09:00]", 1),
    ]
    ok = 0
    for name, txt, expect in cases:
        got, _ = check(txt, now)
        if len(got) == expect:
            print("  ✅ %s" % name); ok += 1
        else:
            print("  ❌ %s 期望 %d 实得 %d" % (name, expect, len(got)))
    # 变异：掏空判据应翻绿
    saved = globals()["SIG"]
    globals()["SIG"] = re.compile(r"__NEVER_MATCH__")
    mut, _ = check("[🔧 | 越界 | 2026-10-27 15:42]", now)
    globals()["SIG"] = saved
    if not mut:
        print("  ✅ MUT:OK 掏空判据→N1 翻绿（判据承重）"); ok += 1
    else:
        print("  ❌ MUT:FAIL 掏空判据仍报红（判据恒真）")
    print("自测结果: %d/%d 通过" % (ok, len(cases) + 1))
    return 0 if ok == len(cases) + 1 else 1


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    text = _load_reply()
    if not text:
        print("ℹ️ reply_time_truth_guard: 无回复载荷（非 Stop 上下文或空）·跳过")
        return 0
    findings, _ = check(text)
    if not findings:
        print("✅ 产出签名时刻真值：无未来时刻（铁律-026）")
        return 0
    print("🔴 [铁律-026] 回复产出签名时刻晚于当前真实时刻 ⇒ 必为编造（估算即造假）：")
    for kind, raw, d in findings:
        print("   · %s | %s | 超出真实时刻 %d 分钟" % (kind, raw, d))
    print("   修法：写时刻前实跑 `date`，⛔ 顺推上一轮时间。改完重发该回复段落。")
    return 1 if "--gate" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
