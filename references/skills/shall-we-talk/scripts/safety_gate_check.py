#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""safety_gate_check.py — SWT 三缺+交接闸（D1/W3/J1/绝对时间闸/数据更正·v1.7.1-1.7.3 口径）

为什么有本件：2026-10-23 真机 dog-fooding 暴露三缺，且旧 run.sh 全绿——
说明三缺都不在机检面。本件把三缺变成**可被删除即红**的机械标记：
  D1：主件「数据质量门」+ flow「数据缺口 ≠ 行为缺口」
  W3：主件「W3 硬停」+「23:30」+ flow「每问时钟闸」
  J1：主件/flow「判官前置」+「AI假设·待你否决」
  v1.7.2/1.7.3 扩展：绝对时间闸（00:30）/数据更正/候选/日记=真相源（main+flow 共 20 标记）

判据：正例全在 exit 0；对任一标记做删除变异必须 exit 1（闸没牙=exit 1）。
诚实边界：本件只证「机制条文在位」，不证真机执行质量（那由 dog-fooding 回放承担）。
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import sys

__version__ = "v1.1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {
    "main": "SKILL.md",
    "flow": os.path.join("references", "flow-talk.md"),
}
REQUIRED = {
    "main": ("数据质量门", "W3 硬停", "23:30", "00:30", "数据更正", "候选", "日记=真相源", "判官前置", "AI假设·待你否决"),
    "flow": ("数据质量门（D1", "数据缺口 ≠ 行为缺口", "数据更正交接", "候选更正", "日记=真相源", "待补记→daily-buddy",
             "W3 硬停", "绝对时间闸", "每问时钟闸", "判官前置（J1", "AI假设·待你否决"),
}


def load():
    texts = {}
    for key, rel in FILES.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            raise SystemExit("❌ 缺件：%s" % p)
        with open(p, encoding="utf-8") as f:
            texts[key] = f.read()
    return texts


def missing(texts):
    out = []
    for key, marks in REQUIRED.items():
        for m in marks:
            if m not in texts[key]:
                out.append("%s:%s" % (key, m))
    return out


def main():
    texts = load()
    miss = missing(texts)
    if miss:
        print("❌ 三缺闸标记缺失：%s" % "、".join(miss))
        return 1
    total = sum(len(v) for v in REQUIRED.values())
    print("✅ 三缺闸标记在位：%d/%d（D1 数据质量 / W3 硬停 / J1 判官前置）" % (total, total))

    fail = 0
    for key, marks in REQUIRED.items():
        for m in marks:
            mutated = dict(texts)
            mutated[key] = texts[key].replace(m, "")
            if mutated[key] == texts[key]:
                print("❌MUT-NOOP %s:%s" % (key, m))
                fail += 1
                continue
            caught = m in missing(mutated) or any(x.endswith(":" + m) for x in missing(mutated))
            print(("✅RED" if caught else "❌GREEN(闸没牙!)") + " %s:%s" % (key, m))
            fail += 0 if caught else 1
    if fail:
        print("❌ 变异检验失败 %d 项" % fail)
        return 1
    print("✅✅ 三缺闸变异全红（%d 项）" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
