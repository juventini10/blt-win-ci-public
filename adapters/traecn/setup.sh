#!/usr/bin/env bash
# ============================================================
# setup.sh — Trae CN adapter 聚合安装入口（幂等）
# 用途: install_scripts.py --platform traecn 按 capability.yaml install_entry 委派到此
# 职责: ① rules 规则文件落盘(~/.trae-cn/user_rules·存在不覆盖·保本地私人版优先)
#       ①a 数字分身恒驻核组装落盘（有 K2 slices 才落·缺则诚实提示·⛔不假绿）
#       ①b 童灵专属 Skill 直落(~/.trae-cn/skills·真目录·⛔不进共享技能配置) + 通用 Skill 软链
#       ② hooks.json 注册（本端唯一写点·安装器 ③ 因此跳过=防双写）
#       ③ 自验证（五系统文件 / 分身核 / Skill / hooks.json 六事件 25 条）
# 判据: Trae CN = 标准 hook 端（注册面 hooks.json）+ rules 常驻注入 + Skill 双通道
# 用法: bash setup.sh "<记忆共享中心绝对路径>"
# 来源: 布洛陀全平台安装包 adapters/traecn/setup.sh（2026-10-25 建·承 traework 六步骨架）
#       差异点：Trae Work 退役（无 hooks·launchd patrol 拉模式）→ Trae CN 单端（hooks.json 事件面实挂）
#       ⛔ 不继承「无钩子/launchd patrol」口径——那对本端是假声明（实盘 250925 六事件 25 条）
# 退出码: 0=端特有链全成功 | 2=真失败（缺 MC/缺源件/hooks.json 不可解析） | 3=文件已落盘·仅手动收尾待办
# ============================================================
set -uo pipefail

G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; C='\033[0;36m'; N='\033[0m'
MC=""
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
RULE_SRC="$SRC_DIR/rules"
CFG="$HOME/.trae-cn"
RULE_DST="$CFG/user_rules"
HOOKS_DIR="$CFG/hooks"
HOOKS_JSON="$CFG/hooks.json"
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

echo -e "${C}=== Trae CN adapter 安装（rules + 分身核 + Skill + hooks.json 注册） ===${N}"
[ -n "$MC" ] || { echo -e "${R}❌ 未给记忆共享中心路径（用法: bash setup.sh \"<MC>\"）${N}"; exit 2; }
[ -n "$PY" ] || { echo -e "${R}❌ 未找到 python（python3/python）——hooks.json 注册与自验证需要${N}"; exit 2; }

fill_ph() {
    local f="$1"
    [ -f "$f" ] || return 0
    grep -qF "$MCP" "$f" 2>/dev/null || return 0
    sed "s@${MCP_RE}@${MC}@g" "$f" > "$f.tmp.$$" && mv "$f.tmp.$$" "$f"
}

link_skill_dir() {
    local src="$1" dst="$2"
    if [ -L "$dst" ]; then
        [ "$(readlink "$dst")" = "$src" ] && return 0
        rm "$dst"
    elif [ -d "$dst" ]; then
        echo -e "  ${Y}SKIP（实体目录已存在·不覆盖）: $(basename "$dst")${N}"
        return 1
    fi
    ln -s "$src" "$dst"
    return 0
}

