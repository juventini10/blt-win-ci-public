#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P6c references 全库常量+命令形态+流程号对账（daily-buddy v3.52.10）

v1.1（2026-10-24）：原 ROOT 硬编码作者机主源路径——用户机/沙箱/包内环境
FileNotFoundError 必炸，且沙箱测试时审计的是主源真身而非被测副本（变异被
"骗绿"实证）。对齐同族三闸口径：--skill-root 显式传入，默认值仍为主源
（裸调用向后兼容）。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import io, os, re, sys

# 权威值（SKILL.md 硬约束区）
AUTH = {
    "入睡": "23:30", "起床": "07:30",
    "睡眠时长": "≥7h", "睡眠严重": "<6h", "番茄": "≥16",
}


def main():
    ap = argparse.ArgumentParser(description="references 全库常量+命令形态+流程号对账")
    ap.add_argument("--skill-root",
                    default=os.path.expanduser("[记忆共享中心]/技能配置/daily-buddy"),
                    help="被审计的 skill 根目录（默认=作者机主源）")
    args = ap.parse_args()
    ROOT = os.path.abspath(args.skill_root)
    violations = []

    files = {}
    for root, dirs, fns in os.walk(os.path.join(ROOT, "references")):
        for fn in fns:
            if fn.endswith(".md"):
                files[fn] = os.path.join(root, fn)
    files["SKILL.md"] = os.path.join(ROOT, "SKILL.md")

    for fn, path in sorted(files.items()):
        if fn == "CHANGELOG.md":
            continue
        if not os.path.isfile(path):
            violations.append(f"[{fn}] 文件不存在: {path}")
            continue
        t = io.open(path, encoding="utf-8").read()
        # 1) 入睡阈值：出现 23:30 之外的入睡时间（如 00:00/22:00）即报
        for m in re.finditer(r"入睡[时约间]*[:：]?\s*(\d{1,2}:\d{2})", t):
            v = m.group(1)
            if v != "23:30":
                violations.append(f"[{fn}] 入睡阈值 {v} ≠ 权威 23:30")
        # 2) 番茄基线：出现 ≥N🍅 且 N≠16
        for m in re.finditer(r"≥\s*(\d+)\s*🍅", t):
            if m.group(1) != "16":
                violations.append(f"[{fn}] 番茄基线 {m.group(0)} ≠ 权威 ≥16🍅")
        # 3) dbbin 调用形态：出现裸 python3 调用硬依赖脚本（排除注释/否证）
        for i, ln in enumerate(t.splitlines(), 1):
            if "dbbin" in ln or "裸" in ln or "FAIL" in ln or "⛔" in ln or "#" == ln.strip()[:1]:
                continue
            if re.search(r"(?<![\w.])python3\s+\S*(finalize_diary|create_skeleton|verify_achievement_seal|check_concept_achievement)\.py", ln):
                violations.append(f"[{fn}:L{i}] 裸 python3 调用硬依赖脚本：{ln.strip()[:60]}")
        # 4) SECTION 计数口径：出现"12 个 SECTION"（旧口径）或"日常骨架=12"
        if re.search(r"12\s*个\s*SECTION\s*是否齐全", t):
            violations.append(f"[{fn}] 旧口径「检查 12 个 SECTION 是否齐全」回流")
        # 5) 流程号引用：周报SOP引用SKILL E步骤号；月报SOP引用F步骤号
        if fn == "weekly-review-sop.md":
            for m in re.finditer(r"SKILL\.md\s*第?\s*(\d+)\s*步", t):
                n = int(m.group(1))
                if n > 4:
                    violations.append(f"[{fn}] 引用 SKILL E 步骤 {n} 超出 E 流程范围(0-4)")

    if violations:
        print(f"❌ {len(violations)} 项不一致：")
        for v in violations:
            print(f"   - {v}")
        sys.exit(1)
    else:
        print(f"P6C:OK {len(files)} 文件全库对账·常量/命令/SECTION/流程号 0 不一致")
        sys.exit(0)


if __name__ == "__main__":
    main()
