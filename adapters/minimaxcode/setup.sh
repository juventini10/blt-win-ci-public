#!/usr/bin/env bash
# ============================================================
# setup.sh — MiniMax Code adapter 聚合安装入口（幂等）
# 用途: install_scripts.py --platform minimaxcode 按 capability.yaml install_entry 委派到此
# 职责: ① AGENTS.md 三合一载体落盘（SOUL+IDENTITY+自定义指令·存在不覆盖）
#       ①a USER.md → memory/user.md（存在不覆盖）
#       ①b MEMORY.md → agents/mavis/memory/MEMORY.md（存在不覆盖）
#       ② 端上 skills 形态归一（整目录软链 → 普通目录）+ 通用 Skill 逐件软链（→ 记忆中心
#          技能配置/ = 唯一真源）+ 端专属 Skill 实体落端内（⛔不进真源·其他端不可见）
#       ③ 插件 hooks.json 注册（3 事件 18 条·Stop 全裹 JSON 适配器·本端唯一写点）
#       ④ 自验证（五系统文件三处 / Skill / 插件 hooks.json 三事件 / Stop 适配器包裹率）
# 判据: MiniMax Code = Plugin Hook 端（注册面 = 插件内 hooks.json·非 settings.json）
#       ⚠️ 本端 hooks.json 由插件 manifest（.minimax-plugin/plugin.json）的 hooks 数组声明装载
#       ⚠️ 旧形态：~/.minimax/skills 是整目录软链 → 记忆中心 技能配置/（唯一真源直连）——
#          代价＝端专属 Skill 无处可落（写进去＝写进真源⇒跨端可见）⇒ 本脚本**自动归一**
#          为普通目录 + 逐件软链（通用件仍直连真源·端专属落端内·形态与 traecn 同构）
#          ⛔ 归一可逆：旧整目录软链改名留存 skills.bak-<ts>·⛔不删除
# 用法: bash setup.sh "<记忆共享中心绝对路径>"
# 退出码: 0=端特有链全成功 | 2=真失败（缺 MC/缺源件/hooks.json 不可解析） | 3=文件已落盘·仅手动收尾待办
# ============================================================
set -uo pipefail

G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; C='\033[0;36m'; N='\033[0m'
MC=""
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
RULE_SRC="$SRC_DIR/rules"
SKILL_SRC="$SRC_DIR/skills"
# 本端配置根 = MiniMax Code 的 activeDataDir（默认 ~/.minimax·可由环境覆盖）
CFG="${MINIMAX_CONFIG_DIR:-${MINIMAX_DATA_DIR:-$HOME/.minimax}}"
PLUGIN_DIR="$CFG/plugins/bulutuo-guards"
HOOKS_DIR="$PLUGIN_DIR/hooks"
HOOKS_JSON="$HOOKS_DIR/hooks.json"
PLUGIN_JSON="$PLUGIN_DIR/.minimax-plugin/plugin.json"
AGENTS_MD="$CFG/AGENTS.md"
USER_MD="$CFG/memory/user.md"
MEMORY_MD="$CFG/agents/mavis/memory/MEMORY.md"
SKILLS_DST="$CFG/skills"
CORE_HEADER="$SRC_DIR/templates/doenglingz-core-header.md"
MCP='[记忆共享中心]'
MCP_RE='\[记忆共享中心\]'
DRY="${DRY:-}"

for _arg in "$@"; do
    case "$_arg" in
        --dry-run|-n) DRY=1 ;;
        -*) ;;
        *) [ -z "$MC" ] && MC="$_arg" ;;
    esac
done

# 解释器运行期解析（条文61：⛔不硬编码解释器路径）
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else PY="" ; fi

echo -e "${C}=== MiniMax Code adapter 安装（AGENTS.md 三合一 + Skill + 插件 hooks.json 注册） ===${N}"
[ -n "$MC" ] || { echo -e "${R}❌ 未给记忆共享中心路径（用法: bash setup.sh \"<MC>\"）${N}"; exit 2; }
[ -n "$PY" ] || { echo -e "${R}❌ 未找到 python（python3/python）——hooks.json 注册与自验证需要${N}"; exit 2; }

