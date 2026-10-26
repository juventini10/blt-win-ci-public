#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory_pointer_reachability_guard.py — 守卫「规则文件指针可达性 + 权威名唯一性」
============================================================
家族：守卫（守） ｜ 部署形态：Hook + pre-commit 门禁
版本：v1.0

为什么需要它（2026-10-23 根因）：
    母本 WB `~/.workbuddy/MEMORY.md` 的「详解存档版」指针指向 `用户基本规则-详解存档.md`，
    而真源实体是 `用户基本规则-详解存档版.md`（2026-10-02 权威名迁移后旧名退役）→ **断链**。
    当时 `rule_three_layer_guard.py` **全程全绿**（exit 0）——因为它只查
    「单名 / 双名并存」，⛔**不查引用可达性**。断链因此潜伏 21 天无人报警：
    铁律-005「冲突→详解版」路径在 WB 端实际不可达。

本守卫补的正是那条缺失的机械判据：
    ① **可达性**：凡把 `记忆规则/` 下的文件当「要 Read 的目标路径」引用，
       该路径必须**真实存在**（exists）——断链即报红。
    ② **退役旧名**：旧名不得再被当作**目标路径**引用（叙述性历史提及不算）。

位置即语义（三条豁免，各有独立理由，⛔不得随意扩大）：
    H1 `rules-curation/` — 发布链路的**策展版中间层**用自有命名（无「版」字），
       源名与包内名差一字是**既定设计**（`mirror-manifest.json` 明写
       `filename_differs: true`）；⛔该处不是断链，改它会崩发布链路。
    H2 守卫脚本的**退役残留探针**（`_first_existing` fallback / `d7_dual_name`
       双名检测 / 自测 fixture）——**旧名正是它们要探测的对象**，改了守卫就废。
    H3 安装脚本的**双名并存检测块**（`_old_nm` + 告警文案）——同上族。
    H4 历史叙述（CHANGELOG / 进度看板历史条目 / 规范历史条目 / 工作日志 /
       归档 / 运行日志 / 外部反馈收件箱）——⛔改历史＝篡改历史。

两问记录（守卫编写规范 §二·十八·AI 提案前置门禁）：
  第一问「能不能建」＝禁设核对：已读 §二·七 守卫清单表退役/永久关闭行 + 守卫编写规范 §3.4·扩
    （被实证否决的判据族）→ 本守卫守「路径可达性」判据族，母本无同族实例、不撞任何退役/关闭行。
  第二问「该不该建」＝量三数（真源＝成长箱 SKILL.md §流程C·C4）：N1 硬缺失=1（母本 MEMORY.md 指向
    退役名 → 断链 21 天·三层守卫全绿无人报警＝实证硬缺失）＞0 ✅ 允许立项；N2 形态错位=24（存量旧名
    活指针，已归一）；N3 仪器假阳性=0（首版 709 处假红已按「位置即语义」四类豁免收敛·自测 12/12 双向）。
    ⛔ 第二问镜像（对象已存在＝修仪器不建仪器）：本守卫为**新增判据族**（母本无等价件）故不适用该镜像。

用法：
    python3 memory_pointer_reachability_guard.py            # 巡检（默认只告警 exit 0）
    python3 memory_pointer_reachability_guard.py --gate     # 门禁形态：检红 exit 1（pre-commit 拦截位）
    python3 memory_pointer_reachability_guard.py --json     # 机器可读
    python3 memory_pointer_reachability_guard.py --self-test # 自测用例
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
VAULT = HOME / "[记忆共享中心]"
RULES_DIR = VAULT / "记忆规则"

# 退役旧名（2026-10-02 权威名迁移后废弃）→ 权威名
RETIRED = {"用户基本规则-详解存档.md": "用户基本规则-详解存档版.md"}
# 已从共享中心**物理删除**的文件（退役文件残留·第二类断链）——实证来源=工作日志
#   记忆路由表.md          → 2026-06-02「记忆路由表正式废弃删除」·工作日志/系统日志/系统日志_2026-06-02.md
#   跨系统协作规范.md      → 2026-06-02 同批删除
#   00_动态状态快照.md     → 2026-06-02 同批删除（现役=情境层/动态状态快照.md）
# ⚠️ 与 RETIRED 的语义差别：**改名迁移类**（有同名替代）→ 旧名在活指针处必是病灶；
#    **物理删除类**（无同名替代）→ 历史文档提及属正常 → 只在「路径语境」判，不做裸名扫描。
RETIRED_DELETED = {"记忆路由表.md", "跨系统协作规范.md", "00_动态状态快照.md"}

