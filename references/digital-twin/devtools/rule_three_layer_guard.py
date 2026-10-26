#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rule_three_layer_guard.py — 守卫「记忆规则三层文件」版本号 + 铁律集合一致性

根因修复（2026-08-21）：
    三层规则文件（铁律版/摘要版/详解存档版）靠「版本号铁律」文档纪律维持一致，
    但 v8.0/v8.1 两次升版均只改了铁律版，另两层停在 v7.9.8 且缺 013-16
    —— 与 card_id_guard / skill_version_guard / mirror verify_parity 同源：
    多文件不变量靠人工记忆同步 = 结构性必然漂移（C-005 承诺衰减）。
    本脚本让「三层一致」成为可被机械检查的运行时门禁（而非文档纪律）。
    ✅ 2026-08-21 首跑检出漂移（铁律版 v8.2 vs 摘要版 v8.1 vs 详解存档版 v8.1）→
    触发摘要版+详解存档版升 v8.2 修复 → 复测三层一致（版本号 + 铁律上界 17 均对齐）。
    根因修复（2026-09-12）：本端 transcript 为嵌套格式 `{"type":role,"message":{role,content:[...]}}`，
    read_transcript 只兜 list 未兜 dict → `d["message"]` 直供正则抛 TypeError，整条守卫在 Stop 上
    崩死（实测 7 次，连带 ④⑤⑥ 与三层一致性检查在受影响会话中从未执行）。修法=dict 解包内层
    content/role + 非 str 归一跳过；④⑤取「末条助手消息」须文本非空，防 tool_use 空条目使检查名存实亡。
    接入扩展（2026-10-25·MiniMax Code 第 21 端）：④-静态 调度层巡查由三端扩为四端——
    新增 MiniMax Code 端（落 ~/.minimax/AGENTS.md·本端无 MEMORY.md 注入面·与 ZCode 端同构）；
    本端 AGENTS.md 同轮补「🔑 触发句（D4 门禁·该读没读）」段（触发句 + 指向铁律版「加载时机」索引）。
    ⚠ 本件为共享件·发布库/win-ci/Github 发布版共 16 处活副本（本轮改后与真源指纹分叉）→ 出副本核对单交各面自取自核（列归属签名制）。

检查不变量：
    ① 版本号：三文件头部 `> 版本：vX.Y` 必须相等
    ② 铁律集合上界：铁律版 vs 详解存档版 所覆盖的 铁律 最大编号必须相等
       - 铁律版：全量 `铁律-0NN` 最大编号
       - 摘要版：**不参与上界比对**（2026-09-16 瘦身为「你画像」文件·架构性不含铁律清单；
         2026-09-17 遗留3根治已在码里排除——见 main() 的 MAX_EXEMPT。本行旧措辞"铁律速查表
         最大编号"引用的是已退役载体，2026-10-01 实测曾把"读注释不读码"的复核者带偏成
         "判据没跟着改"的误判，故按码实况改写）
       - 详解存档版：指针 `铁律-001~NNN` 的 NNN
       - 🔴 假绿根治（2026-10-01 变异实测）：必解析层（铁律版/详解存档版）上界取不到值
         (None) **不等于一致**。旧写法 `if k != "摘要版" and v is not None` 会把消失的被检
         对象静默剔出比对，只剩单层时 len(set)==1 → 判绿=仪器空转却报平安。现改为显形
         （json 键 `tielu_max_unresolved` + 告警行），并补自测例 T5c/T5d 覆盖该形态。
    ③ 铁律版描述计数一致性：铁律版 frontmatter `description:"...N条硬约束"` 与
       标题 `## 🔴 AI执行铁律（N条·不可违反）` 的数字 N，必须 == 实际铁律上界
       （即 `铁律-0NN` 最大编号）。根因修复（2026-08-31）：v8.6 时 description/标题
       仍写 "14条"，而体已 19 条——纯文档纪律查不到，故加机械不变量。
    ④ D4 读取时门禁（该读没读）：进度看板原标"不实现·靠纪律兜底"——但愿景要求
       "全自动化·不靠人记得"，靠纪律=结构性必然漂移。故拆两层机械校验：
       ④-静态（常驻可跑）验证 各端调度层（WB/豆包 MEMORY.md + ZCode AGENTS.md）触发句→铁律版「加载时机」索引布线正确；
       ④-动态（需 WB Stop 钩子喂 transcript·stdin {"transcript_path"}）扫描末条助手
       消息，凡引用具体 铁律-0NN 却无查阅锚点（铁律版/已读/加载时机）即告警。
       默认 warn-only，不谎称完美（G4 透明标残留）。

    ⑤ 冲突/边缘场景→详解版门禁（该读没读）：与 ④ 同族。根因修复（2026-08-31）：
       三层渐进加载中 详解版(第三层) 的"按需加载/冲突才读"只是 prompt 声明路径
       （铁律版 line13-15「①规则冲突 → 必须 Read 详解存档版」），无机械路径——
       settings.json 零"详解/冲突"挂载、本守卫旧版只查版本一致性。真冲突时靠 AI
       自觉走 4 跳（命中铁律触发→读铁律版→看到"冲突须读详解版"→识别冲突），无守卫
       兜底=结构性必然漂移（C-005 承诺衰减·与 D1/D4 同源）。本段把"冲突/边缘场景须读
       详解版"补成机械门禁：扫末条助手消息，凡处冲突/边缘场景（规则冲突/要改规则/边缘
       情况/用户问规则为什么这样/成长箱晋升复查）却无查阅详解版锚点→告警。默认 warn-only。

退出码：0=一致（或仅告警）  1=发现漂移（--strict 时）
默认 warn-only（只告警不拦截），仿 card_id_guard「告警不阻断」模式——
避免升版过程中（先改一层后改另一层）误拦合法编辑；漂移在每次 Stop 可见即达防复发目的。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys as _sys, os as _os; _SCROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))); _SCROOT in _sys.path or _sys.path.insert(1, _SCROOT)  # sc-rootfix-20261014 域搬补路
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_triggers_loader import load_triggers, extract_tielu_index_ids

