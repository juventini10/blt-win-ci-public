#!/usr/bin/env python3
# REG: 通用件（脚本中心守卫族·§13.6 授权登记）·三包内副本为发布自包含投影⛔回接（同 orchestration_gate 通用件纪律）
# -*- coding: utf-8 -*-
"""anchor_reach_check.py — 指针可达性抽测闸（growth-box 第三实例·v1.0·2026-10-23·次例原样复制）
TRUTH_OF: 判据在本文件，⛔不在别处复制。
判据（零误报取向·只报机械可判）：
  A 文件可达：SKILL.md 出现的 `references/*.md` / `pages/*.md` 路径必存在
  B 节名可达：`path#§节名` 形态，节名必须是目标文件某标题的子串
advisory WARN（不计红）：纯 `§节名` 在本文件找不到同名标题（可能指外部规范，人眼判）
用法：python3 scripts/anchor_reach_check.py [--skill-root DIR]
退出码：0=全可达；1=存在断锚
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

PATH_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_./\-]+\.md)")
ANCHOR_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_./\-]+\.md)#§([^\s`）)，,。;；、+]+)")
BARE_SEC_PAT = re.compile(r"§([A-Za-z0-9\u4e00-\u9fa5·\-]{2,16})")


def headings(path):
    if not os.path.isfile(path):
        return None
    out = []
    for line in io.open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"^#{1,6}\s+(.*)$", line.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    a = ap.parse_args()
    root = os.path.abspath(a.skill_root)
    skill = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill):
        print("ANCHOR:FAIL SKILL.md 不可达 %s" % skill, file=sys.stderr)
        return 1
    s = io.open(skill, encoding="utf-8").read()

    bad = []
    paths = sorted({m.group(1) for m in PATH_PAT.finditer(s)})
    for rel in paths:
        if not os.path.isfile(os.path.join(root, rel)):
            bad.append("文件不可达 %s" % rel)
    anchors = sorted({(m.group(1), m.group(2)) for m in ANCHOR_PAT.finditer(s)})
    for rel, sec in anchors:
        hs = headings(os.path.join(root, rel))
        if hs is None:
            bad.append("锚点目标缺失 %s#§%s" % (rel, sec))
            continue
        if not any(sec in h for h in hs):
            bad.append("节名不存在 %s#§%s" % (rel, sec))
    own = headings(skill) or []
    warn = []
    for m in BARE_SEC_PAT.finditer(s):
        sec = m.group(1)
        if not any(sec in h for h in own):
            warn.append(sec)
    warn = sorted(set(warn))

    if bad:
        print("ANCHOR:FAIL %d 处断锚（路径 %d·锚点 %d）：" % (len(bad), len(paths), len(anchors)), file=sys.stderr)
        for b in bad:
            print("   " + b, file=sys.stderr)
        return 1
    print("ANCHOR:OK 路径 %d 条可达·锚点 %d 条可锚（本文件无同名节的 §引用 %d 个=advisory 不计红）"
          % (len(paths), len(anchors), len(warn)))
    if warn:
        print("      advisory: " + "、".join(warn[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
