#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orchestration_gate.py — 编排结构闸（F10·v1.0·2026-10-22）

TRUTH_OF: 编排四律与四区骨架唯一真源 = 方案 v1.1（自定义层/待完成工作/2026-10-22-三明治编排革命重构-方案v1.1.md）
判据（三条，全绿才 exit 0）：
  ① 主体行数 ≤ MAX_LINES（默认 350）——控制注入体积与"迷失在中间"风险
  ② 结论块模板节住末段（heading 行号 ≥ 70% 总行数）——终位合同区（近因效应）
  ③ 指路牌节列出的节名集合 ≡ 实际 `## ` 节集合（排除指路牌自身）——防指路牌说谎；
     且指路牌禁行号（⛔L±数字锚）+每行必带"看哪节"目标（按节名指路三纪律）

设计纪律：代码围栏内不计节（模板里的 `## L{层} …` 是产出样板不是节）；
负例须有牙（S138）：--skill-file 可指向变异副本，缺节/超行/模板前移/行号锚任一项必 FAIL。
用法：python3 orchestration_gate.py [--skill-root DIR] [--skill-file PATH] [--max-lines N]
退出码：0=全绿；1=任一条不过；2=文件不可达。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import io, os, re, sys, argparse

MAX_LINES_DEFAULT = 350
TEMPLATE_HEADING_KEY = "结论块模板"
SIGNPOST_KEY = "指路牌"
TEMPLATE_TAIL_RATIO = 0.70

RE_LINENO = re.compile(r"\bL\d{2,}\b")
ZONE_WORDS = ("首因区", "终位合同区", "硬约束区", "参考区", "指针区", "终位指针", "终位合同")  # v1.1：分区词只住维护层
RE_SIGN_NAME = re.compile(r"`##\s+([^`]+)`")


def split_lines(text):
    return text.splitlines()


def headings_outside_fence(lines):
    """返回 [(行号1based, 节名)]，跳过 ``` 围栏内内容。"""
    out = []
    fence = False
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if ln.startswith("## "):
            out.append((i, ln[3:].strip()))
    return out


def section_body(lines, start_line):
    """取 start_line(1based) 起、到下一个围栏外 `## ` 之前的行。"""
    body = []
    fence = False
    for i, ln in enumerate(lines, 1):
        if i <= start_line:
            continue
        if ln.lstrip().startswith("```"):
            fence = not fence
            body.append(ln)
            continue
        if not fence and ln.startswith("## "):
            break
        body.append(ln)
    return body


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--skill-root", default=os.path.join(here, ".."))
    ap.add_argument("--skill-file", default=None)
    ap.add_argument("--max-lines", type=int, default=MAX_LINES_DEFAULT)
    a = ap.parse_args()

    path = a.skill_file or os.path.join(os.path.abspath(a.skill_root), "SKILL.md")
    if not os.path.isfile(path):
        print("ORCH:FAIL SKILL 不可达 %s" % path, file=sys.stderr)
        return 2

    text = io.open(path, encoding="utf-8").read()
    lines = split_lines(text)
    total = len(lines)
    heads = headings_outside_fence(lines)
    names = [h[1] for h in heads]
    errs = []
    bad_zone = [n for n in names if any(z in n for z in ZONE_WORDS)]
    if bad_zone:
        errs.append("节名含分区词（正文须消费语义）：" + "；".join(bad_zone))

    # ① 行数
    if total > a.max_lines:
        errs.append("行数 %d > 上限 %d" % (total, a.max_lines))

    # ② 结论块模板住末段
    tpl = [(n, s) for n, s in heads if TEMPLATE_HEADING_KEY in s]
    if not tpl:
        errs.append("未找到「%s」节" % TEMPLATE_HEADING_KEY)
    else:
        n = tpl[0][0]
        ratio = float(n) / total if total else 0.0
        if ratio < TEMPLATE_TAIL_RATIO:
            errs.append("「%s」在 %.0f%%（第 %d/%d 行）< 末段阈值 %.0f%%"
                        % (TEMPLATE_HEADING_KEY, ratio * 100, n, total, TEMPLATE_TAIL_RATIO * 100))

    # ③ 指路牌 ≡ 实际节集合
    sp = [(n, s) for n, s in heads if SIGNPOST_KEY in s]
    if not sp:
        errs.append("未找到指路牌节（节名须含「%s」）" % SIGNPOST_KEY)
    else:
        sp_line, sp_name = sp[0]
        body = section_body(lines, sp_line)
        listed = []
        bad_rows = []
        for ln in body:
            s = ln.strip()
            if not s.startswith("|"):
                continue
            if re.match(r"^\|[\s:|-]+\|$", s):
                continue
            if "你要干什么" in s or "看哪节" in s:
                continue
            m = RE_SIGN_NAME.search(s)
            if m:
                listed.append(m.group(1).strip())
            else:
                bad_rows.append(s)
        if bad_rows:
            errs.append("指路牌存在 %d 行未按节名指路（须用 `## 节名` 反引号形态）：%s"
                        % (len(bad_rows), bad_rows[0][:60]))
        lset = set(listed)
        aset = set(names) - {sp_name}
        missing = sorted(aset - lset)
        ghost = sorted(lset - aset)
        if missing:
            errs.append("指路牌漏列 %d 节：%s" % (len(missing), "；".join(missing)))
        if ghost:
            errs.append("指路牌列出不存在的 %d 节：%s" % (len(ghost), "；".join(ghost)))
        for ln in body:
            m = RE_LINENO.search(ln)
            if m:
                errs.append("指路牌含行号锚「%s」（⛔行号必漂，改节名锚）" % m.group(0))
                break
        if len(listed) != len(set(listed)):
            errs.append("指路牌有重复节名行")

    if errs:
        print("ORCH:FAIL 编排结构闸 %d 项：" % len(errs), file=sys.stderr)
        for e in errs:
            print("   - %s" % e, file=sys.stderr)
        return 1

    tpl_ratio = 100.0 * tpl[0][0] / total
    print("ORCH:OK %d 行·模板@%.0f%%·指路牌≡%d 节" % (total, tpl_ratio, len(lset)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
