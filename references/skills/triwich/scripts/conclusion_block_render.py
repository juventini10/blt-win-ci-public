#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: family=工具|registry=记忆蓝图/04_系统文件设计/布洛陀脚本架构设计哲学/守卫编写规范.md§四|board=记忆蓝图/04_系统文件设计/布洛陀脚本架构设计哲学/03-进度看板.md
"""conclusion_block_render.py — 三明智结论块确定性渲染器（v1.5·2026-11-02·WorkBuddy）

v1.5（2026-11-02 皮叔令「不能这样居中，很难看」）：对齐行居中 :-: 全部回退左贴 :---
  （推翻 v1.2 居中令·单源改判以最新令为准）；T11 断言翻转=锁输出去居中标记、必有左贴行。

v1.4（2026-10-30 用户字面授权「修」·内部记录 落地）：未知未知象限接触法锁——列内容条目拒渲、
  传空表只出占位行且不挂档（四象限地图§现形口径「不进档位体系·⛔永不列清单」的机制承接）。
  （v1.3「B形态带框表」被用户生产屏验否决退役，残件存证记忆琥珀；本版基于 v1.2 还原态。）

v1.2（2026-10-29 你令·观感）：表格对齐行左贴 `:---` 全换居中 `:-:`——病名=长内容列左起一路怼右缘，
  整块视觉重心右倾；selftest 新增 T11 锁输出去左贴标记。
v1.1（2026-10-29 你令）：标题/象限名剥掉 markdown 粗体包壳 `**`——病名=端上渲染不一致时
  符号裸奔上屏；纯文本态与渲染态同貌，展示不赌客户端。
还原注（2026-10-29 23:5x）：v1.3「B形态带框表+去表格化」被用户生产屏验否决（判词「太丑」），
  按令回退至本版；B形态残件存证 记忆琥珀/triwich-strip-bold-bak-20261029/conclusion_block_render.v1.3-Bform-rejected.py。

定位：治"格式由 AI 手写产生"这个病源（脚本哲学 §8.9：病源仍在→治源，⛔建守卫）。
  做法：AI 只提供结构化字段，格式由本纯函数按 SKILL 模板渲染输出。
  => 漏级别名 / 字段序错 / 缺行，结构上不可能发生（缺字段直接拒渲）。
  ✅ 内核层：纯函数、零 hook、任何能跑 python 的端一致（不依赖端 hook 支持）。
  ⛔ 不改任何守卫、不扩闸、不绑 hook。

字段（dict）：level / path_name / evidence_level(灯+级别名) / evidence(≤3) / result
  / next_you / next_system 必填；cognition / anchors 可选。
用法：python3 conclusion_block_render.py --selftest
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys, re, json

LEVELS = ("L1", "L2", "L3")
LAMPS = ("🔴", "🟡", "🟢")
TIER_RX = re.compile(r"^[🔴🟡🟢]\s*(推测级|佐证级|实证级)")
QUAD_ORDER = ("已知已知", "已知未知", "未知已知", "未知未知")


def _need_tokens():
    # "认知格"于 4.12.21 批摘出必出锁：模板条文=有货格<2 整区不挂（自适应可省区），
    #   旧实现当固定 token → 合法无货轮被自己拒渲（2026-10-29 实跑自暴）。
    return ("证据等级", "🎯 结果", "证据等级", "下一步·待你", "下一步·系统")


def _validate(f):
    """接触法：缺任一必填 / 值域非法 => ValueError 物理拒渲（⛔降级输出半截）。"""
    if not isinstance(f, dict):
        raise ValueError("字段必须是 dict")
    if f.get("level") not in LEVELS:
        raise ValueError("level 必填且 ∈ %s，实得 %r" % (LEVELS, f.get("level")))
    if not str(f.get("path_name") or "").strip():
        raise ValueError("path_name 必填")
    el = str(f.get("evidence_level") or "").strip()
    if not el:
        raise ValueError("evidence_level 必填（灯 + 级别名，如 '🟡 佐证级'）")
    if not TIER_RX.match(el):
        raise ValueError("evidence_level 非法：须 灯(🔴🟡🟢)+级别名(推测级/佐证级/实证级) 开头，实得 %r" % el)
    ev = f.get("evidence")
    if not isinstance(ev, list) or not ev:
        raise ValueError("evidence 必填且为列表（1~3 条）")
    if len(ev) > 3:
        raise ValueError("evidence 至多 3 条，实得 %d" % len(ev))
    for i, e in enumerate(ev):
        if not isinstance(e, dict):
            raise ValueError("evidence[%d] 必须是 {tier,text}" % i)
        if not TIER_RX.match(str(e.get("tier") or "").strip()):
            raise ValueError("evidence[%d].tier 须 灯+级别名，实得 %r" % (i, e.get("tier")))
        if not str(e.get("text") or "").strip():
            raise ValueError("evidence[%d].text 必填" % i)
    if not isinstance(f.get("sig"), dict) or not all(str(f["sig"].get(k) or "").strip() for k in ("path", "verdict", "digest", "date")):
        raise ValueError("sig 必填且含 path/verdict/digest/date 四段（v4.12.23 签名进表·签名=第三层表末行⛔表外孤行）")
    if f["sig"]["verdict"] not in ("✅", "❌"):
        raise ValueError("sig.verdict 只接受 ✅/❌（签名二值化），实得 %r" % f["sig"]["verdict"])
    if not str(f.get("result") or "").strip():
        raise ValueError("result 必填（✅/🟡/❌ + 一句话）")
    if "next_you" not in f or not str(f.get("next_you") or "").strip():
        raise ValueError("next_you 必填")
    if "next_system" not in f or not str(f.get("next_system") or "").strip():
        raise ValueError("next_system 必填（无则填 '无'）")
    if f.get("level") == "L3":
        if not str(f.get("agent_b") or "").strip():
            raise ValueError("L3 必填 agent_b（Agent B验证行）")
        ls = f.get("landing_steps")
        if not isinstance(ls, list) or not ls:
            raise ValueError("L3 必填 landing_steps（下一步·落地步骤表·≥1步·⛔压成一句话）")
    # 未知未知接触法锁（v1.4·四象限地图§现形口径）：⛔列内容条目——自报未知未知=用自报补自报；占位请传 []
    cog = f.get("cognition")
    if isinstance(cog, dict):
        uu = cog.get("未知未知")
        if isinstance(uu, list) and uu:
            raise ValueError("未知未知象限⛔列内容条目（自报=用自报补自报·四象限地图§现形口径）；要显盲区意识请传空表 [] 出占位行，或归入已知未知")
    return True


def _cognition_block(cog):
    if not isinstance(cog, dict):
        return ""
    filled = [(q, cog[q]) for q in QUAD_ORDER if isinstance(cog.get(q), list) and cog[q]]
    # 未知未知⛔上屏（2026-10-30 用户精修②）：空=同其他格无货不显；有货=T13a 已拒渲；盲区意识走悬置区落盘
    filled = [(q, items) for q, items in filled if q != "未知未知"]
    if len(filled) < 2:
        return ""
    lines = ["认知格", "", "| 象限 | 本轮条目（档位 ｜ 内容 ｜ 指针） |", "|:---|:---|"]
    for q, items in filled:
        q_cell = q[:2] + "<br>" + q[2:] if len(q) == 4 else q  # 象限名2字×2行对称（用户硬性要求·仅本模块）
        for it in items:
            cell = "%s ｜ %s" % (str(it.get("tier") or "").strip(), str(it.get("desc") or "").strip())
            p = str(it.get("pointer") or "").strip()
            if p:
                cell += " ｜ 指针：%s" % p
            lines.append("| %s | %s |" % (q_cell, cell.replace("|", "｜")))
    lines.append("")
    return "\n".join(lines)


def render(f):
    """按 SKILL 结论块模板确定性渲染 Markdown。非法字段 => ValueError。"""
    _validate(f)
    lvl = f["level"]
    out = ["## %s %s 结果" % (lvl, str(f["path_name"]).strip()), ""]
    out.append("【第一层·深度追溯】")
    out.append("")
    anchors = f.get("anchors") or []
    if anchors:
        # v4.12.24 向第三层教科书对齐：真两列分栏，⛔垫字假对齐；正文过长=挤掉名字列的元凶，上限教填法
        out.append("| 追溯项 | 内容 |")
        out.append("|:---|:---|")
        for a in anchors:
            _sp = str(a).split("：", 1)
            if len(_sp) != 2 or not _sp[0].strip() or not _sp[1].strip():
                raise ValueError("anchors 条目须「名称：内容」两段式，实得 %r" % str(a))
            _nm, _ct = _sp[0].strip(), _sp[1].strip().replace("|", "｜")
            if len(_ct) > 40:
                raise ValueError("追溯项内容 %d 字>40上限——细节住键文件(F8呈现边界)，上屏学第三层短句，实得：%r" % (len(_ct), _ct[:20]))
            out.append("| %s | %s |" % (_nm, _ct))
        out.append("")
    cb = _cognition_block(f.get("cognition"))
    if cb:
        out.append(cb)
    out.append("【第二层·关键依据】")
    out.append("")
    out.append("| 证据等级 |")
    out.append("|:---|")
    for e in f["evidence"]:
        out.append("| %s ｜ %s |" % (str(e["tier"]).strip(), str(e["text"]).strip()))
    out.append("")
    out.append("【第三层·结果+下一步】")
    out.append("")
    out.append("| 项 | 内容 |")
    out.append("|:---|:---|")
    if lvl == "L3":
        out.append("| Agent B验证 | %s |" % str(f["agent_b"]).strip())
    if lvl in ("L2", "L3"):
        out.append("| 验证架构 | %s |" % (str(f.get("verify_arch") or ("L2=单 Agent 自检链（验证者=执行者）" if lvl == "L2" else "L3=双 Agent 独立盲审")).strip()))
    out.append("| 🎯 结果 | %s |" % str(f["result"]).strip())
    out.append("| 证据等级 | %s |" % str(f["evidence_level"]).strip())
    out.append("| 下一步·待你 | %s |" % str(f["next_you"]).strip())
    out.append("| 下一步·系统 | %s |" % str(f["next_system"]).strip())
    _sg = f["sig"]
    _sigtxt = "[🧠 三明智 %s %s ｜ %s ｜ %s]" % (_sg["path"].strip(), _sg["verdict"].strip(), _sg["digest"].strip(), _sg["date"].strip())
    out.append("| 签名 | %s |" % _sigtxt.replace("|", "｜"))
    if lvl == "L3":
        out.append("")
        out.append("下一步·落地步骤")
        out.append("")
        out.append("| 步骤 | 动作 |")
        out.append("|:---|:---|")
        for _i, _s in enumerate(f["landing_steps"], 1):
            out.append("| %d | %s |" % (_i, str(_s).strip()))
    out.append("")
    text = "\n".join(out)
    miss = [t for t in _need_tokens() if t not in text]
    if miss:
        raise ValueError("渲染输出缺 SKILL 同源 token：%s" % "、".join(miss))
    return text


def _selftest():
    good = {
        "level": "L2", "path_name": "分析路径", "evidence_level": "🟢 实证级",
        "evidence": [{"tier": "🟢 实证级", "text": "复现：a"}, {"tier": "🟡 佐证级", "text": "指针：b"}],
        "result": "✅ 通过", "next_you": "等确认", "next_system": "无",
        "sig": {"path": "L2 (分析路径)", "verdict": "✅", "digest": "T件", "date": "2026-10-28"},
        "cognition": {"已知已知": [{"tier": "🟢 实证级", "desc": "x", "pointer": "p"}],
                       "已知未知": [{"tier": "🟡 佐证级", "desc": "y"}]},
        "anchors": ["8要素：n"],
    }
    ok = True
    try:
        out = render(good)
        assert all(t in out for t in _need_tokens()), "缺 NEED token"
        assert "| 证据等级 | 🟢 实证级 |" in out, "证据等级行未含级名"
        print("T1 正例渲染 OK·含全部 NEED + 证据等级灯+级名")
    except Exception as e:
        ok = False; print("T1 FAIL %s" % e)
    b = dict(good); b.pop("evidence_level")
    try:
        render(b); ok = False; print("T2 FAIL 缺 evidence_level 竟渲染成功")
    except ValueError:
        print("T2 缺 evidence_level 拒渲 OK")
    b = dict(good); b["evidence_level"] = "🟡"
    try:
        render(b); ok = False; print("T3 FAIL '🟡'无级别名竟渲染成功")
    except ValueError:
        print("T3 '🟡'缺级别名 拒渲 OK(治源核心证明)")
    b = dict(good); b["evidence"] = [{"tier": "🟢 实证级", "text": "x"}] * 4
    try:
        render(b); ok = False; print("T4 FAIL 超3条竟渲染成功")
    except ValueError:
        print("T4 evidence>3 拒渲 OK")
    b = dict(good); b.pop("next_system")
    try:
        render(b); ok = False; print("T5 FAIL 缺 next_system 竟渲染成功")
    except ValueError:
        print("T5 缺 next_system 拒渲 OK")
    b = dict(good); b["level"] = "L1"
    try:
        o1 = render(b)
        assert "验证架构" not in o1 and "Agent B验证" not in o1 and "落地步骤" not in o1, "L1混入高层专属行"
        print("T6 L1 渲染且不含验证架构/AgentB/落地步骤 层级锁 OK")
    except Exception as e:
        ok = False; print("T6 FAIL %s" % e)
    good3 = dict(good); good3["level"] = "L3"
    good3["agent_b"] = "✅真独立子进程·🔖令牌abc"; good3["landing_steps"] = ["改A", "跑B", "验C"]
    try:
        o3 = render(good3)
        assert "| Agent B验证 |" in o3, "L3缺AgentB行"
        assert "下一步·落地步骤" in o3, "L3缺落地步骤表"
        assert "| 1 | 改A |" in o3, "落地步骤未逐行"
        print("T7 L3 含AgentB行+落地步骤表 OK")
    except Exception as e:
        ok = False; print("T7 FAIL %s" % e)
    b = dict(good3); b.pop("agent_b")
    try:
        render(b); ok = False; print("T8 FAIL L3缺agent_b竟渲染成功")
    except ValueError:
        print("T8 L3缺agent_b拒渲 OK")
    b = dict(good3); b.pop("landing_steps")
    try:
        render(b); ok = False; print("T9 FAIL L3缺落地步骤竟渲染成功")
    except ValueError:
        print("T9 L3缺落地步骤拒渲 OK")
    # T10（2026-10-29 你令·去渲染依赖）：输出全文 ⛔含 "**"——纯文本态与渲染态同貌，符号不裸奔
    _o = render(good)
    _bold_left = [ln for ln in _o.splitlines() if "**" in ln]
    if _bold_left:
        ok = False; print("T10 FAIL 输出残留 **：%s" % _bold_left[:3])
    else:
        print("T10 输出无 ** 残留 OK")
    # T11（v1.5·2026-11-02 皮叔令「居中很难看」翻转断言）：输出对齐行一律左贴 :---，⛔居中标记 :-:
    _center_rows = [ln for ln in _o.splitlines() if ln.strip() in ("|:-:|", "|:-:|:-:|")]
    if _center_rows or ":-:" in _o.replace(":---", ""):
        ok = False; print("T11 FAIL 输出含居中对齐行：%s" % _center_rows[:3])
    elif ":---" not in _o:
        ok = False; print("T11 FAIL 输出缺左贴对齐行")
    else:
        print("T11 表格全部左贴列对齐 OK")
    # T12（4.12.21 批·模板条文≡实现修复）：无认知格数据的合法轮必须可渲（自适应区⛔死锁成必出件）
    b = dict(good); b.pop("cognition")
    try:
        _o2 = render(b)
        assert "认知格" not in _o2, "无货轮却渲染了认知格区"
        print("T12 无认知格数据正常渲染且整区不挂 OK")
    except ValueError as e:
        ok = False; print("T12 FAIL 无货合法轮被拒渲：%s" % e)
    # T13（2026-10-30 v1.4·LRN-005 落地）：未知未知列内容=接触法拒渲；键在位传[]=占位行且不挂档
    b = dict(good); b["cognition"] = dict(good["cognition"]); b["cognition"]["未知未知"] = [{"tier": "🔴 推测级", "desc": "自报枚举样"}]
    try:
        render(b); ok = False; print("T13a FAIL 未知未知列内容竟渲染成功")
    except ValueError:
        print("T13a 未知未知列内容拒渲 OK（接触法）")
    b2 = dict(good); b2["cognition"] = dict(good["cognition"]); b2["cognition"]["未知未知"] = []
    try:
        _o3 = render(b2)
        _ls3 = [x for x in _o3.splitlines()]
        assert "未知未知" not in _ls3 and "🕳️" not in _o3, "空表未知未知仍上屏（应整区不显·盲区走悬置区落盘）"
        assert "占位" not in _o3, "占位文案残留"
        print("T13b 未知未知空表整区不显 OK")
    except AssertionError as e:
        ok = False; print("T13b FAIL %s" % e)
    # T14（2026-10-30 用户精修③v2）：认知格=表格呈现，行线由客户端表格自画；⛔任何手画字符线
    _t4 = render(good)
    if "| 象限 |" not in _t4 or "🟢 实证级 ｜ x ｜ 指针：p |" not in _t4:
        ok = False; print("T14 FAIL 认知格非表格形态（表头或条目行缺失）")
    elif any(ch in _t4 for ch in ("┄", "━", "─", "┌")):
        ok = False; print("T14 FAIL 输出含手画字符线（线应由表格结构自生成，零字符）")
    else:
        print("T14 认知格表格化·行线结构自生成·零字符线 OK")
    # T15（2026-10-30 用户点破第一层贴右=渲染器列结构 bug）：anchors 条目="名称：内容"两段式→两列；无冒号=拒渲（结构保证教填法）
    b5 = dict(good); b5["anchors"] = ["8要素：两面正面有分歧→未触发自爆"]
    _o5 = render(b5)
    if "| 8要素 | 两面正面有分歧→未触发自爆 |" not in _o5:  # 教科书两列形
        ok = False; print("T15a FAIL anchors 未两段成两列")
    else:
        b6 = dict(good); b6["anchors"] = ["无冒号整句"]
        try:
            render(b6); ok = False; print("T15a FAIL 无冒号条目竟渲成功")
        except ValueError:
            print("T15a anchors 两段式两列+无冒号拒渲 OK")
        b7 = dict(good); b7["anchors"] = ["实践检验：x：y 内容带冒号也只切第一段"]
        if "| 实践检验 | x：y 内容带冒号也只切第一段 |" not in render(b7):
            ok = False; print("T15b FAIL 内容多冒号切分错位")
        else:
            print("T15b 内容含冒号只切首段 OK")
    # T16（2026-10-30 A方案落码·用户批准）：sig 必填+渲染为第三层表末行（全角竖杠零破列）；缺/非法=拒渲
    good16 = dict(good); good16["sig"] = {"path": "L1 (批判验证)", "verdict": "✅", "digest": "浓缩版", "date": "2026-10-30"}
    _o16 = render(good16)
    if "| 签名 | [🧠 三明智 L1 (批判验证) ✅ ｜ 浓缩版 ｜ 2026-10-30] |" not in _o16:
        ok = False; print("T16a FAIL 签名未进表末行")
    else:
        b8 = dict(good); b8.pop("sig")  # 摘除 sig 测必填
        try:
            render(b8); ok = False; print("T16a FAIL 缺 sig 竟渲成功")
        except ValueError:
            print("T16a sig 必填+进表末行 OK")
    bl = dict(good); bl["anchors"] = ["8要素：" + "长" * 41]
    try:
        render(bl); ok = False; print("T15c FAIL 超长正文竟渲成功")
    except ValueError:
        print("T15c 追溯项>40字拒渲(细节归键文件) OK")
    b9 = dict(good16); b9["sig"] = dict(good16["sig"]); b9["sig"]["verdict"] = "🟡"
    try:
        render(b9); ok = False; print("T16b FAIL 非二值verdict竟渲成功")
    except ValueError:
        print("T16b 签名二值化锁 OK")
    # T17（2026-10-30 用户硬性要求·仅认知格）：象限名=2字×2行对称显示
    if "| 已知<br>已知 |" not in render(good):
        ok = False; print("T17 FAIL 象限名未2×2对称断行")
    else:
        print("T17 象限名2字×2行对称 OK")
    print("SELFTEST:%s" % ("OK 18/18" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return _selftest()
    try:
        data = json.load(sys.stdin)
        print(render(data))
        return 0
    except ValueError as e:
        sys.stderr.write("RENDER:FAIL %s\n" % e)
        return 2
    except Exception as e:
        sys.stderr.write("RENDER:ERROR %s: %s\n" % (type(e).__name__, e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
