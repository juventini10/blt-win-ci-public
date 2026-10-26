#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_gate_negatives.py — title_format_guard 双向负例（v1.1 · 2026-10-26 日期炸弹根治批）

为什么存在：
  title_format_guard 是 growth-box 的记录标题格式闸（缺日期-ID 会被 stats.py 静默漏计）。
  2026-10-25 跨 Skill 体检把它列为裸闸门（无常设负例）。变异抽检证明它当下有牙，但没有
  回归保护：实现一改就可能静默失效，而失效形态恰好是"依旧全绿"。本套件钉住四态。

v1.1 为什么要改（不改成"把断言放宽"）：
  v1.0 的「当日同ID撞号必红」用例把 ID 日期**硬编码成写测试那天的 20261025**，而被测守卫
  按 `date.today()` 实时区分「当日增量→exit 1」与「历史存量→⚠️显形不阻断」。于是 10-26
  起，同一个夹具自动从"当日"变成"存量"，断言必然翻脸——这是**日期炸弹测试**（自爆于日历），
  不是守卫坏了。实证：2026-10-26 06:2x 实跑 4/5 FAIL，被测件行为两处均符合设计意图。
  根治=拆解消阻力：①增量用例的日期在运行时实取，永不为历史；②新增「历史存量不阻断且必须显形」
  反向哨兵，把守卫的另一半行为也钉住——任何一侧漂移（把存量也判红 / 把存量静默吞掉）都会红。

用法：python3 tests/test_gate_negatives.py
判绿口径：末行含 "结果: N/N 通过 ✅"
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import datetime as _dt
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "scripts" / "title_format_guard.py"

results = []


def run(learn_dir):
    return subprocess.run([sys.executable, str(GUARD), str(learn_dir)],
                          capture_output=True, text=True, timeout=120)


def case(name, setup, expect_rc, base, expect_out=None):
    d = base / ("case_" + str(len(results)))
    d.mkdir(parents=True, exist_ok=True)
    setup(d)
    r = run(d)
    out = (r.stdout or "") + (r.stderr or "")
    rc_ok = r.returncode == expect_rc
    out_ok = (expect_out is None) or (expect_out in out)
    ok = rc_ok and out_ok
    results.append(ok)
    tag = "PASS" if ok else "FAIL"
    extra = "" if out_ok else "（显形缺失：期望输出含 %r）" % expect_out
    print(f"[{tag}] {name}: exit={r.returncode} 期望={expect_rc}{extra}")
    if not ok and rc_ok:
        print("   out:", out.strip().splitlines()[:3])


def _today_id(seq="008"):
    """运行时实取当日日期——增量用例永不因日历翻页而降级为存量。"""
    return "ERR-%s-%s" % (_dt.date.today().strftime("%Y%m%d"), seq)


def _hist_id(seq="008"):
    """昨日日期——用于钉住「历史存量显形不阻断」这一半行为。"""
    return "ERR-%s-%s" % ((_dt.date.today() - _dt.timedelta(days=1)).strftime("%Y%m%d"), seq)


def _ok(d):
    # 闸门口径：`## [` 开头且必须包含 `\d{8}-\d{1,3}`（纯数字序号）
    (d / "ERRORS.md").write_text(
        "# 错误记录\n\n## [%s] 合规条目\n\n内容\n" % _today_id("009"), encoding="utf-8")


def _bad_title(d):
    (d / "ERRORS.md").write_text(
        "# 错误记录\n\n## [坏标题没有编号]\n\n内容\n", encoding="utf-8")


def _empty(d):
    return None


def _dup_today(d):
    iid = _today_id("008")
    (d / "ERRORS.md").write_text(
        "# 错误记录\n\n## [%s] 第一条\n\n内容\n\n"
        "## [%s] 撞号第二条\n\n内容\n" % (iid, iid), encoding="utf-8")


def _dup_hist(d):
    iid = _hist_id("006")
    (d / "ERRORS.md").write_text(
        "# 错误记录\n\n## [%s] 历史第一条\n\n内容\n\n"
        "## [%s] 历史撞号第二条\n\n内容\n" % (iid, iid), encoding="utf-8")


def _template_skip(d):
    (d / "LEARNINGS.md").write_text(
        "# 模板\n\n## [ERR-YYYYMMDD-NNN] 模板骨架\n\n占位\n", encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        case("合规标题必绿", _ok, 0, base)
        case("缺日期-ID必红", _bad_title, 1, base)
        case("空目录必红（0文件≠通过）", _empty, 1, base)
        case("当日同ID撞号必红（增量哨兵·日期运行时实取）", _dup_today, 1, base,
             expect_out="定义层编号撞车")
        # 断言取「逐条显形行」的标记而非段头——变异自证发现只查段头会被
        # 「保留标题、吞掉明细」的半静默漂移骗过（v1.1 二次自纠）
        case("历史存量撞号不阻断但必须显形（存量哨兵）", _dup_hist, 0, base,
             expect_out="[存量]")
        case("模板骨架占位应跳过并判绿", _template_skip, 0, base)

    n = sum(results)
    ok = n == len(results)
    print(f"结果: {n}/{len(results)} 通过 {'✅' if ok else '❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
