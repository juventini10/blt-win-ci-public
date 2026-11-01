#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 放量普查件（选片/分级为纯机械活，无 hook/STOP_GUARDS 挂载点，
# REG:      硬填 §四注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
"""bp_survey.py — 蓝图卡放量普查与工单生成（批次3 提效核心件）

要解决的问题：全量目标有两个尺（按字节均摊 208 张 / 每文件至少 1 张 437 张），后者会把任务拖成几十轮，
而其中大量文件是实例记录、看板、变更日志，本身不含「可独立引用的设计判断」。
✅DO 用候选密度（机械抽取：标题/加粗引导/判据信号行）给文件分级，⛔按文件名、按目录印象、按字数决定产不产。

分级判据（阈值可在 --min-cand 调）：
  🟢产卡级  候选 ≥ --tier-heavy(默认 8)：整片做，估卡=候选/5
  🟡抽样级  --tier-light(3) ≤ 候选 < 8：产 1~2 张最高价值判断
  ⚪跳过级  候选 < 3：登记「按判据跳过」并列明候选数，⛔静默忽略（跳过也要留痕，可复核可上诉）

输出：工单台账 markdown（每行一窗一片·含领号/预筛/出厂三行命令），落 10-蓝图索引卡/蓝图卡放量工单.md
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bp_factory as bf  # noqa: E402
import bp_c1_scan as sc  # noqa: E402

HEAD, BOLD_LEAD, SIGNAL = sc.HEAD, sc.BOLD_LEAD, sc.SIGNAL


def cand_count(path):
    """机械数候选判断锚：标题 + 加粗引导 + 判据信号行（与 bp_c1_scan 同一套正则·同源不另立尺）。"""
    n = 0
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except Exception:
        return -1
    for l in lines:
        if HEAD.match(l) or BOLD_LEAD.match(l) or (SIGNAL.search(l) and len(l.strip()) > 24):
            n += 1
    return n


def cards_covered():
    """已被 blueprint-card 引用的源文件名集合（真源=卡 frontmatter，⛔另立台账）。"""
    import glob
    from note_validator import parse_frontmatter
    got = set()
    for p in glob.glob(os.path.join(bf.CARD_DIR, "*.md")):
        try:
            fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        except Exception:
            continue
        if fm.get("type") == "blueprint-card":
            for it in (fm.get("source_files") or []):
                got.add(os.path.basename(str(it).split("#")[0]).strip())
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heavy", type=int, default=8, help="产卡级候选阈值")
    ap.add_argument("--light", type=int, default=3, help="抽样级候选阈值")
    ap.add_argument("--out", default=os.path.join(bf.CARD_DIR, "蓝图卡放量工单.md"))
    ap.add_argument("--check", action="store_true", help="只报分级计数不写工单（自检用）")
    ap.add_argument("--per-card", type=int, default=20000, help="簇颗粒尺：每张卡承载的字节量（标定见注释）")
    a = ap.parse_args()

    files = bf.design_files()
    covered = cards_covered()
    tiers = {"heavy": [], "light": [], "skip": [], "err": []}
    for f in files:
        b = os.path.basename(f)
        if b in covered:
            continue
        c = cand_count(f)
        sz = os.path.getsize(f)
        if c < 0:
            tiers["err"].append((b, sz, c, f))
        elif c >= a.heavy:
            # 估卡尺＝字节/簇颗粒（⛔候选数当尺：候选行在大文件动辄数百，2026-10-27 首版实测估出 3214 张即此错）
            # 标定源：同日实产 46 张 ÷ 实读约 320KB ≈ 7KB/张（现颗粒）；放量按「判断簇」20KB/张执行
            tiers["heavy"].append((b, sz, c, f, max(2, round(sz / a.per_card))))
        elif c >= a.light:
            tiers["light"].append((b, sz, c, f, 1))
        else:
            tiers["skip"].append((b, sz, c, f))
    for k in tiers:
        tiers[k].sort(key=lambda r: -r[1])
    est = sum(r[4] for r in tiers["heavy"]) + sum(r[4] for r in tiers["light"])
    print("零卡文件 %d 个｜产卡级 %d｜抽样级 %d｜跳过级 %d｜读取失败 %d"
          % (len(files) - len(covered), len(tiers["heavy"]), len(tiers["light"]), len(tiers["skip"]), len(tiers["err"])))
    fine = sum(max(1, round(r[1] / 7000)) for r in tiers["heavy"] + tiers["light"])
    print("两尺并列（⛔混用）：现颗粒 7KB/张 ⇒ 约 %d 张｜簇颗粒 %dKB/张 ⇒ 约 %d 张｜跳过级 %d 个文件按判据不产（母卡已覆盖）"
          % (fine, a.per_card // 1000, est, len(tiers["skip"])))
    if a.check:
        return 0

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = ["# 蓝图卡放量工单（批次3 · 一窗一行 · 三行命令照抄即跑）",
         "",
         "生成：%s（bp_survey.py --heavy %d --light %d）" % (now, a.heavy, a.light),
         "分级判据=候选密度（标题+加粗引导+判据信号行，与 bp_c1_scan 同源正则）；⛔按文件名/目录印象/字数决定产不产。",
         "并行规则：一窗一文件（不同文件不冲突）；号段用领号命令预领（.bc_ledger.json 防撞号）；卡面总账只追加不改写。",
         "跳过级也留痕（可复核可上诉）：把该文件行改成 ⏳上诉 即重新入队。",
         "",
         "## 一、产卡级（候选 ≥%d）" % a.heavy, ""]
    for b, sz, c, f, e in tiers["heavy"]:
        L.append("- 🟢 `%s`（%dKB·候选%d）→ 估 %d 张" % (b, sz // 1024, c, e))
        L.append("     领号 `python3 %s/bp_factory.py --reserve %d`" % (HERE, e))
        L.append("     预筛 `python3 %s/bp_c1_scan.py \"%s\" --gap --budget-kb 40`" % (HERE, f))
        L.append("     出厂 `python3 %s/bp_factory.py --ship`" % HERE)
    L += ["", "## 二、抽样级（候选 %d~%d，产 1~2 张最高价值判断）" % (a.light, a.heavy - 1), ""]
    for b, sz, c, f, e in tiers["light"]:
        L.append("- 🟡 `%s`（%dKB·候选%d）→ 1 张｜`\"%s\"`" % (b, sz // 1024, c, f))
    L += ["", "## 三、跳过级（候选 <%d · 按判据不产，留痕可上诉）" % a.light, ""]
    L.append("共 %d 个文件（多为实例记录/看板/变更日志/接入活页），候选密度低于 %d：" % (len(tiers["skip"]), a.light))
    for b, sz, c, f in tiers["skip"][:40]:
        L.append("  - ⚪ `%s`（%dKB·候选%d）" % (b, sz // 1024, c))
    if len(tiers["skip"]) > 40:
        L.append("  - …其余 %d 个见脚本输出（重跑 `--check` 可复核）" % (len(tiers["skip"]) - 40))
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("工单已落盘：%s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
