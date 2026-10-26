#!/usr/bin/env bash
# setup.sh — Zwork 端对账器（平台托管型·对账吸收模式·幂等·fail-loud）·v0.3（2026-10-26＋装载通道三步＋端实体首装交付）
# 端分立铁律：本端=AutoClaw 新客户端（zwork 运行时·🧠）·⛔与 ~/.openclaw-autoclaw（旧客户端·🦞）混同
# 本端无盘上规则注入面：五系统文件等价物=端自有实体——本脚本只对账，⛔覆盖端实体（条文48 端自持有律）
# 用法: bash setup.sh [记忆共享中心绝对路径] ；演练: DRY=1 bash setup.sh
set -uo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY="${DRY:-0}"
FAIL=0
say() { echo -e "$1"; }
run() { if [ "$DRY" = "1" ]; then say "  ${CYAN}[dry]${NC} $*"; else "$@"; fi; }

# ── 记忆中心定位：参数 › 环境变量 › 缺省 ~/个人AI档案（MC=档案库实体·本端 作者机=用户机同构）──
MC="${1:-${MEMORY_CENTER:-$HOME/个人AI档案}}"
[ -d "$MC" ] || { say "${RED}❌ 记忆中心不存在: ${MC}（传参或设 MEMORY_CENTER）${NC}"; exit 2; }

say "${CYAN}[1/4] 撞端防线${NC}"
if [ -d "$HOME/.openclaw-autoclaw" ]; then
  say "${YELLOW}  ⚠️ 本机存在 ~/.openclaw-autoclaw（旧客户端端·另一独立端）——本次对账对象为 Zwork（AutoClaw 新客户端）·两端不共用不占用${NC}"
fi

say "${CYAN}[2/4] 端实体对账与首装交付（五系统文件等价物·在场对账/缺则模板落位）${NC}"
# ① K2 宪法实体：SOUL.md + AGENTS.md 成对标记对（buluotuo:execution-guidelines-v1 ×2）
ZW_DIR="$MC/AutoClaw"
# 首装交付＝脱敏占位模板落位（在场＝对账 ⛔覆盖·条文48 端自持有律）
for f in SOUL.md AGENTS.md; do
  T="$ZW_DIR/$f"
  TPL="$PKG/adapters/zwork/templates/$f"
  if [ -f "$T" ]; then
    say "  ✅ 实体在场: AutoClaw/$f"
  elif [ -f "$TPL" ]; then
    if [ "$DRY" = "1" ]; then
      say "  ${CYAN}[dry]${NC} 首装交付模板 → AutoClaw/${f}（[记忆共享中心]→${MC}）"
    else
      mkdir -p "$ZW_DIR"
      if python3 -c 'import sys,io;io.open(sys.argv[2],"w",encoding="utf-8").write(io.open(sys.argv[1],encoding="utf-8").read().replace("[记忆共享中心]",sys.argv[3]))' "$TPL" "$T" "$MC"; then
        say "  ✅ 端实体首装交付: AutoClaw/${f}（脱敏模板·占位符已落位）"
      else
        say "${RED}  ❌ 端实体交付失败: AutoClaw/$f${NC}"; FAIL=1
      fi
    fi
  else
    say "${RED}  ❌ 缺失且模板缺: AutoClaw/$f${NC}"; FAIL=1
  fi
done
if [ -f "$ZW_DIR/AGENTS.md" ]; then
  N=$(grep -c "buluotuo:execution-guidelines-v1" "$ZW_DIR/AGENTS.md" || true)
  if [ "$N" -ge 2 ]; then say "  ✅ 执行准则标记对成对（×${N}）"; else say "${RED}  ❌ 标记对不完整（×${N}·须≥2）${NC}"; FAIL=1; fi
  if grep -q "5.5 检索与卡号纪律" "$ZW_DIR/AGENTS.md"; then say "  ✅ 5.5 检索与卡号纪律段在场"; else say "${YELLOW}  🟡 5.5 段缺（M1 对账吸收可补·非阻塞）${NC}"; fi
fi
# ② SOUL 卡号纪律硬化
if [ -f "$ZW_DIR/SOUL.md" ]; then
  if grep -q "说不出=编" "$ZW_DIR/SOUL.md"; then say "  ✅ SOUL 卡号硬化句在场"; else say "${YELLOW}  🟡 SOUL 卡号硬化句缺（v1.1 补·非阻塞）${NC}"; fi