# ── 扫描范围：活的 SSOT 文档 / 脚本 / 配置 / 当前发布包 / 母本系统文件 ──
SCAN_DIRS = [
    "记忆蓝图", "脚本中心", "自定义层", "情境层", "核心层", "潜意识层",
    # QClaw记忆 已移出扫描域：QClaw 端 2026-10-23 经你确认卸载，目录为冻结遗留物
    # （列归属签名制下无归属端可自核，留域只产生永动交接噪音）；恢复使用如需纳回，在此加回并复跑 --scope full
    "Trae记忆", "数字分身", "最伟大的我", "未知未知",
    "开发工具", "发布库", "02-技术研究",
]
# 母本端系统文件（断链的真实发生地）
MOTHER_FILES = [HOME / ".workbuddy" / n for n in ("SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md")]
# 轻量档「常驻指针面」：每轮都会被读到的那几个文件（⛔全库 walk 约 2 分钟·不可进 Stop 链）
SYSTEM_SCOPE_FILES = [
    VAULT / "脚本中心" / "route_guard_config.json",
    VAULT / "记忆蓝图" / "00_系统总览" / "五层记忆系统.md",
    VAULT / "脚本中心" / "守卫" / "sync_guard.py",
]

EXCLUDE_DIR_PARTS = {
    "归档", "工作日志", "logs", "记忆琥珀", "存档包", ".git", "node_modules",
    "__pycache__", ".venv", "记忆规则", "miss_candidates.archive",
    "每日日志", "记忆架构", "pre-symlink-backup",
    "scripts.bak-",
}
EXCLUDE_PATH_SUBSTR = [
    "发布库/五层记忆系统/存档包",      # 冻结的历史发布包
    "发布库/布洛陀-安装包-备份版",     # 备份版
    "开发工具/logs",
    "脚本中心/守卫",  # 守卫=仪器非规则文本；其自测夹具含退役旧名负例（T8/T9），自扫会误伤（2026-10-23 Qoder CN 恢复该件时发现）
]
# H4 历史叙述载体
HISTORY_FILE_RE = re.compile(r"(CHANGELOG\.md$|03-进度看板\.md$|01-.*通用规范\.md$|_反馈收件箱/|\.jsonl$|\.log$|fingerprint_state\.json$|变更日志\.md$)")
# H1 策展版中间层
CURATION_MARK = "rules-curation"

TEXT_EXT = {".md", ".json", ".txt", ".yaml", ".yml", ".sh", ".py", ".html", ".ps1", ".cfg", ".ini", ".toml"}

# ── 端归属表（列归属签名制·⛔只登记不代改他端列）──
# 断链修在**写它的那个端**——本守卫是跨端共享件，故只标归属·不代改。
# 归属键 = 路径首段（顶层目录名），值 = 归属端标签。
ENDPOINT_OWNERS = {
    "记忆蓝图": "共享中心（各端哲学文件内的端列由该端自核）",
    "脚本中心": "共享中心",
    "情境层": "共享中心",
    "核心层": "共享中心",
    "潜意识层": "共享中心",
    "发布库": "共享中心（公共产物）",
    "开发工具": "共享中心（发布流水线）",
    "自定义层": "共享中心（待办/方案）",
    "Trae记忆": "Trae 端",
    "QClaw记忆": "QClaw 端（已退役 2026-10-23·端卸载·不再扫描）",
    "WorkBuddy记忆": "WorkBuddy 端",
    "02-技术研究": "共享中心（研究文档）",
}


def owner_of(rel):
    top = rel.split("/", 1)[0]
    return ENDPOINT_OWNERS.get(top, "未登记归属·待裁决")

# ── 线性正则（⛔禁嵌套量词）──
RULES_SLASH = "记忆规则/"
# v1.1 修正：停符集补全——原实现漏了**全角括号**「（）」**尖括号**「<>」**加号**「+」
#   ⇒ 「用户基本规则-摘要版.md（三层：…）」「（触发规格 → …」「铁律版+摘要版」等
#   **说明句残片被整串当成文件名** ⇒ P1 假阳性（v1.0 实测 70 处里 49 处属此类）。
TAIL_RE = re.compile(r"[^\s`\"'()（）\[\]【】<>，、。；：｜|,;+]+")
RETIRED_RE = re.compile("|".join(re.escape(k) for k in RETIRED))

# 叙述性标记：同句出现这些词＝该处是「历史叙述」而非「目标指针」→ 豁免
# （⛔仅作用于 P1 裸名扫描；P0 路径上下文一律按指针判——路径就是路径）
NARRATIVE_RE = re.compile(
    r"(退役|已删除|已废|废弃|删除|历史|旧名|曾用|迁移|失效|滞后|已同步|已批量修复|不要用|勿用|不存在|真名|真源"
    r"|旧路径|当时|原路径|原名|已迁移|已改为|改为|实测于|截至|前值|此前|原为|替代为|取代|作废|遗留)"
)

