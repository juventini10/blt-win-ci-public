#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flow_read_gate.py — sucair 强制 Read 熔断器（机械形态·⛔不是 prose 提醒）

为什么要有本件（复制 system-logger / growth-box 卡B 范式·不复制内容）：SKILL.md 把
执行本体（执行流程+自检清单）下沉到 references/flow-read.md 后，"读到 flow 正文"
从"整份内容在场"变成"多一次 Read"——这一步失败就是拆分新造的漂移点。prose 提醒
靠自觉，故升级为脚本 exit code 物理拦截（依 Skill架构规范 §十二迁移纪律 + §1.1 防误>防错）。

用法：
  python3 flow_read_gate.py              # 校验 flow-read.md 在位且非空壳/非截断残件
  python3 flow_read_gate.py --self-test  # 正例＋负例（缺文件/空壳/残件必须被抓）＋变异检验
退出码：0=通过｜1=flow 文件缺失或空壳/残件（🔴 执行流程禁止执行，⛔不降级裸奔）｜2=用法错误
诚实边界：本件证明"文件在、够长、全部结构锚在场"，不证明"内容正确"；内容守恒由
迁移断言（Δ=∅）与 T3 eval 复验承担。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import sys, os

__version__ = "v1.1"
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "references")
FLOW = "flow-read.md"
MIN_BYTES = 8000  # 本体约 38KB；<8000＝占位未落或半覆盖替换
MARKERS = ("## 🛡️ 自检清单", "### Step 1", "### Step 2", "### Step 2.0", "### Step 3", "### Step 4")


def check(min_bytes=None, root=None, markers=None):
    # 运行期读全局（⛔不用 def 默认值冻结——growth-box 母本 MUT 首课）
    if min_bytes is None:
        min_bytes = MIN_BYTES
    if markers is None:
        markers = MARKERS
    bad = []
    root = root or REF
    p = os.path.join(root, FLOW)
    if not os.path.exists(p):
        bad.append("%s 缺失" % FLOW)
        return bad
    n = os.path.getsize(p)
    if n < min_bytes:
        bad.append("%s 仅 %d 字节（<%d＝疑似空壳/半覆盖）" % (FLOW, n, min_bytes))
    text = open(p, encoding="utf-8", errors="ignore").read()
    miss = [m for m in markers if m not in text]
    if miss:
        bad.append("%s 缺结构锚 %s（疑似截断残件）" % (FLOW, "、".join(miss)))
    return bad


def _self_test():
    global MIN_BYTES, MARKERS
    import tempfile
    ok = True
    root = tempfile.mkdtemp(prefix="sucair_gate_")

    def write(body):
        open(os.path.join(root, FLOW), "w", encoding="utf-8").write(body)

    good = "\n".join(MARKERS) + "\n" + "x" * (MIN_BYTES + 10)
    write(good)
    p1 = check(root=root)
    print("  %s P1 正例：件在、够长、六锚齐 → 通过（bad=%s）" % ("✅" if not p1 else "❌", p1))
    ok &= not p1
    os.remove(os.path.join(root, FLOW))
    p2 = check(root=root)
    print("  %s N1 负例：删掉文件必须被抓（bad=%s）" % ("✅" if p2 else "❌", p2))
    ok &= bool(p2)
    write("# 空壳\n")
    p3 = check(root=root)
    print("  %s N2 负例：空壳文件必须被抓（bad=%s）" % ("✅" if p3 else "❌", p3))
    ok &= bool(p3)
    write("\n".join(MARKERS) + "\n" + "x" * 100)
    p4 = check(root=root)
    print("  %s N3 负例：锚齐但过短（半覆盖）必须被抓（bad=%s）" % ("✅" if p4 else "❌", p4))
    ok &= bool(p4)
    write("x" * (MIN_BYTES + 10))
    p5 = check(root=root)
    print("  %s N4 负例：够长但缺结构锚（截断残件）必须被抓（bad=%s）" % ("✅" if p5 else "❌", p5))
    ok &= bool(p5)

    keep = MIN_BYTES
    MIN_BYTES = 1
    write("\n".join(MARKERS) + "\n" + "x" * 100)
    p6 = check(root=root)          # 阈值改坏 → 短件必过（证明长度判据非恒真）
    MIN_BYTES = keep
    print("  %s MUT-a 变异：阈值降为 1 后短件不再被抓（＝长度判据真在起作用）" % ("✅" if not p6 else "❌"))
    ok &= not p6

    keep_m = MARKERS
    MARKERS = ()
    write("x" * (MIN_BYTES + 10))
    p7 = check(root=root)          # 锚集清空 → 无锚件必过（证明锚判据非恒真）
    MARKERS = keep_m
    print("  %s MUT-b 变异：锚集清空后缺锚件不再被抓（＝锚判据真在起作用）" % ("✅" if not p7 else "❌"))
    ok &= not p7

    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return _self_test()
    if a:
        print("error: 未知参数（支持 --self-test）", file=sys.stderr)
        return 2
    bad = check()
    if bad:
        print("❌ 强制 Read 熔断器：flow 装载单不合格 → 执行流程 🔴 禁止执行（⛔不降级裸奔）")
        for b in bad:
            print("   ·", b)
        print("   → 补法：从 git 恢复 references/%s（本件只证「在/够长/锚齐」，不证内容正确）" % FLOW)
        return 1
    print("✅ flow 装载单在位（%s·≥%d 字节·全部结构锚齐）— 熔断器放行" % (FLOW, MIN_BYTES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
