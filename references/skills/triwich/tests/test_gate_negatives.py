#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_gate_negatives.py — eval_anchor_check 双向负例（v1.0 · 2026-10-25 闸门负例补建批）

为什么存在：
  eval_anchor_check 是 triwich 的「迁移表 vs 实证」对账闸。2026-10-25 跨 Skill 体检
  （66 闸门 / 常设负例覆盖 21%）把它列为裸闸门：变异抽检证明它当下有牙，但**没有回归保护**，
  实现一改就可能静默失效，而失效形态恰好是"依旧全绿"（awaken V1 就是这样坏的）。
  本套件把"能判红"钉成常设断言：合规必绿 + 四类坏样本必红。

用法：python3 tests/test_gate_negatives.py   （已登记进 scripts/run.sh 的 SUITES）
判绿口径：末行含 "结果: N/N 通过 ✅"（run.sh 判绿正则要求，勿改措辞）
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
CHECK = ROOT / "scripts" / "eval_anchor_check.py"
MAP_REL = Path("references") / "eval-migration-map.md"
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache")

results = []


def _run(root):
    return subprocess.run([sys.executable, str(CHECK), "--skill-root", str(root)],
                          capture_output=True, text=True, timeout=180)


def _row_index(lines):
    for i, l in enumerate(lines):
        if l.startswith("|") and l.count("|") >= 4 and "---" not in l:
            cells = l.strip("|").split("|")
            if len(cells) >= 6 and cells[0].strip().isdigit():
                return i, cells
    return None, None


def case(name, mutate, expect_rc, pristine):
    tmp = pristine.parent / ("case_" + str(len(results)))
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(pristine, tmp)
    try:
        mutate(tmp)
    except AssertionError as e:
        results.append(False)
        print(f"[FAIL] {name}: 夹具失效（{e}）")
        return
    r = _run(tmp)
    ok = r.returncode == expect_rc
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: exit={r.returncode} 期望={expect_rc}")
    if not ok:
        print("   stderr:", (r.stderr or "").strip().splitlines()[:2])
    shutil.rmtree(tmp, ignore_errors=True)


def _noop(_):
    return None


def _ghost_token(tmp):
    mp = tmp / MAP_REL
    lines = mp.read_text(encoding="utf-8").split("\n")
    idx, cells = _row_index(lines)
    if idx is None:
        raise AssertionError("未定位到数据行")
    cells[4] = " TOKEN-GHOST-PROBE "
    lines[idx] = "|" + "|".join(cells) + "|"
    mp.write_text("\n".join(lines), encoding="utf-8")


def _drop_row(tmp):
    mp = tmp / MAP_REL
    lines = mp.read_text(encoding="utf-8").split("\n")
    idx, _ = _row_index(lines)
    if idx is None:
        raise AssertionError("未定位到数据行")
    del lines[idx]
    mp.write_text("\n".join(lines), encoding="utf-8")


def _ghost_file(tmp):
    mp = tmp / MAP_REL
    lines = mp.read_text(encoding="utf-8").split("\n")
    idx, cells = _row_index(lines)
    if idx is None:
        raise AssertionError("未定位到数据行")
    cells[3] = " GHOST_FILE.md "
    lines[idx] = "|" + "|".join(cells) + "|"
    mp.write_text("\n".join(lines), encoding="utf-8")


def _drop_map(tmp):
    (tmp / MAP_REL).unlink()


def main():
    with tempfile.TemporaryDirectory() as td:
        pristine = Path(td) / "tw"
        shutil.copytree(ROOT, pristine, ignore=IGNORE)
        case("合规态必绿", _noop, 0, pristine)
        case("校验token幻影必红", _ghost_token, 1, pristine)
        case("迁移表行数≠68必红", _drop_row, 1, pristine)
        case("现位文件不存在必红", _ghost_file, 1, pristine)
        case("迁移表不可达必红", _drop_map, 2, pristine)
    n = sum(results)
    ok = n == len(results)
    print(f"结果: {n}/{len(results)} 通过 {'✅' if ok else '❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
