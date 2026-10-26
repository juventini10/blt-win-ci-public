#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""template_parity_check.py — 结论块模板同构位齐闸（v1.0·2026-10-21·皮叔令「L1/L2/L3 每层都要改·要统一」）

TRUTH_OF: 模板同构位清单与必备件清单唯一真源=本文件常量（⛔不在别处复制清单）。
判据：每个模板位文件必含全部必备 token；缺任一件=FAIL（exit 1）。
覆盖：SKILL 共用模板 + L1×3 + L2 + L3 骨架 + 结果块示例（模板位机检面）。
计数对账：本闸同时核验 SKILL.md「全文N处模板同构」声明值与实测值一致（防计数漂移·v1.1）。
单元格锁：NEED 含「须用户字面确认」（v1.2·2026-10-24 童灵根治批——行名锁不锁单元格，待你行三分叉曾静默存活）。
分层件锁：NEED_SCOPED（v1.3·2026-10-25 clock-loop E 路径独立盲审 P4 根治——扁平表抓不到层级专属行）
用法：python3 scripts/template_parity_check.py [--skill-root DIR]
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import io, os, sys, argparse

FILES = [
    "SKILL.md",
    "references/l1/first-principles.md",
    "references/l1/abstraction.md",
    "references/l1/critical-verify.md",
    "references/l2/dual-routes.md",
    "references/l3/full-flow.md",
    "references/shared/result-block-examples.md",
]
NEED = ["认知格", "出表三段式", "依据（含档位", "🎯 结果", "证据等级", "下一步·待你", "下一步·系统", "负担闸", "单签名行", "须用户字面确认"]  # v1.2(2026-10-24·童灵根治批):+单元格级token——行名锁不锁单元格,待你行三分叉曾静默存活(沙箱实证)

# v1.3(2026-10-25·clock-loop E 路径独立盲审 P4 根治)：分层必备件——只要求出现在**承载该层的文件**里。
#   病名：L3/L2 专属行无法进扁平 NEED（L1 文件本就不该含它），故"唯一源模板缺行"在旧闸下不可逮=机检假绿面。
#   负例保护=tests/test_parity_scoped.py（删任一分层件→判红），⛔不加负例的新锁等于没锁。
# 判据形态取该件现行**最严格写法**：表格行用单元格形态（`| X |`），注记/段头用裸词——
#   病名（v1.3 首跑自曝）：原判据全用裸词，SKILL 的「分层增量正名」声明行自身含该词，
#   于是真删表格行仍判绿（token 在场≠语义在场，与 P4 原病同族）。单元格形态才拦得住删行。
NEED_SCOPED = [
    ("| Agent B验证 |", ["SKILL.md", "references/shared/result-block-examples.md"]),
    ("【Agent B验证行", ["references/l3/full-flow.md"]),
    # N-4 根治（独立复核 M7b 实锤：把 dual-routes 该段实质抽空、只留"验证架构"四字→仍判 OK）：
#   prose 件不能只锁词形，须同锁**实质标记**（差异外显的内容骨架）——"留词去义"即判红。
    ("单Agent 自检链", ["references/l2/dual-routes.md", "references/shared/result-block-examples.md"]),
    ("| 验证架构 |", ["SKILL.md"]),
    ("验证架构", ["references/l2/dual-routes.md", "references/shared/result-block-examples.md"]),
]

SIG_TOKEN = "[\U0001F9E0 三明智 L"

def count_sig_templates(root):
    """实测模板处数：SKILL.md + references/**/*.md（⛔排除 CHANGELOG 历史叙述）"""
    total, per = 0, {}
    paths = [os.path.join(root, "SKILL.md")]
    for d, _, fs in os.walk(os.path.join(root, "references")):
        for f in fs:
            if f.endswith(".md") and f != "CHANGELOG.md":
                paths.append(os.path.join(d, f))
    for p in paths:
        if not os.path.isfile(p):
            continue
        s = io.open(p, encoding="utf-8", errors="ignore").read()
        n = s.count(SIG_TOKEN)
        if n:
            per[os.path.relpath(p, root)] = n
            total += n
    return total, per

def check_narrative_count(root):
    """SKILL.md「全文N处模板同构」声明 vs 实测（v1.1·防 P2 型计数漂移）"""
    import re as _re
    skill = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill):
        print("COUNT:SKIP SKILL.md 不可达", file=sys.stderr)
        return False
    s = io.open(skill, encoding="utf-8").read()
    m = _re.search(r"全文(\d+)处模板同构", s)
    if not m:
        print("COUNT:FAIL SKILL.md 缺「全文N处模板同构」声明行（不得静默跳过）", file=sys.stderr)
        return True
    declared = int(m.group(1))
    actual, per = count_sig_templates(root)
    if declared != actual:
        print("COUNT:FAIL 声明 %d 处 != 实测 %d 处（模板位明细：%s）" % (declared, actual, per), file=sys.stderr)
        return True
    print("COUNT:OK 模板处数声明 %d == 实测 %d" % (declared, actual))
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    a = ap.parse_args()
    root = os.path.abspath(a.skill_root)
    bad = []
    for f in FILES:
        p = os.path.join(root, f)
        if not os.path.isfile(p):
            bad.append((f, ["文件缺失"])); continue
        s = io.open(p, encoding="utf-8").read()
        miss = [n for n in NEED if n not in s]
        if miss: bad.append((f, miss))
    scoped_bad = []
    for tok, files in NEED_SCOPED:
        for f in files:
            p = os.path.join(root, f)
            if not os.path.isfile(p):
                scoped_bad.append((f, tok, "文件缺失"))
                continue
            if tok not in io.open(p, encoding="utf-8").read():
                scoped_bad.append((f, tok, "分层件缺失"))
    n_bad = check_narrative_count(root)
    if scoped_bad:
        bad.extend([(f, [t]) for f, t, _ in scoped_bad])
    if bad:
        print("PARITY:FAIL 模板同构位缺件：", file=sys.stderr)
        for f, m in bad:
            print("   %s → %s" % (f, "、".join(m)), file=sys.stderr)
        return 1
    if n_bad:
        return 1
    print("PARITY:OK %d 文件 × %d 通用件 + %d 分层件 全齐（L1×3/L2/L3/示例/SKILL 同构·分层件按归属层判）" % (
        len(FILES), len(NEED), len(NEED_SCOPED)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