fill_ph() {
    local f="$1"
    [ -f "$f" ] || return 0
    grep -qF "$MCP" "$f" 2>/dev/null || return 0
    sed "s@${MCP_RE}@${MC}@g" "$f" > "$f.tmp.$$" && mv "$f.tmp.$$" "$f"
}

# 实体复制（⛔仅用于端专属 Skill 直落·通用 Skill 走软链）
copy_skill_dir() {
    local src="$1" dst="$2"
    if [ -e "$dst" ]; then
        if [ -L "$dst" ]; then
            rm "$dst"
            cp -r "$src" "$dst"
            find "$dst" -type f -print0 | while IFS= read -r -d '' _f; do fill_ph "$_f"; done
            echo -e "  ${G}✅ 替换软链为实体: $(basename "$dst")${N}"
        else
            echo -e "  ${Y}SKIP（实体已存在·保本地/私人版）: $(basename "$dst")${N}"
        fi
        return 0
    fi
    if [ -n "$DRY" ]; then
        echo -e "  ${C}[dry-run] 将复制: $(basename "$dst")${N}"
        return 0
    fi
    cp -r "$src" "$dst"
    find "$dst" -type f -print0 | while IFS= read -r -d '' _f; do fill_ph "$_f"; done
    echo -e "  ${G}✅ 复制落盘: $(basename "$dst")${N}"
}

# 通用 Skill 软链（→ 记忆中心 技能配置/<name> = 唯一真源·与 traecn 同款）
#   幂等三态：同指向软链⇒跳过（return 0）｜异指向软链⇒换指｜实体已存在⇒不覆盖（return 1）
#   ⚠️ 换指用 ln -sfn（原子替换·⛔不用 rm：删除动作非必要 + 无「删了没建成」空窗）
link_skill_dir() {
    local src="$1" dst="$2"
    if [ -L "$dst" ]; then
        [ "$(readlink "$dst")" = "$src" ] && return 0
        ln -sfn "$src" "$dst"
    elif [ -e "$dst" ]; then
        echo -e "  ${Y}SKIP（实体已存在·不覆盖）: $(basename "$dst")${N}"
        return 1
    fi
    ln -s "$src" "$dst"
    return 0
}

# ─── [1/6] AGENTS.md 三合一载体落盘（SOUL+IDENTITY+自定义指令同文件·存在不覆盖）
#     ⚠️ 三格同指一个文件（平台拼接块只有一份 AGENTS.md）⇒ 只落一次·不拆三件
echo -e "${C}[1/6] AGENTS.md 三合一载体 → $AGENTS_MD${N}"
if [ -f "$AGENTS_MD" ]; then
    echo -e "  ${Y}SKIP（已存在·保用户本机铁律/切片覆盖块·⛔不覆盖）: AGENTS.md${N}"
elif [ ! -f "$RULE_SRC/core-agents.md" ]; then
    echo -e "  ${R}❌ 缺 adapter 模板: $RULE_SRC/core-agents.md（打包缺陷·⛔不落无模板载体）${N}"
    exit 2
elif [ -n "$DRY" ]; then
    echo -e "  ${C}[dry-run] 将落盘: AGENTS.md（SOUL+IDENTITY+自定义指令 三合一）${N}"
else
    mkdir -p "$(dirname "$AGENTS_MD")"
    cp "$RULE_SRC/core-agents.md" "$AGENTS_MD"
    fill_ph "$AGENTS_MD"
    echo -e "  ${G}✅ 落盘: AGENTS.md（$(wc -c < "$AGENTS_MD" | tr -d ' ') bytes）${N}"
fi

# ─── [2/6] USER.md → memory/user.md（存在不覆盖·⛔覆盖会毁用户画像）
echo -e "${C}[2/6] USER.md → $USER_MD${N}"
if [ -f "$USER_MD" ]; then
    echo -e "  ${Y}SKIP（已存在·保用户画像·⛔不覆盖）: memory/user.md${N}"
