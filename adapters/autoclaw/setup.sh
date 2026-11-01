#!/usr/bin/env bash
# setup.sh — AutoClaw 端执行准则注入器（幂等）
# 判据：OpenClaw workspace bootstrap = AGENTS.md 常驻注入（平台原生·非 AI 自觉）
# 用法：bash setup.sh [--all | --workspace <path>]
set -euo pipefail

# DRY=1（安装器委派契约·2026-10-03）：本脚本未实现零写入演练——显式跳过而非"演练着写盘"（⛔假绿）
if [ "${DRY:-0}" = "1" ]; then
  echo "[dry-run] DRY=1：本脚本未实现零写入演练，已跳过实际写入（幂等安全·真装请不带 --dry-run 重跑）"
  exit 0
fi

MARK="buluotuo:execution-guidelines-v1"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SRC_DIR/rules/execution-guidelines.md"
# ⚠️ 2026-11-01 隔离链根治（全端统一口径）：端根以 DOENGLINGZ_CONFIG_DIR 为首优先级
#   （安装器委派唯一透传键＝唯一隔离真源）⇒ 隔离装不写真机 ~/.openclaw-autoclaw。
DEFAULT_ROOT="${DOENGLINGZ_CONFIG_DIR:-${HOME}/.openclaw-autoclaw}"

# 从通用版提取注入正文：去 frontmatter、去「本端注入说明」节，保留 # 标题至第 9 条
extract_body() {
  awk 'BEGIN{fm=0; body=0}
       NR==1&&/^---$/{fm=1;next}
       fm&&/^---$/{fm=2;next}
       fm==2{body=1}
       body&&/^## 本端注入说明/{exit}
       body{print}' "$SRC" | sed '/^[[:space:]]*$/d' > /tmp/_bg_exec_body.$$.md
  echo /tmp/_bg_exec_body.$$.md
}

inject_one() {
  local f="$1" body="$2"
  if grep -q "$MARK" "$f" 2>/dev/null; then
    echo "  SKIP（已含标记）: $f"
    return 0
  fi
  [ -f "$f" ] || { echo "  ⚠️ AGENTS.md 不存在（跳过·非 bootstrap 工作区）: $f"; return 0; }
  local tmp; tmp="$(mktemp)"
  { printf '<!-- %s · 安装包通用版同步 %s -->\n\n' "$MARK" "$(date +%F)"
    cat "$body"
    printf '\n\n<!-- /%s -->\n' "$MARK"
    cat "$f"; } > "$tmp"
  mv "$tmp" "$f"
  echo "  ✅ 注入: $f"
}

main() {
  [ -f "$SRC" ] || { echo "❌ 找不到 $SRC"; exit 2; }
  local body; body="$(extract_body)"
  # trap 定义时展开 $body 的值（EXIT 触发时已不在 main 作用域·set -u 会报 unbound）
  trap "rm -f '$body'" EXIT

  if [ "${1:-}" = "--workspace" ] && [ -n "${2:-}" ]; then
    inject_one "$2/AGENTS.md" "$body"
    return 0
  fi

  # --all：读 openclaw.json agents.list[].workspace + defaults.workspace 逐个注入
  local wss
  # ⚠️ 2026-11-01 D9 全新机崩溃根治：宿主 openclaw.json 是**宿主自己生成的配置**（安装器不写）
  #   ⇒ 全新机器上该文件不存在 ⇒ json.load 抛 FileNotFoundError + set -e ⇒ 整个端 setup 崩
  #   （exit 1·端接入未完成）。实锤：2026-11-01 沙箱全新安装实跑 autoclaw exit=1
  #   （作者机有该文件⇒此病隐形）。修法=存在性防护：读不到就按「无可注入 workspace」继续
  #   （⛔不静默崩·显形告警）。
  if [ -f "$DEFAULT_ROOT/openclaw.json" ]; then
    wss="$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('$DEFAULT_ROOT/openclaw.json')))
ag = d.get('agents', {})
ws = []
dw = ag.get('defaults', {}).get('workspace')
if dw: ws.append(os.path.expanduser(dw))
for a in ag.get('list', []):
    w = a.get('workspace')
    if w: ws.append(os.path.expanduser(w))
print('\n'.join(sorted(set(ws))))
")"
  else
    wss=""
    echo "  ⚠️ 未找到宿主配置 $DEFAULT_ROOT/openclaw.json（全新机·宿主尚未生成）——workspace 探测跳过（⛔不崩）"
  fi
  echo "注入面清单："
  echo "$wss" | sed 's/^/  - /'
  while IFS= read -r ws; do
    [ -n "$ws" ] && inject_one "$ws/AGENTS.md" "$body"
  done <<< "$wss"
  echo "完成。验证：新开会话问『你必须遵守哪几条执行准则』→ 答出 9 条即生效。"
}

main "$@"