# ─── [1/5] rules 规则文件落盘（承载名→注入名映射·条文12）
[ -d "$RULE_SRC" ] || { echo -e "${R}❌ 找不到 rules: $RULE_SRC${N}"; exit 2; }
mkdir -p "$RULE_DST"
echo -e "${C}[1/5] rules 规则文件落盘 → $RULE_DST${N}"
for f in "$RULE_SRC"/*.md; do
    src_name="$(basename "$f")"
    dst_name="$src_name"
    case "$src_name" in
        core-identity.md)       dst_name="IDENTITY.md" ;;
        core-memory.md)         dst_name="MEMORY.md" ;;
        core-soul.md)           dst_name="SOUL.md" ;;
        core-user.md)           dst_name="USER.md" ;;
        execution-guidelines.md) dst_name="trae_solo_rules.md" ;;
    esac
    dst="$RULE_DST/$dst_name"
    if [ -f "$dst" ]; then
        echo -e "  ${Y}SKIP（已存在·保本地/私人版）: $src_name → $dst_name${N}"
    elif [ -n "$DRY" ]; then
        echo -e "  ${C}[dry-run] 将落盘: $src_name → $dst_name${N}"
    else
        cp "$f" "$dst"
        fill_ph "$dst"
        echo -e "  ${G}✅ 落盘: $src_name → $dst_name${N}"
    fi
done

# ─── [2/5] 数字分身恒驻核组装（单一真源=K2 生成器产物·⛔包内不带静态核）
SLICES="$MC/数字分身/K2切片蒸馏/slices"
DT_CORE="$RULE_DST/doenglingz-core.md"
echo -e "${C}[2/5] 数字分身恒驻核 → $DT_CORE${N}"
if [ -f "$DT_CORE" ]; then
    echo -e "  ${Y}SKIP（已存在·保本地/私人版）: doenglingz-core.md${N}"
elif [ -f "$SLICES/core_slice.md" ] && [ -f "$SLICES/L6_反向约束.md" ]; then
    if [ -n "$DRY" ]; then
        echo -e "  ${C}[dry-run] 将从 K2 slices 组装 doenglingz-core.md（头模板 + core_slice + L6）${N}"
    elif [ ! -f "$CORE_HEADER" ]; then
        echo -e "  ${R}❌ 缺恒驻核头模板: ${CORE_HEADER}（打包缺陷·⛔不落无头核）${N}"
    else
        SLICE_HASH="（见 slices/manifest.json）"
        if [ -f "$SLICES/manifest.json" ]; then
            SLICE_HASH="$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1],encoding='utf-8')).get('src_hash',''))" "$SLICES/manifest.json" 2>/dev/null)"
            [ -n "$SLICE_HASH" ] || SLICE_HASH="（manifest 读取失败）"
        fi
        {
            cat "$CORE_HEADER"
            cat "$SLICES/core_slice.md"
            printf '\n\n'
            cat "$SLICES/L6_反向约束.md"
            printf '\n'
        } > "$DT_CORE.tmp.$$"
        sed "s@__SLICE_HASH__@${SLICE_HASH}@g" "$DT_CORE.tmp.$$" > "$DT_CORE"
        rm -f "$DT_CORE.tmp.$$"
        fill_ph "$DT_CORE"
        echo -e "  ${G}✅ 组装落盘（头模板 + core_slice + L6·hash=${SLICE_HASH}）${N}"
    fi
else
    echo -e "  ${Y}⚠️ 未生成 K2 切片·跳过数字分身恒驻核（⛔不落空壳）${N}"
    echo -e "  ${C}   生成后重跑本脚本即可（幂等）：python3 \"$MC/数字分身/k2-slice-generator/k2_slice_generator.py\"${N}"
fi

# ─── [3/5] 童灵专属 Skill 实体直落（⛔不进共享技能配置·防他端串用）+ 通用 Skill 软链
TRAE_SKILLS_SRC="$SRC_DIR/skills"
SKILLS_DST="$CFG/skills"
echo -e "${C}[3/5] 童灵专属 Skill 直落 ${SKILLS_DST}（⛔不进共享技能配置）${N}"
if [ -d "$TRAE_SKILLS_SRC" ]; then
    mkdir -p "$SKILLS_DST"
    for skill in "$TRAE_SKILLS_SRC"/*; do
        [ -d "$skill" ] || continue
        src_name="$(basename "$skill")"
        case "$src_name" in
            doenglingz-guard)     skill_name="布洛陀-童灵守护" ;;
            doenglingz-slice-nav) skill_name="布洛陀-童灵切片导航" ;;
            *)                    skill_name="$src_name" ;;
        esac
        dst="$SKILLS_DST/$skill_name"
        if [ -L "$dst" ]; then
            if [ -n "$DRY" ]; then
                echo -e "  ${C}[dry-run] 将替换软链为实体: $skill_name${N}"
            else
                rm "$dst"; cp -r "$skill" "$dst"
                find "$dst" -type f -print0 | while IFS= read -r -d '' _f; do fill_ph "$_f"; done
                echo -e "  ${G}✅ 替换软链为实体: $skill_name${N}"
            fi
        elif [ -d "$dst" ]; then
            echo -e "  ${Y}SKIP（实体已存在·保本地/私人版）: $skill_name${N}"
        elif [ -n "$DRY" ]; then
            echo -e "  ${C}[dry-run] 将落盘童灵 Skill: $skill_name${N}"
        else
            cp -r "$skill" "$dst"
            find "$dst" -type f -print0 | while IFS= read -r -d '' _f; do fill_ph "$_f"; done
            echo -e "  ${G}✅ 落盘童灵 Skill: $skill_name${N}"
        fi
    done
else
    echo -e "  ${Y}⚠️ 未找到适配器童灵 Skill: $TRAE_SKILLS_SRC${N}"
fi
mkdir -p "$SKILLS_DST"
SK=0; TOT=0
for skill in "$MC/技能配置"/*; do
    [ -d "$skill" ] || continue
    TOT=$((TOT+1))
    link_skill_dir "$skill" "$SKILLS_DST/$(basename "$skill")" && SK=$((SK+1))
done
echo -e "  ${C}通用 Skill 软链结果: $SK/$TOT${N}"

# ─── [4/5] hooks.json 注册（本端唯一写点·安装器 ③ 按 capability 跳过）
#     ⚠️ 与安装器 ② 的分工：② 只把脚本副本落 <CFG>/hooks/；本步只写注册面。
#     ⚠️ 命令一律指向 <CFG>/hooks/（用户机可达）·⛔不写作者机路径。
#     ⚠️ 幂等键=命令里是否已含脚本 basename：命中即跳过（⛔不迁移用户既有命令·不改写他人配置）。
echo -e "${C}[4/5] hooks.json 注册 → $HOOKS_JSON${N}"
if [ -n "$DRY" ]; then
    echo -e "  ${C}[dry-run] 将写入 6 事件 25 条（已存在按 basename 跳过）${N}"
else
    "$PY" - "$HOOKS_JSON" "$HOOKS_DIR" "$CFG" "$MC" <<'PYEOF'
import json, os, re, shutil, sys, time
cfg_path, hooks_dir, cfg, mc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
py = "python3" if shutil.which("python3") else "python"
def q(p): return '"%s"' % p
ENV_BASE = "env -u PYTHONHOME -u PYTHONPATH "
def pycmd(sub, args="", extra_env=""):
    p = os.path.join(hooks_dir, sub)
    pre = (extra_env + " ") if extra_env else ""
    return ("%s%s%s %s%s" % (pre, ENV_BASE, py, q(p), (" " + args) if args else "")).strip()
def shcmd(sub):
    return "bash %s" % q(os.path.join(hooks_dir, sub))
DZ = "DOENGLINGZ_CONFIG_DIR=%s WORKBUDDY_CONFIG_DIR=%s" % (cfg, cfg)
TSLENV = "TSL_INJECT_STATE=%s TSL_TREE_OUT=%s" % (
    os.path.join(cfg, "doenglingz_inject_state.json"), os.path.join(cfg, "tsl_last_tree.md"))
ADP = os.path.join(hooks_dir, "traecn_transcript_adapter.py")
def wrapped(target, args="", extra_env=""):
    pre = (extra_env + " ") if extra_env else ""
    t = os.path.join(hooks_dir, target)
    return ("%s%s%s %s --run %s%s" % (pre, ENV_BASE, py, q(ADP), q(t), (" " + args) if args else "")).strip()

ENTRIES = [
    ("SessionStart", None, shcmd("host_identity_hook.sh")),
    ("UserPromptSubmit", None, shcmd("host_identity_hook.sh")),
    ("UserPromptSubmit", None, pycmd("traecode_title_namer.py")),
    ("UserPromptSubmit", None, pycmd("secret_key_guard.py")),
    ("UserPromptSubmit", None, pycmd("doenglingz_inject_prompt.py", "--src auto", DZ)),
    ("UserPromptSubmit", None, pycmd("tsl_echo_hook.py", "--hook-protocol=text", TSLENV)),
    ("UserPromptSubmit", None, pycmd("traecn_transcript_adapter.py")),
    ("UserPromptSubmit", None, pycmd(os.path.join("route", "route_inject_prompt.py"), "--hook-protocol=text")),
    ("UserPromptSubmit", None, pycmd("route_miss_feeder.py")),
    ("UserPromptSubmit", None, pycmd("kb_inject_prompt.py", "--hook-protocol=text")),
    ("UserPromptSubmit", None, pycmd(os.path.join("rule", "rule_fragment_inject.py"), "--hook-protocol=text")),
    ("PreToolUse", "*", pycmd("traecn_pretool_guard.py")),
    ("PreToolUse", "*", pycmd("doenglingz_skill_onduty_tier_promote.py", "", DZ + " DOENGLINGZ_SRC=traecn")),
    ("Stop", None, pycmd("route_unknown_unknown.py")),
    ("Stop", None, pycmd("traecn_transcript_adapter.py")),
    ("Stop", None, wrapped("route_audit.py", "--src traecn")),
    ("Stop", None, wrapped("route_guard_audit.py", "--src traecn")),
    ("Stop", None, wrapped("audit_search_kb.py")),
    ("Stop", None, wrapped("feedback_detect.py")),
    ("Stop", None, wrapped(os.path.join("rule", "rule_three_layer_guard.py"))),
    ("Stop", None, pycmd("card_id_guard.py")),
    ("Stop", None, pycmd("doenglingz_guard.py", "--check --src traecn", DZ)),
    ("Stop", None, pycmd("doenglingz_level_declare_guard.py", "", DZ + " TSL_INJECT_STATE=%s" % os.path.join(cfg, "doenglingz_inject_state.json"))),
    ("Stop", None, wrapped("tsl_closeout_guard.py", "", DZ + " " + TSLENV)),
    ("Stop", None, pycmd("tsl_tree_hook.py", "", DZ + " " + TSLENV)),
]

data = {"version": 1, "hooks": {}}
if os.path.isfile(cfg_path):
    try:
        data = json.load(open(cfg_path, encoding="utf-8"))
    except Exception as e:
        print("❌ hooks.json 不可解析（未改动·请人工修复后重跑）：%s" % e)
        sys.exit(2)
    if not isinstance(data, dict):
        print("❌ hooks.json 顶层不是对象（未改动）")
        sys.exit(2)
data.setdefault("version", 1)
hooks = data.setdefault("hooks", {})

def already(ev, cmd):
    base = os.path.basename(re.findall(r'"[^"]+\.(?:py|sh|ps1)"', cmd)[-1]) if re.findall(r'"[^"]+\.(?:py|sh|ps1)"', cmd) else ""
    for grp in hooks.get(ev, []) or []:
        if not isinstance(grp, dict):
            continue
        for h in grp.get("hooks", []):
            if isinstance(h, dict) and base and base in (h.get("command") or ""):
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
    if os.path.isfile(cfg_path):
        shutil.copy2(cfg_path, cfg_path + ".bak-traecn-setup-" + time.strftime("%Y%m%d%H%M%S"))
    tmp = cfg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, cfg_path)
print("  hooks.json：新增 %d · 已存在跳过 %d（共声明 %d 条）" % (added, skipped, len(ENTRIES)))
sys.exit(0)
PYEOF
    rc=$?
    if [ $rc -ne 0 ]; then
        echo -e "  ${R}❌ hooks.json 注册失败（rc=${rc}）——安装器 ② 仍会部署副本，但注册面未完成${N}"
        exit 2
    fi
fi

# ─── [5/5] 自验证（⛔不谎报：缺件逐条显形）
echo -e "${C}[5/5] 自验证${N}"
MISS=0
for n in SOUL.md IDENTITY.md USER.md MEMORY.md trae_solo_rules.md; do
    if [ -f "$RULE_DST/$n" ]; then echo -e "  ${G}✅${N} user_rules/$n"
    else echo -e "  ${R}❌${N} user_rules/$n 缺失"; MISS=$((MISS+1)); fi
done
if [ -f "$DT_CORE" ]; then echo -e "  ${G}✅${N} user_rules/doenglingz-core.md"
else echo -e "  ${Y}⚠️${N} user_rules/doenglingz-core.md 未生成（K2 slices 缺失·非本步失败）"; fi
if [ -d "$SKILLS_DST" ]; then
    echo -e "  ${G}✅${N} skills 目录可达（$(ls -1 "$SKILLS_DST" 2>/dev/null | wc -l | tr -d ' ') 项）"
else echo -e "  ${R}❌${N} skills 目录缺失"; MISS=$((MISS+1)); fi
if [ -f "$HOOKS_JSON" ] && "$PY" -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));assert isinstance(d.get('hooks'),dict)" "$HOOKS_JSON" 2>/dev/null; then
    echo -e "  ${G}✅${N} hooks.json 可解析（$(ls -l "$HOOKS_JSON" | awk '{print $5}') bytes）"
else
    [ -f "$HOOKS_JSON" ] && { echo -e "  ${R}❌${N} hooks.json 不可解析"; MISS=$((MISS+1)); }
fi
if [ $MISS -eq 0 ]; then
    echo -e "${G}✅ 端特有链完成：rules 5 件 + 分身核状态 + Skill + hooks.json${N}"
    echo -e "${C}   钩子脚本副本由安装器 ② 随后落 <CFG>/hooks/（本步只写注册面）${N}"
    exit 0
else
    echo -e "${R}❌ 自验证发现 $MISS 项硬缺失（⛔不假绿）${N}"
    exit 2
fi