elif [ ! -f "$RULE_SRC/core-user.md" ]; then
    echo -e "  ${R}❌ 缺 adapter 模板: $RULE_SRC/core-user.md${N}"
    exit 2
elif [ -n "$DRY" ]; then
    echo -e "  ${C}[dry-run] 将落盘: memory/user.md${N}"
else
    mkdir -p "$(dirname "$USER_MD")"
    cp "$RULE_SRC/core-user.md" "$USER_MD"
    fill_ph "$USER_MD"
    echo -e "  ${G}✅ 落盘: memory/user.md${N}"
fi

# ─── [3/6] MEMORY.md → agents/mavis/memory/MEMORY.md（存在不覆盖·⛔不毁用户长期记忆）
echo -e "${C}[3/6] MEMORY.md → $MEMORY_MD${N}"
if [ -f "$MEMORY_MD" ]; then
    echo -e "  ${Y}SKIP（已存在·保用户长期记忆·⛔不覆盖）: agents/mavis/memory/MEMORY.md${N}"
elif [ ! -f "$RULE_SRC/core-memory.md" ]; then
    echo -e "  ${R}❌ 缺 adapter 模板: $RULE_SRC/core-memory.md${N}"
    exit 2
elif [ -n "$DRY" ]; then
    echo -e "  ${C}[dry-run] 将落盘: agents/mavis/memory/MEMORY.md${N}"
else
    mkdir -p "$(dirname "$MEMORY_MD")"
    cp "$RULE_SRC/core-memory.md" "$MEMORY_MD"
    fill_ph "$MEMORY_MD"
    echo -e "  ${G}✅ 落盘: agents/mavis/memory/MEMORY.md${N}"
fi

# ─── [4/6] 端上 skills 形态归一 + 通用 Skill 软链（→ 记忆中心 技能配置/<name> = 唯一真源）
#     为什么要归一（2026-10-25 愿景裁决·与 traecn 同构）：
#       旧形态（作者机实盘）：~/.minimax/skills 是**整目录软链** → <MC>/技能配置
#       ⇒ 端上可见的 skill ＝ 真源一层 ⇒ 端专属 Skill 只能写进唯一真源
#       ⇒ 跨端可见（traecn 的 setup 把真源全部链走）⇒ 违反「端专属不进共享技能配置·其他端不可见」
#       ⇒ 且端专属两件＝**童灵上岗仪式 + 域切片加载两条核心腿**·缺了本端童灵能力残缺
#     归一后：通用 Skill 逐件软链 → 真源（唯一真源直连·真源更新即时反映到端上）
#             端专属 Skill 实体落端内（不进真源·其他端不可见）
#     ⛔ 迁移可逆：旧整目录软链**改名留存**（skills.bak-<ts>）·⛔不删除
echo -e "${C}[4/6] 端上 skills 形态归一 + 通用 Skill 软链 → $SKILLS_DST${N}"
if [ -L "$SKILLS_DST" ]; then
    _old_tgt="$(readlink "$SKILLS_DST")"
    _bak="$SKILLS_DST.bak-$(date +%Y%m%d_%H%M%S)"
    if [ -n "$DRY" ]; then
        echo -e "  ${C}[dry-run] 将把整目录软链（${_old_tgt}）迁移为普通目录·旧链留存 ${_bak}${N}"
    elif mv "$SKILLS_DST" "$_bak"; then
        mkdir -p "$SKILLS_DST"
        echo -e "  ${G}✅ 已归一：整目录软链 → 普通目录（旧链留存 ${_bak}·可恢复）${N}"
    else
        echo -e "  ${R}❌ 归一失败：mv $SKILLS_DST ${_bak} 未成功${N}"
    fi