HOME = os.path.expanduser("~")
BASE = os.path.join(os.path.expanduser("[记忆共享中心]"), "记忆规则")  # v2.1.5(2026-10-08 Qoder CN·Stop真红回修)：v2.1.4注释写HOME+相对段却塞了作者机绝对路径(v1.2.237③所罚之病·假绿藏形态)→脱敏投影通道剥段回写成~/记忆规则(v2.1.1病根)→D4真红。正解=HOME+相对段三例齐。
_CFG_ROOT = os.environ.get("WORKBUDDY_CONFIG_DIR") or os.path.join(HOME, ".workbuddy")
MEMORY_PATH = os.path.join(_CFG_ROOT, "MEMORY.md")
# 豆包办公端 MEMORY（2026-09-11 P2 扩展：豆包端无钩子·静态常驻可跑同样适用·双端同巡）
DOUBAO_MEMORY_PATH = os.path.join(os.path.expanduser("[记忆共享中心]"), "豆包办公系统文件", "MEMORY.md")  # v2.1.5 剥段回修（真文件7460B在·10-08 ls实证）
# ZCode 端注入通道（2026-09-12 接入：ZCode 实测 MEMORY.md 不注入·唯一常驻通道=AGENTS.md，
# 故布线巡查落 AGENTS.md 而非 MEMORY.md——与童灵 K2 切片落点同构）
ZCODE_AGENTS_PATH = os.path.join(HOME, ".zcode", "AGENTS.md")
# MiniMax Code 端注入通道（2026-10-25 接入：第 21 端·本端无 MEMORY.md 注入面·
# 唯一常驻通道=AGENTS.md，故布线巡查落 AGENTS.md——与 ZCode 端同构）
MINIMAX_AGENTS_PATH = os.path.join(HOME, ".minimax", "AGENTS.md")
# ── 端配置根目录（在场判据）·抽成模块常量 ⇐ 夹具可注入（2026-10-25 治尺）──
# 病：d4_static 里豆包/ZCode/MiniMax 三端的在场目录原先从 HOME **内联硬算** ⇒
#   夹具改不动 ⇒ 「端不在本机」场景**根本没被测到**（自测 12/16·T6a/b/c 全红·实测根因）。
#   治法：四端配置根目录一律模块级常量 ⇒ 运行期可注入 ⇒ 缺席/在场两态真能测。
DOUBAO_CFG_DIR = os.path.join(os.path.expanduser("[记忆共享中心]"), "豆包办公系统文件")
ZCODE_CFG_DIR = os.path.join(HOME, ".zcode")
MINIMAX_CFG_DIR = os.path.join(HOME, ".minimax")
# ── 端在场判据（2026-10-25·MiniMax Code 端·端缺席治尺）────────────────────
# 病：d4_static 对「四端调度层文件」逐端硬判存在性 ⇒ 在**只装了其中一端**的机器上，
#   缺席端一律报「调度层文件缺失」⇒ **跨端假红**（实测：只装 ZCode 的机器 ⇒ 报 WB/豆包/MiniMax 三端缺失）。
#   ⛔ 该病是**既存病**（WB/豆包/ZCode 三元组时代就有）·不是本轮引入 —— 但本轮加第四端会再添一条。
#   ⚠️ 影响面真存在：该守卫挂在 LobsterAI / Qoder CN / Trae Work 三端（发布面 capability 实证），
#      这三端所在机器通常**不装** WB/豆包/ZCode/MiniMax Code ⇒ 副本一旦带第四端行 ⇒ 那些端立刻报红。
# 治法（治尺·不放松真检测）：
#   **端不在本机 ⇒ 跳过该端**（端缺席 ≠ 端失守）；**端在场但接线没做 ⇒ 仍报红**。
#   在场判据＝该端**配置根目录**存在（比调度层文件存在更宽·端装了但文件没落=真失守仍要报）。
#   ⇒ 端在但文件缺 ⇒ 报红（真失守）｜端不在 ⇒ 跳过（假红归零）｜端在且接线缺失 ⇒ 报红（真病灶）
TIELU_FILE = os.path.join(BASE, "用户基本规则-铁律版.md")
def _first_existing(*names):
    """取第一个真实存在的路径；全不存在 ⇒ 返回第一个（供报「文件缺失」用）。"""
    for n in names:
        p = os.path.join(BASE, n)
        if os.path.isfile(p):
            return p
    return os.path.join(BASE, names[0])


# 🆕 2026-10-03 修「改名后守卫读旧名」：真源侧三层第三层已在 10-02 迁到
#   `用户基本规则-详解存档版.md`（47KB·v8.28·权威名·MEMORY/安装器 RULE_FILES 均用它），
#   旧名 `用户基本规则-详解存档.md`（24KB·10-01）是退役残留。守卫仍读旧名 ⇒
#   装完声明的是「版」而守卫找「无版」⇒ e2e 门禁判「文件缺失」（假红·2026-10-03 实锤）。
#   修法=**新版优先·旧名兜底**：⛔ 不只改死新名（下次再改名又红），兼容两个已知名。
FILES = {
    "铁律版": os.path.join(BASE, "用户基本规则-铁律版.md"),
    "摘要版": os.path.join(BASE, "用户基本规则-摘要版.md"),
    "详解存档版": _first_existing("用户基本规则-详解存档版.md",
                                 "用户基本规则-详解存档.md"),
}

VERSION_RE = re.compile(r"版本：v(\d+\.\d+)")
TIELU_RE = re.compile(r"铁律-(\d{3})")
DETAIL_PTR_RE = re.compile(r"铁律-001~(\d{3})")
DESC_COUNT_RE = re.compile(r"(\d+)条硬约束")
TITLE_COUNT_RE = re.compile(r"AI执行铁律（(\d+)条")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_version(text):
    m = VERSION_RE.search(text)
    return m.group(1) if m else None


def parse_tielu_max(text, which):
    if which == "详解存档版":
        m = DETAIL_PTR_RE.search(text)
        return int(m.group(1)) if m else None
    nums = [int(x) for x in TIELU_RE.findall(text)]
    return max(nums) if nums else None


def parse_desc_count(text):
    m = DESC_COUNT_RE.search(text)
    return int(m.group(1)) if m else None


def parse_title_count(text):
    m = TITLE_COUNT_RE.search(text)
    return int(m.group(1)) if m else None


