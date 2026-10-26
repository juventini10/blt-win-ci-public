#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sandbox_check.py — SWT 沙箱回放检查器（v1.1·2026-10-24·格式同口径根治）

用途：把 N1-N6+SPEC 合成对话（fixture）喂给同一套判据，验证 D1/W3/绝对闸/J1/数据更正
在“对话文本”层面能不能被抓出来。正例必须 0 error，负例必须报错。

v1.1（2026-10-24 沙箱测试 N-a/N-b 对照实验根治）：问题行解析兼容两种格式——
  方言格式（夹具历史）`🎤 第1问 @22:40 正文…` 与主件标注格式 `🎤 第X问 [@HH:MM]`
  （标注行+问题正文随后）；时间戳必填，缺 [@HH:MM] 即违规（每问时钟闸机械痕）。
  根治 v1.0 对主件格式整篇假绿的盲区（0 问解析=0 违规）。

v1.2（2026-10-27 评估台账#13 三盲区根治）：①空转录/无问题行→报违规（0问=0违规假绿）；
  ②时间戳合法性 HH≤23·MM≤59（@25:99 不再放行）；③J1 扫描扩展到问题块外 AI 可见文本
  （开场白定性「你就是回避」同样违规·[AI假设·待你否决]/[判官-双源] 行豁免）。

诚实边界：本件验的是“检查器 + 夹具”，不是模型真机行为。模型是否照做，
仍需另一端/另一模型做盲回放（本端自证无效·S006/S1090）。

用法：
  python3 sandbox_check.py --self-test
  python3 sandbox_check.py --transcript <file>
退出码：0=通过｜1=有违规/夹具失败｜2=用法错误
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import re
import sys

__version__ = "v1.2"
# 方言：🎤 第1问 @22:40 正文… ｜ 主件格式：🎤 第1问 [@22:40]（标注行+正文随后）
Q_RE = re.compile(r"^🎤\s*第(\d+)问\s*[\[(]?@?(\d{2}):(\d{2})[\])]?\s*(.*)$")
BARE_Q_RE = re.compile(r"^🎤\s*第(\d+)问")
STOP_PREFIX = ("[绝对闸]", "[W3硬停]", "[数据质量]", "[数据更正]", "[带宽-")
NEG = ("没做", "没写", "没记", "回避", "拖延", "敷衍", "矛盾", "不想要", "低估")


def _minutes(hh, mm):
    return int(hh) * 60 + int(mm)


def _parse(text):
    """返回 (lines, qs, qblock)；qs=[(行号, 题号, hh|int|None, mm|int|None, 块文本)]，qblock=问题块行号集合。"""
    lines = text.splitlines()
    qs = []
    qblock = set()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        m = BARE_Q_RE.match(s)
        if not m:
            i += 1
            continue
        num = int(m.group(1))
        tq = Q_RE.match(s)
        if tq:
            hh, mm, rest = int(tq.group(2)), int(tq.group(3)), tq.group(4)
        else:
            hh, mm, rest = None, None, s[m.end():].strip()
        buf = [rest] if rest else []
        qblock.add(i)
        j = i + 1
        while j < len(lines):
            t = lines[j].strip()
            if BARE_Q_RE.match(t) or t.startswith(STOP_PREFIX):
                break
            if t:
                buf.append(t)
                qblock.add(j)
            j += 1
        qs.append((i, num, hh, mm, " ".join(buf)))
        i = j
    return lines, qs, qblock