fi
SK=0; TOT=0
for skill in "$MC/技能配置"/*; do
    # ⛔ 不过滤非目录项：真源里的 .sh/.txt 运维件在整目录软链形态下端上可见，
    #    归一后一并软链 ⇒ 端上逐项 ≡ 真源（零丢失·形状等价）
    # ⛔ 排除隐藏项（.DS_Store / .git 等·系统与编辑器垃圾）
    case "$(basename "$skill")" in .*) continue ;; esac
    [ -e "$skill" ] || continue
    TOT=$((TOT+1))
    if [ -n "$DRY" ]; then SK=$((SK+1)); continue; fi
    link_skill_dir "$skill" "$SKILLS_DST/$(basename "$skill")" >/dev/null 2>&1 && SK=$((SK+1))
done
echo -e "  ${C}通用 Skill 软链结果: ${SK}/${TOT}（软链 → 记忆中心 技能配置/ = 唯一真源）${N}"

# ─── [5/6] 端专属 Skill 实体落盘（⛔不进共享技能配置·其他端不可见·与 traecn 同款）
echo -e "${C}[5/6] 端专属 Skill 实体落盘 → $SKILLS_DST${N}"
if [ -L "$SKILLS_DST" ]; then
    echo -e "  ${Y}⚠️ 端上 skills 仍是整目录软链（形态归一未生效）——⛔跳过端专属落盘以免写进唯一真源${N}"
elif [ -d "$SKILL_SRC" ]; then
    mkdir -p "$SKILLS_DST"
    for skill in "$SKILL_SRC"/*; do
        [ -d "$skill" ] || continue
        src_name="$(basename "$skill")"
        case "$src_name" in
            doenglingz-guard)     skill_name="布洛陀-童灵守护" ;;
            doenglingz-slice-nav) skill_name="布洛陀-童灵切片导航" ;;
            *)                    skill_name="$src_name" ;;
        esac
        copy_skill_dir "$skill" "$SKILLS_DST/$skill_name"
    done
else
    echo -e "  ${Y}⚠️ 未找到适配器端专属 Skill: $SKILL_SRC${N}"
fi

# ─── [6/6] 插件 hooks.json 注册（本端唯一写点·安装器 ③ 按 capability 跳过）
#     ⚠️ 与安装器 ② 的分工：② 只把脚本副本落 <CFG>/hooks/；本步只写注册面。
#     ⚠️ Stop 事件每条命令必裹 minimaxcode_hook_adapter.py —— 宿主要求 stdout 单 JSON 对象，
#        共享守卫的纯文本 stdout 会被宿主判 HOOK_INVALID_OUTPUT 直接丢弃（挂载在·产出不到=假绿）。
#     ⚠️ 幂等键=命令里是否已含脚本 basename：命中即跳过（⛔不迁移用户既有命令·不改写他人配置）。
echo -e "${C}[6/6] 插件 hooks.json 注册 → $HOOKS_JSON${N}"
if [ -n "$DRY" ]; then
    echo -e "  ${C}[dry-run] 将写入 3 事件 18 条（UPS 6 + Stop 8 全裹适配器 + SessionStart 4）${N}"
else
    mkdir -p "$HOOKS_DIR" "$(dirname "$PLUGIN_JSON")"
    # 插件 manifest（宿主按 "hooks" 数组装载挂点·⛔缺此声明＝插件装了不派发）
    if [ ! -f "$PLUGIN_JSON" ]; then
        cat > "$PLUGIN_JSON.tmp.$$" <<'PLUGINEOF'
{
  "schemaVersion": 1,
  "name": "bulutuo-guards",
  "displayName": "布洛陀守卫链",
  "version": "1.1.0",
  "description": "布洛陀端物理闸口：UserPromptSubmit 路由注入 + 铁律段预注入 + 对话标题自动命名、Stop 未知未知兜底、SessionStart 规则指针可达性巡检。",
  "author": "MiniMax Code",
  "category": "Code",
  "apps": [],
  "mcpServers": [],
  "skills": [],
  "hooks": ["hooks/hooks.json"]
}
PLUGINEOF
        mv "$PLUGIN_JSON.tmp.$$" "$PLUGIN_JSON"
        echo -e "  ${G}✅ 插件 manifest 落盘: .minimax-plugin/plugin.json${N}"
    fi
    "$PY" - "$HOOKS_JSON" "$CFG" "$MC" <<'PYEOF'
import json, os, re, shutil, sys, time
hooks_json, cfg, mc = sys.argv[1], sys.argv[2], sys.argv[3]
py = "python3" if shutil.which("python3") else "python"
# 脚本副本落点：安装器 ② 部署到 <CFG>/hooks/（本端 hooks 目录与插件目录分离）
SCRIPTS = os.path.join(cfg, "hooks")

# ── 路径择优（判据面＝落点面·⛔不猜路径·⛔不写不存在的路径）────────────
#   ①<CFG>/hooks/<name>       = 装机态（安装器②落的独立副本·端上 <CFG>/hooks/）
#   ②<MC>/脚本中心/**/<name>  = 作者态（源侧真源·带子目录·唯一真源直连）
#   ⛔ 两边都没有 ⇒ 仍指①（命令可见·派发会失败 ⇒ 由安装器②补件·显形在安装器侧）
#   ⚠️ 既有 hooks.json 条目一律不迁改（幂等键＝basename 命中即跳过）⇒ 择优只作用于新增条目
_SIDX = {}
if mc:
    _sroot = os.path.join(mc, "脚本中心")
    if os.path.isdir(_sroot):
        for _dp, _dn, _fs in os.walk(_sroot):
            for _f in _fs:
                _SIDX.setdefault(_f, os.path.join(_dp, _f))

