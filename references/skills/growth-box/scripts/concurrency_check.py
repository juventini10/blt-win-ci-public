#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""concurrency_check.py — 多会话并发互见检查（v1.0·2026-10-24·三会话走廊实证根治）

病根（2026-10-24 实测）：三个会话并行写成长箱面（流程A/E），互相不知道对方的写入——
并行会话已落 E3.5 批 5 条，本会话靠铁律-028 全载体扫描才避免重复立卡（运气+纪律，非机制）；
pyc 被并行进程 force-add 进他人 commit。G2 指纹去重只管 CANDIDATES 采集通道，
不管会话间人工流程 A/E 的并发去重——写入前互见 = 把"静默互不知"改成"显形互见"。

判据（exit 1=有并发信号·显形不阻断，写入方须先 Read 对账防重复）：
  A 近 30 分钟内 LEARNINGS.md / 规范反哺日志.md / INDEX.md 任一被写过（mtime）
  B git status 三文件存在未提交改动（工作树脏=可能他方在写·仅在真实档案树启用）
用法：python3 scripts/concurrency_check.py [--self-test] [--window-minutes N]
退出码：0=无并发信号｜1=有并发信号（先对账再写）｜2=用法错误
诚实边界：本件只显形信号，不证明"没有并发"（窗外/未落盘的内存态并发不可见）——
它把检查从"靠会话自觉扫描"降为"每次启动自检必跑的机械步"。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os, sys, time, io, subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
DATA_FILES = [
    os.path.expanduser("[记忆共享中心]/成长箱/learnings/LEARNINGS.md"),
    os.path.expanduser("[记忆共享中心]/成长箱/experience/规范反哺日志.md"),
    os.path.expanduser("[记忆共享中心]/成长箱/learnings/INDEX.md"),
]
GIT_ROOT = os.path.expanduser("[记忆共享中心]")
DEFAULT_WINDOW = 30  # 分钟


def check(window_min=DEFAULT_WINDOW, now=None, run_git=True):
    now = now or time.time()
    signals = []
    for p in DATA_FILES:
        if not os.path.isfile(p):
            continue
        age_min = (now - os.path.getmtime(p)) / 60.0
        if age_min < window_min:
            signals.append("A 近写入: %s（%.0f 分钟前）" % (os.path.basename(p), age_min))
    if run_git:
        try:
            rels = [os.path.relpath(p, GIT_ROOT) for p in DATA_FILES]
            r = subprocess.run(["git", "status", "--short", "--"] + rels,
                               cwd=GIT_ROOT, capture_output=True, text=True, timeout=15)
            for l in r.stdout.splitlines():
                if l.strip():
                    signals.append("B 未提交改动: " + l.strip()[:90])
        except Exception:
            pass  # 非 git 环境降级：A 判据独立成立
    return signals


def _self_test():
    import tempfile, shutil
    ok = True
    d = tempfile.mkdtemp(prefix="conc_")
    f1 = os.path.join(d, "LEARNINGS.md")
    io.open(f1, "w", encoding="utf-8").write("x")
    global DATA_FILES
    keep = list(DATA_FILES)
    try:
        DATA_FILES[:] = [f1]
        s1 = check(window_min=30, now=time.time(), run_git=False)
        print("  %s P1 正例：30 分钟内有写入 → 信号（%d 条）" % ("✅" if s1 else "❌", len(s1)))
        ok &= bool(s1)
        os.utime(f1, (time.time() - 7200, time.time() - 7200))
        s2 = check(window_min=30, now=time.time(), run_git=False)
        print("  %s P2 反例：2 小时前写入 → 无信号（%d 条）" % ("✅" if not s2 else "❌", len(s2)))
        ok &= not s2
        s3a = check(window_min=90, now=time.time(), run_git=False)
        s3b = check(window_min=130, now=time.time(), run_git=False)
        moved = (not s3a) and bool(s3b)
        print("  %s P3 变异：90 分钟窗放过 120min 前写入、130 分钟窗抓到（%d/%d 条·证 window 边界在移动非恒真装饰）" % ("✅" if moved else "❌", len(s3a), len(s3b)))
        ok &= moved
    finally:
        DATA_FILES[:] = keep
    shutil.rmtree(d, ignore_errors=True)
    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv[1:]:
        return _self_test()
    window = DEFAULT_WINDOW
    if "--window-minutes" in sys.argv[1:]:
        window = int(sys.argv[sys.argv.index("--window-minutes") + 1])
    signals = check(window_min=window)
    if signals:
        print("⚠️ 并发互见：检测到 %d 条他方写入信号（窗口 %d 分钟）——写入候选/条目前先 Read 对账防重复：" % (len(signals), window))
        for s in signals[:6]:
            print("   ·", s)
        return 1
    print("✅ 并发互见：近 %d 分钟无他方写入信号（三写入面干净）" % window)
    return 0


if __name__ == "__main__":
    sys.exit(main())
