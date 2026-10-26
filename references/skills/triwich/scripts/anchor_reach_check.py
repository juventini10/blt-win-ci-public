#!/usr/bin/env python3
# REG: 通用件（脚本中心守卫族·§13.6 授权登记）·三包内副本为发布自包含投影（回接，同 orchestration_gate 通用件纪律）
# -*- coding: utf-8 -*-
r"""anchor_reach_check.py — 指针可达性抽测闸（v1.1·2026-10-24）
TRUTH_OF: 判据在本文件，⛔不在别处复制。
判据（零误报取向·只报机械可判）：
  A 文件可达：SKILL.md 出现的 `references/*.md` / `pages/*.md` 路径必存在
  B 节名可达：`path#§节名` 形态，节名必须是目标文件某标题的子串
advisory WARN（不计红）：纯 `§节名` 在本文件找不到同名标题（可能指外部规范，人眼判）
v1.1（2026-10-24·迁理之外测试批 N7b/N7c 对照实验实证根治）：路径字符类补
  \u4e00-\u9fa5·——v1.0 字符类 [A-Za-z0-9_./\-] 不含中文，中文命名 references
  （斯多葛.md/寓意与结算.md 等）整体落闸外：路径不检、死锚落 advisory 放行
  （ASCII 死锚红·中文死锚绿=同形态只差字符集）。全库 55 件损伤面预扫 0 死锚，
  放开无副作用。--selftest 内嵌正例+三类负例（ASCII死锚/中文死锚/死路径）。
v1.3（2026-10-25·clock-loop E 路径独立复核 N-6 根治·童灵 D3）：①合法锚点补定义（标题+粗体内联标签同认，此前约定内合法锚被判查不到→整段降级 advisory=仪器恒0检出的结构性成因）②扫描域由 SKILL.md 单件扩到 SKILL+references+pages（⛔排除 CHANGELOG）③裸 § 不硬判红改三档分层计数。
v1.3b（同轮·2026-10-25）：路径字符类补斜杠——v1.0 起该类不含 `/`，而本库主力引用形态是嵌套路径（references/l1/first-principles.md 等），这批引用从建成至今整体落在闸外（报"11 条可达"其实全是单层件）。由 v1.3 扩域当轮的 N6/N7 负例自曝（负例该红而绿=仪器没看这一项）。
v1.4（2026-10-25·挂账清零轮）：§ 引用改「最长可匹配前缀回退」+ 剩余分三档（跨件待确认／包外规范／序号写法／真可疑）。病名：中文无词边界，「§节名」后直接粘正文时被整串比对误判成死锚（本包 7 处），逐条改文档是错治法。配 N8 吞词不误报 + N9 真死锚仍红 双向负例（防回退变放水）。
v1.4b（同轮）：回退下界改 2 字（`§L3` 双字段名曾是盲区）；advisory 由三档扩四档（跨件／包外规范／序号／**形态示例**——反引号内的 `§节名` 是教写法的示例不是指向）；配「分档哨兵」断言防某档吃掉了真死锚。\nv1.4c（同轮·复核 D-2 二次收口）：修本工具自造假绿（resolve_anchor 改二元组后调用点仍用
  真值判断→裸 § 恒"命中"、未匹配恒 0）；分档改为形态示例→序号→包外→归属→未匹配；
  新增「靠前缀回退救回」计数外显；哨兵改双向（救回可见 + 未匹配档仍能响）。
v1.2（2026-10-24·ZCode 童灵·advisory 双计根治）：BARE_SEC_PAT 加 (?<!#) 负向断言——
  path#§锚 形态已由 ANCHOR_PAT 验证可达，其 § 段不再重复落 advisory 名单（此前已验证锚
  与真裸引用混报·读者无法分辨哪些需人眼判·sucair 实测 7 advisory 中 6 个为双计）。
  纯 §裸引用（§前非#）照报·selftest 不依赖 warn 判据。
用法：python3 scripts/anchor_reach_check.py [--skill-root DIR] [--selftest]
退出码：0=全可达/selftest 全过；1=存在断锚/selftest 有失守
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import io
import os
import re
import shutil
import sys
import tempfile

PATH_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_/\u4e00-\u9fa5·\-]+\.md)")
ANCHOR_PAT = re.compile(r"(?<![A-Za-z0-9_./\-])((?:references|pages)/[A-Za-z0-9_/\u4e00-\u9fa5·\-]+\.md)#§([^\s`）)，,。;；、+]+)")
BARE_SEC_PAT = re.compile(r"(?<!#)§([A-Za-z\u4e00-\u9fa5][A-Za-z0-9\u4e00-\u9fa5\-]{1,15})")  # v1.3d：· 是描述词分隔符不是节名字符  # v1.3c：首字符须为字母/汉字（剔 §2d、§12 这类序号写法），后续类不含顿号句点（§一、存量… 此前被切成"三存量既往不计入…"当节名报=噪声淹信号）


BOLD_LABEL = re.compile(r"^(?:[*>+-]\s*)?\*\*([^*]{2,48}?)\*\*")


def headings(path):
    """合法锚点 = ①Markdown 标题 ②粗体内联标签。
    ②不是妥协是本库既有约定（flow-agent-b.md 自注「段锚非节标题·v4.5.1 如实标注」）：
    v1.0-1.2 只认标题，于是约定内的合法锚全被判"查不到"，只能整段降级 advisory 放行——
    这正是"仪器恒 0 检出=它其实没测这一项"的结构性成因（本窗 p-mechanism §10 死指针从此缝漏走，
    直到人眼抓）。v1.3 起两者同认。"""
    if not os.path.isfile(path):
        return None
    out = []
    for line in io.open(path, encoding="utf-8", errors="ignore"):
        t = line.strip()
        m = re.match(r"^#{1,6}\s+(.*)$", line.strip())
        if m:
            out.append(m.group(1).strip())
            continue
        m2 = BOLD_LABEL.match(t)
        if m2:
            out.append(m2.group(1).strip())
    return out


EXTERNAL_HINT = re.compile(
    r"(?:规范|白皮书|协议|OWASP|宪法|原则|记忆蓝图|Skill架构|v\d+\.\d+|通用规范)")
ORDINAL = re.compile(r"^(?:[一二三四五六七八九十0-9]{1,3}(?:、|[.．]|[0-9]|附)?|[一二三四五六七八九十]{1,3})")
# 反引号内的 § 是「形态示例」（教人怎么写引用），不是对某节的指向——与"包外规范""序号写法"同属非可疑档。
# 判据=§ 之前反引号个数为奇（在开着的 code span 内）。⚠️曾用 `[^`]*$` 式正则判：那等于"后面没反引号就算内"，
#      被 selftest 分档哨兵当场证伪（把闭合反引号之后的正常引用也判成示例档）。
def in_codespan(prefix):
    return prefix.count("`") % 2 == 1


def resolve_anchor(sec, pool):
    """§ 引用判定：中文无词边界，`§节名` 后常直接粘正文（本包实测 7 处被吞），整串比对会把
    合法引用误报成死锚——逐条改文档是错治法。v1.4 用「最长可匹配前缀回退」；
    v1.4c 返回 (命中名, 是否靠回退) 供调用方统计"被救回条数"（降噪量＝可疑量）；
    2 字档只认去装饰后从头命中，⛔走 contains（短档 contains＝放水）。"""
    DECOR = " #@\t·、,，.。:：()（）【】-—"
    if not sec:
        return None, False
    for k in range(len(sec), 1, -1):
        cand = sec[:k]
        for h in pool:
            if k >= 3:
                if cand in h:
                    return cand, k < len(sec)
            elif h.lstrip(DECOR).startswith(cand):
                return cand, k < len(sec)
    return None, False


def domain_files(root, primary):
    """扫描域 = 主文件 + references/**.md + pages/**.md；⛔排除 CHANGELOG 历史叙述
    （叙述性记录不是合同，纳入判据=假红制造机；与考题项44/55 同口径）。"""
    files = [primary]
    for sub in ("references", "pages"):
        for dirpath, _dn, fs in os.walk(os.path.join(root, sub)):
            for f in fs:
                if f.endswith(".md") and f != "CHANGELOG.md":
                    files.append(os.path.join(dirpath, f))
    return [f for f in files if os.path.isfile(f)]


def check(root):
    """返回 (bad, paths, anchors, warn)；供 CLI 与 selftest 共用。"""
    skill = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill):
        return ["SKILL.md 不可达 %s" % skill], [], [], [], 0, [], [], [], [], [], []
    texts = {p: io.open(p, encoding="utf-8", errors="ignore").read()
             for p in domain_files(root, skill)}

    bad = []
    paths = sorted({p for t in texts.values() for p in PATH_PAT.findall(t)})
    for rel in paths:
        if not os.path.isfile(os.path.join(root, rel)):
            bad.append("文件不可达 %s" % rel)
    anchors = sorted({(a, b) for t in texts.values() for a, b in ANCHOR_PAT.findall(t)})
    for rel, sec in anchors:
        hs = headings(os.path.join(root, rel))
        if hs is None:
            bad.append("锚点目标缺失 %s#§%s" % (rel, sec))
            continue
        if not any(sec in h for h in hs):
            bad.append("节名不存在 %s#§%s" % (rel, sec))
    # 纯 § 裸引用：⛔不硬判红（包外规范如「指令编写规范 §1.1」合法存在，硬判=造大批假红），
    # 改**三档分层**把最可疑那档摊到台面上：命中本件=静默 / 命中包内他件=跨件待人眼确认归属 / 全包未命中=最可疑。
    LEDGER_HINTS = ("decision-room",)  # v1.3d：台账件＝叙述位（与 CHANGELOG 同理），裸§只从合同件采集
    files = [p for p in texts if not any(h in p for h in LEDGER_HINTS)]
    own_map = {p: (headings(p) or []) for p in files}
    all_head = {h for hs in own_map.values() for h in hs}
    warn, elsewhere, external, ordinal, example, rescued = [], [], [], [], [], []
    for p in files:                      # v1.3d：按缩后的采集域遍历
        body = texts[p]
        for m in BARE_SEC_PAT.finditer(body):
            sec = m.group(1)
            pre = body[:m.start()]
            _ls = body.splitlines()
            _li = pre.count("\n")
            line = _ls[_li] if _li < len(_ls) else (_ls[-1] if _ls else "")
            if pre.split("\n")[-1].count("`") % 2 == 1:
                example.append(sec)                        # 反引号内＝形态示例，非指向
                continue
            if ORDINAL.match(sec):
                ordinal.append(sec)                        # 序号引用
                continue
            if EXTERNAL_HINT.search(line):
                external.append(sec)                       # 同句含规范/版本＝包外引用
                continue
            # ⚠️ 修本工具自造的假绿（复核 D-2·lead 复算证实）：v1.4 把 resolve_anchor 改成返回
            #    二元组后调用点仍写 `if resolve_anchor(...)`——非空元组恒真 ⇒ 所有裸 § 一律判"命中"，
            #    "真可疑=0"是这把闸自己造的假数。现显式判 None，并把靠回退救回的条数单独摊出来。
            hit_own, fell_own = resolve_anchor(sec, own_map[p])
            if hit_own is not None:
                if fell_own:
                    rescued.append(sec)
                continue
            hit_el, fell_el = resolve_anchor(sec, all_head)
            if hit_el is not None:
                elsewhere.append(sec)
                if fell_el:
                    rescued.append(sec)
                continue
            warn.append(sec)                               # 未匹配
    warn, elsewhere, external, ordinal, example, rescued = (sorted(set(x)) for x in
                                                            (warn, elsewhere, external, ordinal,
                                                             example, rescued))
    return (bad, paths, anchors, warn + elsewhere, len(texts), warn, elsewhere,
            external, ordinal, example, rescued)


def selftest():
    base = tempfile.mkdtemp(prefix="anchor_reach_selftest_")
    ok = True
    try:
        def run_case(name, expect_red, skill_body, refs):
            nonlocal ok
            root = os.path.join(base, name)
            os.makedirs(os.path.join(root, "references"), exist_ok=True)
            io.open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8").write(skill_body)
            for fn, content in refs.items():
                fp = os.path.join(root, "references", fn)
                os.makedirs(os.path.dirname(fp), exist_ok=True)  # v1.3 自纠：夹具带子目录时首版必崩
                io.open(fp, "w", encoding="utf-8").write(content)
            bad, paths, anchors, warn = check(root)[:4]
            red = bool(bad)
            good = red == expect_red
            if not good:
                ok = False
            print("%s %s%s" % ("✅" if good else "❌失守", name,
                               "" if good else " | bad=%s paths=%s" % (bad[:2], paths)))

        good_refs = {"中文件.md": "# 中文件\n\n## 存在节\n", "ascii.md": "# ascii\n\n## sec-one\n"}
        run_case("T0-正例(应绿)", False,
                 "# T\n\n看 `references/中文件.md` 与 `references/ascii.md`；实锚 references/中文件.md#§存在节。\n",
                 good_refs)
        run_case("N1-ASCII死锚(应红)", True,
                 "# T\n\n坏 references/ascii.md#§不存在的节XYZ\n", good_refs)
        run_case("N2-中文路径死锚(应红·v1.0盲区)", True,
                 "# T\n\n坏 references/中文件.md#§不存在的节XYZ\n", good_refs)
        run_case("N3-中文路径缺失(应红·v1.0盲区)", True,
                 "# T\n\n坏 `references/不存在的中文文件.md`\n", good_refs)
        run_case("N4-模板占位不误伤(应绿)", False,
                 "# T\n\n详见 `references/{视角}.md` 追问指南。\n", good_refs)
        # v1.3 新增三例：粗体标签可锚（判据变更兑现）+ 域内死锚/死路径必须被逮（扩域兑现）
        refs_v13 = dict(good_refs)
        refs_v13["bold.md"] = "# b\n\n> **段锚标签**：正文\n\n## 真标题\n"
        run_case("N5-粗体内联标签可锚(应绿·v1.3判据)", False,
                 "# T\n\n实锚 references/bold.md#§段锚标签 与 references/bold.md#§真标题。\n",
                 refs_v13)
        run_case("N6-域内件死锚(应红·v1.2域外在闸)", True,
                 "# T\n\n看 references/l1/x.md#§根本没有的节XYZ\n",
                 {"l1/x.md": "# x\n\n## 只有这节\n"})
        run_case("N7-域内路径死链(应红·扩域兑现)", True,
                 "# T\n\n看 `references/l1/ghost.md`。\n",
                 {"l1/x.md": "# x\n\n## 只有这节\n"})
        # v1.4 双向负例：吞节名后正文不得误报成死锚（本包实测 7 处），
        #        同时真死锚必须仍然判红（防"回退"退化成放水）
        swallow = {"sw.md": "# s\n\n**思维顺序判定(v4.4.0)**：正文\n\n## 输出格式\n\n## 路径基线\n"}
        run_case("N8-吞节名后正文不误报(应绿·v1.4)", False,
                 "# T\n\n见 `references/sw.md`：顺序由 §思维顺序判定决定；下文 §输出格式的 全文；"
                 "另 §路径基线声明段 同源。\n", swallow)
        run_case("N9-真死锚仍判红(应红·回退不放水)", True,
                 "# T\n\n坏 references/sw.md#§幽灵节名XYZ\n", swallow)

        # v1.4 分档哨兵：形态示例 / 纯序号 / 包外规范 三档不得吃掉真可疑
        tier_root = os.path.join(base, "tiers")
        os.makedirs(os.path.join(tier_root, "references"))
        io.open(os.path.join(tier_root, "SKILL.md"), "w", encoding="utf-8").write(
            "# T\n\n判据写法 `§节名` 属示例；本包另有 `§节名` 之外的引用；"
            "引用外部规范 §十一.4 本质属性；同句另有 §五、5 型序号。\n")
        io.open(os.path.join(tier_root, "references", "t.md"), "w", encoding="utf-8").write(
            "# t\n\n## 真标题\n")
        _b, _p, _a, _w4, _n, tier_warn, tier_else, tier_ext, tier_ord, tier_ex = check(tier_root)[:10]
        # 断言：示例档只吃"反引号内"那一个；序号档接到 §十一/§五；包外档接住带规范字样的；真可疑清零
        tier_ok = (not tier_warn and set(tier_ex) == {"节名"} and len(tier_ord) >= 1)
        print("%s 分档哨兵: 真可疑=%s 示例档=%s 序号档=%s 包外档=%s" % (
            "✅" if tier_ok else "❌失守", tier_warn, tier_ex, tier_ord, tier_ext))
        if not tier_ok:
            ok = False
        # D-2 双哨兵：a) 被回退救回的伪引用必须可见；b) 无锚可回的裸 § 必须落未匹配
        #（只测 a 会漏"整档恒 0"型假绿——上一版断言正栽在这儿）
        d2 = os.path.join(base, "d2")
        os.makedirs(os.path.join(d2, "references"))
        io.open(os.path.join(d2, "SKILL.md"), "w", encoding="utf-8").write(
            "# T\n\n参见 `references/d.md`：§甲乙根本不存在的一长串字。\n"
            "另有 §完全无锚可回退XYZ 属未匹配。\n")
        io.open(os.path.join(d2, "references", "d.md"), "w", encoding="utf-8").write(
            "# d\n\n## 甲乙丙丁戊\n")
        _r = check(d2)
        a_ok = any("甲乙" in x for x in _r[10])
        b_ok = any("完全无锚可回退" in x for x in _r[5])
        print("%s D-2 双哨兵: 救回可见=%s 未匹配仍响=%s | 救回%s 未匹配%s" % (
            "✅" if a_ok and b_ok else "❌失守", a_ok, b_ok, list(_r[10]), list(_r[5])))
        if not (a_ok and b_ok):
            ok = False
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SELFTEST:%s（正例绿·死锚连红·吞词不误报·占位符不误伤）" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = os.path.abspath(a.skill_root)
    bad, paths, anchors, _all, nfiles, warn, elsewhere, external, ordinal, example, rescued = check(root)
    if bad:
        print("ANCHOR:FAIL %d 处断锚（路径 %d·锚点 %d）：" % (len(bad), len(paths), len(anchors)), file=sys.stderr)
        for b in bad:
            print("   " + b, file=sys.stderr)
        return 1
    print("ANCHOR:OK 全域 %d 件·路径 %d 条可达·锚点 %d 条可锚"
          "（合法锚=标题+粗体内联标签；§引用=最长可匹配前缀回退·v1.4）"
          % (nfiles, len(paths), len(anchors)))
    print("      advisory 分档：跨件待确认 %d·包外规范 %d·序号写法 %d·形态示例 %d·⚠️未匹配 %d"
          % (len(elsewhere), len(external), len(ordinal), len(example), len(warn)))
    print("      靠前缀回退救回 %d 条（吞词降噪面＝可疑面；未匹配归零≠包内无死裸 §引用；判红只由 path#§ 承担）：%s"
          % (len(rescued), "、".join(rescued[:6]) or "无"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
