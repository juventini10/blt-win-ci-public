#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_acceptance.py — 可机器化验收 V1-V9 的**双向断言**套件（v8.5.2 新增）

为什么存在（元因治理）：
  V1-V8 原为 SKILL.md 里的一张 prose 表，验收方式=人跑一次默认路径看 exit 0。
  「正常态绿」无法区分「闸门在岗」与「闸门空转」：v8.5.1 实测 8 条缺陷中，5 条正是
  以「全绿」形态长期存活 ——
    · V1 把"找不到"与"外部引用"合并 continue，从未判过红；
    · V7 因此常年 PASS，却在真断链面前无鉴别力；
    · dry-run 写盘且自称"未实际写入"；
    · 位置参数失效，指向沙箱仍读真档案（验收假绿）；
    · eval#39 的 exit 1 判据被表序自愈永久短路（恒真）。
  本套件把每条闸门落成双向断言：**正常态必须绿 + 坏样本必须红**。
  只证明"测过的维度"是不够的（C-040），所以坏样本必须覆盖本次每个真实缺陷形态。

用法：python3 -m pytest scripts/test_acceptance.py -q
"""
from __future__ import annotations
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass

import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc")


def _copy_skill(tmp_path: Path) -> Path:
    """复制被测件到临时目录；补一个同级 daily-buddy 空目录满足目录型依赖存在性。"""
    dst = tmp_path / "skill"
    shutil.copytree(ROOT, dst, ignore=IGNORE)
    (tmp_path / "daily-buddy").mkdir(exist_ok=True)
    return dst


def _run(skill: Path, *args, env=None, timeout=90):
    e = os.environ.copy()
    for k in ("PYTHONHOME", "PYTHONPATH"):
        e.pop(k, None)
    if env:
        e.update(env)
    return subprocess.run([sys.executable, *map(str, args)], cwd=str(skill),
                          capture_output=True, text=True, env=e, timeout=timeout)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


_SNAPSHOT_TMPL = """# 快照夹具（验收套件）

## 📝 最近变更摘要

| 日期 | 工具 | 文件 | 说明 |
|------|------|------|------|
{rows}

## 其他区域