def check(text):
    errors = []
    lines, qs, qblock = _parse(text)
    first_q_idx = qs[0][0] if qs else None
    dq_idx = None
    low_bw = False
    stop_idx = {}
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("[数据质量]"):
            dq_idx = i
        if s.startswith("[带宽-低]"):
            low_bw = True
        if s.startswith("[W3硬停]"):
            stop_idx["w3"] = i
        if s.startswith("[绝对闸]"):
            stop_idx["abs"] = i

    # 盲区①(v1.2)：空转录/无问题行不构成有效回放（0问=0违规的假绿）
    if not qs:
        errors.append("回放转录无任何问题行（空对话/纯标记不构成有效回放·评估台账#13盲区①）")

    # 时间戳必填：每问时钟闸的机械痕，缺 = 违规（v1.0 对主件格式假绿的根治）
    for _, n, hh, mm, _ in qs:
        if hh is None:
            errors.append("第%d问缺 [@HH:MM] 时间戳（每问时钟闸机械痕·主件标注格式）" % n)
        elif hh > 23 or mm > 59:
            errors.append("第%d问时间戳非法 @%02d:%02d（HH≤23·MM≤59·评估台账#13盲区②）" % (n, hh, mm))

    # D1：数据质量行必须在第一问之前，且带日记/跨端两个字段
    if first_q_idx is not None:
        if dq_idx is None or dq_idx > first_q_idx:
            errors.append("D1 缺 [数据质量] 行（或出现在第一问之后）")
        else:
            dq = lines[dq_idx]
            if "日记:" not in dq or "跨端:" not in dq:
                errors.append("D1 [数据质量] 缺 日记:/跨端: 字段")

    # 绝对闸：任何 >=00:30（凌晨）的问题都违规；必须在末问后出现 [绝对闸]
    def _abs_late(q):
        # 00:30-06:59 都算凌晨；07:00 后才不算
        return (q[2] == 0 and q[3] >= 30) or (1 <= q[2] < 7)

    timed = [q for q in qs if q[2] is not None]
    late_abs = [q for q in timed if _abs_late(q)]
    if late_abs:
        errors.append("绝对闸违规：存在 >=00:30 的新问题（第%s问）" % ",".join(str(q[1]) for q in late_abs))
    if late_abs and "abs" not in stop_idx:
        errors.append("绝对闸缺 [绝对闸] 收口标记")

    # W3：低带宽最多 3 问；>=23:30 本身即违规（时钟闸=出口前查，到了就不发）
    if low_bw:
        if len(qs) > 3:
            errors.append("W3 违规：低带宽共 %d 问（>3）" % len(qs))
        late = [q for q in timed if q[2] * 60 + q[3] >= _minutes(23, 30)]
        if late:
            errors.append("W3 违规：低带宽下 >=23:30 仍发新问（第%s问）" % ",".join(str(q[1]) for q in late))

    # 硬停/绝对闸之后不得再有新问题
    for key, name in (("w3", "W3硬停"), ("abs", "绝对闸")):
        if key in stop_idx:
            after = [q for q in qs if q[0] > stop_idx[key]]
            if after:
                errors.append("%s 之后仍有新问题（第%s问）" % (name, ",".join(str(q[1]) for q in after)))

    # J1：含负面词的问题必须有双源或 AI假设 标签（扫问题块全文=题号行+标注行+正文）
    for _, n, _, _, btxt in qs:
        if any(w in btxt for w in NEG):
            if "[判官-双源]" not in btxt and "[AI假设·待你否决]" not in btxt:
                errors.append("J1 违规：第%d问含负面定性但无 [判官-双源]/[AI假设·待你否决]" % n)

    # 盲区③(v1.2)：J1 扩展到问题块外 AI 可见文本（开场白定性同样违规）
    _SKIP = ("🎤", "[数据质量]", "[带宽-", "[W3硬停]", "[绝对闸]", "[数据更正]",
             "### 数据更正", "[待补记", "[判官-双源]", "[AI假设·待你否决]")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith(_SKIP) or i in qblock:
            continue
        if any(w in s for w in NEG):
            errors.append("J1违规：问题块外文本含负面定性（第%d行「%s」）——须 [AI假设·待你否决] 或删除定性（评估台账#13盲区③）" % (i + 1, s[:40]))

    # 数据更正交接：出现 [数据更正] 就必须有系统日志标题 + daily-buddy 交接
    if any("[数据更正]" in l for l in lines):
        if not any("### 数据更正：" in l for l in lines):
            errors.append("数据更正缺系统日志标题 `### 数据更正：{date} {字段}`")
        if not any("待补记→daily-buddy" in l for l in lines):
            errors.append("数据更正缺 `[待补记→daily-buddy 工作流C]` 交接行")

    return errors


