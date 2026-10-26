#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_gate_negatives.py — systemlog_gate_check 双向负例（v1.0 · 2026-10-25 闸门负例补建批）

为什么存在：
  systemlog_gate_check 是 system-logger 的写前五查合一闸。2026-10-25 跨 Skill 体检把
  它列为裸闸门（无常设负例）。变异抽检证明它当下有牙，但没有回归保护：实现一改就可能
  静默失效，而失效形态恰好是"依旧全绿"。本套件把五查各自的"能判红"钉成常设断言。

覆盖五查：①h1 唯一 ②今日概览唯一 ③体积 <800KB ④normalize_tool exit 0 ⑤SKILL.md ≥200 行
用法：bash scripts/run_gate_selftest.sh   （或直接 python3 tests/test_gate_negatives.py）
判绿口径：末行含 "结果: N/N 通过 ✅"
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
CHECK = ROOT / "scripts" / "systemlog_gate_check.py"
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.md.bak")

OK_LOG = """# 系统日志

## 今日概览

- 夹具条目一条

## Qoder CN

### 夹具记录

- **工具**：Qoder CN
- **完成**：09:30
"""

results = []


def case(name, log_text, expect_rc, pristine, truncate_skill=False):
    tmp = pristine.parent / ("case_" + str(len(results)))
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(pristine, tmp)
    log = tmp / "fixture_log.md"
    if log_text is not None:
        log.write_text(log_text, encoding="utf-8")
    if truncate_skill:
        sm = tmp / "SKILL.md"
        sm.write_text("\n".join(["# 截断夹具"] + ["- 行"] * 90), encoding="utf-8")
    chk = tmp / "scripts" / "systemlog_gate_check.py"
    target = str(log) if log_text is not None else str(tmp / "no_such_log.md")
    r = subprocess.run([sys.executable, str(chk), target],
                       capture_output=True, text=True, timeout=180)
    ok = r.returncode == expect_rc
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: exit={r.returncode} 期望={expect_rc}")
    if not ok:
        print("   out:", (r.stdout or "").strip().splitlines()[:2])
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        pristine = Path(td) / "sl"
        shutil.copytree(ROOT, pristine, ignore=IGNORE)

        case("合规日志必绿（五查全过）", OK_LOG, 0, pristine)
        case("文件不存在必红", None, 1, pristine)
        case("一级标题重复必红", OK_LOG.replace("# 系统日志", "# 系统日志\n\n## 今日概览\n\n# 系统日志", 1), 2, pristine)
        case("今日概览缺失必红", OK_LOG.replace("## 今日概览", "## 概览别名"), 3, pristine)
        case("体积超 800KB 必红", OK_LOG + ("填充行" * 120000), 4, pristine)
        case("未知工具名必红", OK_LOG.replace("## Qoder CN", "## 某未知端XYZ"), 5, pristine)
        case("SKILL.md 塌陷必红", OK_LOG, 6, pristine, truncate_skill=True)

    n = sum(results)
    ok = n == len(results)
    print(f"结果: {n}/{len(results)} 通过 {'✅' if ok else '❌'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
