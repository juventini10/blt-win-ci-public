#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_scan_budget_gate.py — 扫描预算物理闸锁常驻负例（v1.0 · 2026-10-25 童灵 D3 根治批 P7 配套）

为什么存在：
  考题项45 要求的 rc13（同轮指纹重扫拦截）/ rc14（--force 无理由拦截）在 2026-10-25 之前
  **只靠评估轮手工实跑**——`grep triwich_scan tests/ scripts/run.sh` 零命中=零回归保护，
  属"改了不会被 run.sh 逮到"的裸闸（独立审查 P7 实锤·与 P1 否证族假绿互为因果）。
  本套件把三条腿钉成常驻断言。三态纪律同批钉住：零命中(rc0) ≠ 不存在 ≠ 工具失败(非0)。

判绿口径：末行含 "结果: N/N 通过 ✅"
用法：python3 tests/test_scan_budget_gate.py（已登记进 scripts/run.sh 的 SUITES）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "scripts" / "triwich_scan.py"
SKILL = ROOT / "SKILL.md"
results = []


def _run(args, ledger, ts):
    return subprocess.run([sys.executable, str(SCAN), "--mode", "list",
                           "--pattern", "anchor", "--root", str(ROOT / "references"),
                           "--ts", ts, "--ledger", ledger] + args,
                          capture_output=True, text=True, timeout=120)


def expect(name, rc, want, extra=""):
    ok = rc == want
    results.append(ok)
    print("[{s}] {n}: exit={e} 期望={x}{x2}".format(
        s="PASS" if ok else "FAIL", n=name, e=rc, x=want,
        x2=(" " + extra if extra and not ok else "")))


def main():
    with tempfile.TemporaryDirectory() as td:
        ledger = os.path.join(td, "scan_ledger.log")   # ⛔不写包内台账（他轮证据不可代改）
        ts = "20991231_100000"                         # 合成键·不与真实轮次撞
        r1 = _run([], ledger, ts)
        expect("首扫正向必绿", r1.returncode, 0)
        r2 = _run([], ledger, ts)
        expect("同轮指纹重扫必红(rc13)", r2.returncode, 13, r2.stdout.strip().splitlines()[:1])
        r3 = _run(["--force"], ledger, ts)
        expect("force无理由必红(rc14)", r3.returncode, 14, r3.stdout.strip().splitlines()[:1])
        r4 = _run(["--force", "--reason", "回归夹具复扫"], ledger, ts)
        expect("force带理由放行必绿", r4.returncode, 0)

        # 三态纪律：零命中=查成功无结果（exit 0），⛔不得与工具失败混同
        r5 = subprocess.run([sys.executable, str(SCAN), "--mode", "list",
                             "--pattern", "zzz_不存在_token_xxx",
                             "--root", str(ROOT / "references"),
                             "--ts", ts + "b", "--ledger", ledger],
                            capture_output=True, text=True, timeout=120)
        expect("零命中属查成功必绿", r5.returncode, 0, r5.stdout.strip()[:80])

        # 扫描根不存在=工具层失败，必须非0且不静默（零命中≠不存在≠查询失败）
        r6 = subprocess.run([sys.executable, str(SCAN), "--mode", "list",
                             "--pattern", "anchor", "--root", str(ROOT / "nope_dir"),
                             "--ts", ts + "c", "--ledger", ledger],
                            capture_output=True, text=True, timeout=120)
        expect("扫描根缺失必非0", 0 if r6.returncode == 0 else 1, 1, "rc=%s" % r6.returncode)

        # 台账留痕义务（S4 对账腿的数据源）——本例首跑自曝：条件写反（有痕反而判红）
        lines = [l for l in open(ledger, encoding="utf-8").read().splitlines() if l.strip()]
        expect("台账留痕非空", 1 if lines else 0, 1, "ledger=%d 行" % len(lines))

    # 名实钉：预算常量唯一真源在脚本，SKILL 条款⛔不复制参数值（防双本账·TRUTH_OF 声明）
    sk = SKILL.read_text(encoding="utf-8")
    dup = [k for k in ("DEFAULT_MAX_LINES", "MAX_CAPTURE_BYTES", "2000 行", "30 秒") if k in sk]
    expect("SKILL 未复制预算数值", 1 if not dup else 0, 1, "命中=%s" % dup)

    n = sum(results)
    ok = n == len(results)
    print("结果: {n}/{t} 通过 {s}".format(n=n, t=len(results), s="✅" if ok else "❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