FIXTURES = {
    "N1_good": (True, """[数据质量] 日记:未封口(2026-10-23)｜系统日志:9条 as_of=2026-10-23｜跨端:已查(豆包办公3)｜降级源:日记
[带宽-充足]
🎤 第1问 @22:40 [维度3][L1][AI假设·待你否决] 日记里今天没记文案，是没做，还是记在别处了？
"""),
    "N1_bad": (False, """[带宽-充足]
🎤 第1问 @22:40 你今天怎么没写文案？
"""),
    "N2_good": (True, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-低]
🎤 第1问 @22:40 你现在最卡的是什么？
🎤 第2问 @23:00 这一步谁先接？
🎤 第3问 @23:20 明天先做哪一件？
[W3硬停] 23:35 收口
"""),
    "N2_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-低]
🎤 第1问 @22:40 你现在最卡的是什么？
🎤 第2问 @23:00 这一步谁先接？
🎤 第3问 @23:35 明天先做哪一件？
🎤 第4问 @23:40 再聊最后一个
"""),
    "N2b_good": (True, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
🎤 第1问 @23:00 今天最值钱的一件事是什么？
[绝对闸] 00:31 收口
"""),
    "N2b_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
🎤 第1问 @23:00 今天最值钱的一件事是什么？
🎤 第2问 @00:35 再聊最后一个
"""),
    "N3_good": (True, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
🎤 第1问 @22:40 [维度3][L1][判官-双源] 你说要做文案，日记和系统日志都没记，是没做还是记在别处？
"""),
    "N3_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
🎤 第1问 @22:40 你说要做文案，结果没做，为什么？
"""),
    "N4_good": (True, """[数据质量] 日记:未封口(2026-10-23)｜系统日志:9条 as_of=2026-10-23｜跨端:已查(豆包办公3)｜降级源:日记
[数据更正] 日期=2026-10-23 字段=tomato 原值=0→8 依据=用户原话+豆包办公3条
### 数据更正：2026-10-23 tomato
[待补记→daily-buddy 工作流C 补录]
[带宽-充足]
🎤 第1问 @22:40 下午那 8🍅 主要花在哪一段？
"""),
    "N4_bad": (False, """[数据质量] 日记:未封口(2026-10-23)｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[数据更正] 日期=2026-10-23 字段=tomato 原值=0→8
[带宽-充足]
🎤 第1问 @22:40 下午那 8🍅 主要花在哪一段？
"""),
    "SPEC_good": (True, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-低]
🎤 第1问 [@22:40]
[维度3][L1-第一性原理][哲学-未触发][深度1/4·表层]

你现在最卡的是什么？

🎤 第2问 [@23:00]
[维度3][L1-第一性原理][哲学-未触发][深度2/4·模式层]

这一步谁先接？

🎤 第3问 [@23:20]
[维度3][L1-第一性原理][哲学-未触发][深度2/4·模式层]

明天先做哪一件？
[W3硬停] 23:35 收口
"""),
    "SPEC_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-低]
🎤 第1问 [@22:40]
[维度3][L1-第一性原理][哲学-未触发][深度1/4·表层]

你现在最卡的是什么？

🎤 第2问 [@23:00]
[维度3][L1-第一性原理][哲学-未触发][深度2/4·模式层]

这一步谁先接？

🎤 第3问 [@23:20]
[维度3][L1-第一性原理][哲学-未触发][深度2/4·模式层]

明天先做哪一件？

🎤 第4问 [@00:35]
[维度3][L1-第一性原理][哲学-未触发][深度3/4·信念层]

再聊最后一个：这个标准最早是谁给你立的？
"""),
    "V12_empty_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
"""),
    "V12_badtime_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
🎤 第1问 @25:99 你现在最卡的是什么？
"""),
    "V12_open_bad": (False, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
开场白：你就是回避，别装了。
🎤 第1问 @22:40 你现在最卡的是什么？
"""),
    "V12_open_good": (True, """[数据质量] 日记:已封口｜系统日志:9条 as_of=2026-10-23｜跨端:已查
[带宽-充足]
[AI假设·待你否决] 我看到日记里没记，是没做还是记在别处了？
🎤 第1问 @22:40 你现在最卡的是什么？
"""),
}


def self_test():
    ok = True
    for name, (expect_ok, text) in FIXTURES.items():
        errs = check(text)
        passed = (not errs) if expect_ok else bool(errs)
        print(("✅PASS " if passed else "❌FAIL ") + name + ("" if passed else " -> " + "; ".join(errs)))
        ok &= passed
    print("✅✅ 沙箱夹具全过（%d 组）" % len(FIXTURES) if ok else "❌ 沙箱夹具有失败")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return self_test()
    if "--transcript" in a:
        i = a.index("--transcript")
        if i + 1 >= len(a):
            print("error: --transcript 后须跟文件", file=sys.stderr)
            return 2
        p = a[i + 1]
        if not os.path.exists(p):
            print("error: 文件不存在 %s" % p, file=sys.stderr)
            return 2
        errs = check(open(p, encoding="utf-8").read())
        if errs:
            print("❌ 沙箱回放发现 %d 个违规：" % len(errs))
            for e in errs:
                print("   ·", e)
            return 1
        print("✅ 沙箱回放通过（0 违规）")
        return 0
    print("用法: sandbox_check.py --self-test | --transcript <file>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
