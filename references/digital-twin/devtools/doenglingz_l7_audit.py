#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doenglingz_l7_audit.py — 童灵 L7 五通道机械对账器（观察制·不裁决）

设计定位（你令 2026-09-09「三件现在能做几件？能做的都做完」）：
  把 L7 五项从「文本特征命中」（弱证据·可被话术触发）升为「台账 + 落盘产物对账」（强证据）——
  ①错误→成长箱   = LEARNINGS/ERRORS 中 来源 AI=<tool> 且 Logged 在窗口内的条目数
  ②铁律反哺     = experience/规范反哺日志.md 中窗口内新增条目数 + 目标文件版本是否随之变动
  ③立场卡反哺   = AI学习库/INDEX.md 窗口内新增卡数 + step3-first-review-log.md 窗口内初审行数
  ④系统日志     = 当日系统日志 <tool> 段条目数 + 守护台账 tsl_l7_syslog 命中行数
  ⑤反思沉淀     = 当日系统日志 [童灵思考] 条目数 + 守护台账 tsl_l7_reflection 命中行数

防镀金（立场卡 S030「改机制不镀金」）：
  每个通道必须给出 分子/分母 + 数据源条数，⛔DO NOT 只给布尔值。
  观察制：本脚本只报数不裁决（L7 是否达标由 06 §2.7.3 人工复核口径 + 你终审）。

用法：
  python3 doenglingz_l7_audit.py                    # 默认 --days 1 --tool LobsterAI
  python3 doenglingz_l7_audit.py --days 7 --json
"""
# Win console UTF-8 guard (auto by clock-loop 1.7.2)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta

HOME = os.path.expanduser("~")
BASE = os.path.expanduser("[记忆共享中心]")
LEARNINGS = os.path.join(BASE, "成长箱/learnings")
FANBU = os.path.join(BASE, "成长箱/experience/规范反哺日志.md")
INDEX = os.path.join(BASE, "AI学习库/INDEX.md")
REVIEW = os.path.join(BASE, "数字分身/steps/step3-first-review-log.md")
SYSLOG_DIR = os.path.join(BASE, "工作日志/系统日志")
LEDGER_FMT = os.path.join(HOME, ".workbuddy/doenglingz_guard_state_%s.json")

TOOL_LEDGER_KEY = {"LobsterAI": "lobsterai", "AutoClaw": "autoclaw", "WorkBuddy": "workbuddy",
                   "Qoder Desktop": "qoderdesktop", "Qoder CN": "qodercn", "MiniMax Code": "minimaxcode"}
TOOL_LEDGER_ROOT = {"qoderdesktop": "~/.qoder", "qodercn": "~/.qoder-cn", "minimaxcode": "~/.minimax"}


def _read(p, limit=4_000_000):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except Exception:
        return ""


def _dates(win):
    return {(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(win)}


def _tool_names(tool):
    """端名归一：工具名 → 可匹配名集合（规范名 + 同组变体）·真源=system-logger/normalize_tool.py。

    2026-10-23 实证（假红形态·铁律-031 阴性读数先验尺）：LEARNINGS 写「WorkBuddy」87 条，
    评级器传 end_id「workbuddy」⇒ 字符串不等 ⇒ ①通道 num=0——「尺没量到」被当成「对象真缺」。
    ⚠️ 只收同组变体（VARIANTS 值相同者）⛔不跨组（否则 Trae/Trae CN/Trae Work 互撞）；
    ⛔排除 <4 字符短变体（wb/zw/tl 等易假匹配）。
    """
    names = {tool}
    try:
        import importlib.util
        _p = os.path.expanduser("[记忆共享中心]/技能配置/system-logger/scripts/normalize_tool.py")
        _spec = importlib.util.spec_from_file_location("_ntool", _p)
        _m = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_m)
        _canon = _m.VARIANTS.get(_m.norm_key(tool)) or (tool if tool in _m.ALLOWLIST else None)
        if _canon:
            names.add(_canon)
            for _k, _v in _m.VARIANTS.items():
                if _v == _canon and len(_k) >= 4:
                    names.add(_k)
    except Exception:
        pass
    return names


def _name_pat(tool):
    """端名集合 → 正则（大小写不敏感·整词优先）"""
    return re.compile("|".join(re.escape(n) for n in sorted(_tool_names(tool), key=len, reverse=True)),
                      re.IGNORECASE)


def ch1_growthbox(tool, win, dates):
    """① 错误→成长箱：来源 AI=<tool> 且 Logged 日期在窗口内。"""
    num, den, src = 0, 0, []
    _pat1 = re.compile(r"来源 AI\*\*:\s*(" +
                       "|".join(re.escape(n) for n in sorted(_tool_names(tool), key=len, reverse=True)) + ")",
                       re.IGNORECASE)
    for name in os.listdir(LEARNINGS) if os.path.isdir(LEARNINGS) else []:
        if not name.endswith(".md") or name.startswith("INDEX"):
            continue
        p = os.path.join(LEARNINGS, name)
        t = _read(p)
        if not t:
            continue
        src.append(name)
        # 2026-10-23 切块口径根治：原式只切 `## [`（二级标题）·⛔不认 `### [`（三级标题·LEARNINGS.md 近期记录的实际方言）
        #   ⇒ 整份文件被当成一块·取块内第一处 Logged（他人旧记录）⇒ 本端新记录一条数不到（实测 num=0·den=1）
        #   ⛔ 改前口径与 growth_box_schema_check.py v2.3.4「方言兼容·`### [ID]` 同认」不一致（两台仪器口径打架）
        #   ✅ 改法：每个记录头（二级或三级）独立成块 ⇒ 逐条判 Logged·本端记录算数
        for block in re.split(r"\n(?=#{2,3}\s+\[)", t):
            if _pat1.search(block):
                den += 1
                m = re.search(r"\*\*Logged\*\*:\s*(\d{4}-\d{2}-\d{2})", block)
                if m and m.group(1) in dates:
                    num += 1
    return num, den, src


def ch2_rule_feedback(tool, win, dates):
    """② 铁律反哺：反哺日志窗口内新增条目（## 段）数。"""
    t = _read(FANBU)
    if not t:
        return 0, 0, ["（反哺日志缺失）"]
    blocks = [b for b in re.split(r"\n## ", t) if b.strip()]
    num = sum(1 for b in blocks if any(d in b[:200] for d in dates))
    return num, len(blocks), ["规范反哺日志.md"]