# ---- D4：读取时门禁（该读没读）----
# 根因修复（2026-08-31）：进度看板原标 D4「不实现（拦截 Read 更重更脆，靠纪律兜底）」。
#   但「全自动化·不靠人记得」是愿景四方向之一——靠纪律=结构性必然漂移（C-005 承诺衰减）。
#   本段把 D4 拆为两层机械校验：
#     ④-静态（常驻可跑·无需会话）：MEMORY.md 触发句必须存在且指向 铁律版「加载时机」索引，
#             且 铁律版 该索引真实存在 → 保证门禁*目标布线*正确（纪律的靶子被机械锁死）。
#     ④-动态（需 WB Stop 钩子喂 transcript）：扫描末条助手消息，凡引用具体 铁律-0NN 却未带
#             查阅锚点（铁律版/已读/加载时机）→ 告警。锚点是"真读了细则"的可观测代理：
#             真读必引 铁律版 或 加载时机 或 标"已读"，凭记忆断言则无锚点 → 门禁可见。
#   默认 warn-only（与守卫整体哲学一致），不阻断合法编辑流；不谎称完美（G4 透明标残留）。
D4_APPLY_RE = re.compile(r"铁律-(0\d\d)")
D4_ANCHOR_RE = re.compile(r"铁律版|已读铁律|read 铁律|Read 铁律|加载时机")


def read_stdin_transcript():
    """WB Stop 钩子约定：stdin 喂 {"transcript_path": "..."}。返回路径或 None。"""
    # 交互式手动运行（stdin 是 TTY 且不会 EOF）→ 直接跳过，避免 read() 永久阻塞
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.buffer.read().decode('utf-8', errors='replace').strip()
    except Exception:
        return None
    if not raw:
        return None
    try:
        d = json.loads(raw)
    except Exception:
        # 非 JSON（裸文本）则当作转录内容直接用
        return raw if os.path.exists(raw) else None
    p = d.get("transcript_path") or d.get("transcript") or d.get("path")
    return p


def read_transcript(path):
    """读 JSONL transcript → [(role, text)]。

    2026-09-23 童灵根治：收敛到共享解析层（守卫编写规范 §3.12 单一入口律）。
    原自写实现已兼容双格式，此处替换为等价调用，端扩展只改共享层一处。
    """
    import sys as _sys
    _root = os.path.join(os.path.expanduser("[记忆共享中心]"), "脚本中心")  # v2.1.5 剥段回修
    if _root not in _sys.path:
        _sys.path.insert(0, _root)
    try:
        import transcript_reader as _tr
        return _tr.iter_messages(path)
    except Exception:
        return []


def d4_static():
    """④-静态：调度层触发句布线 + 铁律版 加载时机索引存在性（WB + 豆包办公 + ZCode + MiniMax Code 四端）。
    WB 布线标记=「触发句」/「D4」；豆包办公端标记=「铁律骨架」；ZCode 端标记=「三层触发链」；
    MiniMax Code 端标记=「触发句」（本端 AGENTS.md 已补 D4 触发句段·2026-10-25·同 ZCode 形态）
    （落 AGENTS.md——ZCode 实测 MEMORY.md 不注入，唯一常驻通道=AGENTS.md，2026-09-12 接入）。
    豆包端无钩子（rule_fragment_inject 不可复刻），静态布线检查为机制在场兜底，warn-only 不阻断。

    **端缺席跳过**（2026-10-25·端缺席治尺）：端**不在本机**⇒ 跳过该端（端缺席 ≠ 端失守），
    端**在场**但调度层文件缺/未接线 ⇒ 仍报红（真失守不放过）。
    治的是既存跨端假红（只装一端的机器上其余端一律报缺失）——⛔不放松真检测。"""
    results = []
    skipped = []
    for name, mp, cfg_dir in (
        ("WB", MEMORY_PATH, _CFG_ROOT),
        ("豆包办公", DOUBAO_MEMORY_PATH, DOUBAO_CFG_DIR),
        ("ZCode", ZCODE_AGENTS_PATH, ZCODE_CFG_DIR),
        ("MiniMax Code", MINIMAX_AGENTS_PATH, MINIMAX_CFG_DIR),
    ):
        # 端不在本机 ⇒ 跳过（不判红）——2026-10-25 端缺席治尺
        if not os.path.isdir(cfg_dir):
            skipped.append(name)
            continue
        if not os.path.exists(mp):
            results.append(f"{name}端 调度层文件缺失")
            continue
        mt = read(mp)
        has_wire = ("触发句" in mt) or ("D4" in mt) or ("铁律骨架" in mt) or ("三层触发链" in mt)
        if not has_wire:
            results.append(f"{name}端 调度层缺「触发句/铁律骨架/三层触发链」→ 该读没读门禁未布线")
            continue
        if "加载时机" not in mt:
            results.append(f"{name}端 调度层触发句未指向 铁律版「加载时机」索引")
            continue
        results.append(f"{name}端 布线正确")
    if not os.path.exists(TIELU_FILE):
        return False, "铁律版 文件缺失"
    tt = read(TIELU_FILE)
    if "加载时机" not in tt:
        return False, "铁律版 缺「加载时机」索引表 → 触发句无靶可瞄"
    bad = [r for r in results if "正确" not in r]
    if bad:
        return False, "；".join(bad)
    # 全部在场端都通过；缺席端显形（不判红·但可见）
    if skipped:
        return True, "四端调度层 触发句→铁律版加载时机索引 布线正确（" + "；".join(results) + "）｜缺席端跳过：" + "、".join(skipped) + "（端不在本机·非失守）"
    return True, "四端调度层 触发句→铁律版加载时机索引 布线正确（" + "；".join(results) + "）"


# stdin 单次解析缓存：D4 与 ⑤ 同一次 Stop 调用共享，避免第二次 read() 拿到空 stdin
_STDIN_TP_CACHE = None
_STDIN_TP_DONE = False


def get_transcript_path():
    """解析 stdin（Stop 钩子喂 {"transcript_path"}），结果缓存供 D4/⑤ 复用。"""
    global _STDIN_TP_CACHE, _STDIN_TP_DONE
    if not _STDIN_TP_DONE:
        _STDIN_TP_CACHE = read_stdin_transcript()
        _STDIN_TP_DONE = True
    return _STDIN_TP_CACHE


def d4_dynamic():
    """④-动态：末条助手消息引用具体铁律却无查阅锚点→告警。需 transcript 传入。"""
    tp = get_transcript_path()
    if not tp:
        return None, "未收到会话文本，跳过（WB 钩子传参启用后自动激活）"
    msgs = read_transcript(tp)
    if not msgs:
        return None, "transcript 解析为空，跳过"
    # 取最后一条 assistant 消息
    last = ""
    for role, text in reversed(msgs):
        if role.lower() in ("assistant", "ai", "tool_result_excluded") and text.strip():
            last = text
            break
    if not last:
        return None, "末条助手消息未定位，跳过"
    applies = D4_APPLY_RE.findall(last)
    if not applies:
        return True, "末条回复未引用具体铁律号，无需锚点"
    has_anchor = bool(D4_ANCHOR_RE.search(last))
    if has_anchor:
        return True, f"末条回复引用铁律-{','.join(sorted(set(applies)))} 且带查阅锚点 ✅"
    return False, f"末条回复引用铁律-{','.join(sorted(set(applies)))} 但无查阅锚点（铁律版/已读/加载时机）→ 疑似凭记忆断言未读细则"


