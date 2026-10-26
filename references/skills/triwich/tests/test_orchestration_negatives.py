#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_orchestration_negatives.py — 编排结构闸双向负例（v1.0 · 2026-10-25 童灵 D3 挂账清零批）

为什么存在：
  orchestration_gate.py 是 2026-10-22 F10 编排革命时建的常驻闸（行数/末段/指路牌≡节集合/行号锚）。
  CHANGELOG 记过"负例五连测全中"，但那是一次性人工构造——**包内无常设回归**：
  独立复核 `grep -rn orchestration_gate tests/` 零命中实锤（N-8），该闸改坏不会被 run.sh 逮到，
  且它没有 --selftest（anchor_reach 同类病）。本套件把七类判据钉成常驻断言：
  合成夹具 + 真实 SKILL 双跑，合规必绿 / 每类坏样本必红。

判绿口径：末行含 "结果: N/N 通过 ✅"
用法：python3 tests/test_orchestration_negatives.py（登记进 scripts/run.sh 的 SUITES）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "orchestration_gate.py"
results = []

SEC_A, SEC_B, TPL, SP = "## 铁律声明", "## 装载表", "## 结论块模板", "## 指路牌"


def synth(template_early=False, drop_row=False, ghost=False, lineno=False, zone=False):
    """造一个结构合法的最小 SKILL：总 40 行量级，模板默认落在末段。"""
    # 指路牌必须列全（除自身外的每个 ## 节）——夹具不列全=闸判红，那是夹具错不是闸错
    named = [SEC_A, SEC_B, TPL, "## 签名规则"]
    rows = []   # 指路牌不列自身（真实件同口径：列自身=判幽灵节）
    rows += ["| 要过 %-4s | `## %s` |" % ("第%d节" % (i + 1), h.replace("## ", "")) for i, h in enumerate(named)]
    if drop_row:
        rows = rows[:2]                      # 漏列两节（制造"指路牌≠节集合"）
    if ghost:
        rows.append("| 要查幽灵 | `## 根本不存在的节` |")
    name = SP if not zone else "## 指路牌（首因区）"   # 分区词入节名=违反正文消费语义
    body = ["---", "name: synth", "version: \"1.0\"", "---", "", "# 合成夹具", "",
            name, "", "| 你要干什么 | 看哪节 |", "|:--|:--|"] + rows + ["", SEC_A, "铁律正文。", ""]
    if lineno:
        body += ["详见 L7 的旧写法。", ""]
    body += [SEC_B, "装载正文。", ""]
    filler = ["占位行 %d" % i for i in range(1, 13)]
    if template_early:
        body = body[:6] + [TPL, "模板正文提前。", ""] + body[6:] + filler
    else:
        body = body + filler + [TPL, "模板正文住末段。", ""]
    body += ["## 签名规则", "签名正文。", ""]
    return "\n".join(body) + "\n"


def run(path, extra=None):
    cmd = [sys.executable, str(GATE), "--skill-file", str(path)] + (extra or [])
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def case(name, skill_text, expect_rc, extra=None, fname="SKILL.md"):
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / fname
        if skill_text is not None:
            f.write_text(skill_text, encoding="utf-8")
        r = run(f, extra)
        ok = r.returncode == expect_rc
        results.append(ok)
        print("[{s}] {n}: exit={e} 期望={x}".format(s="PASS" if ok else "FAIL",
                                                    n=name, e=r.returncode, x=expect_rc))
        if not ok:
            print("   stderr:", (r.stderr or "").strip().splitlines()[:2])


def main():
    case("合规态必绿", synth(), 0)
    # 真实件走 --skill-root（更严：默认上限 350）
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([sys.executable, str(GATE), "--skill-root", str(ROOT)],
                           capture_output=True, text=True, timeout=60)
        ok = r.returncode == 0
        results.append(ok)
        print("[{s}] 真实对象必绿: exit={e} 期望=0".format(s="PASS" if ok else "FAIL", e=r.returncode))
        if not ok:
            print("   stderr:", (r.stderr or "").strip().splitlines()[:2])

    case("指路牌幽灵节必红", synth(ghost=True), 1)
    case("指路牌漏列必红", synth(drop_row=True), 1)
    case("正文行号锚必红", synth(lineno=True), 1)
    case("模板未住末段必红", synth(template_early=True), 1)
    case("节名含分区词必红", synth(zone=True), 1)
    case("超行数上限必红", synth(), 1, extra=["--max-lines", "20"])
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([sys.executable, str(GATE), "--skill-file", str(Path(td) / "none.md")],
                           capture_output=True, text=True, timeout=60)
        ok = r.returncode == 2
        results.append(ok)
        print("[%s] 目标缺失判 rc2（不静默按绿）: exit=%d" % ("PASS" if ok else "FAIL", r.returncode))

    n = sum(results)
    ok = n == len(results)
    print("结果: {n}/{t} 通过 {s}".format(n=n, t=len(results), s="✅" if ok else "❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