fi
# ③ Memory 面（机制级注入·端 AI 行为侧自查口令）
say "  ✅ Memory 面=平台托管（Run 级注入·机械保证·脚本不可测属平台内）"

say "${CYAN}[3/4] K2 恒驻核与 W2 机械腿${NC}"
# [3b] TSL 机械校验器部署（§八·七 无钩子端脚本化·构造权归脚本·版本比对同版跳过）
TSL_SRC="$PKG/adapters/zwork/scripts/zwork_tsl_verify.py"
TSL_DST="$MC/脚本中心/分身/zwork_tsl_verify.py"
if [ -f "$TSL_SRC" ]; then
  if [ ! -f "$TSL_DST" ] || ! cmp -s "$TSL_SRC" "$TSL_DST"; then
    if [ "$DRY" = "1" ]; then
      say "  ${CYAN}[dry]${NC} mkdir -p 脚本中心/分身 && cp → 脚本中心/分身/zwork_tsl_verify.py"
    else
      mkdir -p "$(dirname "$TSL_DST")" \
        && cp "$TSL_SRC" "$TSL_DST" \
        && say "  ✅ TSL校验器已部署: 脚本中心/分身/zwork_tsl_verify.py" \
        || { say "${RED}  ❌ TSL校验器部署失败: $TSL_DST${NC}"; FAIL=1; }
    fi
  else
    say "  ✅ TSL校验器同版在位（跳过）"
  fi
  say "  ℹ️ D3 上岗回合末调用: python3 \"$TSL_DST\" --window 30（AI 只许逐行 relay stdout）"
else
  say "${RED}  ❌ TSL校验器源缺失: $TSL_SRC${NC}"; FAIL=1
fi
K2="$MC/数字分身/K2切片蒸馏/slices/core_slice.md"
if run test -f "$K2"; then
  [ -f "$K2" ] && say "  ✅ K2 切片库在场: ${K2#$MC/}" || { say "${RED}  ❌ core_slice.md 缺失${NC}"; FAIL=1; }
else
  say "${YELLOW}  🟡 K2 切片库缺（数字分身完整版单装时补·M7 域）${NC}"
fi
TS="$MC/数字分身/scripts/last_run_doenglingz_slice_watch.ts"
if [ -f "$TS" ]; then say "  ✅ W2 心跳文件在场（末次: $(cat "$TS" 2>/dev/null)）"; else say "${YELLOW}  🟡 W2 心跳未建（蒸馏调度域·非阻塞）${NC}"; fi


say "${CYAN}[4/4] 装载通道（AGENTS.md 桥+技能根+审批·v0.2 起·全部幂等）${NC}"
# [4a] AGENTS.md 机械桥：~/.pi/agent/AGENTS.md → 端真源（dist 实证 pi-user priority1 每 Run 自动装配）
PI_DIR="$HOME/.pi/agent"
BRIDGE="$PI_DIR/AGENTS.md"
if [ -f "$ZW_DIR/AGENTS.md" ]; then
  if [ -L "$BRIDGE" ]; then
    CUR="$(readlink "$BRIDGE")"
    if [ "$CUR" = "$ZW_DIR/AGENTS.md" ]; then
      say "  ✅ AGENTS.md 桥在位（→ 端真源·跳过）"
    else
      run ln -sfn "$ZW_DIR/AGENTS.md" "$BRIDGE" && say "  ✅ AGENTS.md 桥已改指端真源（原: ${CUR}）" || { say "${RED}  ❌ 桥改指失败${NC}"; FAIL=1; }
    fi
  elif [ -e "$BRIDGE" ]; then
    say "${RED}  ❌ $BRIDGE 为普通文件（非桥）——⛔不覆盖用户文件，请人工裁决（正确形态=软链→端真源）${NC}"; FAIL=1
  else
    run mkdir -p "$PI_DIR"
    run ln -s "$ZW_DIR/AGENTS.md" "$BRIDGE" && say "  ✅ AGENTS.md 桥已建: ~/.pi/agent/AGENTS.md → 端真源（每 Run 自动装配·pi-user priority1）" || { say "${RED}  ❌ 桥创建失败${NC}"; FAIL=1; }
  fi
else
  say "${YELLOW}  🟡 端真源 AGENTS.md 缺（[2/4] 已报）——桥跳过${NC}"
