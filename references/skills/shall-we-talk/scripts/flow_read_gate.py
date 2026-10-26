#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flow_read_gate.py — Shall We Talk 强制 Read 熔断器（机械形态·⛔不是 prose 提醒）

为什么有本件：SWT 是对话型 Skill，执行本体按消费点分三片下沉：
  flow-talk.md     启动后（Step 1-3 + 双角色）
  flow-sediment.md Step 4 前（六道锁全文 + 奥德赛 + 终身记忆）
  flow-review.md   阅读复习模式触发时
本件证明"该片文件在、够长、结构锚齐"；缺件/空壳/截断→exit 1 中止对应流程，
⛔不降级凭记忆裸奔。诚实边界：本件不证明内容正确；守恒由迁移断言 Δ=∅ 承担。

用法：
  python3 flow_read_gate.py                 # 三片全检（--all）
  python3 flow_read_gate.py --only talk     # 只检 talk/sediment/review
  python3 flow_read_gate.py --self-test
退出码：0=通过｜1=缺件/空壳/截断｜2=用法错误
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import sys

__version__ = "v1.0"
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "references")
FLOWS = {
    "talk": ("flow-talk.md", 8000, ("## 启动门禁与数据读取", "## 追问引擎", "## 双角色")),
    "sediment": ("flow-sediment.md", 4000, ("## 主动沉淀", "### 锁一", "### 锁六")),
    "review": ("flow-review.md", 800, ("阅读复习模式", "### 流程")),
}


def check(flows, root=None, min_bytes=None, markers=None):
    bad = []
    root = root or REF
    for key in flows:
        fname, base_min, base_markers = FLOWS[key]
        need = base_min if min_bytes is None else min_bytes
        marks = base_markers if markers is None else markers
        p = os.path.join(root, fname)
        if not os.path.exists(p):
            bad.append("%s 缺失" % fname); continue
        n = os.path.getsize(p)
        if n < need:
            bad.append("%s 仅 %d 字节（<%d＝疑似空壳/半覆盖）" % (fname, n, need))
        text = open(p, encoding="utf-8", errors="ignore").read()
        miss = [m for m in marks if m not in text]
        if miss:
            bad.append("%s 缺结构锚 %s（疑似截断残件）" % (fname, "、".join(miss)))
    return bad


def _self_test():
    import tempfile
    ok = True
    root = tempfile.mkdtemp(prefix="swtgate_")

    def write(key, body):
        open(os.path.join(root, FLOWS[key][0]), "w", encoding="utf-8").write(body)

    def good(key):
        fname, base, marks = FLOWS[key]
        return "\n".join(marks) + "\n" + ("x" * (base + 100))

    for k in FLOWS: write(k, good(k))
    p1 = check(FLOWS, root=root)
    print(("✅" if not p1 else "❌") + " P1 三片齐/够长/锚齐 → 通过（bad=%s）" % p1); ok &= not p1

    write("talk", "# 空\n"); p2 = check(("talk",), root=root)
    print(("✅" if p2 else "❌") + " N1 空壳必须被抓（bad=%s）" % p2); ok &= bool(p2)

    os.remove(os.path.join(root, "flow-sediment.md")); p3 = check(("sediment",), root=root)
    print(("✅" if p3 else "❌") + " N2 缺件必须被抓（bad=%s）" % p3); ok &= bool(p3)

    write("talk", "\n".join(FLOWS["talk"][2]) + "\n" + "x" * 100); p4 = check(("talk",), root=root)
    print(("✅" if p4 else "❌") + " N3 锚齐但过短必须被抓（bad=%s）" % p4); ok &= bool(p4)

    write("review", "x" * 1000); p5 = check(("review",), root=root)
    print(("✅" if p5 else "❌") + " N4 够长但缺锚（截断残件）必须被抓（bad=%s）" % p5); ok &= bool(p5)

    keep = dict(FLOWS)
    globals()["FLOWS"] = {k: (v[0], 1, ()) for k, v in FLOWS.items()}
    write("talk", "x" * 10); p6 = check(("talk",), root=root)
    globals()["FLOWS"] = keep
    print(("✅" if not p6 else "❌") + " MUT 阈值/锚集放宽后短件不再被抓（判据真在起作用）"); ok &= not p6

    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()
    if "--only" in a:
        i = a.index("--only")
        if i + 1 >= len(a):
            print("error: --only 后须跟 talk/sediment/review", file=sys.stderr); return 2
        keys = tuple(x for x in a[i + 1].split(",") if x in FLOWS)
        if not keys:
            print("error: --only 取值非法", file=sys.stderr); return 2
    else:
        keys = tuple(FLOWS)
    bad = check(keys)
    if bad:
        print("❌ 强制 Read 熔断器：%s 不合格 → 对应流程 🔴 禁止执行（⛔不降级裸奔）" % "/".join(keys))
        for b in bad: print("   ·", b)
        return 1
    print("✅ flow 装载单在位（%s）— 熔断器放行" % "/".join(keys))
    return 0


if __name__ == "__main__":
    sys.exit(main())