哨兵串 SNAP-GUARD
"""


def _snapshot(rows) -> str:
    return _SNAPSHOT_TMPL.replace("{rows}", "\n".join(rows))


def _center(tmp_path: Path, days_overdue: int = 30) -> Path:
    d = (datetime.date.today() - datetime.timedelta(days=days_overdue)).isoformat()
    p = tmp_path / "center_fixture.md"
    p.write_text(
        "# 蒸馏中心夹具\n\n## 2026-01\n\n"
        "| 日期 | 类型 | 状态 | 摘要 | 下次执行日期 |\n"
        "|------|------|------|------|--------------|\n"
        f"| 2026-01-01 | 📊 系统日志蒸馏 | ✅ | 夹具行 | {d} |\n",
        encoding="utf-8",
    )
    return p


# ---------- 结构面 ----------

def test_01_structure_and_version():
    s = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    lines = s.splitlines()
    assert len(lines) <= 400, f"SKILL.md {len(lines)} 行 > 400"
    m = re.search(r'^version:\s*"([\d.]+)"', s, re.M)
    assert m, "frontmatter version 缺失"
    heads = [l for l in lines if l.startswith("## ")]
    assert len(heads) == len(set(heads)), "存在重复的 ## 节标题"


def test_02_oneclick_block_covers_all_gates():
    s = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"一条命令跑完全部.*?```bash(.*?)```", s, re.S)
    assert m, "缺少「一条命令跑完全部」块"
    body = m.group(1)
    for key in ("awaken_version_gate_check", "update_snapshot_from_diary",
                "awaken_distill_due_check", "awaken_health_dashboard",
                "test_distill_core", "check_refs_integrity",
                "skill_neutrality_check", "orchestration_gate", "test_acceptance"):
        assert key in body, f"一键验收块缺 {key}（P2-1 回归：声称跑完全部却漏项）"


# ---------- V7 引用完整性：正常绿 + 三类坏样本红 ----------

def test_03_refs_integrity_clean_is_green(tmp_path):
    sk = _copy_skill(tmp_path)
    r = _run(sk, "scripts/check_refs_integrity.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_04_ghost_path_ref_is_red(tmp_path):
    """带 references/ 前缀的幻影引用必须判红（V1 曾把"找不到"当外部引用跳过）。"""
    sk = _copy_skill(tmp_path)
    p = sk / "references/dual-mode.md"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "# 双模式执行手册（轻量 1 步 / 全量 3 步）",
        "# 双模式执行手册（轻量 1 步 / 全量 3 步）\n\n> 探针：references/ghost_acceptance.md §1",
        1), encoding="utf-8")
    r = _run(sk, "scripts/check_refs_integrity.py")
    assert r.returncode == 1, f"V1 空转回归：幻影引用未判红\n{r.stdout}"
    assert "V1 文件不可达" in r.stdout


def test_05_bare_filename_is_skipped_but_counted(tmp_path):
    """裸文件名（外部规范）应跳过，但跳过数必须上屏，不能静默。"""
    sk = _copy_skill(tmp_path)
    p = sk / "references/dual-mode.md"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "# 双模式执行手册（轻量 1 步 / 全量 3 步）",
        "# 双模式执行手册（轻量 1 步 / 全量 3 步）\n\n> 探针：Skill标准规范.md §1.1",
        1), encoding="utf-8")
    r = _run(sk, "scripts/check_refs_integrity.py")
    assert r.returncode == 0, r.stdout
    assert "裸文件名跳过" in r.stdout, "跳过必须可观测，不得静默"


def test_06_missing_file_dep_is_red(tmp_path):
    sk = _copy_skill(tmp_path)
    (sk / "scripts/awaken_patrol.sh").unlink()
    r = _run(sk, "scripts/check_refs_integrity.py")
    assert r.returncode == 1, "V4 文件型依赖缺失未判红"
    assert "V4 依赖缺失" in r.stdout


def test_07_missing_dir_dep_is_red(tmp_path):
    """目录型依赖 ../daily-buddy/ 必须被校验（原实现正则只认 py/sh/ps1/template）。"""
    sk = _copy_skill(tmp_path)
    shutil.rmtree(tmp_path / "daily-buddy")
    r = _run(sk, "scripts/check_refs_integrity.py")
    assert r.returncode == 1, "V4 目录型依赖缺失未判红（P1-2 回归）"
    assert "目录" in r.stdout and "daily-buddy" in r.stdout


# ---------- P0-1 蒸馏路径可指定 ----------

def test_08_distill_positional_arg_wins(tmp_path):
    """位置参数必须生效：HOME 指向空目录时，若回落 Path.home() 只会得到 NONE。"""
    sk = _copy_skill(tmp_path)
    center = _center(tmp_path)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    r = _run(sk, "scripts/awaken_distill_due_check.py", center,
             env={"HOME": str(fake_home)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "DUE|🔴严重逾期|📊 系统日志蒸馏" in r.stdout, \
        f"P0-1 回归：位置参数被忽略，回落 Path.home() 得到 {r.stdout!r}"


def test_09_dashboard_distill_env_wins(tmp_path):
    """dashboard 的 DISTILL_CENTER_PATH 必须生效（同一条缺陷的第二张脸）。"""
    sk = _copy_skill(tmp_path)
    center = _center(tmp_path)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    r = _run(sk, "scripts/awaken_health_dashboard.py", "--summary",
             env={"HOME": str(fake_home), "DISTILL_CENTER_PATH": str(center)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "蒸馏🔴1" in r.stdout, f"P0-1 回归：DISTILL_CENTER_PATH 失效 → {r.stdout!r}"


# ---------- P1-3 / P1-4 快照写入契约 ----------

def test_10_dryrun_never_writes(tmp_path):
    """非降序表 + --dry-run：md5 必须一致（表序自愈曾绕过 dry-run 写盘）。"""
    sk = _copy_skill(tmp_path)
    snap = tmp_path / "snap_dry.md"
    snap.write_text(_snapshot([
        "| 10-21 | 手动 | x | 旧行 |",
        "| 10-22 | 手动 | x | 新行 |",
    ]), encoding="utf-8")
    before = _md5(snap)
    h = tmp_path / "h"
    h.mkdir()
    r = _run(sk, "scripts/update_snapshot_from_diary.py", "--dry-run",
             "--snapshot", snap, "--no-archive", env={"HOME": str(h)})
    assert r.returncode in (0, 2), r.stdout + r.stderr
    assert _md5(snap) == before, f"P1-3 回归：--dry-run 写了盘\n{r.stdout}"


def test_11_archive_guard_path_is_reachable(tmp_path):
    """--no-normalize 下非降序表必须触发归档守卫 exit 1（原判据被自愈永久短路）。"""
    sk = _copy_skill(tmp_path)
    snap = tmp_path / "snap_guard.md"
    snap.write_text(_snapshot([
        "| 10-21 | 手动 | x | 旧行 |",
        "| 10-22 | 手动 | x | 新行 |",
    ]), encoding="utf-8")
    h = tmp_path / "h2"
    h.mkdir()
    r = _run(sk, "scripts/update_snapshot_from_diary.py", "--snapshot", snap,
             "--no-backfill", "--no-normalize", "--archive-window", "1",
             env={"HOME": str(h)})
    assert r.returncode == 1, f"P1-4 回归：守卫路径不可达 exit={r.returncode}\n{r.stdout}"
    assert "非降序" in r.stdout


# ---------- P2 文档面 ----------

def test_12_eval_ids_monotonic():
    t = (ROOT / "references/eval-set.md").read_text(encoding="utf-8")
    ids = [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", t, re.M)]
    assert ids == sorted(ids), f"eval-set 编号乱序（P2-2 回归）：{ids}"
    assert len(ids) == len(set(ids)), "eval-set 编号重复"


def test_13_tests_version_follows_skill():
    s = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    v = re.search(r'^version:\s*"([\d.]+)"', s, re.M).group(1)
    for f in ("tests/trigger-positive.md", "tests/trigger-negative.md"):
        t = (ROOT / f).read_text(encoding="utf-8")
        assert f"v{v}" in t, f"{f} 版本未跟随 SKILL v{v}（P2-4 回归）"


def test_14_presentation_sentinels():
    """嵌套哨兵（eval#40）+ 围栏声明（eval#41）。"""
    for f in ("SKILL.md", "references/dual-mode.md", "references/patrol.md"):
        t = (ROOT / f).read_text(encoding="utf-8")
        assert "│  ├" not in t, f"{f} 出现嵌套续行符号"
    dm = (ROOT / "references/dual-mode.md").read_text(encoding="utf-8")
    pt = (ROOT / "references/patrol.md").read_text(encoding="utf-8")
    assert "代码围栏" in dm and "整体包代码围栏" in pt


def test_15_distill_core_suite_still_green():
    """原有 5 例不得被本次改动破坏（回归门）。"""
    r = _run(ROOT, "scripts/test_distill_core.py")
    # test_distill_core.py 自带 unittest/pytest 两种入口，直接执行时以 exit code 判定
    assert r.returncode == 0, r.stdout + r.stderr