# ---- ⑤：冲突/边缘场景 → 详解版门禁（该读没读）----
# 根因（2026-08-31）：三层渐进加载中 详解版(第三层) 的"按需加载/冲突才读"
#   只是 prompt 声明路径（铁律版 line13-15「①规则冲突 → 必须 Read 详解存档版」），
#   无机械路径——settings.json 零"详解/冲突"挂载、本守卫旧版只查版本一致性。真冲突时
#   靠 AI 自觉走 4 跳（命中铁律触发→读铁律版→看到"冲突须读详解版"→识别冲突），无守卫
#   兜底=结构性必然漂移（C-005 承诺衰减·与 D1/D4 同源）。本段把"冲突/边缘场景须读
#   详解版"补成机械门禁，与 ④ 同族（该读没读），复用 get_transcript_path + read_transcript；
#   默认 warn-only，不阻断。
D5_TRIGGER_RE = re.compile(
    r"规则冲突|冲突.*规则|铁律.*冲突|要修改.*规则|修改.*这条规则|"
    r"边缘情况|为什么.*这.*规则|成长箱.*晋升|晋升.*复查"
)
# 锚点须是「正向读取动作 + 详解版」，且前面无否定词（没/未/不/无/没有/未读/不去），
# 否则"没有去读详解版"会被误判成已读（B 组负例实证）
D5_ANCHOR_RE = re.compile(
    r"(?<!没)(?<!未)(?<!不)(?<!无)(?<!没有)(?<!未读)(?<!不去)"
    r"(?:Read|读了|查阅|已读|参考|看了|去读|读取|阅读)\s*"
    r"(?:用户基本规则-?)?详解存档版?"
)


def d5_static():
    """⑤-静态：铁律版必须声明 冲突/边缘→详解版 路径（靶子被机械锁死）。"""
    if not os.path.exists(TIELU_FILE):
        return False, "铁律版 文件缺失"
    tt = read(TIELU_FILE)
    if "规则冲突" not in tt or "详解存档" not in tt:
        return False, "铁律版 未声明「冲突→详解存档版」路径 → ⑤门禁无靶"
    return True, "铁律版 已声明「冲突→详解存档版」路径 ✅"


def d5_dynamic():
    """⑤-动态：末条助手消息处冲突/边缘场景却无查阅详解版锚点→告警。需 transcript。"""
    tp = get_transcript_path()
    if not tp:
        return None, "未收到会话文本，跳过（WB 钩子传参启用后自动激活）"
    msgs = read_transcript(tp)
    if not msgs:
        return None, "transcript 解析为空，跳过"
    last = ""
    for role, text in reversed(msgs):
        if role.lower() in ("assistant", "ai", "tool_result_excluded") and text.strip():
            last = text
            break
    if not last:
        return None, "末条助手消息未定位，跳过"
    m = D5_TRIGGER_RE.search(last)
    if not m:
        return True, "末条回复未处冲突/边缘场景，无需读详解版"
    has_anchor = bool(D5_ANCHOR_RE.search(last))
    if has_anchor:
        return True, "末条回复处冲突/边缘场景且带查阅详解版锚点 ✅"
    return False, (f"末条回复处冲突/边缘场景（'{m.group(0)}'）但无查阅详解版锚点 "
                   f"→ 应 Read 用户基本规则-详解存档版")


# ---- ⑥ 规则触发规格覆盖守卫（yaml 条数 == 铁律版索引表条数·数字不落注释）----
# 根因修复（2026-09-01 Solution A）：rule_triggers.yaml 是 铁律版「加载时机索引表」的编译产物，
#   预注入机制(rule_fragment_inject.py)靠它工作。若两处 id 漂移（加铁律忘更 yaml / 反之），
#   预注入会漏注或注错=硬墙出现洞=结构性必然漂移（与 ④⑤ 同源 C-005）。
#   本段把"触发规格 == 真源索引表"补成机械门禁（静态·无需 transcript），与 ④⑤ 同族。
# ⚠️ 2026-10-01 去写死计数：本注释与下方 docstring 原均写「19 条」，实盘已 29 条——
#   铁律每加一条这里就漂一次，且漂的是**描述层**（判定用 len(yaml_ids) 变量·不受影响）。
#   这正是本日 021④「描述层当现状」事故的载体侧根源，故按"计数要么机械派生要么不落注释"清除。
def _match_gap_notice(triggers):
    """match 覆盖显形（2026-10-01·只报数不翻 pass/fail）。

    空 match ＝「有法无触发器」：条文在册，但没有任何场景会把它读出来——
    属"无人知晓时最可能造成不可逆损害"那一类（铁律-029 自己就是这么漏的）。
    ⛔ 不因此判红：`rule_fragment_eval.py:244` 明示 020-028 是**有意留空**
    （"凑话覆盖 020-029＝假覆盖比无覆盖更坏"），判红会天天假红、把真缺口淹成噪音。
    做法＝把留空条数与名单摆到巡检输出里，让"在册≠在跑"从隐形变成显形。
    """
    res = [str(t.get("id")) for t in triggers if t.get("resident")]
    empty = [str(t.get("id")) for t in triggers
             if not (t.get("match") or []) and str(t.get("id")) not in res]
    if not empty:
        return "｜match 覆盖：非 resident 条全部有触发词 ✅"
    return ("｜⚠️ match 留空 %d 条（有法无触发器·有意取舍非缺陷·名单与实测见 "
            "rule_fragment_eval.py）：%s" % (len(empty), ",".join(empty)))


def d6_coverage():
    """⑥ 覆盖守卫：rule_triggers.yaml 须覆盖铁律版索引表全部条目且 anchor 存在。"""
    yaml_path = os.path.join(BASE, "rule_triggers.yaml")
    if not os.path.exists(yaml_path):
        return False, "rule_triggers.yaml 缺失 → 预注入机制无触发规格"
    try:
        triggers = load_triggers(yaml_path)
    except Exception as e:
        return False, f"解析 rule_triggers.yaml 失败: {e}"
    yaml_ids = sorted(t.get("id") for t in triggers)
    if not os.path.exists(TIELU_FILE):
        return False, "铁律版 缺失"
    idx_ids = extract_tielu_index_ids(read(TIELU_FILE))
    if yaml_ids != idx_ids:
        return False, f"触发规格与铁律版索引表 id 漂移: yaml={yaml_ids} 索引={idx_ids}"
    tt = read(TIELU_FILE)
    for t in triggers:
        anc = t.get("source_anchor")
        if anc and anc not in tt:
            return False, f"触发 {t.get('id')} anchor 不在铁律版: {anc}"
    return True, ("触发规格覆盖 %d 条且与铁律版索引表对齐 ✅" % len(yaml_ids)) + _match_gap_notice(triggers)


