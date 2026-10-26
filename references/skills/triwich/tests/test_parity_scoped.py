#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_parity_scoped.py — 模板同构位「分层件锁」双向负例（v1.0 · 2026-10-25 童灵 D3 根治批 P4 配套）

为什么存在：
  P4 实锤——SKILL.md 自称"逐字填槽唯一源"的结论块模板缺 L3「Agent B验证」行与 L2「验证架构」行，
  而 parity 闸用扁平 NEED（7 文件必含同一组 token）：层级专属行**无法**进扁平表（L1 本就不该含），
  于是"唯一源缺行"在旧闸下不可逮=机检假绿面。v1.3 引入 NEED_SCOPED 分层件锁后，
  按「⛔不加负例的新锁等于没锁」（同批 P1 教训）补本套件：合规必绿 + 删分层件必红 + 结构钉。

判绿口径：末行含 "结果: N/N 通过 ✅"
用法：python3 tests/test_parity_scoped.py（已登记进 scripts/run.sh 的 SUITES）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PC = ROOT / "scripts" / "template_parity_check.py"
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "steps")
results = []


def _run(root):
    return subprocess.run([sys.executable, str(PC), "--skill-root", str(root)],
                          capture_output=True, text=True, timeout=180)


def case(name, mutate, expect_rc, pristine):
    tmp = pristine.parent / ("p" + str(len(results)))
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(pristine, tmp, ignore=IGNORE)
    try:
        mutate(tmp)
    except AssertionError as e:
        results.append(False)
        print("[FAIL] {n}: 夹具失效（{e}）".format(n=name, e=e))
        return
    r = _run(tmp)
    ok = r.returncode == expect_rc
    results.append(ok)
    print("[{s}] {n}: exit={e} 期望={x}".format(s="PASS" if ok else "FAIL", n=name,
                                               e=r.returncode, x=expect_rc))
    if not ok:
        print("   stdout:", (r.stdout or "").strip().splitlines()[:2])
        print("   stderr:", (r.stderr or "").strip().splitlines()[:3])
    shutil.rmtree(tmp, ignore_errors=True)


def _noop(_):
    return None


def _cut_line(rel, needle):
    def _m(tmp):
        p = tmp / rel
        lines = p.read_text(encoding="utf-8").splitlines(True)
        keep = [l for l in lines if needle not in l]
        if len(keep) == len(lines):
            raise AssertionError("夹具未命中：%s 内无含「%s」的行" % (rel, needle))
        p.write_text("".join(keep), encoding="utf-8")
    return _m


def _unlink(rel):
    def _m(tmp):
        (tmp / rel).unlink()
    return _m


def _structural_pin():
    """防"分层件锁被悄悄摘回扁平"：源码必须仍在主流程消费 NEED_SCOPED。"""
    src = PC.read_text(encoding="utf-8")
    ok = ("NEED_SCOPED = [" in src) and ("for tok, files in NEED_SCOPED" in src)
    results.append(ok)
    print("[%s] 结构钉: parity 主流程须消费 NEED_SCOPED" % ("PASS" if ok else "FAIL"))


def main():
    with tempfile.TemporaryDirectory() as td:
        pristine = Path(td) / "tw"
        shutil.copytree(ROOT, pristine, ignore=IGNORE)
        case("合规态必绿", _noop, 0, pristine)
        case("SKILL删Agent B验证行必红", _cut_line("SKILL.md", "| Agent B验证 |"), 1, pristine)
        case("SKILL删验证架构行必红", _cut_line("SKILL.md", "| 验证架构 |"), 1, pristine)
        case("dual-routes删验证架构注记必红", _cut_line("references/l2/dual-routes.md", "验证架构"), 1, pristine)
        case("L3承载件缺失必红", _unlink("references/l3/full-flow.md"), 1, pristine)
        # N-4 哨兵（独立复核 M7b 实锤）：留词去义——只留「验证架构」四字、抽掉实质骨架标记，必须判红
        def _hollow(tmp):
            q = tmp / "references/l2/dual-routes.md"
            txt = q.read_text(encoding="utf-8")
            if "单Agent 自检链" not in txt:
                raise AssertionError("夹具前提失效：dual-routes 无实质标记")
            q.write_text(txt.replace("单Agent 自检链", "验证架构"), encoding="utf-8")
        case("留词去义必红（N-4 实质标记锁）", _hollow, 1, pristine)
        # 哨兵说明：上方「SKILL删Agent B验证行必红」即 v1.3 首跑自曝病（提及即绿）的常驻哨兵——
        # 判据为单元格形态，声明行仍在场也必须判红。
        case("L1件不含分层件不误伤", _noop, 0, pristine)
    _structural_pin()
    n = sum(results)
    ok = n == len(results)
    print("结果: {n}/{t} 通过 {s}".format(n=n, t=len(results), s="✅" if ok else "❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