# H2/H3 逐行豁免（守卫探针 + 双名检测块）
H2_H3_LINE_RE = re.compile(
    r"(旧名\s*`?用户基本规则-详解存档\.md`?|退役残留|"
    r"_first_existing|"
    r"_o\s*=\s*os\.path\.join\(BASE,|"
    r"\"详解存档版\"\s*:\s*\"用户基本规则-详解存档\.md\"|"
    r"_old_nm\s*=\s*os\.path\.join\(|"
    r"双名并存|"
    r"从「用户基本规则-详解存档\.md」迁到|"
    r"用户基本规则-详解存档版\.md\|用户基本规则-详解存档\.md|"
    r"CURATION_NAME\s*=|"
    r"\"detail\"\s*:\s*\"用户基本规则-详解存档\.md\"|"
    r"均存在于本机，由步骤生成)"
)
H2_H3_FILES = {
    "install_scripts.py", "consistency_guard.py", "audit_staleness.sh",
    "rules-strip.py",   # FILES["detail"] 指向**策展版目录**内的文件（该目录自有命名·无「版」字）
}
# H2-整文件豁免：这两个守卫脚本通篇引用旧名，是「退役残留探针」本身（_first_existing
# fallback + d7_dual_name 双名检测 + 自测 fixture）——⛔改了守卫就废。
H2_WHOLE_FILE = {"rule_three_layer_guard.py", "pkg_cleanliness_check.py"}
# He5 语境豁免：方案/历史/待办类文档中的路径是「当时叙述」而非「当前指针」
#   依据=守卫编写规范 §3.4·扩「描述性文本不得成为判据证据·提到它≠做了它」
# gate 域＝**共享中心真活文档**（本端负责修的域）
#   ⛔ 各端列（各端哲学文件夹的端列）·⛔ 派生物（发布库/发布流水线/CI 副本·由 mirror-sync 再生）
#   ⛔ 历史方案/待办（方案记的是「当时路径」）
#   → 这些不是本端该修的：gate 域外只报不拦（端归属制·⛔不代改他端列）
GATE_DOMAIN_EXCLUDE = re.compile(
    r"(02-平台端适配类/|自定义层/待完成工作/|自定义层/项目跟进/|发布库/|开发工具/blt-win-ci-|"
    r"Trae记忆/|QClaw记忆/|WorkBuddy记忆/|04_系统文件设计/品格设计哲学/02-品格设计实例/)"
)
HE5_NARRATIVE_FILE_RE = re.compile(
    r"(待完成工作/|记忆架构/|更新日志|_交接包|变更日志\.md$|CHANGELOG\.md$|00_系统总览/五层记忆系统\.md$)"
)
# He8 版本化发布快照（v1.10 介绍等）——快照里的旧名是**当时事实**·不是活指针
#   实证（2026-10-23·v1.1 修抽取器后 P0 首现）：「五层记忆系统-布洛陀1.10介绍.html」里的
#   「记忆规则/00_动态状态快照.md」被判 P0 红色——但**活手册**同一行上轮已归一
#   ⇒ 该手册是 **1.10 版发布快照**（mtime 2026-09-01 未再动）⇒ 不豁免则 P0 被历史快照永久占红
#   （报警疲劳·母本 §3.4 假红族）。
HE8_RELEASE_SNAPSHOT_RE = re.compile(
    r"[^/]*\d+\.\d+[^/]*(介绍|说明|发布|快照)[^/]*\.(html|md|txt)$"
)


def is_excluded(rel: str) -> bool:
    if any(("/%s/" % d) in rel or rel.startswith(d + "/") for d in EXCLUDE_DIR_PARTS):
        return True
    return any(s in rel for s in EXCLUDE_PATH_SUBSTR)


RG = shutil.which("rg") or "/usr/local/bin/rg"


def rg_lines(roots, pattern, exts):
    """用 ripgrep 取候选行（path:lineno:content）——比 Python walk 全库快两个数量级。
    ⛔ 关键：cwd 必须设为 VAULT 且用相对根目录——否则 rg 输出的路径是相对调用方 cwd 的
    （如 ../../Trae记忆/…），`-g '!每日日志/**'` 这类 glob 就匹配不上（实测踩过）。"""
    inc = ["*%s" % e for e in exts]
    exc = ["!**/%s/**" % d for d in EXCLUDE_DIR_PARTS]
    exc += ["!**/%s/**" % s for s in EXCLUDE_PATH_SUBSTR]
    exc += ["!*.bak", "!*.bak-*", "!*.jsonl", "!*.log"]
    cmd = [RG, "--no-heading", "--line-number", "--no-messages", "-e", pattern]
    # ⚠️ ripgrep 的 glob 规则：后匹配者胜——⛔排除必须排在 include 之后，否则会被重新包含
    for x in inc + exc:
        cmd += ["-g", x]
    cmd += list(roots)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(VAULT)).stdout
    except Exception:
        return []
    res = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        p, ln, txt = parts
        res.append((p, int(ln), txt))
    return res


def iter_candidates(scope, pattern):
    """返回 [(rel, lineno, line)] 候选行。full 档走 ripgrep（秒级）·system 档读固定文件集。"""
    if scope == "full":
        return rg_lines(SCAN_DIRS, pattern, sorted(TEXT_EXT))
    out = []
    for p, rel in iter_scan_files(scope):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for ln, line in enumerate(text.split("\n"), 1):
            if pattern in line:
                out.append((rel, ln, line))
    return out


