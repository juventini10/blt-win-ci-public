#!/usr/bin/env python3
# REG: 通用件（脚本中心守卫族·§13.6 授权登记）·三包内副本为发布自包含投影（回接，同 orchestration_gate 通用件纪律）
# -*- coding: utf-8 -*-
r"""anchor_reach_check.py — 指针可达性抽测闸（v1.1·2026-10-24）
TRUTH_OF: 判据在本文件，⛔不在别处复制。
判据（零误报取向·只报机械可判）：
  A 文件可达：SKILL.md 出现的 `references/*.md` / `pages/*.md` 路径必存在
  B 节名可达：`path#§节名` 形态，节名必须是目标文件某标题的子串
advisory WARN（不计红）：纯 `§节名` 在本文件找不到同名标题（可能指外部规范，人眼判）
v1.1（2026-10-24·迁理之外测试批 N7b/N7c 对照实验实证根治）：路径字符类补
  \u4e00-\u9fa5·——v1.0 字符类 [A-Za-z0-9_./\-] 不含中文，中文命名 references
  （斯多葛.md/寓意与结算.md 等）整体落闸外：路径不检、死锚落 advisory 放行
  （ASCII 死锚红·中文死锚绿=同形态只差字符集）。全库 55 件损伤面预扫 0 死锚，
  放开无副作用。--selftest 内嵌正例+三类负例（ASCII死锚/中文死锚/死路径）。
用法：python3 scripts/anchor_reach_check.py [--skill-root DIR] [--selftest]
退出码：0=全可达/selftest 全过；1=存在断锚/selftest 有失守
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import io
import os
import re
import shutil
import sys
import tempfile

PATH_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_\u4e00-\u9fa5·\-]+\.md)")
ANCHOR_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_\u4e00-\u9fa5·\-]+\.md)#§([^\s`）)，,。;；、+]+)")
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


def check(root):
    """返回 (bad, paths, anchors, warn)；供 CLI 与 selftest 共用。"""
    skill = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill):
        return ["SKILL.md 不可达 %s" % skill], [], [], []
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
    return bad, paths, anchors, warn


def selftest():
    base = tempfile.mkdtemp(prefix="anchor_reach_selftest_")
    ok = True
    try:
        def run_case(name, expect_red, skill_body, refs):
            nonlocal ok
            root = os.path.join(base, name)
            os.makedirs(os.path.join(root, "references"), exist_ok=True)
            io.open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8").write(skill_body)
            for fn, content in refs.items():
                io.open(os.path.join(root, "references", fn), "w", encoding="utf-8").write(content)
            bad, paths, anchors, warn = check(root)
            red = bool(bad)
            good = red == expect_red
            if not good:
                ok = False
            print("%s %s%s" % ("✅" if good else "❌失守", name,
                               "" if good else " | bad=%s paths=%s" % (bad[:2], paths)))

        good_refs = {"中文件.md": "# 中文件\n\n## 存在节\n", "ascii.md": "# ascii\n\n## sec-one\n"}
        run_case("T0-正例(应绿)", False,
                 "# T\n\n看 `references/中文件.md` 与 `references/ascii.md`；实锚 references/中文件.md#§存在节。\n",
                 good_refs)
        run_case("N1-ASCII死锚(应红)", True,
                 "# T\n\n坏 references/ascii.md#§不存在的节XYZ\n", good_refs)
        run_case("N2-中文路径死锚(应红·v1.0盲区)", True,
                 "# T\n\n坏 references/中文件.md#§不存在的节XYZ\n", good_refs)
        run_case("N3-中文路径缺失(应红·v1.0盲区)", True,
                 "# T\n\n坏 `references/不存在的中文文件.md`\n", good_refs)
        run_case("N4-模板占位不误伤(应绿)", False,
                 "# T\n\n详见 `references/{视角}.md` 追问指南。\n", good_refs)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SELFTEST:%s（正例绿·负例3连红·占位符不误伤）" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = os.path.abspath(a.skill_root)
    bad, paths, anchors, warn = check(root)
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