def _script_path(sub):
    p1 = os.path.join(SCRIPTS, sub)
    if os.path.isfile(p1):
        return p1
    return _SIDX.get(sub, p1)

ADAPTER = _script_path("minimaxcode_hook_adapter.py")

def q(p): return '"%s"' % p
ENV_BASE = "env -u PYTHONHOME -u PYTHONPATH "
def pycmd(sub, args="", extra_env=""):
    p = _script_path(sub)
    pre = (extra_env + " ") if extra_env else ""
    return ("%s%s%s %s%s" % (pre, ENV_BASE, py, q(p), (" " + args) if args else "")).strip()
def wrapped(sub, args="", extra_env=""):
    """Stop 事件专用：必裹 JSON 契约适配器（宿主 stdout 单 JSON 契约）"""
    pre = (extra_env + " ") if extra_env else ""
    t = _script_path(sub)
    return ("%s%s%s %s -- %s%s" % (pre, ENV_BASE, py, q(ADAPTER), q(t), (" " + args) if args else "")).strip()
DZ = "DOENGLINGZ_CONFIG_DIR=%s" % cfg
TSLENV = "TSL_INJECT_STATE=%s" % os.path.join(cfg, "doenglingz_inject_state.json")

ENTRIES = [
    # ── UserPromptSubmit（6 条·直挂·⛔不裹适配器：实测纯文本可投递）──
    ("UserPromptSubmit", None, pycmd("doenglingz_inject_prompt.py", "--src minimaxcode --hook-protocol=text", DZ)),
    ("UserPromptSubmit", None, pycmd("rule_fragment_inject.py", "--hook-protocol=text")),
    ("UserPromptSubmit", None, pycmd("minimaxcode_title_namer.py")),
    ("UserPromptSubmit", None, pycmd("route_inject_prompt.py", "--hook-protocol=text")),
    ("UserPromptSubmit", None, pycmd("route_miss_feeder.py")),
    ("UserPromptSubmit", None, pycmd("kb_inject_prompt.py", "--hook-protocol=text")),
    # ── Stop（8 条·⛔全部裹 minimaxcode_hook_adapter.py）──
    ("Stop", None, wrapped("doenglingz_guard.py", "--check --src minimaxcode", DZ)),
    ("Stop", None, wrapped("route_unknown_unknown.py")),
    ("Stop", None, wrapped("audit_search_kb.py")),
    ("Stop", None, wrapped("route_audit.py", "--src minimaxcode")),
    ("Stop", None, wrapped("route_guard_audit.py")),
    ("Stop", None, wrapped("feedback_detect.py")),
    ("Stop", None, wrapped("rule_three_layer_guard.py", "--deliver")),
    ("Stop", None, wrapped("card_id_guard.py", "", "CARD_GUARD_HOST=minimaxcode")),
    # ── SessionStart（4 条·⛔不裹适配器：实测零 HOOK_INVALID_OUTPUT）──
    ("SessionStart", None, pycmd("memory_pointer_reachability_guard.py", "--scope system")),
    ("SessionStart", None, pycmd("crossend_guard.py")),
    ("SessionStart", None, pycmd("minimaxcode_health_aggregator.py")),
    # 补链器＝值侧对账（补真源新增 Skill 自动可见·⛔不碰端专属实体·⛔真源只读）
    ("SessionStart", None, pycmd("minimaxcode_skill_link_reconciler.py")),
]