def iter_scan_files(scope="full"):
    if scope == "system":
        # 轻量档：只扫「常驻指针面」——每轮都会读到的那几个文件（母本四系统文件 +
        # 路由真相源 + 架构卡）。⛔全库 walk 约 2 分钟，⛔不可进每轮 Stop 链。
        for p in list(MOTHER_FILES) + list(SYSTEM_SCOPE_FILES):
            if p.exists():
                yield p, ("~/.workbuddy/" + p.name if p in MOTHER_FILES else str(p.relative_to(VAULT)))
        return
    for root_name in SCAN_DIRS:
        root = VAULT / root_name
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_PARTS]
            rel_dir = os.path.relpath(dirpath, VAULT)
            if is_excluded(rel_dir):
                continue
            for fn in filenames:
                p = Path(dirpath) / fn
                if p.suffix.lower() not in TEXT_EXT:
                    continue
                if fn.endswith((".bak", ".jsonl", ".log")):
                    continue
                rel = str(p.relative_to(VAULT))
                if is_excluded(rel):
                    continue
                yield p, rel
    for p in MOTHER_FILES:
        if p.exists():
            yield p, "~/.workbuddy/" + p.name


def refs_in_line(line: str):
    """返回该行里指向 记忆规则/ 目录的目标文件名集合。"""
    out = set()
    idx = 0
    while True:
        i = line.find(RULES_SLASH, idx)
        if i < 0:
            break
        m = TAIL_RE.match(line, i + len(RULES_SLASH))
        if m:
            out.add(m.group(0))
        idx = i + len(RULES_SLASH)
    return out


# ── v1.1 候选切分（把「一行多目标」「说明句残片」「自测夹具」从文件名里剥出来）──
# 实测依据（v1.0 全库 70 处 P1 的重分类）：**49/70 是抽取器把非文件名串当文件名**
#   ① 一行多文件并列（「记忆规则/用户基本规则-铁律版.md/摘要版.md/详解存档.md」——共同前缀省略）
#   ② 说明句残片（「…摘要版.md（三层：摘要/铁律/详解存档）」「（触发规格 → …」）
#   ③ 自测夹具字符串（审计脚本自测里内嵌的假路径）
#   ⇒ P1 必须只收「**单目标 + 形似文件名 + 不在共享中心**」的真死指针，否则是假红制造机。
FIXTURE_CTX_RE = re.compile(
    r"(==|!=|chk\(|assert\b|normalize\(|startswith\(|endswith\(|fixture|夹具|自测)"
)
FILENAME_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")


def rules_subdirs():
    """共享中心规则目录下的子目录名（用于区分「子目录路径」与「多文件并列」）。"""
    try:
        return {p.name for p in RULES_DIR.iterdir() if p.is_dir()}
    except Exception:
        return set()


def rule_ref_groups(line: str, subdirs=()):
    """返回 [(候选文件名, 是否并列组)]。

    · 「记忆规则/子目录/文件.md」且首段是共享中心**真实子目录** → 单候选（完整相对路径）
    · 「记忆规则/a.md/b.md/c.md」首段不是子目录 → **多文件并列** → 每段各为候选
    ⛔ 不做「猜共同前缀」——猜错即假阳性；并列组整体降级为「写法待归一」（不判债）。
    """
    groups = []
    idx = 0
    while True:
        i = line.find(RULES_SLASH, idx)
        if i < 0:
            break
        m = TAIL_RE.match(line, i + len(RULES_SLASH))
        if not m:
            idx = i + len(RULES_SLASH)
            continue
        segs = m.group(0).split("/")
        if len(segs) > 1 and segs[0] in subdirs:
            groups.append(("/".join(segs), False))
        else:
            for s in segs:
                if s:
                    groups.append((s, len(segs) > 1))
        idx = i + len(RULES_SLASH)
    return groups


# ── 共享中心标识：出现在 记忆规则/ **之前** 的上下文里即视为「指向本机共享中心」──
# ⚠️ 2026-10-23 修正：原实现把含「记忆规则/」的串放进 MARK 列表，而 prefix 恰好止于
#    「记忆规则/」**之前** ⇒ shared 判定恒假 ⇒ 共享中心前缀的断链**从未被检出**
#    （真病灶：§3.9e「依赖缺失被当成无问题」同族·全绿是空转的遮羞布）。
#    正确判据＝看「记忆规则/」**之前**那段有没有共享中心/家目录标识。
SHARED_CENTER_MARKS = ("个人AI档案/", "记忆共享中心", "/Users/", "~/")
GLOB_CHARS = set("*?{}[")
# 共享中心里真实存在的文件名（动态计算·自维护）
def shared_center_names():
    try:
        return {p.name for p in RULES_DIR.iterdir() if p.is_file()}
    except Exception:
        return set()


def classify_ref(line: str, fname: str, shared_names: set):
    """返回 'shared' | 'bare' | 'glob' | 'unknown'"""
    if any(c in fname for c in GLOB_CHARS):
        return "glob"
    i = line.find(RULES_SLASH)
    if i < 0:
        return "unknown"
    prefix = line[max(0, i - 40):i]
    if any(mk in prefix for mk in SHARED_CENTER_MARKS):
        return "shared"
    # 裸相对：只有当该文件名在共享中心里真实存在时才可判（否则属端内布局·歧义）
    if fname in shared_names:
        return "bare"
    return "unknown"


