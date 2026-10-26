#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flow_read_gate.py — system-logger 强制 Read 熔断器（机械形态·⛔不是 prose 提醒）

为什么要有本件（复制 growth-box 卡B 范式·不复制内容）：SKILL.md 把写入流程步骤本体
下沉到 references/flow-write.md 后，"读到 flow 正文"从"整份内容在场"变成"多一次 Read"
——这一步失败就是拆分新造的漂移点。prose 提醒靠自觉，故升级为脚本 exit code 物理拦截
（依 Skill架构规范 §十二迁移纪律 + §5.7 防误>防错）。

用法：
  python3 flow_read_gate.py              # 校验 flow-write.md 装载单在位且非空壳
  python3 flow_read_gate.py --self-test  # 正例＋负例（缺文件/空壳必须被抓）＋变异检验
退出码：0=通过｜1=flow 文件缺失或空壳（🔴 写入流程禁止执行，⛔不降级裸奔）｜2=用法错误
诚实边界：本件证明"文件在且非空壳"，不证明"内容正确"；内容守恒由迁移断言（Δ=∅）与
T3 收尾链 eval 复验承担。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import sys, os

__version__ = "v1.0"
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "references")
FLOW = "flow-write.md"
MIN_BYTES = 4096  # 本体 326+16 行迁移后 ≈14KB；<4096＝占位未落或半覆盖（对齐 growth-box 同判据思想）


def check(min_bytes=None, root=None):
    # min_bytes 运行时读全局（⛔不用 def 默认值冻结——growth-box 母本 MUT 首课）
    if min_bytes is None:
        min_bytes = MIN_BYTES
    bad = []
    root = root or REF
    p = os.path.join(root, FLOW)
    if not os.path.exists(p):
        bad.append("%s 缺失" % FLOW)
    else:
        n = os.path.getsize(p)
        if n < min_bytes:
            bad.append("%s 仅 %d 字节（<%d＝疑似空壳/半覆盖）" % (FLOW, n, min_bytes))
    return bad


def _self_test():
    global MIN_BYTES
    import tempfile
    ok = True
    root = tempfile.mkdtemp(prefix="slgate_")
    open(os.path.join(root, FLOW), "w", encoding="utf-8").write("x" * (MIN_BYTES + 10))
    p1 = check(root=root)
    print("  %s P1 正例：件在且够长 → 通过（bad=%s）" % ("✅" if not p1 else "❌", p1))
    ok &= not p1
    os.remove(os.path.join(root, FLOW))
    p2 = check(root=root)
    print("  %s N1 负例：删掉文件必须被抓（bad=%s）" % ("✅" if p2 else "❌", p2))
    ok &= bool(p2)
    open(os.path.join(root, FLOW), "w", encoding="utf-8").write("# 空壳\n")
    p3 = check(root=root)
    print("  %s N2 负例：空壳文件必须被抓（bad=%s）" % ("✅" if p3 else "❌", p3))
    ok &= bool(p3)
    keep = MIN_BYTES
    MIN_BYTES = 1
    p4 = check(root=root)          # 阈值改坏 → 空壳必过（证明判据非恒真）
    MIN_BYTES = keep
    mutated = (not p4)
    print("  %s MUT 变异：阈值降为 1 后空壳不再被抓（＝该判据真的在起作用）" % ("✅" if mutated else "❌"))
    ok &= mutated
    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()
    if a:
        print("error: 未知参数（支持 --self-test）", file=sys.stderr); return 2
    bad = check()
    if bad:
        print("❌ 强制 Read 熔断器：flow 装载单不合格 → 写入流程 🔴 禁止执行（⛔不降级裸奔）")
        for b in bad:
            print("   ·", b)
        print("   → 补法：从 git 恢复 references/%s（本件只证「在且非空壳」，不证内容正确）" % FLOW)
        return 1
    print("✅ flow 装载单在位（%s·≥%d 字节）— 熔断器放行" % (FLOW, MIN_BYTES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
