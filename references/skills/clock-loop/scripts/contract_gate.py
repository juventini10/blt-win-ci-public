#!/usr/bin/env python3
# REG: skip clock-loop 包内合同完整性闸（发布自包含投影·非脚本中心治理件）
# -*- coding: utf-8 -*-
"""contract_gate.py — 合同完整性闸（v1.1·2026-10-24）

补结构闸盲区：整段删除但节还在时，结构闸与 skill_eval 都可能静默通过。
v1.1 加固：不只数标签，验最小正文——T5 每条须含 ⛔DO NOT；禁令行须含 ⛔DO NOT；
熔断器块须 ≥3 条判据行；📦 只数 `📦 产出物:` 声明行（不数节标题/正文提及）。
能力边界（诚实）：拦「整块/整条删除」与「保留标题清空正文」；不判语义稀释
（条款被改写成一句含糊话仍可能通过——语义归 AI+人眼）。
判据：T5>=11 条且每条有 ⛔DO NOT / 禁令>=13 行且每行有 ⛔DO NOT / 熔断器>=6 块且每块>=3 判据行 /
阶段7节 / G+H / 产出物声明>=8 / 四层契约4词。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import io
import os
import re
import sys

STAGES = ("### 阶段0", "### 🔀 阶段0.5", "### 阶段1:", "### 阶段1.5",
          "### 阶段2:", "### 阶段3:", "### 阶段4:")
FOUR = ("输入契约", "输出契约", "行为契约", "演化契约")


def _section(t, head):
    m = re.search(r"^%s[^\n]*$" % re.escape(head), t, re.M)
    if not m:
        return ""
    nxt = re.search(r"^## ", t[m.end():], re.M)
    return t[m.end(): m.end() + (nxt.start() if nxt else len(t))]


def check_text(t):
    issues = []
    # ① T5 11 条 + 每条正文有 ⛔DO NOT
    t5 = list(re.finditer(r"^### (\d+)\. [^\n]*\n(.*?)(?=^### |\Z)", t, re.M | re.S))
    if len(t5) < 11:
        issues.append("T5 条目 %d<11" % len(t5))
    empty_t5 = [m.group(1) for m in t5 if "⛔DO NOT" not in m.group(2)]
    if empty_t5:
        issues.append("T5 条目正文空/无⛔DO NOT: %s" % "、".join(empty_t5[:3]))
    # ② 禁止行为 13 行 + 每行有 ⛔DO NOT（只数本节）
    ban_sec = _section(t, "## 禁止行为")
    ban_rows = re.findall(r"^\| *(\d+) *\|[^\n]*$", ban_sec, re.M)
    if len(ban_rows) < 13:
        issues.append("禁止行为 %d<13" % len(ban_rows))
    bad_ban = [r for r in re.findall(r"^\| *\d+ *\|[^\n]*$", ban_sec, re.M) if "⛔DO NOT" not in r]
    if bad_ban:
        issues.append("禁止行为行缺⛔DO NOT: %d 行" % len(bad_ban))
    # ③ 熔断器 6 块 + 每块>=3 判据行（按锚点计块·块体被删空也算块）
    anchors = [m.start() for m in re.finditer(r"^🔌 熔断器", t, re.M)]
    if len(anchors) < 6:
        issues.append("熔断器 %d<6" % len(anchors))
    thin = []
    for i, pos in enumerate(anchors):
        end = anchors[i + 1] if i + 1 < len(anchors) else len(t)
        body = t[pos:end]
        n_fields = len(re.findall(r"^[├└]─", body, re.M))
        if n_fields < 3:
            thin.append(i + 1)
    if thin:
        issues.append("熔断器块判据<3行: 第%s块" % "、".join(map(str, thin[:3])))
    # ④ 阶段 / ⑤ G+H
    miss = [s for s in STAGES if s not in t]
    if miss:
        issues.append("缺阶段 %s" % "、".join(miss))
    if "### G路径" not in t or "### H路径" not in t:
        issues.append("缺 G/H 路径")
    # ⑥ 产出物声明（只数声明行）
    n_pkg = len(re.findall(r"^📦 产出物[:：]", t, re.M))
    if n_pkg < 8:
        issues.append("产出物声明 %d<8" % n_pkg)
    # ⑧ 每个阶段块/G/H 分流块须有 ✅DO 与 📦（防「保留标题删执行指令」）
    thin_stage = []
    for s in STAGES + ("### G路径", "### H路径"):
        m = re.search(r"^%s[^\n]*\n(.*?)(?=^### |^## |\Z)" % re.escape(s), t, re.M | re.S)
        body = m.group(1) if m else ""
        if "✅DO" not in body or "📦" not in body:
            thin_stage.append(s.replace("### ", ""))
    if thin_stage:
        issues.append("阶段块缺✅DO/📦: %s" % "、".join(thin_stage[:3]))
    # ⑦ 四层契约
    miss4 = [f for f in FOUR if f not in t]
    if miss4:
        issues.append("缺四层契约 %s" % "、".join(miss4))
    return issues


def _fixture():
    lines = ["# T", ""]
    for i in range(1, 12):
        lines += ["### %d. 声明%d" % (i, i), "⛔DO NOT 违反%d" % i, ""]
    lines += ["## 四层契约", "", "| 输入契约 | x |", "| 输出契约 | x |",
              "| 行为契约 | x |", "| 演化契约 | x |", ""]
    lines += ["## 禁止行为", ""]
    for i in range(1, 14):
        lines.append("| %d | ⛔DO NOT x | y |" % i)
    lines.append("")
    for s in STAGES:
        lines += [s, "", "📦 产出物:x", "✅DO 执行", "", "🔌 熔断器",
                  "├─ 成功条件:x", "├─ 失败处理:跳过", "└─ 降级方案:继续步骤3", ""]
    lines += ["### G路径", "", "📦 产出物:x", "✅DO 执行", "", "### H路径", "", "📦 产出物:x", "✅DO 执行", ""]
    return "\n".join(lines) + "\n"


def selftest():
    base = _fixture()
    ok = True

    def case(name, text, expect_red):
        nonlocal ok
        good = bool(check_text(text)) == expect_red
        if not good:
            ok = False
        print("%s %s" % ("✅" if good else "❌失守", name))

    case("T0-正例(应绿)", base, False)
    case("N1-删T5条(应红)", base.replace("### 11. 声明11\n⛔DO NOT 违反11\n", "", 1), True)
    case("N2-删禁止行(应红)", base.replace("| 13 | ⛔DO NOT x | y |\n", "", 1), True)
    case("N3-删熔断器×2(应红)", base.replace("🔌 熔断器\n├─ 成功条件:x\n├─ 失败处理:跳过\n└─ 降级方案:继续步骤3\n", "", 2), True)
    case("N4-删阶段2(应红)", base.replace("### 阶段2:\n\n📦 产出物:x\n✅DO 执行\n\n🔌 熔断器\n├─ 成功条件:x\n├─ 失败处理:跳过\n└─ 降级方案:继续步骤3\n", "", 1), True)
    case("N5-删G路径(应红)", base.replace("### G路径\n", "", 1), True)
    case("N6-T5正文清空(应红)", base.replace("⛔DO NOT 违反5", "x", 1), True)
    case("N7-禁令正文清空(应红)", base.replace("| 7 | ⛔DO NOT x | y |", "| 7 | x | y |", 1), True)
    case("N8-熔断器判据删空(应红)", base.replace("├─ 成功条件:x\n├─ 失败处理:跳过\n└─ 降级方案:继续步骤3\n", "", 1), True)
    case("N9-产出物删到7(应红)", base.replace("📦 产出物:x\n", "", 1), True)
    case("N10-阶段2删执行指令(应红)", base.replace("### 阶段2:\n\n📦 产出物:x\n✅DO 执行", "### 阶段2:\n\n📦 产出物:x", 1), True)
    case("N11-G路径删✅DO(应红)", base.replace("### G路径\n\n📦 产出物:x\n✅DO 执行", "### G路径\n\n📦 产出物:x", 1), True)
    print("SELFTEST:%s（正例绿·负例11连红）" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root")
    ap.add_argument("--skill-file")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.skill_file and not a.skill_root:
        print("CONTRACT:FAIL 须给 --skill-root 或 --skill-file", file=sys.stderr)
        return 2
    p = a.skill_file or os.path.join(os.path.abspath(a.skill_root), "SKILL.md")
    if not os.path.isfile(p):
        print("CONTRACT:FAIL SKILL 不可达 %s" % p, file=sys.stderr)
        return 2
    issues = check_text(io.open(p, encoding="utf-8").read())
    if issues:
        print("CONTRACT:FAIL %d 项：%s" % (len(issues), "；".join(issues)), file=sys.stderr)
        return 1
    print("CONTRACT:OK 合同清单 7 类全在（T5≥11且每条有⛔/禁令≥13且每行有⛔/熔断≥6且每块≥3判据/阶段7/GH/📦≥8/四层4）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
