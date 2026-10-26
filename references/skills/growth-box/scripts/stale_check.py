#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stale_check.py — 改版未复跑机检 tripwire（v1.0·2026-10-24·P0 断锚案防复发）

病根：v4.14.1 后两批改版未复跑 run.sh，引用闸红灯带病存活 30+ 小时（2026-10-24 沙箱实测）——
「改完必跑机检」原是纪律（prose），纪律必漂（立场卡 S257：检测机制靠"记得跑检测"的纪律会衰减）。
本件把判据挂到启动自检首序：SKILL.md/references/scripts/tests 任一源文件 mtime 晚于
logs/last_green_run（run.sh 全绿时自动写入）→ exit 1 = 改版未复跑，先跑 run.sh 再进流程。

用法：python3 scripts/stale_check.py [--self-test]
退出码：0=绿灯新鲜｜1=改版未复跑（或绿灯标记缺失）｜2=用法错误
诚实边界：本件证明「上次绿灯后源面没再动过」，不证明绿灯当时的内容现在仍适用；
run.sh 本体即复跑动作，本件只负责把"该跑了"在每次启动时显形出来（绕过留痕）。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os, sys

MARKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "logs", "last_green_run")
SCAN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
SCAN_DIRS = ("references", "scripts", "tests")
SKIP_DIRS = {"__pycache__", ".cache", "logs"}
SKIP_EXT = (".pyc", ".DS_Store")


def newest_source():
    """返回 (最新源文件相对路径, mtime)；扫描域=SKILL.md + references/scripts/tests 下 .md/.py/.sh。"""
    best, best_t = None, 0.0
    cand = [os.path.join(SCAN_ROOT, "SKILL.md")]
    for d in SCAN_DIRS:
        base = os.path.join(SCAN_ROOT, d)
        if not os.path.isdir(base):
            continue
        for dp, dns, fns in os.walk(base):
            dns[:] = [x for x in dns if x not in SKIP_DIRS]
            for fn in fns:
                if fn.endswith(SKIP_EXT) or not fn.endswith((".md", ".py", ".sh")):
                    continue
                cand.append(os.path.join(dp, fn))
    for p in cand:
        if os.path.isfile(p):
            t = os.path.getmtime(p)
            if t > best_t:
                best, best_t = os.path.relpath(p, SCAN_ROOT), t
    return best, best_t


def check(marker_path=None, root_newest=None):
    mp = marker_path or MARKER
    if not os.path.isfile(mp):
        return 1, "无绿灯标记（从未复跑机检或首装）→ 先跑 bash scripts/run.sh"
    newest, nt = root_newest if root_newest is not None else newest_source()
    mt = os.path.getmtime(mp)
    if newest and nt > mt:
        import datetime as dt
        return 1, "改版未复跑：源面最新改动 %s（%s）晚于绿灯标记（%s）→ 先跑 bash scripts/run.sh" % (
            newest, dt.datetime.fromtimestamp(nt).strftime("%m-%d %H:%M"),
            dt.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"))
    import datetime as dt
    return 0, "绿灯新鲜（标记 %s·源面无更新）" % dt.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M")


def _self_test():
    import tempfile, io as _io
    ok = True
    root = tempfile.mkdtemp(prefix="stale_")
    os.makedirs(os.path.join(root, "references"))
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "logs"))
    _io.open(os.path.join(root, "SKILL.md"), "w").write("x")
    src = os.path.join(root, "references", "flow-A.md")
    _io.open(src, "w").write("x")
    marker = os.path.join(root, "logs", "last_green_run")
    # P1 正例：标记晚于源 → 新鲜
    _io.open(src, "w").write("x")
    os.utime(src, (1000, 1000))
    _io.open(marker, "w").write("t")
    os.utime(marker, (2000, 2000))
    rc1, _ = check(marker, ("references/flow-A.md", 1000.0))
    print("  %s P1 正例：标记晚于源 → exit 0" % ("✅" if rc1 == 0 else "❌"))
    ok &= rc1 == 0
    # N1 负例：源晚于标记 → STALE
    os.utime(src, (3000, 3000))
    rc2, msg2 = check(marker, ("references/flow-A.md", 3000.0))
    print("  %s N1 负例：源晚于标记 → exit 1（%s）" % ("✅" if rc2 == 1 else "❌", "抓到" if rc2 == 1 else "漏报"))
    ok &= rc2 == 1
    # N2 负例：无标记 → STALE
    os.remove(marker)
    rc3, _ = check(marker, (None, 0.0))
    print("  %s N2 负例：标记缺失 → exit 1" % ("✅" if rc3 == 1 else "❌"))
    ok &= rc3 == 1
    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv[1:]:
        return _self_test()
    rc, msg = check()
    print(("✅" if rc == 0 else "🔴"), "stale_check:", msg)
    return rc


if __name__ == "__main__":
    sys.exit(main())