def check(scope="full", rules_dir=None, retired=None, retired_deleted=None, candidates=None,
          gate_domain=False, disable=()):
    """rules_dir / retired / retired_deleted / candidates 四参可注入 → 供隔离夹具与变异测试使用
    （⛔路径一律**函数内求值**·禁模块级冻结——否则自测与夹具会切走真身·守卫编写规范 §二·二十二之二）。
    disable: v1.1 新增——关掉某条「假阳性降级规则」（enum/ext/fixture）⇒ 供两向探针验证该规则承重。"""
    broken = []         # P0 硬断链（保留槽·当前语义并入 retired_used / stale_ref）
    retired_used = []   # P0 退役名（改名类/删除类）被当作目标路径引用
    stale_ref = []      # P1 陈旧引用：**单目标 · 形似文件名 · 不在共享中心**（真死指针）
    unresolved = []      # P2 待核：裸相对·目标不在共享中心（端内布局歧义·不报红）
    ambiguous = []       # v1.1 新增：写法歧义组（多文件并列/说明句残片/自测夹具）——**不是债**·只计数可见
    alias_present = []  # P0 退役旧名实体复现
    _rules = Path(rules_dir) if rules_dir else RULES_DIR
    _retired = RETIRED if retired is None else retired
    _retired_del = RETIRED_DELETED if retired_deleted is None else retired_deleted
    shared_names = {p.name for p in _rules.iterdir() if p.is_file()} if _rules.exists() else set()
    _subdirs = {p.name for p in _rules.iterdir() if p.is_dir()} if _rules.exists() else set()
    _cand = candidates if candidates is not None else iter_candidates(scope, RULES_SLASH)

    for rel, ln, line in _cand:
        if rel.endswith("memory_pointer_reachability_guard.py"):
            continue  # 自我豁免
        if CURATION_MARK in line:          # H1 策展版中间层豁免
            continue
        if HISTORY_FILE_RE.search(rel):    # H4 历史叙述豁免
            continue
        if "备份" in rel or "副本" in rel:   # 备份/副本版 → 冻结
            continue
        if HE5_NARRATIVE_FILE_RE.search(rel):   # He5 方案/历史/待办类文档 → 路径叙述非活指针
            continue
        if HE8_RELEASE_SNAPSHOT_RE.search(rel):  # He8 版本化发布快照 → 旧名是当时事实·非活指针
            continue
        if gate_domain and GATE_DOMAIN_EXCLUDE.search(rel):   # gate 域外（各端列/派生物）→ 只报不拦
            continue
        if rel.rsplit("/", 1)[-1] in H2_WHOLE_FILE:        # H2 整文件豁免（探针本体）
            continue
        if rel.rsplit("/", 1)[-1] in H2_H3_FILES and H2_H3_LINE_RE.search(line):  # H3 行级豁免
            continue
        for fname, is_enum in rule_ref_groups(line, _subdirs):
            kind = classify_ref(line, fname, shared_names)
            if kind == "glob":
                continue
            if fname in _retired_del and NARRATIVE_RE.search(line):
                continue   # 物理删除类·同句为叙述（"已失效/已迁移"）→ 非指针
            if fname in _retired or fname in _retired_del:
                retired_used.append((rel, ln, fname))
                continue
            if kind in ("shared", "bare"):
                if (_rules / fname).exists():
                    continue
                # v1.1 判据收紧（假阳性治理·母本 §3.4 假红族）：
                #   P1 只收「**单目标 + 形似文件名 + 非自测夹具**」的真死指针。
                #   ① 一行多文件并列 → 写法待归一（读者按共同前缀理解·机器不猜）
                #   ② 说明句残片      → 非文件名（无扩展名）
                #   ③ 自测夹具内嵌假路径 → 夹具语境
                if is_enum and "enum" not in disable:
                    ambiguous.append((rel, ln, fname, "多文件并列·写法待归一"))
                    continue
                if not FILENAME_EXT_RE.search(fname) and "ext" not in disable:
                    ambiguous.append((rel, ln, fname, "非文件名残片·说明句"))
                    continue
                if FIXTURE_CTX_RE.search(line) and "fixture" not in disable:
                    ambiguous.append((rel, ln, fname, "自测夹具内嵌假路径"))
                    continue
                stale_ref.append((rel, ln, fname))
            elif kind == "unknown" and ("用户基本规则" in fname or "记忆路由表" in fname):
                unresolved.append((rel, ln, fname))

    for name in list(_retired) + list(_retired_del):
        if (_rules / name).exists():
            alias_present.append(str(_rules / name))
    return broken, retired_used, alias_present, unresolved, stale_ref, ambiguous