data = {"hooks": {}}
if os.path.isfile(hooks_json):
    try:
        data = json.load(open(hooks_json, encoding="utf-8"))
    except Exception as e:
        print("❌ hooks.json 不可解析（未改动·请人工修复后重跑）：%s" % e)
        sys.exit(2)
    if not isinstance(data, dict):
        print("❌ hooks.json 顶层不是对象（未改动）")
        sys.exit(2)
hooks = data.setdefault("hooks", {})

def already(ev, cmd):
    names = re.findall(r'"[^"]+\.(?:py|sh|ps1)"', cmd)
    base = os.path.basename(names[-1]) if names else ""
    if not base:
        return False
    for grp in hooks.get(ev, []) or []:
        if not isinstance(grp, dict):
            continue
        for h in grp.get("hooks", []):
            if isinstance(h, dict) and base in (h.get("command") or ""):
                return True
    return False

added = skipped = 0
for ev, matcher, cmd in ENTRIES:
    arr = hooks.setdefault(ev, [])
    if already(ev, cmd):
        skipped += 1
        continue
    grp = {}
    if matcher:
        grp["matcher"] = matcher
    grp["hooks"] = [{"type": "command", "command": cmd, "timeout": 30}]
    arr.append(grp)
    added += 1

if added:
    if os.path.isfile(hooks_json):
        shutil.copy2(hooks_json, hooks_json + ".bak-minimaxcode-setup-" + time.strftime("%Y%m%d%H%M%S"))
    tmp = hooks_json + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, hooks_json)
print("  hooks.json：新增 %d · 已存在跳过 %d（共声明 %d 条）" % (added, skipped, len(ENTRIES)))
sys.exit(0)
PYEOF
    rc=$?
    if [ $rc -ne 0 ]; then
        echo -e "  ${R}❌ hooks.json 注册失败（rc=${rc}）——安装器 ② 仍会部署副本，但注册面未完成${N}"
        exit 2
    fi
fi

