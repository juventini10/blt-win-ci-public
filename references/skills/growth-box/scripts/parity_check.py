#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip growth-box Skill 包内形态/计数对账闸（非脚本中心守卫族）·版本纪律走本 Skill CHANGELOG·先例=daily-buddy parity 同口径
"""parity_check.py — 形态/计数对账闸（growth-box 第三实例·v1.0·2026-10-23）

TRUTH_OF: 弱锚升级三件套（形态级判据+否证族+计数对账）唯一真源 = Skill架构规范 pages/09-orchestration.md §弱锚升级·形态级判据。
本件判据族=任务卡 P0·D5 决策（与次例内容不同构·设计同构）：
  A 总步数对账：SKILL 声明的 A／B／C／E 四元组与路由表「共 N 步」 ≡ flow 文件实测步骤标题数
  B 步序串对账：级联锁锚点行四条步序串 ≡ flow 文件步骤标题编号序列（逐项含 .5/-b）
  C eval 计数对账：eval-set 头部「用例总数 N 条」 ≡ 双形态实测（字母编号+纯数字编号）
  D 否证族：已废除形态回流即红——"E16" 仅许出现在历史说明行（含"曾记"）；
    "通知箱/流程D" 仅许出现在废除声明行（含"废除/移除"）。扫描域=SKILL+flow 四件。
设计纪律：判据可枚举、一行算一处；⛔词级 token 只查存在性（§13.5）。
负例有牙（S138）：--skill-file/--flows-dir 可指变异副本；改声明数字/删 flow 步骤/注入旧形态任一项必 FAIL。
用法：python3 parity_check.py [--skill-root DIR] [--skill-file PATH]
退出码：0=全绿；1=任一条不过；2=文件不可达。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse, io, os, re, sys

RE_TOTAL4 = re.compile(r"A(\d+)／B(\d+)／C(\d+)／E(\d+)")          # 全角斜杠四元组
RE_ROUTE = re.compile(r"^\| ([ABCE]) [^|]+\|[^|]+\|.*?（共 (\d+) 步", re.M)  # 路由表行
RE_STEP_HEAD = re.compile(r"^#{4,5} 步骤 ([A-E][0-9.]+(?:-b)?)", re.M)
RE_CASCADE = re.compile(r"\*\*锚点\*\*：(.+?)——")
RE_EVAL_DECL = re.compile(r"用例总数：(\d+)条")
RE_EVAL_ALPHA = re.compile(r"^[|] *[TNR][0-9]+ *[|]", re.M)
RE_EVAL_NUM = re.compile(r"^[|] *[0-9]+ *[|]", re.M)

FLOWS = ("A", "B", "C", "E")
EXEC_FILES = ("SKILL.md", "references/flow-A.md", "references/flow-B.md",
              "references/flow-C.md", "references/flow-E.md")


def read(root, rel):
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return None
    return io.open(p, encoding="utf-8").read()


def split_cascade(skill):
    m = RE_CASCADE.search(skill)
    if not m:
        return None
    return [re.findall(r"[A-E][0-9.]+(?:-b)?(?=→|$)", seg.strip())
            for seg in m.group(1).split(" / ")]


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--skill-root", default=os.path.join(here, ".."))
    ap.add_argument("--skill-file", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.skill_root)

    skill = read(root, "SKILL.md") if not a.skill_file else io.open(a.skill_file, encoding="utf-8").read()
    if not skill:
        print("PARITY:FAIL SKILL 不可达", file=sys.stderr); return 2
    flow_txt = {}
    for f in FLOWS:
        p = os.path.join(root, "references", "flow-%s.md" % f)
        if a.skill_file:  # 变异副本模式：flow 与变异 SKILL 同根（skill-file 的 ../references）
            p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(a.skill_file))), "references", "flow-%s.md" % f)
        flow_txt[f] = read(root, "references/flow-%s.md" % f) if not a.skill_file else io.open(p, encoding="utf-8").read() if os.path.isfile(p) else None
        if flow_txt[f] is None:
            print("PARITY:FAIL flow-%s 不可达" % f, file=sys.stderr); return 2

    errs = []
    actual = {f: RE_STEP_HEAD.findall(flow_txt[f]) for f in FLOWS}
    counts = {f: len(actual[f]) for f in FLOWS}

    # A 总步数：四元组声明逐处 ≡ 实测；路由表「共 N 步」逐行 ≡ 实测
    quads = RE_TOTAL4.findall(skill)
    if not quads:
        errs.append("[A] SKILL 未找到 A／B／C／E 四元组声明（判据失锚）")
    for q in quads:
        if [int(x) for x in q] != [counts[f] for f in FLOWS]:
            errs.append("[A] 四元组声明 %s ≠ 实测 %s" % ("/".join(q), "/".join(str(counts[f]) for f in FLOWS)))
    for letter, n in RE_ROUTE.findall(skill):
        if int(n) != counts[letter]:
            errs.append("[A] 路由表 %s 声明共%s步 ≠ 实测 %d" % (letter, n, counts[letter]))

    # B 步序串：级联锁四串 ≡ flow 标题编号序列
    chains = split_cascade(skill)
    if not chains or len(chains) != 4:
        errs.append("[B] 级联锁锚点串不可解析（判据失锚）")
    else:
        for letter, chain in zip(FLOWS, chains):
            if chain != actual[letter]:
                errs.append("[B] %s 串分叉：级联锁 %s ≠ flow 实际 %s" % (letter, chain, actual[letter]))

    # C eval 计数
    ev = read(root, "references/eval-set.md")
    if ev is None:
        errs.append("[C] eval-set 不可达")
    else:
        d = RE_EVAL_DECL.search(ev)
        if not d:
            errs.append("[C] eval 头部无「用例总数 N 条」声明（判据失锚）")
        else:
            n_act = len(RE_EVAL_ALPHA.findall(ev)) + len(RE_EVAL_NUM.findall(ev))
            if int(d.group(1)) != n_act:
                errs.append("[C] eval 声明 %s ≠ 双形态实测 %d" % (d.group(1), n_act))

    # D 否证族（形态白名单行豁免·枚举口径=docstring）
    files = {"SKILL.md": skill}
    files.update({"references/flow-%s.md" % f: flow_txt[f] for f in FLOWS})
    for rel, txt in files.items():
        for ln in txt.splitlines():
            if "E16" in ln and "曾记" not in ln:
                errs.append("[D] 旧步数 E16 现于非历史行 @ %s：%s" % (rel, ln.strip()[:50]))
            if ("通知箱" in ln or "流程D" in ln) and not re.search(r"废除|移除", ln):
                errs.append("[D] 已废形态回流 @ %s：%s" % (rel, ln.strip()[:50]))

    if errs:
        print("PARITY:FAIL 形态/计数闸 %d 项：" % len(errs), file=sys.stderr)
        for e in errs[:12]:
            print("   - %s" % e, file=sys.stderr)
        return 1
    print("PARITY:OK 步数≡%s·四串同构·eval≡声明·否证族0命中" %
          "/".join(str(counts[f]) for f in FLOWS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
