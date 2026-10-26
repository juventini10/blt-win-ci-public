#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_t9_trail_teeth.py — T9 回执机制双向牙齿测试（常驻·2026-10-23 T9转单卡判据2固化）
正方向：W4 夹具注入假坑（clean 侧 guard 输出 skill_lead=1）→ ok=False + 快照落盘 + 现场含 TREE/CMD；
反方向：还原后 W4 ok=True 且不自证误报。
防的是：T9 红时无取证（读数分裂不可判）——快照/回执通道哑掉=机制白装（S138 双向）。
用法：python3 tests/test_t9_trail_teeth.py（退出码 0=牙齿在）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import io, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "scripts"))
import immunity_l1_draft as m

SNAP = os.path.join(HERE, os.pardir, "logs", "t9_fail_snapshot_W4.txt")

def main():
    orig = m.POSITIVE["W4"][1]
    def inject_fake_pit(r):
        p = orig(r)
        for root, _, fs in os.walk(r):
            for f in fs:
                if f == "skill_version_guard.sh":
                    with open(os.path.join(root, f), "w") as gf:
                        gf.write('#!/bin/sh\necho \'{"skills_with_version": 9, "skill_lead": 1, "alarm": true}\'\n')
        return p
    for f in glob.glob(SNAP):
        os.remove(f)
    m.POSITIVE["W4"] = (m.POSITIVE["W4"][0], inject_fake_pit)
    try:
        res, _ = m.run_positive_controls(wids=["W4"], quiet=True)
        wid, ok, hp, hc, _loc = res[0]
        assert ok is False, "变异未咬：ok=%s（检波器或牙齿哑了）" % ok
        assert os.path.exists(SNAP), "红现场快照未落盘"
        snap = io.open(SNAP, encoding="utf-8").read()
        for probe in ("ROOT=", "TREE:", "CMD=", "skill_version_guard.sh"):
            assert probe in snap, "快照缺字段 %s" % probe
        print("✅ 正方向：假坑→判红→快照含现场（TREE/CMD 齐）")
    finally:
        m.POSITIVE["W4"] = (m.POSITIVE["W4"][0], orig)
    res2, rc2 = m.run_positive_controls(wids=["W4"], quiet=True)
    assert res2[0][1] is True and rc2 == 0, "还原后不误报失败"
    print("✅ 反方向：还原→判绿（无恒红误报）")
    for f in glob.glob(SNAP):
        os.remove(f)
    print("TEETH:OK T9 取证通道双向活着")
    return 0

if __name__ == "__main__":
    sys.exit(main())
