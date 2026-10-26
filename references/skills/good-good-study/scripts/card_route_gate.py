#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""card_route_gate.py — GGS 入库路由闸（v1.0·2026-10-24）

把「价值层卡必须转用户终审，⛔不自动入库」从条文变成 exit code：
  - frontmatter `level` 含「价值层」 或 `type` 含「价值」→ user_review（exit 1）
  - 其余 → auto_inbound（exit 0）
  - 缺 frontmatter/读不到 → user_review（fail-closed）

诚实边界：本闸只认**显式标注**的价值层；未标注但语义上是价值层的卡仍由
分身初审/用户终审兜底。本闸不判语义，只判“标签到了就必须转人”。

用法：python3 card_route_gate.py <卡.md> | --self-test
退出码：0=auto_inbound｜1=user_review｜2=用法错误
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import re
import sys
import tempfile

__version__ = "v1.0"


def _frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = text[3:end]
    out = {}
    for line in fm.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def route(text):
    fm = _frontmatter(text)
    if not fm:
        return "user_review", "缺 frontmatter（fail-closed）"
    level = fm.get("level", "")
    typ = fm.get("type", "")
    if "价值层" in level or "价值" in typ:
        return "user_review", "显式价值层（level=%s / type=%s）→ 转用户终审" % (level, typ)
    return "auto_inbound", "非价值层（level=%s / type=%s）→ 可自动入库" % (level, typ)


def self_test():
    tmp = tempfile.mkdtemp(prefix="ggsroute_")
    cases = [
        ("价值层 level", "---\ntopic: x\nlevel: 价值层\ntype: 价值\n---\n", "user_review"),
        ("价值层 type", "---\ntopic: x\ntype: 价值\n---\n", "user_review"),
        ("方法层", "---\ntopic: x\nlevel: 方法层\ntype: 方法\n---\n", "auto_inbound"),
        ("缺 frontmatter", "没有头\n", "user_review"),
    ]
    ok = True
    for name, text, want in cases:
        got, why = route(text)
        passed = got == want
        print(("✅PASS " if passed else "❌FAIL ") + name + " → %s（%s）" % (got, why))
        ok &= passed
    print("✅✅ 路由闸全过（%d 组）" % len(cases) if ok else "❌ 路由闸有失败")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return self_test()
    if len(a) != 1:
        print("用法: card_route_gate.py <卡.md> | --self-test", file=sys.stderr)
        return 2
    p = a[0]
    if not os.path.isfile(p):
        print("user_review")
        return 1
    got, why = route(open(p, encoding="utf-8", errors="replace").read())
    print(got)
    print("依据：" + why, file=sys.stderr)
    return 0 if got == "auto_inbound" else 1


if __name__ == "__main__":
    sys.exit(main())
