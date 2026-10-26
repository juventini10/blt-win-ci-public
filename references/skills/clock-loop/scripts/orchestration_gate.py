#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 通用件（脚本中心守卫族·Skill架构规范 pages/09-orchestration.md §机检（防说谎·可复用件）/§迁移到其他 Skill 的三件套 授权登记）·非任何单 Skill 包内件
"""orchestration_gate.py — 编排结构闸·通用件（v1.4·2026-10-24）

三实例验证链已成（triwich v4.12.0 首例 / daily-buddy v3.52.10 次例 / growth-box v4.13.0 第三例），
按规范 §13.8「验证第二个实例后升级为通用件」升格。新 Skill 迁移或大改 Skill 时以本件为母：
  python3 [记忆共享中心]/脚本中心/orchestration_gate.py --skill-root <DIR> \
    --template-key "<终位合同节关键词>" --signpost-key "指路牌" --max-lines N --tail-ratio 0.65
既有三包内副本（triwich/daily-buddy/growth-box scripts/）为发布自包含投影，⛔回接本件（断链风险>
复用收益）；本件演进须反向对账三副本（漂移由各自 run.sh 负例逮）。

TRUTH_OF: 编排四律与四区骨架唯一真源 = Skill架构规范 pages/09-orchestration.md（v6.0.0）。
判据（六条，全绿才 exit 0）：
  ① 主体行数 ≤ --max-lines（必备参数：包体量因件而异，通用件⛔预设他件数字）
  ② 合同模板节（--template-key 定位）住末段（heading 行位 ≥ --tail-ratio，默认 0.65）
  ③ 指路牌节（--signpost-key 定位）列出的节名集合 ≡ 实际 `## ` 节集合（排除指路牌自身）；
     禁行号锚（⛔L±数字）+每行必带"看哪节"目标；节名必须反引号 `## 全名` 形态
  ④ 分区词禁入正文节名（规范 §13.9：首因区/终位合同区/硬约束区/参考区/指针区/终位指针/终位合同）
  ⑤ 正文节头唯一（v1.1·2026-10-24）：`## ` 标题重复=结构病——set 语义对比漏重复节头
     （system-logger v3.19.5 L219-220 `## references/ 目录索引` 连续两行实证放行）
  ⑥ 正文行号锚三形态（v1.4·2026-10-24 迁理之外测试批 N5b 实证根治）：行号锚扫描从指路牌节
     扩到正文全域（围栏内与指路牌段除外·指路牌段沿用③的从严检查防双报）。对齐硬约束4
     「锚点用节名；⛔行号锚」。判据按 pages/09 弱锚升级边界「枚举不清先补定义」收敛为
     三种可枚举形态（全库 55 个 SKILL.md 校准：真阳性 2 处全中·lieflat-charts 图表码
     L1–L15 零误伤）：
       a. 引导词+L（见/详见/参见/位于/区间/行号/@/± + L1~2位数）
       b. 文件指针+L（`xxx.md/.py/.sh/.js/.ts` 紧邻 L3位数）
       c. 规范词+L（规范/手册/协议/白皮书/指南 紧邻 L3位数）
     ⚠️ 枚举边界如实声明：裸「（L63）」形态（无文件/引导词/规范词上下文）不在判据内——
     同词形承载图表分类码（L1–L15）与层级术语（L1/L2/L3），上下文不可机械区分，不硬上；
     该形态存量 2 处（clock-loop L63）留待其域自清。
  行号锚收紧沿 v1.2（2026-10-24）：单位数 L 锚（如「见 L7」）实测放行=缝，对齐全量口径；
  三包内副本同批对账（triwich v4.12.9/daily-buddy v3.53.4/growth-box v4.15.1）。
负例必过（S138）：--skill-file 指变异副本——缺节/幽灵节/模板前移/行号锚/超行/分区词/重复节
任一不红=闸没牙；--selftest 内嵌正例+负例自证（负例不红=闸没牙）。
用法：orchestration_gate.py (--skill-root DIR | --skill-file PATH) --template-key K
      [--signpost-key K] [--max-lines N] [--tail-ratio R] [--selftest]
退出码：0=全绿/selftest 全过；1=任一条不过/selftest 有失守；2=参数错/文件不可达。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import io, os, re, sys, argparse, tempfile, shutil

ZONE_WORDS = ("首因区", "终位合同区", "硬约束区", "参考区", "指针区", "终位指针", "终位合同")
RE_LINENO = re.compile(r"\bL\d{2,}\b")  # 行号锚·指路牌从严（两位以上·L451 形态）
RE_LINENO_SHORT = re.compile(r"(?:见|详见|参见|位于|区间|行号?|@|±)\s*L\d{1,2}\b")  # 引导词+短行号锚（「见 L7」缝修补·形态级精细化——纯 \d{1,} 一刀切误伤 triwich L1/L2/L3 层级术语·2026-10-24 实证回撤）
# v1.4 正文行号锚三形态（判据⑥·枚举清晰防误伤：lieflat 图表码 L1–L15 与层级词 L1/L2/L3 均无此三上下文）
RE_BODY_FILE_L = re.compile(r"(?:\.md|\.py|\.sh|\.js|\.ts)`?\s*`?L\d{2,}\b")
RE_BODY_SPEC_L = re.compile(r"(?:规范|手册|协议|白皮书|指南)\s*`?L\d{2,}\b")
RE_SIGN_NAME = re.compile(r"`##\s+([^`]+)`")


def headings_outside_fence(lines):
    out, fence = [], False
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence and ln.startswith("## "):
            out.append((i, ln[3:].strip()))
    return out


def section_body(lines, start_line):
    body, fence = [], False
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


def check(path, template_key, signpost_key, max_lines, tail_ratio):
    """返回 (errs, ok_msg)；供 CLI 与 selftest 共用。"""
    text = io.open(path, encoding="utf-8").read()
    lines = text.splitlines()
    total = len(lines)
    heads = headings_outside_fence(lines)
    names = [h[1] for h in heads]
    errs = []
    bad_zone = [n for n in names if any(z in n for z in ZONE_WORDS)]
    if bad_zone:
        errs.append("节名含分区词（正文须消费语义·§13.9）：" + "；".join(bad_zone))
    # v1.1 判据⑤：正文节头唯一（判据③的 lset/aset 均为 set 语义，重复节头只计一份=漏检）
    _seen, _dups = set(), []
    for _n in names:
        if _n in _seen and _n not in _dups:
            _dups.append(_n)
        _seen.add(_n)
    if _dups:
        errs.append("正文节头重复 %d 个（节集合必须唯一）：%s" % (len(_dups), "；".join(_dups[:3])))
    if total > max_lines:
        errs.append("行数 %d > 上限 %d" % (total, max_lines))

    tpl = [(n, s) for n, s in heads if template_key in s]
    if not tpl:
        errs.append("未找到「%s」合同节" % template_key)
    else:
        ratio = float(tpl[0][0]) / total if total else 0.0
        if ratio < tail_ratio:
            errs.append("「%s」在 %.0f%%（第 %d/%d 行）< 末段阈值 %.0f%%"
                        % (template_key, ratio * 100, tpl[0][0], total, tail_ratio * 100))

    sp = [(n, s) for n, s in heads if signpost_key in s]
    if not sp:
        errs.append("未找到指路牌节（节名须含「%s」）" % signpost_key)
        sp_line, sp_name, listed = None, None, []
    else:
        sp_line, sp_name = sp[0]
        body = section_body(lines, sp_line)
        listed, bad_rows = [], []
        for ln in body:
            s = ln.strip()
            if not s.startswith("|") or re.match(r"^\|[\s:|-]+\|$", s) or "你要干什么" in s or "看哪节" in s:
                continue
            m = RE_SIGN_NAME.search(s)
            if m:
                listed.append(m.group(1).strip())
            else:
                bad_rows.append(s)
        if bad_rows:
            errs.append("指路牌存在 %d 行未按节名指路（须 `## 节名` 反引号形态）：%s" % (len(bad_rows), bad_rows[0][:60]))
        lset, aset = set(listed), set(names) - {sp_name}
        if sorted(aset - lset):
            errs.append("指路牌漏列 %d 节：%s" % (len(aset - lset), "；".join(sorted(aset - lset))))
        if sorted(lset - aset):
            errs.append("指路牌列出不存在的 %d 节：%s" % (len(lset - aset), "；".join(sorted(lset - aset))))
        for ln in body:
            m = RE_LINENO.search(ln) or RE_LINENO_SHORT.search(ln)
            if m:
                errs.append("指路牌含行号锚「%s」（⛔行号必漂，改节名锚）" % m.group(0))
                break
        if len(listed) != len(set(listed)):
            errs.append("指路牌有重复节名行")

    # v1.4 判据⑥：正文行号锚三形态（全域扫·围栏内与指路牌段除外——指路牌段由③从严检查负责，防双报）
    sp_end = total + 1
    if sp_line is not None:
        sp_end = min([i for i, _ in heads if i > sp_line] or [total + 1])
    fence = False
    body_hits = []
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or (sp_line is not None and sp_line <= i < sp_end):
            continue
        for pat, tag in ((RE_LINENO_SHORT, "引导词"), (RE_BODY_FILE_L, "文件指针"), (RE_BODY_SPEC_L, "规范词")):
            m = pat.search(ln)
            if m:
                body_hits.append("第 %d 行 %s行号锚「%s」" % (i, tag, m.group(0)))
                break
    if body_hits:
        errs.append("正文含行号锚 %d 处（硬约束4：锚点用节名；围栏内豁免）：%s" % (len(body_hits), "；".join(body_hits[:3])))

    if errs:
        return errs, None
    return [], "ORCH:OK %d 行·模板@%.0f%%·指路牌≡%d 节" % (total, 100.0 * tpl[0][0] / total, len(listed))


# ---------------- selftest（v1.4·负例内嵌·负例不红=闸没牙） ----------------

def _write_fixture(root, mutate=None):
    """最小合规 Skill 夹具；mutate(lines) 返回变异后行列表。"""
    lines = [
        "# 测试件", "",
        "## 📍 指路牌", "",
        "| 你要干什么 | 看哪节 |",
        "|:--|:--|",
        "| 触发判定 | `## 触发条件` |",
        "| 执行主链 | `## 单视角模式` |",
        "| 核对防误 | `## 防误层` |",
        "| 收尾填槽 | `## 📝 收尾模板` |",
        "",
        "---", "",
        "## 触发条件", "",
        "正文提及层级术语 L1/L2/L3 与图表码（L1–L15）及比较 L15、F5——合法词形，不得误伤。", "",
        "## 单视角模式", "",
        "执行说明。", "",
        "## 防误层", "",
        "防误说明。", "",
        "---", "",
        "## 📝 收尾模板", "",
        "| 项 | 内容 |",
        "|:--|:--|",
        "| 结论 | X |",
    ]
    if mutate:
        lines = mutate(lines)
    os.makedirs(root, exist_ok=True)
    io.open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def selftest():
    base = tempfile.mkdtemp(prefix="orch_gate_selftest_")
    ok = True
    try:
        def run_case(name, expect_red, mutate=None):
            nonlocal ok
            root = os.path.join(base, name)
            _write_fixture(root, mutate)
            errs, ok_msg = check(os.path.join(root, "SKILL.md"), "收尾模板", "指路牌", 100, 0.65)
            red = bool(errs)
            good = red == expect_red
            if not good:
                ok = False
            print("%s %s%s" % ("✅" if good else "❌失守", name,
                               "" if good else " | errs=%s ok_msg=%s" % (errs[:2], ok_msg)))

        run_case("T0-正例(应绿)", False)
        run_case("N1-幽灵节(应红)", True, lambda ls: ls + ["", "## 幽灵节", ""])
        run_case("N2-删指路行(应红)", True, lambda ls: [l for l in ls if "`## 单视角模式`" not in l])
        run_case("N3-模板前移(应红)", True, lambda ls: ls[:9] + ls[-4:] + ls[9:-4])
        run_case("N4-分区词节名(应红)", True, lambda ls: [l.replace("## 防误层", "## 防误参考区").replace("`## 防误层`", "`## 防误参考区`") for l in ls])
        run_case("N5-超行(应红)", True, lambda ls: ls + ["尾行"] * 30)
        run_case("N6-重复节头(应红)", True, lambda ls: ls + ["", "## 触发条件", "重复节"])
        run_case("N7-指路牌行号锚(应红)", True, lambda ls: [l + " 见L7" if "收尾模板`" in l else l for l in ls])
        run_case("N8-正文引导词行号锚(应红)", True, lambda ls: ls + ["", "历史沿革详见 L12。", ""])
        run_case("N9-正文文件指针行号锚(应红)", True, lambda ls: ls + ["", "定位根因：`fixgen.py` L31 把根目录当工作区。", ""])
        run_case("N10-正文规范词行号锚(应红)", True, lambda ls: ls + ["", "守卫编写规范 L706：规则一行。", ""])
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SELFTEST:%s（正例绿·负例11连红·合法词形不误伤）" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=None)
    ap.add_argument("--skill-file", default=None)
    ap.add_argument("--template-key", help="终位合同节 heading 关键词（如 呈现层三块式骨架/结论块）")
    ap.add_argument("--signpost-key", default="指路牌")
    ap.add_argument("--max-lines", type=int)
    ap.add_argument("--tail-ratio", type=float, default=0.65)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.template_key or not a.max_lines:
        print("ORCH:FAIL --template-key 与 --max-lines 必备（或 --selftest）", file=sys.stderr)
        return 2
    if not a.skill_file and not a.skill_root:
        print("ORCH:FAIL 须给 --skill-root 或 --skill-file", file=sys.stderr)
        return 2
    path = a.skill_file or os.path.join(os.path.abspath(a.skill_root), "SKILL.md")
    if not os.path.isfile(path):
        print("ORCH:FAIL SKILL 不可达 %s" % path, file=sys.stderr)
        return 2
    errs, ok_msg = check(path, a.template_key, a.signpost_key, a.max_lines, a.tail_ratio)
    if errs:
        print("ORCH:FAIL 编排结构闸 %d 项：" % len(errs), file=sys.stderr)
        for e in errs:
            print("   - %s" % e, file=sys.stderr)
        return 1
    print(ok_msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
