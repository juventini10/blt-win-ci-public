#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip daily-buddy Skill 包内形态/计数对账闸（非脚本中心守卫族）·版本纪律走本 Skill CHANGELOG·先例=triwich orchestration_gate.py 同口径
"""parity_check.py — 形态/计数对账闸（daily-buddy·v1.0·2026-10-23）

TRUTH_OF: 弱锚升级三件套（形态级判据 + 否证族 + 计数对账）唯一真源 =
          Skill架构规范 §13.5（v5.45）。

判据（全绿才 exit 0）：
  A 步骤范围对账：SKILL.md / 工作流C SOP / eval-set 声明的「1-N」≡ SOP 顶层步骤最大号
  B 封口确认块同构：SKILL.md 与 工作流C 6.4 的字段行逐字一致（槽位名/括注不许分叉）
  C SECTION 计数对账：声明「日常骨架 11 / 全集 12」≡ create_skeleton 实际 11 /
      diary-template 唯一 SECTION 名 12（占位 XXX 不计）
  D 否证族：旧形态回流即红（检查 12 个 SECTION / 含齐12个SECTION /
      三硬依赖脚本裸 python3 调用）

设计纪律：判据须可枚举（一行什么算一处说清）；⛔词级 token 只查存在性。
用法：python3 parity_check.py [--skill-root DIR]
退出码：0=全绿；1=任一条不过；2=文件不可达。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import io
import os
import re
import sys

# 扫描域：执行面三文件（CHANGELOG 是历史账，不参与现行形态判据）
EXEC_FILES = ("SKILL.md",
              "references/工作流C-晚间复盘.md",
              "references/工具与参考.md")
SOP_FILE = "references/工作流C-晚间复盘.md"
EVAL_FILE = "references/eval-set.md"
TPL_FILE = "references/diary-template.md"
MONTHLY_SPEC = "references/monthly-review-spec.md"
SKELETON = "scripts/create_skeleton.py"

RE_STEP_DECL = re.compile(r"1-(\d+)\s*顺序执行")
RE_EVAL_DECL = re.compile(r"步骤\s*1-(\d+)")
RE_STEP_HEAD = re.compile(r"^(\d+)\.\s")
RE_SECTION = re.compile(r"<!--\s*SECTION:\s*([A-Z_]+)\s*-->")
RE_BARE_CALL = re.compile(r"(?<![\w.])python3\s+[^\n|`]*"
                          r"(finalize_diary|create_skeleton|verify_achievement_seal)\.py")
# 命令形态（⛔词级存在）：create_skeleton.py --date X 之后必须紧跟 --out Y
RE_SKELETON_FULL = re.compile(r"create_skeleton\.py\s+--date\s+[^\s`]+(?:\s+--out\s+[^\s`]+)")


def read(root, rel):
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return None
    return io.open(p, encoding="utf-8").read()


def fence_block_after(text, anchor):
    """取 anchor 所在（或紧随其后的）围栏块行列表（去首尾空白）。

    anchor 常住在块内首行（模板本体），此时块围栏在 anchor 前一行；
    若 anchor 在块外说明文字里，则向后找块首。⛔不可一律向后找，
    否则会取到本块结束围栏与下一块的并集（v1.0 实测误报「缺失」）。
    """
    lines = text.splitlines()
    idx = next((i for i, ln in enumerate(lines) if anchor in ln), -1)
    if idx < 0:
        return None
    if idx > 0 and lines[idx - 1].strip().startswith("```"):
        start = idx - 1
    else:
        start = next((j for j in range(idx, len(lines))
                      if lines[j].strip().startswith("```")), None)
        if start is None:
            return None
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].strip().startswith("```")), None)
    if end is None:
        return None
    return [ln.strip() for ln in lines[start + 1:end] if ln.strip()]


def check_step_range(skill, sop, evalset, errs):
    heads = [int(m.group(1)) for m in
             (RE_STEP_HEAD.match(ln) for ln in sop.splitlines()) if m]
    actual = max(heads) if heads else 0
    decls = []
    for ln in skill.splitlines():
        m = RE_STEP_DECL.search(ln) or RE_EVAL_DECL.search(ln)
        if m:
            decls.append(("SKILL.md", int(m.group(1))))
    for ln in sop.splitlines():
        m = RE_STEP_DECL.search(ln)
        if m:
            decls.append((SOP_FILE, int(m.group(1))))
    for ln in (evalset or "").splitlines():
        m = RE_EVAL_DECL.search(ln)
        if m:
            decls.append((EVAL_FILE, int(m.group(1))))
    if not decls:
        errs.append("[A] 未找到任何「1-N 顺序执行」声明（判据失锚）")
        return
    bad = [(f, n) for f, n in decls if n != actual]
    if bad:
        errs.append("[A] 步骤范围漂移：SOP 实际 1-%d，声明 %s"
                    % (actual, "；".join("%s=1-%d" % (f, n) for f, n in bad)))


def check_seal_block(skill, sop, errs):
    a = fence_block_after(skill, "📋 日记封口确认")
    b = fence_block_after(sop, "📋 日记封口确认")
    if not a or not b:
        errs.append("[B] 封口确认块缺失（SKILL.md=%s / SOP=%s）"
                    % ("OK" if a else "缺", "OK" if b else "缺"))
        return
    if a != b:
        diff = []
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else "<无>"
            y = b[i] if i < len(b) else "<无>"
            if x != y:
                diff.append("SKILL「%s」≠ SOP「%s」" % (x, y))
        errs.append("[B] 封口确认块形态分叉 %d 处：%s" % (len(diff), "；".join(diff[:3])))


def check_section_count(root, skill, tpl, errs):
    skel = read(root, SKELETON) or ""
    skel_names = set(RE_SECTION.findall(skel))
    tpl_names = set(RE_SECTION.findall(tpl)) - {"XXX"}
    # v1.1（2026-10-24）：re.search 只锚全文首处——SKILL.md 有两处「日常骨架 N」声明
    # （工作流D / 模板区），改非首处不红=假绿实证。判据须可枚举：finditer 全枚举逐一对账。
    daily_decls = [int(m.group(1)) for m in re.finditer(r"日常骨架\s*[=＝]?\s*(\d+)", skill)]
    full_decls = [int(m.group(1)) for m in re.finditer(r"全集\s*(\d+)", skill)]
    if not daily_decls or not full_decls:
        errs.append("[C] SKILL.md 缺「日常骨架 N / 全集 N」计数声明（判据失锚）")
        return
    for i, n in enumerate(daily_decls, 1):
        if n != len(skel_names):
            errs.append("[C] 日常骨架声明#%d=%d ≠ create_skeleton 实际 %d"
                        % (i, n, len(skel_names)))
    for i, n in enumerate(full_decls, 1):
        if n != len(tpl_names):
            errs.append("[C] SECTION 全集声明#%d=%d ≠ diary-template 唯一 SECTION %d"
                        % (i, n, len(tpl_names)))
    # 日常骨架 = 全集 - MILESTONES（有才显示）
    if len(skel_names) != len(tpl_names) - 1:
        errs.append("[C] 骨架 %d 与模板 %d 不是「仅差 MILESTONES」关系"
                    % (len(skel_names), len(tpl_names)))


def check_negative_family(files, errs):
    """否证族：旧形态回流即红。"""
    banned = [
        (r"检查\s*12\s*个\s*SECTION\s*是否齐全", "工作流D 旧口径「检查 12 个 SECTION」"),
        (r"含齐\s*12\s*个\s*SECTION", "月报 spec 旧口径「含齐12个SECTION」"),
    ]
    for rel, text in files.items():
        if text is None:
            continue
        for pat, desc in banned:
            if re.search(pat, text):
                errs.append("[D] 旧形态回流：%s @ %s" % (desc, rel))
    for rel in EXEC_FILES:
        text = files.get(rel)
        if text is None:
            continue
        for ln in text.splitlines():
            if "dbbin" in ln or "裸" in ln or "FAIL" in ln:
                continue
            if RE_BARE_CALL.search(ln):
                errs.append("[D] 裸 python3 调用硬依赖脚本 @ %s：%s" % (rel, ln.strip()[:60]))
    # E 骨架命令必须带 --out（stdout 模式不落盘·P4 动态面实证 2026-10-23）
    for rel in list(EXEC_FILES) + [EVAL_FILE]:
        text = files.get(rel)
        if text is None:
            continue
        for ln in text.splitlines():
            if "create_skeleton.py" in ln and "--date" in ln:
                if not RE_SKELETON_FULL.search(ln):
                    errs.append("[E] 骨架命令缺 --out（只打 stdout 不落盘）@ %s：%s"
                                % (rel, ln.strip()[:60]))


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--skill-root", default=os.path.join(here, ".."))
    a = ap.parse_args()
    root = os.path.abspath(a.skill_root)

    skill = read(root, "SKILL.md")
    sop = read(root, SOP_FILE)
    if skill is None or sop is None:
        print("PARITY:FAIL SKILL.md 或 SOP 不可达 @ %s" % root, file=sys.stderr)
        return 2

    files = {rel: read(root, rel) for rel in
             set(EXEC_FILES) | {EVAL_FILE, TPL_FILE, MONTHLY_SPEC}}
    evalset = files.get(EVAL_FILE)
    tpl = files.get(TPL_FILE) or ""

    errs = []
    check_step_range(skill, sop, evalset, errs)
    check_seal_block(skill, sop, errs)
    check_section_count(root, skill, tpl, errs)
    check_negative_family(files, errs)

    if errs:
        print("PARITY:FAIL 形态/计数闸 %d 项：" % len(errs), file=sys.stderr)
        for e in errs:
            print("   - %s" % e, file=sys.stderr)
        return 1
    print("PARITY:OK 步骤范围≡1-9·封口块同构·SECTION 11/12·否证族 0 命中")
    return 0


if __name__ == "__main__":
    sys.exit(main())