def scan_bare_alias(scope="full"):
    """P1：退役旧名/退役删除文件以**裸文件名**形式出现（无 记忆规则/ 前缀）——多在「文件清单表」里，
    读者会照着找 → 同样是病灶；但也可能出现在叙述句中 → 列为待核，交人工裁决。"""
    out = []
    # P1 只扫「改名迁移类」——它有明确的同名替代，旧名在任何活指针处都是病灶。
    # 「物理删除类」无同名替代，历史文档里提及属正常 → 只在 P0 路径语境判。
    names = list(RETIRED)
    pat = "|".join(re.escape(n) for n in names)
    for rel, ln, line in iter_candidates(scope, pat):
        if rel.endswith("memory_pointer_reachability_guard.py"):
            continue
        if CURATION_MARK in line or HISTORY_FILE_RE.search(rel):
            continue
        if HE8_RELEASE_SNAPSHOT_RE.search(rel):  # He8 版本化发布快照
            continue
        if "备份" in rel or "副本" in rel:            # 备份/副本版手册 → 冻结
            continue
        if rel.rsplit("/", 1)[-1] in H2_WHOLE_FILE:   # H2 整文件豁免（探针本体）
            continue
        if rel.rsplit("/", 1)[-1] in H2_H3_FILES and H2_H3_LINE_RE.search(line):
            continue
        if NARRATIVE_RE.search(line):
            continue
        for name in names:
            if name in line and RULES_SLASH + name not in line:
                out.append((rel, ln, name))
                break
    return out


def emit_handover(stale_ref, owner_filter):
    """端归属交接单：**断链修在写它的那个端**（列归属签名制·⛔共享守卫不代改他端产物/端列）。
    输出 = 可直接贴进端接入记录 / 交接包的清单（精确到行·含归属与修法参照）。
    ⛔ 本函数**只读不改**：交接单是「机制自动产出待办」——不靠人记得（愿景①全自动化）。"""
    rows = [(rel, ln, f) for rel, ln, f in stale_ref
            if owner_filter == "全部" or owner_filter in owner_of(rel)]
    if not rows:
        print("端归属交接单（%s）：0 条" % owner_filter)
        return 0
    print("# 端归属交接单 · %s" % owner_filter)
    print("# 生成器：脚本中心/守卫/memory_pointer_reachability_guard.py --handover %s" % owner_filter)
    print("# 原则：断链修在**写它的那个端**·⛔共享守卫不代改他端产物/端列（列归属签名制）")
    print("# 修法参照：共享中心权威名 = 记忆规则/用户基本规则-{铁律版,摘要版,详解存档版}.md"
          "（认知层/行为层 → 摘要版·铁律与执行规范 → 铁律版·按需加载详解 → 详解存档版）")
    print("# 语境判定：**活指针**（配置/注入路由指向）→ 归一到权威名；**改造记录**（陈述当时改了哪个文件）"
          "→ 保留原名 + 加时代标注（读者可寻到现权威名）")
    for rel, ln, f in rows:
        print("- %s:%d  记忆规则/%s" % (rel, ln, f))
    print("# 共 %d 条" % len(rows))
    return 0


def main():
    ap = argparse.ArgumentParser(description="守卫 规则文件指针可达性 + 权威名唯一性")
    ap.add_argument("--gate", action="store_true",
                    help="门禁形态：检红→exit 1（**只 gate 共享中心真活域**·各端列/派生物/历史方案域外只报不拦）·默认 hook 形态恒 0 全量报")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--scope", choices=["system", "full"], default="full",
                    help="system=只扫常驻指针面（轻量·可进 Stop 链）·full=全库扫描（重·进 pre-commit/cron）")
    ap.add_argument("--self-test", action="store_true", help="跑自测用例")
    ap.add_argument("--handover", metavar="归属标签",
                    help="生成**端归属交接单**（断链修在写它的那个端·⛔守卫不代改他端产物/端列）")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    broken, retired_used, alias_present, unresolved, stale_ref, ambiguous = check(
        args.scope, gate_domain=args.gate)
    bare = scan_bare_alias(args.scope)

    if args.handover:
        return emit_handover(stale_ref, args.handover)

    if args.json:
        print(json.dumps({
            "broken_count": len(broken), "broken": broken,
            "retired_used_count": len(retired_used), "retired_used": retired_used,
            "alias_present": alias_present,
            "unresolved_count": len(unresolved), "unresolved": unresolved,
            "bare_alias_count": len(bare), "bare_alias": bare,
            "stale_count": len(stale_ref), "stale": stale_ref,
            "ambiguous_count": len(ambiguous), "ambiguous": ambiguous,
        }, ensure_ascii=False, indent=2))
    else:
        print("规则文件指针可达性巡检（scope=%s）：" % args.scope)
        if alias_present:
            for a in alias_present:
                print("  ❌ 退役旧名实体复现：%s" % a)
        else:
            print("  ✅ 退役旧名未复现（记忆规则/ 下单名·权威名唯一）")
        if retired_used:
            print("  ❌ 退役旧名被当作目标路径引用：%d 处" % len(retired_used))
            for rel, ln, f in retired_used:
                print("     %s:%d  %s" % (rel, ln, f))
        else:
            print("  ✅ 无「退役旧名」目标路径引用")
        if retired_used or stale_ref:
            print("  ✅ P0 硬断链：0（退役名目标路径引用 = %d 处·见上）" % len(retired_used))
            print("  ⚠️ P1 陈旧引用（**真死指针**：单目标 · 形似文件名 · 不在共享中心·修法依语境·不报红）：%d 处" % len(stale_ref))
            by_owner = {}
            for rel, ln, f in stale_ref:
                by_owner.setdefault(owner_of(rel), []).append((rel, ln, f))
            for owner in sorted(by_owner, key=lambda k: -len(by_owner[k])):
                print("     ── 归属：%s（%d 处）" % (owner, len(by_owner[owner])))
                for rel, ln, f in by_owner[owner][:4]:
                    print("        %s:%d  记忆规则/%s" % (rel, ln, f))
                if len(by_owner[owner]) > 4:
                    print("        …另 %d 处" % (len(by_owner[owner]) - 4))
        else:
            print("  ✅ 全部规则文件指针可达")
        if ambiguous:
            kinds = {}
            for rel, ln, f, why in ambiguous:
                kinds.setdefault(why, []).append((rel, ln, f))
            print("  ℹ️ 写法歧义组（**不是债**·多文件并列/说明句残片/自测夹具·v1.1 新增降级）：%d 处" % len(ambiguous))
            for why in sorted(kinds):
                print("     ── %s：%d 处" % (why, len(kinds[why])))
                for rel, ln, f in kinds[why][:2]:
                    print("        %s:%d" % (rel, ln))
                if len(kinds[why]) > 2:
                    print("        …另 %d 处" % (len(kinds[why]) - 2))
        if bare:
            print("  ⚠️ 待核（退役旧名裸文件名形态·可能是指针也可能是叙述）：%d 处" % len(bare))
            for rel, ln, f in bare:
                print("     %s:%d  %s" % (rel, ln, f))
        if unresolved:
            print("  ⚠️ 待核（裸相对·目标不在共享中心·端内布局歧义·不报红）：%d 处" % len(unresolved))
            for rel, ln, f in unresolved:
                print("     %s:%d  记忆规则/%s" % (rel, ln, f))
    # 退出码语义律（守卫编写规范 §八·退出码语义·2026-10-07 报警噪声根治卡）：
    #   检红 = rc 0 + 输出红行（平台钩子契约把 rc 消费为执行状态信号，检红占 rc 会被记
    #   failed → 匿名聚合 → 报警疲劳）；rc≠0 专留真崩（不可执行/文件缺失/未捕获异常）。
    #   --gate 是**门禁形态**（pre-commit 拦截位），刻意反义：检红→rc 1 供 shell 判红。
    # P0 = 退役名目标路径引用 + 退役旧名实体复现（语义确定·可机械判）
    # P1 = 陈旧引用（修法依语境）→ ⛔不参与 gate（否则对派生物/他端列永久假红＝假红制造机）
    if args.gate and (retired_used or alias_present):
        return 1
    return 0