def ch3_stance_cards(tool, win, dates):
    """③ 立场卡反哺：INDEX 窗口内新增卡数（日期列）+ 初审台账窗口内行数。"""
    t = _read(INDEX)
    cards = re.findall(r"^\|\s*(立场卡#[SK]\d+)\s*\|[^\n]*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", t, re.M)
    num_cards = sum(1 for _, d in cards if d in dates)
    rt = _read(REVIEW)
    rows = re.findall(r"^\|\s*\d+\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", rt, re.M)
    num_rows = sum(1 for d in rows if d in dates)
    return num_cards + num_rows, len(cards) + len(rows), ["AI学习库/INDEX.md", "step3-first-review-log.md"]


def own_attribution(tool, dates):
    """本端自有产物计数（端归属归因·观察口径·2026-10-23 反哺 R-20261023-01 补信号）。

    背景：②规范反哺日志 与 ③立场卡 INDEX/初审台账 是**跨端共享面**，条目不带端归属字段
    ⇒ 他端产物可代偿本端达标（端级等级假绿来源：机械推导 L7 而本端②③自有产物=0）。
    本函数只加『条目内含端名标记』这一正交信号：
      - num（ch2/ch3 的全局池计数）**口径不变** ⇒ 不扰他端既有评级结论；
      - own（本端自有）另计，供端级定档区分「本端自有达标」与「共享池代偿达标」。
    端标记缺失的存量条目仍落在全局池 ⇒ 其归因不可机械判定 ⇒ 须显形（见输出 note_own）。
    """
    own = {}
    t = _read(FANBU)
    if t:
        blocks = [b for b in re.split(r"\n## ", t) if b.strip()]
        _p2 = _name_pat(tool)
        own["②铁律反哺"] = sum(1 for b in blocks if any(d in b[:200] for d in dates) and _p2.search(b))
    ti = _read(INDEX)
    if ti:
        rows = [l for l in ti.splitlines() if re.match(r"^\|\s*(立场卡#[SK]\d+)\s*\|", l)]
        _p3 = _name_pat(tool)
        own["③立场卡反哺"] = sum(1 for l in rows if _p3.search(l) and any(d in l for d in dates))
    tr = _read(REVIEW)
    if tr:
        rows = [l for l in tr.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
        own["③立场卡反哺"] = own.get("③立场卡反哺", 0) + sum(
            1 for l in rows if _p3.search(l) and any(d in l for d in dates))
    return own


def _syslog_section(tool, date):
    p = os.path.join(SYSLOG_DIR, f"系统日志_{date}.md")
    t = _read(p)
    if not t:
        return "", 0, 0
    _pat2 = re.compile(r"^##\s+(?:" +
                       "|".join(re.escape(n) for n in sorted(_tool_names(tool), key=len, reverse=True)) +
                       r")\s*$([\s\S]*?)(?=^##\s|\Z)", re.M | re.IGNORECASE)
    m = _pat2.search(t)
    sec = m.group(1) if m else ""
    entries = len([l for l in sec.splitlines() if l.strip() and not l.startswith(("-", ">", "①", "②", "③", "④", "⑤"))])
    reflections = sec.count("[童灵思考]") + sec.count("[童灵反思]")
    return sec, entries, reflections


def ch45_syslog_reflection(tool, win, dates, ledger_rows):
    """④ 系统日志 / ⑤ 反思沉淀：当日段条目数 + 台账 tsl 命中行数。"""
    e4 = e5 = 0
    for d in sorted(dates):
        _, entries, refl = _syslog_section(tool, d)
        e4 += entries
        e5 += refl
    h4 = sum(1 for r in ledger_rows if "ts_l7_syslog" in (r.get("tsl_hits") or ""))
    h5 = sum(1 for r in ledger_rows if "ts_l7_reflection" in (r.get("tsl_hits") or ""))
    return (e4, h4), (e5, h5), ["工作日志/系统日志/系统日志_YYYY-MM-DD.md", "守护台账 tsl_hits"]


def load_ledger(tool, dates):
    key = TOOL_LEDGER_KEY.get(tool, tool.lower())
    root = os.path.expanduser(TOOL_LEDGER_ROOT.get(key, "~/.workbuddy"))
    p = os.path.join(root, f"doenglingz_guard_state_{key}.json")
    rows = []
    for line in _read(p).splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        ts = str(r.get("ts", ""))[:10]
        if ts in dates or any(d[5:] in ts for d in dates):  # 容忍 UTC/本地差
            rows.append(r)
    return rows, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", default="LobsterAI")
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    dates = _dates(a.days)
    ledger_rows, ledger_path = load_ledger(a.tool, dates)

    n1, d1, s1 = ch1_growthbox(a.tool, a.days, dates)
    n2, d2, s2 = ch2_rule_feedback(a.tool, a.days, dates)
    n3, d3, s3 = ch3_stance_cards(a.tool, a.days, dates)
    (e4, h4), (e5, h5), s45 = ch45_syslog_reflection(a.tool, a.days, dates, ledger_rows)

    ch = [
        {"ch": "①错误→成长箱", "num": n1, "den": d1, "src": ",".join(s1), "note": "来源 AI=%s 且 Logged 在窗口内" % a.tool},
        {"ch": "②铁律反哺", "num": n2, "den": d2, "src": ",".join(s2), "note": "反哺日志窗口内新增段"},
        {"ch": "③立场卡反哺", "num": n3, "den": d3, "src": ",".join(s3),
         "note": "全库窗口内新增卡+初审行（⚠️归端不可机械判定·观察口径·卡/行未记工具归属）"},
        {"ch": "④系统日志", "num": max(h4, e4), "den": max(len(ledger_rows), e4), "src": ",".join(s45),
         "note": "台账 ts_l7_syslog 命中 %d / 台账 %d 行；产物=当日段条目 %d（2026-10-21 起 产物∪台账取或·动作即凭证）" % (h4, len(ledger_rows), e4)},
        {"ch": "⑤反思沉淀", "num": max(h5, e5), "den": max(len(ledger_rows), e5), "src": ",".join(s45),
         "note": "台账 ts_l7_reflection 命中 %d / 台账 %d 行；产物=当日 [童灵思考] %d（2026-10-21 起 产物∪台账取或·动作即凭证）" % (h5, len(ledger_rows), e5)},
    ]
    own = own_attribution(a.tool, dates)
    # ①④⑤ 天然按端取数（来源 AI=<tool> / 系统日志段名）⇒ own==num
    # ②③ 为跨端共享面 ⇒ own=条目内含端归属标记者（🌐反哺端 / 🔧反哺工具 / 分区标题 / INDEX来源列）
    own["①错误→成长箱"] = n1
    own["④系统日志"] = max(h4, e4)
    own["⑤反思沉淀"] = max(h5, e5)
    for _c in ch:
        _c["own"] = own.get(_c["ch"], _c["num"])
    out = {"tool": a.tool, "window_days": a.days, "ledger": ledger_path, "ledger_rows": len(ledger_rows),
           "channels": ch, "own": own,
           "note_own": "own=本端自有产物计数（条目内含端名标记·按端归因）；num=全局池计数（既有口径·本轮未改·不扰他端评级结论）"
                       "；②③为跨端共享面 ⇒ num-own 之差=代偿读数·不得作本端定档依据（反哺 R-20261023-01·E9.2 待你终审）"
                       "；评级器读数三态：own>0=✅本端自证／num>0且own=0=🟠共享池·本端不可自证（不截断·不记绿）／num=0=🟡证据零（截断）"}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print("## 🧾 童灵 L7 五通道机械对账（%s · 近 %d 天）" % (a.tool, a.days))
    print()
    print("| 通道 | 分子 | 分母 | 说明 | 数据源 |")
    print("|---|---:|---:|---|---|")
    for c in ch:
        print("| %s | %d | %d | %s | %s |" % (c["ch"], c["num"], c["den"], c["note"], c["src"]))
    print()
    print("> 台账 %s · 窗口内 %d 行 · 判据=台账/落盘产物对账（⛔不采文本特征）" % (ledger_path, len(ledger_rows)))
    print("> 观察制：只报数不裁决——L7 达标与否由 06 §2.7.3 人工复核口径 + 你终审")


if __name__ == "__main__":
    main()
    sys.exit(0)
