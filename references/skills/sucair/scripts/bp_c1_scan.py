#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 蓝图卡 C1 预筛件（与 note_validator/bp_quote_verify/bp_factory 同族，无挂载点可声明，
# REG:      硬填注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
"""
bp_c1_scan.py — 蓝图卡 C1 候选预筛（把「整读大文件」换成「按候选段读」+ 节级缺口报）

为什么存在：批次2 源文件动辄 400-700KB，整读既吃光上下文又慢；而「可独立引用的设计判断」
在中文规范文档里有强形态特征（标题行 / 加粗引导句 / ⛔✅判据词 / 律·原则·根因·实证）。
形态可机械抽，判断不可——所以脚本只列候选与行号，产不产卡由 AI 定（Poka-Yoke：脚本不替模型下判断）。

用法：
  python3 bp_c1_scan.py <源.md> [--budget-kb 60] [--show-cards]   # 候选段 + 分片建议
  python3 bp_c1_scan.py <源.md> --gap                            # 只报「有候选但无卡覆盖」的节
输出：候选清单（行号/类型/字节/节名）→ AI 按 slice 定点 Read，⛔不再整读。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from note_validator import parse_frontmatter

CARD_DIR = os.path.expanduser("~/[日记仓库]/2-知识库/10-蓝图索引卡")
SIGNAL = re.compile(r"(⛔|✅DO|判据|根因|律$|律[：:]|原则|铁律|必须|禁止|实证|def |exit [0-9])")
HEAD = re.compile(r"^(#{2,4})\s*(.+?)\s*$")
BOLD_LEAD = re.compile(r"^\s*(?:[-*]\s*)?\*\*([^*]{4,60})\*\*\s*[：:]")

SEC_RE = re.compile(r"^#{2,4}\s*([0-9A-Za-z一二三四五六七八九十·.、]+[^\n]{0,40})")


def anchors_of(src_name):
    """返回该源文件已被 blueprint-card 引用到的节名集合（节级覆盖·⛔只看文件名=假覆盖）。"""
    out = set()
    for p in glob.glob(os.path.join(CARD_DIR, "*.md")):
        try:
            fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        except Exception:
            continue
        if fm.get("type") != "blueprint-card":
            continue
        for it in (fm.get("source_files") or []):
            s = str(it)
            f, _, sec = s.partition("#")
            if os.path.basename(f.strip()) == src_name and sec.strip():
                out.add(sec.strip().lstrip("§"))
    return out


def scan(path, budget_kb):
    lines = open(path, encoding="utf-8").read().split("\n")
    name = os.path.basename(path)
    cands = []
    sec = "(前言)"
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            sec = m.group(2).strip()
            cands.append((i, "标题", len(l), sec, l.strip()[:70]))
            continue
        b = BOLD_LEAD.match(l)
        if b:
            cands.append((i, "加粗引导", len(l.encode()), "%s｜%s" % (sec, b.group(1).strip()[:44]), l.strip()[:70]))
            continue
        if SIGNAL.search(l) and len(l.strip()) > 24:
            cands.append((i, "判据行", len(l.encode()), sec, l.strip()[:60]))
    # 合并为分片：同一节内相邻候选合并，累计超预算则切断
    # 切断判据=累计字节超预算（⛔用「候选间隔>25 行」切：规范文档候选极密，间隔条件永不满足
    #  → 整份文件合成一片=等于整读，本件的意义归零。2026-10-27 首跑实测复现后改。）
    budget = budget_kb * 1024
    slices, cur = [], None
    for c in cands:
        if cur and cur["bytes"] + c[2] > budget:
            slices.append(cur)
            cur = None
        if cur is None:
            cur = {"start": c[0], "end": c[0], "bytes": 0, "n": 0, "sec": c[3], "secs": []}
        cur["end"] = c[0]
        cur["bytes"] += c[2]
        cur["n"] += 1
        cur["secs"].append(c[3])
    if cur:
        slices.append(cur)
    used = anchors_of(name)
    print("源：%s ｜ 行 %d ｜ 候选 %d 个 ｜ 建议分片 %d 片（每片 ≤%dKB 定点读，⛔整读）"
          % (name, len(lines), len(cands), len(slices), budget_kb))
    print("已覆盖节（blueprint-card 引用）：%d 个" % len(used))
    print("\n分片计划（Read 用 start,end）：")
    for s in slices:
        flag = "🟡无卡" if not any(k in s["sec"] for k in used) else "✅有卡"
        import collections
        dom = collections.Counter(s["secs"]).most_common(1)[0][0]
        print("  %s L%-5d-%-5d %4dKB %3d候选  %s" % (flag, s["start"], s["end"], s["bytes"] // 1024, s["n"], dom[:46]))
    if len(sys.argv) > 1 and "--gap" in sys.argv:
        print("\n未覆盖候选（节名未被任何卡引用·产卡优先做这些）：")
        shown = 0
        for ln, kind, by, sec, txt in cands:
            if any(k in sec for k in used):
                continue
            print("  L%-5d %-6s %s" % (ln, kind, sec[:40]))
            shown += 1
            if shown >= 25:
                print("  …（截 25 条·全量 %d 条候选）" % len(cands)); break
        if shown == 0:
            print("  无（该文件候选节已全部被卡覆盖）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--budget-kb", type=int, default=60)
    ap.add_argument("--gap", action="store_true")
    a = ap.parse_args()
    p = os.path.expanduser(a.src)
    if not os.path.isfile(p):
        print("⛔ 源不存在:", p); return 1
    scan(p, a.budget_kb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