def self_test():
    results = []

    def ck(name, cond):
        results.append((name, bool(cond)))

    ck("T1 退役旧名表非空", len(RETIRED) > 0)
    ck("T2 权威名在真源实体中存在", (RULES_DIR / "用户基本规则-详解存档版.md").exists())
    ck("T3 退役旧名实体当前不存在", not (RULES_DIR / "用户基本规则-详解存档.md").exists())

    # 路径提取（线性·无嵌套量词）
    ck("T4 提取 记忆规则/x.md",
       "用户基本规则-铁律版.md" in refs_in_line("- 铁律版：`[记忆共享中心]/记忆规则/用户基本规则-铁律版.md`"))
    ck("T5 提取 [记忆共享中心] 形态",
       "用户基本规则-摘要版.md" in refs_in_line("| `[记忆共享中心]/记忆规则/用户基本规则-摘要版.md` |"))
    ck("T6 无 记忆规则/ 词时不误提",
       refs_in_line("assets/rules-curation/用户基本规则-详解存档.md") == set())

    # 豁免判定
    ck("T7 策展版行被 H1 豁免", CURATION_MARK in "开发工具/x/rules-curation/用户基本规则-详解存档.md")
    ck("T8 守卫探针行被 H2 豁免",
       bool(H2_H3_LINE_RE.search('_o = os.path.join(BASE, "用户基本规则-详解存档.md")')))
    ck("T9 双名检测块被 H3 豁免",
       bool(H2_H3_LINE_RE.search('_old_nm = os.path.join(dst_dir, "用户基本规则-详解存档.md")')))
    ck("T10 普通活引用不被豁免",
       not H2_H3_LINE_RE.search("- 详解存档版（按需）：`[记忆共享中心]/记忆规则/用户基本规则-详解存档.md`"))

    # He8 版本化发布快照豁免（v1.1 新增·实证：1.10 介绍 HTML 里的旧名是当时事实）
    ck("T11a He8 版本化发布快照被识别",
       bool(HE8_RELEASE_SNAPSHOT_RE.search("发布库/说明手册/五层记忆系统-布洛陀1.10介绍.html")))
    ck("T11b He8 不误伤活手册（非版本化文件名）",
       not HE8_RELEASE_SNAPSHOT_RE.search("发布库/说明手册/五层记忆系统 · 布洛陀手册.html"))

    # 分类器
    ck("T11 退役旧名识别", "用户基本规则-详解存档.md" in RETIRED)
    ck("T12 非退役名不入表", "用户基本规则-铁律版.md" not in RETIRED)

    # ── 变异测试（守卫编写规范 §3.9 判据类产出的出厂动作）──
    # 隔离夹具：⛔不碰真实文件（规范 §二·三十二：探针不得写入被测对象的生产台账）
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        _root = Path(td)
        _rules = _root / "记忆规则"
        _rules.mkdir()
        (_rules / "用户基本规则-详解存档版.md").write_text("x", encoding="utf-8")
        (_rules / "用户基本规则-铁律版.md").write_text("x", encoding="utf-8")
        (_rules / "共享核心").mkdir()
        (_rules / "共享核心" / "core-soul.md").write_text("x", encoding="utf-8")
        _line_ok = ("t.md", 1, "见 [记忆共享中心]/记忆规则/用户基本规则-详解存档版.md")
        _line_old = ("t.md", 1, "见 [记忆共享中心]/记忆规则/用户基本规则-详解存档.md")
        b_ok, r_ok, a_ok, u_ok, st_ok, am_ok = check(candidates=[_line_ok], rules_dir=_rules)
        ck("MUT:OK 权威名在位不误报（可达性判据检出力·放行侧）", len(b_ok) == 0 and len(r_ok) == 0)
        b_old, r_old, a_old, u_old, st_old, am_old = check(candidates=[_line_old], rules_dir=_rules)
        ck("MUT:OK 退役旧名必红（退役判据检出力·拦截侧）", len(r_old) == 1)
        _line_gap = ("t.md", 1, "见 [记忆共享中心]/记忆规则/不存在.md")  # ⛔须带共享中心前缀
        b_gap, r_gap, a_gap, u_gap, st_gap, am_gap = check(candidates=[_line_gap], rules_dir=_rules)
        ck("MUT:OK 不存在文件必被列为 P1 陈旧引用（不报红·修法依语境）",
           len(b_gap) == 0 and len(st_gap) == 1)
        # MUT:FAIL 变异体（退役清单清空）必须改变行为 ⇒ 变异可被杀死（防假绿灯）
        b_mut, r_mut, a_mut, u_mut, st_mut, am_mut = check(
            candidates=[_line_old], rules_dir=_rules, retired={})
        ck("MUT:FAIL 退役判据变异体改变行为（变异可杀·非恒真）",
           len(r_mut) == 0 and len(r_old) == 1)

        # ── v1.1 假阳性治理（抽取器+判据收紧）·三类降级各配正负夹具 ──
        _line_enum = ("t.md", 1, "见 [记忆共享中心]/记忆规则/用户基本规则-铁律版.md/摘要版.md/详解存档.md")
        b_e, r_e, a_e, u_e, st_e, am_e = check(candidates=[_line_enum], rules_dir=_rules)
        ck("v1.1 多文件并列不判债（写法待归一·不报红·存在者直接静默）",
           len(st_e) == 0 and len(am_e) == 2)
        _line_desc = ("t.md", 1, "见 [记忆共享中心]/记忆规则/用户基本规则-铁律版.md（三层：摘要/铁律/详解存档）")
        b_d, r_d, a_d, u_d, st_d, am_d = check(candidates=[_line_desc], rules_dir=_rules)
        ck("v1.1 说明句残片不判债（提取到存在实体·不报红）", len(st_d) == 0)
        _line_fix = ("t.md", 1, "chk(\"T4b\", normalize('echo \"/x/[记忆共享中心]/记忆规则/A.md\"') !=")
        b_f, r_f, a_f, u_f, st_f, am_f = check(candidates=[_line_fix], rules_dir=_rules)
        ck("v1.1 自测夹具内嵌假路径不判债", len(st_f) == 0 and len(am_f) >= 1)
        _line_sub = ("t.md", 1, "见 [记忆共享中心]/记忆规则/共享核心/core-soul.md")
        b_s, r_s, a_s, u_s, st_s, am_s = check(candidates=[_line_sub], rules_dir=_rules)
        ck("v1.1 共享中心子目录路径按单候选解析（存在即不报）", len(st_s) == 0)
        # 两向探针（真·可杀）：三条降级规则各自「关掉即须判债」⇒ 证明判据承重（非恒真假绿）
        b_pe, r_pe, a_pe, u_pe, st_pe, am_pe = check(
            candidates=[_line_enum], rules_dir=_rules, disable=("enum",))
        ck("PROBE v1.1 并列降级判据可杀（关掉即须判债·非恒真）",
           len(st_pe) == 2 and len(am_pe) == 0)
        b_pf, r_pf, a_pf, u_pf, st_pf, am_pf = check(
            candidates=[_line_fix], rules_dir=_rules, disable=("fixture",))
        ck("PROBE v1.1 夹具降级判据可杀（关掉即须判债·非恒真）",
           len(st_pf) == 1 and len(am_pf) == 0)
        b_pd, r_pd, a_pd, u_pd, st_pd, am_pd = check(
            candidates=[("t.md", 1, "见 [记忆共享中心]/记忆规则/核心层等说明句残片")],
            rules_dir=_rules, disable=("ext",))
        ck("PROBE v1.1 残片降级判据可杀（关掉即须判债·非恒真）",
           len(st_pd) == 1 and len(am_pd) == 0)

    npass = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print("  %s %s" % ("✅" if ok else "❌", name))
    print("[memory_pointer_reachability_guard self-test] %d/%d 通过" % (npass, len(results)))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