def self_test():
    """--self-test 五组用例（2026-09-17 补·核销 2026-08-22 高危无自测欠账·守卫编写规范 §3.0·5）。

    T4/T5 为崩溃回归负例：drift 非空时 --deliver 路径不得因 drift[:2] 抛 TypeError。
    实锤（2026-09-17）：drift = 六个布尔 or 链 → 结果是 bool，第457行 drift[:2] 对 bool 切片
    → TypeError: 'bool' object is not subscriptable → 守卫崩溃静默掩盖三层漂移达 19 天
    （config_guard 检出 150 次崩溃却被回落律当存量旧账容忍）。修复=drift 改为原因列表。
    全程临时目录 patch 路径常量——不碰真库；hook_protocol 打桩不真送达。
    """
    import importlib.util, tempfile, types, io, contextlib, ast, shutil

    # 打桩 hook_protocol（避免真送达宿主）
    delivered = []
    fake = types.ModuleType("hook_protocol")
    fake.alert = lambda *a, **k: (delivered.append(a), 0)[1]
    sys.modules["hook_protocol"] = fake

    # 载入自身副本（隔离全局，不污染运行态）
    spec = importlib.util.spec_from_file_location("rtl_selftest_copy", __file__)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.read_stdin_transcript = lambda: None  # d4/d5 动态锚点跳过（无 transcript）

    results = []

    def ck(name, cond):
        results.append((name, bool(cond)))

    # T1-T3 单元：解析函数正确性
    ck("T1 parse_version", m.parse_version("xx 版本：v8.16 yy") == "8.16")
    ck("T2 parse_tielu_max(铁律版=22/详解=19)",
       m.parse_tielu_max("铁律-001 铁律-022", "铁律版") == 22
       and m.parse_tielu_max("铁律-001~019", "详解存档版") == 19)
    ck("T3 parse_desc/title_count",
       m.parse_desc_count("22条硬约束") == 22
       and m.parse_title_count("AI执行铁律（22条") == 22)

    def build(tmp, versions, maxes):
        names = {"铁律版": "用户基本规则-铁律版.md",
                 "摘要版": "用户基本规则-摘要版.md",
                 "详解存档版": "用户基本规则-详解存档.md"}
        paths = {}
        for layer, fn in names.items():
            p = os.path.join(tmp, fn)
            mx = maxes[layer]
            body = "版本：v%s\n" % versions[layer]
            if layer == "详解存档版":
                # mx=None 夹具＝指针行消失（假绿根治用例 T5c 用）
                body += ("铁律-001~%03d\n" % mx) if mx else ""
            elif mx:
                body += "铁律-001 铁律-%03d\n" % mx
                if layer == "铁律版":
                    body += "%d条硬约束\nAI执行铁律（%d条·不可违反）\n" % (mx, mx)
            with open(p, "w", encoding="utf-8") as f:
                f.write(body)
            paths[layer] = p
        return paths

    tmp = tempfile.mkdtemp(prefix="rtl_selftest_")
    old_argv = sys.argv

    def setup(versions, maxes):
        paths = build(tmp, versions, maxes)
        m.FILES = paths
        m.TIELU_FILE = paths["铁律版"]
        m.BASE = tmp
        m.MEMORY_PATH = os.path.join(tmp, "no_memory.md")
        m.DOUBAO_MEMORY_PATH = os.path.join(tmp, "no_db.md")
        m.ZCODE_AGENTS_PATH = os.path.join(tmp, "no_zcode.md")
        m.MINIMAX_AGENTS_PATH = os.path.join(tmp, "no_minimax.md")

    def run_json():
        buf = io.StringIO()
        sys.argv = ["rule_three_layer_guard.py", "--json"]
        with contextlib.redirect_stdout(buf):
            m.main()
        out = buf.getvalue().strip()
        return ast.literal_eval(out.splitlines()[-1]) if out else {}

    try:
        V = {"铁律版": "8.16", "摘要版": "8.16", "详解存档版": "8.16"}
        # T5a 假红回归（遗留3根治）：摘要版画像残留"铁律-019"，铁律版=详解版=22
        #   → 排除摘要版后 max_drift 应 False（不再假红）
        setup(V, {"铁律版": 22, "摘要版": 19, "详解存档版": 22})
        try:
            ck("T5a 摘要版画像残留不误报(max_drift=False)", run_json().get("tielu_max_drift") is False)
        except Exception:
            ck("T5a 摘要版画像残留不误报(max_drift=False)", False)

        # T5b 真检出：铁律版22 vs 详解版19（真上界漂移·排除摘要版后仍须检出·防只会回落不会再红）
        setup(V, {"铁律版": 22, "摘要版": 22, "详解存档版": 19})
        try:
            ck("T5b 真上界漂移仍检出(max_drift=True)", run_json().get("tielu_max_drift") is True)
        except Exception:
            ck("T5b 真上界漂移仍检出(max_drift=True)", False)

        # T5c 假绿回归（2026-10-01 变异实测·被检对象消失不得判绿）：
        #   详解版指针行消失→上界解析 None→参与比对只剩铁律版一层
        #   旧写法 len(set)==1 判绿(仪器空转报平安)；根治后须 max_drift=True 且 unresolved 显形
        setup(V, {"铁律版": 22, "摘要版": 22, "详解存档版": None})
        try:
            _r = run_json()
            ck("T5c 详解版上界消失判红(max_drift=True)", _r.get("tielu_max_drift") is True)
            ck("T5c 判据失效层显形(unresolved=[详解存档版])",
               _r.get("tielu_max_unresolved") == ["详解存档版"])
        except Exception:
            ck("T5c 详解版上界消失判红(max_drift=True)", False)
            ck("T5c 判据失效层显形(unresolved=[详解存档版])", False)

        # T5d 豁免不误伤：摘要版 None（画像文件常态）不得进 unresolved——
        #   否则 09-16 瘦身的架构性事实被当成判据失效，守卫天天假红
        setup(V, {"铁律版": 22, "摘要版": None, "详解存档版": 22})
        try:
            _r = run_json()
            ck("T5d 摘要版None不误红(max_drift=False)", _r.get("tielu_max_drift") is False)
            ck("T5d 摘要版不入失效名单(unresolved=[])", _r.get("tielu_max_unresolved") == [])
        except Exception:
            ck("T5d 摘要版None不误红(max_drift=False)", False)
            ck("T5d 摘要版不入失效名单(unresolved=[])", False)

        # T6 端缺席治尺（2026-10-25·MiniMax Code 端）——**四向夹具**：
        #   ① 端**不在本机**（配置根目录不存在）⇒ 跳过该端（不得判红）——治既存跨端假红
        #      （只装一端的机器上其余端一律报「调度层文件缺失」= 假红·该守卫挂在 LobsterAI/Qoder CN/Trae Work 三端）
        #   ② 端**在场**（配置根目录存在）但调度层文件缺 ⇒ 仍须报红（端缺席治尺不得放松真检测）
        #   ③ 端**在场**且接线完整 ⇒ 判绿
        #   ④ 端**在场**、文件在但**接线没做**（无触发句）⇒ 仍须报红（治的是「缺席」不是「失守」）
        #   ⚠️ 夹具要点（实测踩坑·2026-10-25）：
        #     a) 须让**配置根目录不存在**（不是只把文件路径指空）——只指空文件路径＝「端在场但文件缺」＝②场景。
        #     b) 须让**四端配置根目录全部可注入**——原实现里豆包/ZCode/MiniMax 三端从 HOME **内联硬算**，
        #        夹具改不动 ⇒ 「端缺席」场景根本没被测到（真源已治：抽成模块常量 DOUBAO_CFG_DIR/ZCODE_CFG_DIR/MINIMAX_CFG_DIR）。
        #     c) 须让 **TIELU_FILE 含「加载时机」索引**——d4_static 在靶子层会早退（返回「铁律版 缺加载时机」），
        #        端侧结果根本没被比到 ⇒ ②的 ok=False 会「撞对」而文案断言必失败。
        _cfg = os.path.join(tmp, "endirs")
        os.makedirs(_cfg, exist_ok=True)
        _absent = os.path.join(tmp, "absent_endirs")  # 故意不创建＝端不在本机
        # 伪铁律版（含「加载时机」索引⇒d4_static 靶子层不早退）
        _tielu_t6 = os.path.join(tmp, "tielu_t6.md")
        with open(_tielu_t6, "w", encoding="utf-8") as _f:
            _f.write("版本：v8.16\n铁律-001 铁律-022\n22条硬约束\nAI执行铁律（22条·不可违反）\n加载时机\n")
        # 端状态统一注入器：cfg_dirs=四端配置根目录·files=四端调度层文件路径
        _END_KEYS = ("MEMORY_PATH", "DOUBAO_MEMORY_PATH", "ZCODE_AGENTS_PATH", "MINIMAX_AGENTS_PATH",
                     "_CFG_ROOT", "DOUBAO_CFG_DIR", "ZCODE_CFG_DIR", "MINIMAX_CFG_DIR", "TIELU_FILE")

        def _end_state(cfg_dirs, files):
            (m.MEMORY_PATH, m.DOUBAO_MEMORY_PATH, m.ZCODE_AGENTS_PATH, m.MINIMAX_AGENTS_PATH,
             m._CFG_ROOT, m.DOUBAO_CFG_DIR, m.ZCODE_CFG_DIR, m.MINIMAX_CFG_DIR, m.TIELU_FILE) = \
                files[0], files[1], files[2], files[3], cfg_dirs[0], cfg_dirs[1], cfg_dirs[2], cfg_dirs[3], _tielu_t6

        _abs_files = (os.path.join(_absent, "wb", "MEMORY.md"),
                      os.path.join(_absent, "db", "MEMORY.md"),
                      os.path.join(_absent, ".zcode", "AGENTS.md"),
                      os.path.join(_absent, ".minimax", "AGENTS.md"))
        _abs_dirs = (os.path.join(_absent, "wb"), os.path.join(_absent, "db"),
                     os.path.join(_absent, ".zcode"), os.path.join(_absent, ".minimax"))
        _save_end = {}

        def _t6_run(cfg_dirs, files):
            """注入端状态 → 跑一次 → 还原（任何异常都还原·不留脏状态）"""
            nonlocal _save_end
            for _k in _END_KEYS:
                _save_end[_k] = getattr(m, _k)
            try:
                _end_state(cfg_dirs, files)
                return run_json()
            finally:
                for _k, _v in _save_end.items():
                    setattr(m, _k, _v)

        # ① 全端缺席（配置根目录不存在）⇒ d4_static 必判绿
        try:
            _r = _t6_run(_abs_dirs, _abs_files)
            ck("T6a 全端缺席⇒d4_static 判绿(ok=True)", _r.get("d4_static", {}).get("ok") is True)
            ck("T6a 缺席端显形于 msg（含「缺席端跳过」）",
               "缺席端跳过" in _r.get("d4_static", {}).get("msg", ""))
        except Exception:
            ck("T6a 全端缺席⇒d4_static 判绿(ok=True)", False)
            ck("T6a 缺席端显形于 msg（含「缺席端跳过」）", False)
        # ② 端在场但文件缺（配置根存在·调度层文件不存在）⇒ 必报红
        try:
            _r = _t6_run((_cfg, _cfg, _cfg, _cfg),
                         (os.path.join(_cfg, "no_wb.md"), os.path.join(_cfg, "no_db.md"),
                          os.path.join(_cfg, "no_zcode.md"), os.path.join(_cfg, "no_minimax.md")))
            ck("T6b 端在场但调度层文件缺⇒仍报红(ok=False)", _r.get("d4_static", {}).get("ok") is False)
            ck("T6b 报红文案含「调度层文件缺失」",
               "调度层文件缺失" in _r.get("d4_static", {}).get("msg", ""))
        except Exception:
            ck("T6b 端在场但调度层文件缺⇒仍报红(ok=False)", False)
            ck("T6b 报红文案含「调度层文件缺失」", False)
        # ③ 端在场且接线完整 ⇒ 判绿
        try:
            _wired = os.path.join(_cfg, "wired.md")
            with open(_wired, "w", encoding="utf-8") as _f:
                _f.write("触发句：见铁律版 加载时机\n加载时机\n")
            _r = _t6_run((_cfg, _cfg, _cfg, _cfg), (_wired, _wired, _wired, _wired))
            _d4 = _r.get("d4_static", {})
            ck("T6c 端在场且接线完整⇒判绿(ok=True)", _d4.get("ok") is True)
            ck("T6c 接线完整时四端均显形「布线正确」",
               _d4.get("msg", "").count("端 布线正确") == 4)
        except Exception:
            ck("T6c 端在场且接线完整⇒判绿(ok=True)", False)
            ck("T6c 接线完整时四端均显形「布线正确」", False)
        # ④ 端在场·文件在·但接线没做 ⇒ 仍须报红（治的是「缺席」不是「失守」）
        try:
            _unwired = os.path.join(_cfg, "unwired.md")
            # ⚠️ 伪文件正文**不得含**「触发句/D4/铁律骨架/三层触发链」任一字样——
            #    否则 has_wire 判据被喂饱 ⇒ 撞进下一分支（文案变「未指向加载时机」）⇒ 夹具失准。
            with open(_unwired, "w", encoding="utf-8") as _f:
                _f.write("端调度层空壳文件\n（本端未接入调度层）\n")
            _r = _t6_run((_cfg, _cfg, _cfg, _cfg), (_unwired, _unwired, _unwired, _unwired))
            ck("T6d 端在场但接线未做⇒仍报红(ok=False)", _r.get("d4_static", {}).get("ok") is False)
            ck("T6d 报红文案含「该读没读门禁未布线」",
               "该读没读门禁未布线" in _r.get("d4_static", {}).get("msg", ""))
        except Exception:
            ck("T6d 端在场但接线未做⇒仍报红(ok=False)", False)
            ck("T6d 报红文案含「该读没读门禁未布线」", False)

        # T4 崩溃回归：drift 非空（承 T5b 场景 max_drift=True）+ --deliver → 不得 TypeError + 告警送达
        delivered.clear()
        buf2 = io.StringIO()
        try:
            sys.argv = ["rule_three_layer_guard.py", "--deliver"]
            with contextlib.redirect_stdout(buf2):
                m.main()
            ck("T4 deliver 崩溃回归(drift[:2] 不得 TypeError)", True)
            ck("T4b deliver 告警已送达宿主桩", len(delivered) >= 1)
        except Exception:
            ck("T4 deliver 崩溃回归(drift[:2] 不得 TypeError)", False)
            ck("T4b deliver 告警已送达宿主桩", False)
    finally:
        sys.argv = old_argv
        shutil.rmtree(tmp, ignore_errors=True)

    npass = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print("  %s %s" % ("✅" if ok else "❌", name))
    print("[rule_three_layer_guard self-test] %d/%d 通过" % (npass, len(results)))
    return 0 if npass == len(results) else 1


