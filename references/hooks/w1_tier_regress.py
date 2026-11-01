#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1_tier_regress.py v1.0（2026-10-07 童灵D3·假触发根治轮·预注册判据先行·铁律-020/S875）
引擎本体回归网：直接 import doenglingz_inject_prompt.w1_fired 跑判组。
用例来源全绑实录：POS=真召唤应上岗；NEG=被谈论的召唤应静默。
预注册期望（改动写下前锁定）：
  - n2「没有说启动童灵」引用式、n3「要启动成长箱…么？」是非问句形 = 本轮两假触发实录，修复前应红
  - p3 09-23 判例、p1/p2 肯定式口令 修复后必须仍绿（防矫枉过正）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import importlib.util, os, sys

# ── 被测脚本路径解析（2026-10-08·判据=verifier_target_fidelity_guard 路径保真）──
# 病根：原式硬编码 `[记忆共享中心]/脚本中心/...` ⇒ 换落点/多端时测到另一份，回归器仍可能报全绿。
# 判据：脚本 TARGET 必须解析自 runtime_paths；降级按候选探测 + stderr 显形。
def _resolve_devtools(name):
    import json as _json
    base = None
    rp = os.path.expanduser("~/.hermes/doenglingz/runtime_paths.json")
    if os.path.isfile(rp):
        try:
            with open(rp, encoding="utf-8") as fh:
                base = _json.load(fh).get("devtools")
        except Exception:
            base = None
    cands = []
    if base:
        cands.append(os.path.join(base, name))
    cands.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), name))
    for c in cands:
        if os.path.isfile(c):
            return c
    sys.stderr.write("[w1_tier_regress][WARN] 未定位 %s\n" % name)
    return cands[0]


ENG = _resolve_devtools("doenglingz_inject_prompt.py")
spec = importlib.util.spec_from_file_location("dg", ENG)
dg = importlib.util.module_from_spec(spec)
sys.argv = ["dg"]
spec.loader.exec_module(dg)

POS = [
    ("p1", "启动童灵"),
    ("p2", "启动成长箱，检查晋升"),
    ("p3", "我的指令是启动童灵，不应该是D3了吗？还显示D1干嘛？"),   # 09-23 判例
    ("p4", "那童灵，你有什么收获吗？"),                              # 直呼
    ("p5", "启动童灵吧，把这单干完"),
    ("p6", "用童灵审一下这个方案"),
]
NEG = [
    ("n1", "这一轮的对话我没有启动童灵啊，怎么又出TSL了"),            # 10-01 v1.14 锚
    ("n2", "首先第一个我不等了执行吧；为什么我的指令没有说启动童灵，但是你走了童灵D3的流程呢？是真触发还是假触发"),  # 10-07 实录·引述式
    ("n3", "什么意思？意思是要启动成长箱走E流程么？2、这个又是什么操作？"),  # 10-07 实录·是非问
    ("n4", "我和童灵儿聊了几句"),
    ("n5", "讨论：现在基于童灵的特性，是不是封装成 Skill 是最好的选择？"),
    # ── 2026-10-08 预注册（你质证「我没明确说启动童灵，你还是启动了」·v1.23 假触发根治轮）──
    # 分母 11→15；改动前先锁期望（铁律-020）。四类根因各一条：
    ("n6", "帮我看下童灵的设计"),            # 根因A：⑤宽松匹配命中高频动词「帮我」·动词不指向童灵
    ("n7", "我想了解一下童灵"),              # 根因B：③句中直呼把句尾宾语位当呼唤
    ("n8", "我不打算用童灵"),                # 根因C：②否定窗口只查前2字·「不打算」跨词否定漏网
    ("n9", "童灵暂时不用"),                  # 根因D：W1_VERBS 含单字「用」·否定语境亦命中
    ("n10", "童灵的人格切片在哪"),           # 根因E：句尾宾语位·属性问句（补边界·防矫枉过正）
]
POS_EXTRA = [
    # ── 2026-10-08 预注册：明确上岗口令漏触发（W1_TRIGGERS 缺「童灵上岗」）──
    ("p7", "童灵上岗"),
]
# ── 安静态进入判据语料组（2026-10-30·K007 重落批·01规范 §二·三十「词表增删须同轮追加语料」）──
# ⚠️ 本组同时补上一处历史空头声称：注入器 v1.26（2026-10-19）版本行自述「新增安静用例组入
#    w1_tier_regress」，盘上本件此前无任何安静语料（本轮 grep 实锤）。判据本体＝_quiet_enter_hit
#    （纯函数·无副作用）——原式内联在 _inject 里，无法进回归网，这本身就是"规则只住文档层"的形态。
QUIET_POS = [
    ("q1", "安静模式", "安静模式"),
    ("q3", "进入安静模式", "安静模式"),
]
QUIET_NEG = [
    ("qn1", "他说了一句 闭眼执行 而已"),          # 转述（差分面 2026-10-30 实抓）
    ("qn2", "刚才那句是「安静模式」，我在引用规则不是下命令"),  # 引号内引述（差分面实抓）
    ("qn3", "关闭安静模式"),                      # 反向话术：退出只认"启动童灵"
    ("qn4", "结束闭眼执行"),                      # 反向话术（差分面抓出的漏词）
    ("qn5", "安静模式是什么意思？"),               # 疑问形（审查4.2）
    ("qn6", "我没有说闭眼执行"),                   # 否定引述
    ("qn7", "<internal-error> 系统回显 安静模式"),   # C类机器块（审查4.4）
    ("qn8", "我们来讨论一下安静模式和闭眼执行这两档安全词在童灵上岗机制建立以后应该怎么分层，"
            "以及粘滞窗口是不是应该共享同一个 flag，我担心共享以后退出路径只剩一条，"
            "但分开又会有两本账，两本账迟早漂移，漂移就得对账，想想还是先跑回归再说"),  # 长句讨论>30字无动词
    # ── 2026-11-01 你裁「现在就只有安静模式」：闭眼执行退出安全词·原 q2/q4/q5 正例转负 ──
    ("qn9", "闭眼执行"),                       # 原 q2 正例·退出后不再进入安静态
    ("qn10", "切闭眼执行"),                    # 原 q4
    ("qn11", "闭眼执行，把这单干完"),          # 原 q5
]
def main():
    bad = 0
    for tag, p in POS + POS_EXTRA:
        got = dg.w1_fired(p)
        if got is not True: bad += 1
        print(("✅" if got else "❌"), tag, "期望上岗", "实跑", got)
    for tag, p in NEG:
        got = dg.w1_fired(p)
        if got is not False: bad += 1
        print(("✅" if not got else "❌"), tag, "期望静默", "实跑", got)
    for tag, p, want in QUIET_POS:
        got = dg._quiet_enter_hit(p)
        if got != want: bad += 1
        print(("✅" if got == want else "❌"), tag, "期望进安静(%s)" % want, "实跑", got or "不进入")
    for tag, p in QUIET_NEG:
        got = dg._quiet_enter_hit(p)
        if got: bad += 1
        print(("✅" if not got else "❌"), tag, "期望不进入安静态", "实跑", got)
    n = len(POS) + len(POS_EXTRA) + len(NEG) + len(QUIET_POS) + len(QUIET_NEG)
    print("结果:", "全绿 %d/%d" % (n, n) if bad == 0 else "%d 红 / 共 %d 例" % (bad, n))
    return 1 if bad else 0
if __name__ == "__main__":
    sys.exit(main())