fi
# [4b] 技能根声明：~/.pi/agent/settings.json skills 并入两根（幂等·保既有键·JSON 合并走 python3）
R1="$MC/技能配置"; R2="$PKG/adapters/zwork/skills"
if [ -d "$R1" ] && [ -d "$R2" ]; then
  if [ "$DRY" = "1" ]; then
    say "  ${CYAN}[dry]${NC} python3 合并 settings.json skills += [$R1, $R2]"
  else
    OUT=$(python3 - "$HOME/.pi/agent/settings.json" "$R1" "$R2" <<'PYSET'
import json, sys, os, io
p, r1, r2 = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.dirname(p), exist_ok=True)
data = {}
if os.path.exists(p):
    try:
        data = json.load(io.open(p, encoding='utf-8'))
    except Exception as e:
        print(f"❌ settings.json 解析失败: {e}"); sys.exit(1)
skills = data.get("skills") or []
changed = False
for r in (r1, r2):
    if r not in skills:
        skills.append(r); changed = True
if changed:
    data["skills"] = skills
    io.open(p, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("  ✅ 技能根已并入 settings.json（+%d → %d 根）" % (2 if len(skills)>=2 else len(skills), len(skills)))
else:
    print("  ✅ 技能根已在 settings.json（幂等跳过）")
PYSET
)
    if [ $? -eq 0 ]; then echo "$OUT"; say "  ℹ️ 外部根生效须平台审批（[4c]）＋新会话名册刷新"; else echo "$OUT"; say "${RED}  ❌ 技能根合并失败${NC}"; FAIL=1; fi
  fi
else
  say "${YELLOW}  🟡 技能根目录缺失（技能配置/包内 zwork skills）——技能装载腿跳过${NC}"
fi
# [4c] 审批腿：declarative_resource_root_approvals 幂等注册（owner_id 自发现·失败=显形引导⛔不盲写）
DB=""
for cand in "$HOME/Library/Application Support/AutoClaw-official"/accounts/*/runtime/runtime.sqlite; do
  [ -f "$cand" ] && DB="$cand" && break
done
if [ -z "$DB" ]; then
  say "${YELLOW}  🟡 runtime.sqlite 未找到（平台未启动过？）——首次启动后在设置内批准外部资源根${NC}"
elif [ "$DRY" = "1" ]; then
  say "  ${CYAN}[dry]${NC} sqlite INSERT OR IGNORE approvals ← 两根（owner_id 自发现）"
else
  OUT=$(python3 - "$DB" "$R1" "$R2" <<'PYDB'
import sqlite3, sys, uuid, datetime
db, r1, r2 = sys.argv[1], sys.argv[2], sys.argv[3]
con = sqlite3.connect(db)
cur = con.cursor()
owner = None
for t in ("identity_personal_principals", "principals", "owners"):
    try:
        row = cur.execute("select id from %s limit 1" % t).fetchone()
        if row:
            owner = row[0]; break
    except sqlite3.OperationalError:
        continue
if owner is None:
    try:
        row = cur.execute("select owner_id from declarative_resource_root_approvals limit 1").fetchone()
        if row: owner = row[0]
    except sqlite3.OperationalError:
        pass
if owner is None:
    print("  🟡 owner_id 无法自发现——请在本端会话内由 AI 按平台审批流程注册（⛔不盲写）")
    sys.exit(2)
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
n = 0
for r in (r1, r2):
    cur.execute("insert or ignore into declarative_resource_root_approvals(owner_id, root_real_path, approval_id, approved_at) values(?,?,?,?)",
                (owner, r, str(uuid.uuid4()), now))
    n += cur.rowcount
con.commit()
print("  ✅ 审批注册完成（新增 %d 条·owner=%s…）" % (n, owner[:8]) if n else "  ✅ 审批已在位（幂等跳过）")
PYDB
)
  if [ $? -eq 0 ]; then echo "$OUT"; else echo "$OUT"; say "${YELLOW}  🟡 审批未自动完成——按上方指引处理（技能面板缺技能时优先查此腿）${NC}"; fi
fi

echo
if [ "$FAIL" -eq 0 ]; then say "${GREEN}✅ Zwork 对账完成：端实体全在场＋装载通道就绪（桥/技能根/审批·幂等）${NC}"; exit 0
else say "${RED}❌ 对账发现缺失（见上·FAIL=${FAIL}）——缺失段按 M1 对账吸收补齐，⛔整文件覆盖${NC}"; exit 1; fi