def d7_dual_name():
    """⑦ 双名并存巡查（2026-10-09 缺陷③根治·布洛陀2.1.0上游反馈·告警不裁决）。

    根因：上游 10-02 把第三层权威名从「用户基本规则-详解存档.md」迁到
    「用户基本规则-详解存档版.md」，安装器 RULE_FILES/守卫都改了，但**旧名没有
    退役动作**——老用户升级后双名并存，守卫 _first_existing 按权威名优先读数，
    旧名若才是更全的本机内容就被判「三层漂移」（假红·刚叔 r2 实测 v8.28/上界30 误报）。
    处置：只显形告警（并入→归档是文件主/你的裁决，⛔守卫不代删——本机=唯一主源，
    守卫对主源文件只做观察）。返回 (ok, msg)。"""
    _n = os.path.join(BASE, "用户基本规则-详解存档版.md")
    _o = os.path.join(BASE, "用户基本规则-详解存档.md")
    if os.path.isfile(_n) and os.path.isfile(_o):
        return False, ("双名并存：详解存档版.md(权威名)与详解存档.md(旧名)同时在——"
                       "巡检以权威名为准；旧名含权威名没有的增量则先并入，再将旧名移入 记忆琥珀/ 归档")
    return True, "单名·无双名并存"


def main():
    ap = argparse.ArgumentParser(description="守卫 记忆规则三层 版本号+铁律集合 一致性")
    ap.add_argument("--strict", action="store_true", help="发现漂移时 exit 1（默认只告警 exit 0）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--deliver", action="store_true",
                    help="漂移经 hook_protocol.alert() 送达宿主（Stop 挂载用；默认行为不变）")
    ap.add_argument("--self-test", action="store_true",
                    help="跑自测用例（含 drift[:2] 崩溃回归负例·2026-09-17 补·核销高危无自测欠账）")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    vers, maxes = {}, {}
    for name, path in FILES.items():
        if not os.path.exists(path):
            print(f"[ERR] 文件缺失: {path}", file=sys.stderr)
            return 2
        t = read(path)
        vers[name] = parse_version(t)
        maxes[name] = parse_tielu_max(t, name)

    ver_drift = len(set(vers.values())) > 1
    # 铁律集合上界比对排除摘要版：摘要版 2026-09-16 瘦身为「你画像」文件·不含铁律清单
    #   （正文偶引"铁律-019"≠铁律上界），只比铁律版 vs 详解存档版——守卫判据须与被守对象
    #   结构对齐（遗留3根治·2026-09-17·假红 19≠22 消除）。版本号一致性仍三层全比。
    # 🔴 假绿根治（2026-10-01·变异实测）：豁免只给"架构性不含铁律清单"的摘要版；
    #   铁律版/详解存档版 解析不出上界＝判据失效，不得静默剔出比对后报绿。
    MAX_EXEMPT = {"摘要版"}
    _max_cmp = {k: v for k, v in maxes.items() if k not in MAX_EXEMPT and v is not None}
    _max_unresolved = [k for k, v in maxes.items() if k not in MAX_EXEMPT and v is None]
    # 参与比对的层 <2 = 无比对对象（仪器空转）；有必解析层取不到值 = 判据失效 → 一律显形
    max_drift = (len(set(_max_cmp.values())) > 1) or bool(_max_unresolved) or len(_max_cmp) < 2

    # ③ 铁律版描述计数一致性（仅铁律版含 "N条硬约束" / "（N条·不可违反）"）
    tierlu_text = read(FILES["铁律版"])
    desc_count = parse_desc_count(tierlu_text)
    title_count = parse_title_count(tierlu_text)
    actual_max = maxes["铁律版"]
    count_drift = (desc_count != actual_max) or (title_count != actual_max) or (desc_count != title_count)

    # ⚠️ 此处曾有一份**完整重复**的 ①②③ 输出块（json 摘要＋人读巡检文本）：
    #   它在 ④⑤⑥ 尚未计算时就把"三层一致"结论打出来，随后 :553 那份又打一遍
    #   ⇒ 同一份巡检在 stdout 出现两次（告警文案被双打＝噪音，且首份属"半截结论"）。
    #   2026-10-01 童灵上岗回合去重：判定与输出统一由 ④⑤⑥ 之后那份负责（自测
    #   run_json() 取 out.splitlines()[-1]＝末份，语义不变）。

    # ④ D4：读取时门禁（该读没读）
    d4s_ok, d4s_msg = d4_static()
    d4d_ok, d4d_msg = d4_dynamic()  # None=未激活/跳过
    d4_drift = (not d4s_ok)  # 静态布线错误=真漂移；动态仅告警不阻断

    # ⑤ 冲突/边缘场景 → 详解版门禁（该读没读）
    d5s_ok, d5s_msg = d5_static()
    d5d_ok, d5d_msg = d5_dynamic()  # None=未激活/跳过
    d5_drift = (not d5s_ok)  # 静态声明缺失=真漂移；动态仅告警不阻断
    # ⑥ 规则触发规格覆盖守卫（yaml 条数 == 铁律版索引表条数·条数由代码派生）
    d6_ok, d6_msg = d6_coverage()
    d6_drift = (not d6_ok)  # 触发规格与真源脱钩=真漂移；预注入硬墙出现洞
    # ⑦ 双名并存巡查（2026-10-09 缺陷③根治·只告警不进 drift——归档属人的裁决）
    d7_ok, d7_msg = d7_dual_name()

    if args.json:
        print({
            "versions": vers,
            "tielu_max": maxes,
            "version_drift": ver_drift,
            "tielu_max_drift": max_drift,
            "tielu_max_unresolved": _max_unresolved,
            "desc_count": desc_count,
            "title_count": title_count,
            "count_drift": count_drift,
            "d4_static": {"ok": d4s_ok, "msg": d4s_msg},
            "d4_dynamic": {"ok": d4d_ok, "msg": d4d_msg},
            "d5_static": {"ok": d5s_ok, "msg": d5s_msg},
            "d5_dynamic": {"ok": d5d_ok, "msg": d5d_msg},
            "d6_coverage": {"ok": d6_ok, "msg": d6_msg},
            "d7_dual_name": {"ok": d7_ok, "msg": d7_msg},
        })
    else:
        print("记忆规则三层一致性巡检：")
        for n in FILES:
            _tail = "  （豁免：画像文件·架构性不含铁律清单·不参与上界比对）" if n in MAX_EXEMPT else ""
            print(f"  {n}: 版本 v{vers[n]} | 铁律上界 {maxes[n]}{_tail}")
        print(f"  铁律版描述计数：frontmatter={desc_count}条 / 标题={title_count}条 / 实际铁律上界={actual_max}条")
        print()
        if not ver_drift and not max_drift and not count_drift:
            print("✅ 三层一致（版本号 + 铁律集合上界 + 描述计数 均对齐）")
        else:
            print("⚠️ 三层漂移 detected：")
            if ver_drift:
                print(f"   - 版本号不一致: {vers}")
            if max_drift:
                if _max_unresolved or len(_max_cmp) < 2:
                    print(f"   - 🔴 铁律上界判据失效（≠一致）：必解析层取不到上界 {_max_unresolved}"
                          f"｜实际参与比对 {_max_cmp}（参与层<2＝仪器空转，⛔不判绿）")
                else:
                    print(f"   - 铁律集合上界不一致: {_max_cmp}")
            if count_drift:
                print(f"   - 铁律版描述计数漂移：frontmatter={desc_count}条 / 标题={title_count}条 / 实际={actual_max}条 → 改铁律条数须同步 description+标题")
            print("   → 改任一层须三层版本号+铁律集合一起升（版本号铁律）")
        print()
        print(f"④ D4 静态布线：{'✅ ' if d4s_ok else '⚠️ '}{d4s_msg}")
        if d4d_ok is None:
            print(f"④ D4 动态锚点：⚪ {d4d_msg}")
        else:
            print(f"④ D4 动态锚点：{'✅ ' if d4d_ok else '⚠️ '}{d4d_msg}")
        print(f"⑤ 冲突→详解版 静态声明：{'✅ ' if d5s_ok else '⚠️ '}{d5s_msg}")
        if d5d_ok is None:
            print(f"⑤ 冲突→详解版 动态：⚪ {d5d_msg}")
        else:
            print(f"⑤ 冲突→详解版 动态：{'✅ ' if d5d_ok else '⚠️ '}{d5d_msg}")
        print(f"⑥ 触发规格覆盖：{'✅ ' if d6_ok else '⚠️ '}{d6_msg}")
        print(f"⑦ 双名并存巡查：{'✅ ' if d7_ok else '⚠️ '}{d7_msg}")

    # drift 改为「漂移原因列表」：空列表 falsy / 非空 truthy（455/458 判真假不变），
    # 且 457 行 drift[:2] 可切片取前2条原因 join（原 bool 切片=TypeError 崩溃·2026-09-17 修复）
    drift_reasons = []
    if ver_drift:
        drift_reasons.append("版本号不一致 %s" % vers)
    if max_drift:
        drift_reasons.append("铁律集合上界不一致 %s" % maxes)
    if count_drift:
        drift_reasons.append("铁律版描述计数漂移 frontmatter=%s/标题=%s/实际=%s" % (desc_count, title_count, actual_max))
    if d4_drift:
        drift_reasons.append("D4 静态布线错误")
    if d5_drift:
        drift_reasons.append("冲突→详解版静态声明缺失")
    if d6_drift:
        drift_reasons.append("触发规格覆盖脱钩")
    drift = drift_reasons
    # 送达律（2026-09-05·--deliver 仅本端 Stop 挂载启用）：漂移不只在 stdout 印一遍就算完——
    # 本端 Stop 的 stdout 不回灌模型，warn-only 等于没人听见（实证：三层 19≠22 红了 19 天）。
    if "--deliver" in sys.argv:
        sys.path.insert(0, os.path.join(os.path.expanduser("~"), "脚本中心"))  # v2.1.4 同族回正(hook_mode腿)
        try:
            import hook_protocol as _hp
        except Exception:
            _hp = None
        if _hp is not None and drift:
            return _hp.alert("三层守卫", "记忆规则三层漂移：%s → 改任一层须三层版本号+铁律集合一起升"
                             % "；".join(drift[:2]), via_hook=True)
    return 1 if (drift and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