# ─── 自验证（⛔不谎报：缺件逐条显形）
echo -e "${C}自验证${N}"
MISS=0
if [ -f "$AGENTS_MD" ]; then echo -e "  ${G}✅${N} AGENTS.md（SOUL+IDENTITY+自定义指令 三合一）"
else echo -e "  ${R}❌${N} AGENTS.md 缺失"; MISS=$((MISS+1)); fi
if [ -f "$USER_MD" ]; then echo -e "  ${G}✅${N} memory/user.md"
else echo -e "  ${R}❌${N} memory/user.md 缺失"; MISS=$((MISS+1)); fi
if [ -f "$MEMORY_MD" ]; then echo -e "  ${G}✅${N} agents/mavis/memory/MEMORY.md"
else echo -e "  ${R}❌${N} agents/mavis/memory/MEMORY.md 缺失"; MISS=$((MISS+1)); fi
if [ -d "$SKILLS_DST" ]; then
    echo -e "  ${G}✅${N} skills 目录可达（$(ls -1 "$SKILLS_DST" 2>/dev/null | wc -l | tr -d ' ') 项·实体通道）"
    # 形态自检（⛔判据面＝落点面：顶层软链 ⇒ 端专属无处可落 ⇒ 必红）
    if [ -n "$DRY" ]; then
        echo -e "  ${C}[dry-run] 形态腿不判红（归一未实跑·端专属未落盘）${N}"
    elif [ -L "$SKILLS_DST" ]; then
        echo -e "  ${R}❌${N} skills 顶层仍是整目录软链（形态归一未生效·端专属 Skill 无处可落）"; MISS=$((MISS+1))
    else
        _CS=$("$PY" -c "
import os,sys
d=sys.argv[1]
try: items=os.listdir(d)
except Exception: items=[]
ln=[x for x in items if os.path.islink(os.path.join(d,x))]
print(len(ln), len(items))
" "$SKILLS_DST" 2>/dev/null)
        _LNK="${_CS%% *}"; _ALL="${_CS##* }"
        echo -e "  ${G}✅${N} skills 形态＝普通目录（通用软链 ${_LNK}/${_ALL} 件 → 唯一真源）"
        for _es in 布洛陀-童灵守护 布洛陀-童灵切片导航; do
            if [ -L "$SKILLS_DST/$_es" ]; then
                echo -e "  ${R}❌${N} 端专属 Skill ${_es} 是软链（应实体落端内·⛔不进真源）"; MISS=$((MISS+1))
            elif [ -d "$SKILLS_DST/$_es" ]; then
                echo -e "  ${G}✅${N} 端专属 Skill ${_es} 实体在位（⛔其他端不可见）"
            else
                echo -e "  ${R}❌${N} 端专属 Skill ${_es} 缺失"; MISS=$((MISS+1))
            fi
        done
    fi
else echo -e "  ${R}❌${N} skills 目录缺失"; MISS=$((MISS+1)); fi
if [ -f "$PLUGIN_JSON" ]; then echo -e "  ${G}✅${N} 插件 manifest 在位（hooks 数组声明）"
else echo -e "  ${R}❌${N} 插件 manifest 缺失（宿主不会装载钩子）"; MISS=$((MISS+1)); fi
if [ -f "$HOOKS_JSON" ] && "$PY" -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));assert isinstance(d.get('hooks'),dict)" "$HOOKS_JSON" 2>/dev/null; then
    EVN=$("$PY" -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));h=d.get('hooks',{});print(sum(len(g.get('hooks',[])) for ev in h.values() for g in ev))" "$HOOKS_JSON")
    echo -e "  ${G}✅${N} 插件 hooks.json 可解析（$EVN 条命令）"
    # Stop 包裹率自检（⛔裸挂＝宿主丢弃＝假绿）
    STOPW=$("$PY" -c "
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
h=d.get('hooks',{}).get('Stop',[])
tot=wrap=0
for g in h:
    for x in g.get('hooks',[]):
        tot+=1
        if 'minimaxcode_hook_adapter.py' in (x.get('command') or ''): wrap+=1
print(f'{wrap}/{tot}')
" "$HOOKS_JSON" 2>/dev/null)
    echo -e "  ${G}✅${N} Stop 事件 JSON 适配器包裹率: ${STOPW}（⛔裸挂会被宿主丢弃）"
else
    [ -f "$HOOKS_JSON" ] && { echo -e "  ${R}❌${N} hooks.json 不可解析"; MISS=$((MISS+1)); }
fi
if [ $MISS -eq 0 ]; then
    echo -e "${G}✅ 端特有链完成：AGENTS.md 三合一 + user.md + MEMORY.md + Skill 实体 + 插件 hooks.json${N}"
    echo -e "${C}   钩子脚本副本由安装器 ② 随后落 <CFG>/hooks/（本步只写注册面）${N}"
    echo -e "${C}   ⚠️ 用默认会话使用：长期记忆通道只对内置默认会话开放（选自定义 agent 拿不到 MEMORY）${N}"
    exit 0
else
    echo -e "${R}❌ 自验证发现 $MISS 项硬缺失（⛔不假绿）${N}"
    exit 2
fi
