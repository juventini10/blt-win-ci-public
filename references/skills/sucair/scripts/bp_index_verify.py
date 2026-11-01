# -*- coding: utf-8 -*-
"""bp_index_verify.py v1.0 — 母卡(blueprint-index)等价机验：source_files 在位核验。
# REG: skip 生产线机检件（sucair scripts 族·非守卫注册表管辖）——登记面=蓝图卡任务卡§四十八+sucair CHANGELOG v4.20.0
动因：任务卡§十-6 挂账「46母卡 trust 装饰字段」——母卡面声明 machine-confirmed 但
无 verified: 字段喂引擎 trust_of()，声明态≠运行态。本件补最小等价机验（文件在位级，
⛔引文级——母卡无逐字引文承重，硬上引文闸=过度工程）。
判据：全部 source_files 在 source_path 实盘存在 → 过；任一缺失 → 挂(⛔升 trust)。
自测五例内置：--selftest（正/负/空/目录缺失/类型不误检），未过夹具⛔对真库出结论。
用法：
  python3 bp_index_verify.py --selftest
  python3 bp_index_verify.py --run [--apply]   # --apply=对过验卡双写 verified:
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import os, sys, glob, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 真源在 sucair scripts 族（工作区副本位同样可跑·双候选路径）
for _cand in (os.path.expanduser("[记忆共享中心]/技能配置/sucair/scripts"),):
    if _cand not in sys.path and os.path.isdir(_cand):
        sys.path.insert(0, _cand)
from note_validator import parse_frontmatter

POOL = os.path.expanduser("~/[日记仓库]/2-知识库/10-蓝图索引卡")
VERIFIED_LINE = 'verified:\n  - "machine:bp_index_verify v1.0"\n'


def check_card(path):
    """返回 (verdict, detail)。verdict: pass/fail/no-src/skip/parse-err"""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        return "parse-err", str(e)
    fm, _ = parse_frontmatter(text)
    if not fm or fm.get("type") != "blueprint-index":
        return "skip", "非 blueprint-index"
    sp = (fm.get("source_path") or "").strip()
    sfs = fm.get("source_files") or []
    if not isinstance(sfs, list):
        sfs = [sfs]
    sfs = [str(x).strip() for x in sfs if str(x).strip()]
    if not sfs:
        return "no-src", "source_files 空"
    if not sp or not os.path.isdir(os.path.expanduser(sp)):
        return "fail", "source_path 目录缺失: %r" % sp
    miss = [f for f in sfs
            if not _file_decl_resolves(os.path.expanduser(sp), f)]
    if miss:
        return "fail", "缺 %d/%d: %s" % (len(miss), len(sfs), miss[:3])
    return "pass", "%d/%d 在位" % (len(sfs), len(sfs))


def _file_decl_resolves(root, decl):
    """源文件声明解析：真文件/真目录在位即过；带 glob 花括号/星号的聚合声明⛔静默放过——
    声明本身不可机械回指=判据缺陷（本轮真跑逮出 3 例），必须红着暴露。"""
    base = os.path.join(root, decl.split("#")[0].strip())
    return os.path.exists(base)


def _mkcard(d, name, source_path, files, ftype="blueprint-index"):
    p = os.path.join(d, name + ".md")
    sf = "\n".join('  - "%s"' % f for f in files) if files else ""
    open(p, "w", encoding="utf-8").write(
        "---\ntype: %s\ncard_id: 蓝图索引卡-%s\nsource_path: %s\nsource_files:\n%s\n---\n\n## 覆盖\n" % (ftype, name, source_path, sf))
    return p


def selftest():
    tmp = tempfile.mkdtemp(prefix="bpidx-selftest-")
    ok = True
    try:
        src = os.path.join(tmp, "srcdir"); os.makedirs(os.path.join(src, "sub"))
        open(os.path.join(src, "sub", "b.md"), "w").write("x")
        open(os.path.join(src, "a.md"), "w").write("x")
        p1 = _mkcard(tmp, "t1", src, ["a.md", "sub/b.md"])
        v1 = check_card(p1)[0]; ok &= v1 == "pass"
        print("T1 正例在位(含子目录递归):", v1, "OK" if v1 == "pass" else "FAIL")
        p2 = _mkcard(tmp, "t2", src, ["a.md", "ghost.md"])
        v2 = check_card(p2)[0]; ok &= v2 == "fail"
        print("T2 负例缺文件必红:", v2, "OK" if v2 == "fail" else "FAIL")
        p3 = _mkcard(tmp, "t3", src, [])
        v3 = check_card(p3)[0]; ok &= v3 == "no-src"
        print("T3 空集判no-src(不当绿):", v3, "OK" if v3 == "no-src" else "FAIL")
        p4 = _mkcard(tmp, "t4", os.path.join(tmp, "nodir"), ["a.md"])
        v4 = check_card(p4)[0]; ok &= v4 == "fail"
        print("T4 目录缺失必红:", v4, "OK" if v4 == "fail" else "FAIL")
        p5 = _mkcard(tmp, "t5", src, ["a.md"], ftype="blueprint-card")
        v5 = check_card(p5)[0]; ok &= v5 == "skip"
        print("T5 细卡不误检:", v5, "OK" if v5 == "skip" else "FAIL")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST", "ALL-PASS" if ok else "RED")
    return 0 if ok else 1


def run(apply_: bool):
    cards = sorted(glob.glob(os.path.join(POOL, "蓝图索引卡-*.md")))
    passed, failed, skipped = [], [], []
    for p in cards:
        v, detail = check_card(p)
        if v == "pass":
            passed.append(p)
            if apply_:
                t = open(p, encoding="utf-8").read()
                head = t.split("---\n")
                if len(head) >= 3 and "verified:" not in head[1]:
                    head[1] = head[1].rstrip("\n") + "\n" + VERIFIED_LINE
                    open(p, "w", encoding="utf-8").write("---\n".join(head))
        elif v == "skip":
            skipped.append(p)
        else:
            failed.append((p, v, detail))
    print("母卡机验：%d 张在册｜过验 %d｜挂红 %d｜跳过 %d" % (len(cards), len(passed), len(failed), len(skipped)))
    for p, v, d in failed[:12]:
        print("  RED", os.path.basename(p), "=>", v, d)
    if apply_:
        print("已对过验卡双写 verified（声明态→运行态接通）：%d 张" % len(passed))
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run("--apply" in sys.argv))
