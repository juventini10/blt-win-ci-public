#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""traecn_pretool_guard.py v0.2 — Trae CN PreToolUse 事前物理闸（deny 升级落地件）

v0.2（2026-10-21）：**R3 误拦收窄**——共享判据含裸「发布」，目录名「安装发布」即命中并阻断只读命令；
      R3 命中后须含真外传工具词才 deny，否则提示放行并记 r3_false_positive（防愿景②摩擦）。

立法: 皮叔 2026-10-09「deny 升级…按符合愿景第一性原理最优解推进」（提案登记=接入记录-Trae CN §三.3·禁设第一问过闸）
判据族: 复用 route_guard_config.json rules（R1_delete/R2_core_write/R3_external·本身即 tool_input 形正则·零新判据）
分档设计（防误拦第一性·误伤概率分档）:
  - R1_delete（rm -rf/trash 清空/find -delete·不可逆物理族）→ deny（exit 2）
  - R3_external（curl/wget 外传 × 个人AI档案·隐私红线族）→ deny（exit 2）
  - R2_core_write（核心规则文件写·合法维护高频）→ warn 不拦（exit 0 + stderr 提醒 + 台账）——硬拦会把日常授权维护变成每日摩擦（愿景②）
机制: 官方 docs.trae.cn/ide_hook-configuration-reference——PreToolUse exit 2 = block 该工具调用 + stderr 展示给 agent；
      exit 0 = 放行。本件 exit 2 为官方 deny 语义（⚠️ 与 Stop 事件 exit2=block 回复的红线相反·两事件语义不同·勿混用）
纪律: 失败放行（配置缺失/解析失败/未预见异常→exit 0 + 台账留痕·⛔不阻断主流程）·deny 必留痕（可观测黑箱红线）
台账: [记忆共享中心]/脚本中心/logs/pretool_guard.jsonl（deny/warn/config_missing/stdin_unparsed/crash/r3_false_positive 六事件）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import json
import os
import re
import sys
import datetime

CFG = os.path.expanduser("[记忆共享中心]/脚本中心/route_guard_config.json")
LOG = os.path.expanduser("[记忆共享中心]/脚本中心/logs/pretool_guard.jsonl")
DENY_RULES = {"R1_delete", "R3_external"}   # 硬拦族（不可逆/外传·误伤≈0）
WARN_RULES = {"R2_core_write"}               # 提醒族（合法维护高频·不拦）
# 真外传证据词（2026-10-21 误拦收窄·v0.2）：共享 R3 判据含裸「发布」关键词，
# 目录名「安装发布」即命中 → 事前硬拦把只读 ls/find 阻断（实证：2026-10-21 本端审计轮）。
# 收窄：R3 命中后须同时出现**真实外传命令名**才 deny；中文描述词（外传/发布/上传…）
# ⛔不得单独作证据——否则"写变更日志提到外传二字"也被拦（同日二次实证）。
# 判据最小化：只认 curl/wget/scp/rsync/sendmail/mail -s/https URL/post /api/。
TRUE_EXFIL = re.compile(
    r"\bcurl\b|\bwget\b|\bscp\b|\brsync\b|\bsendmail\b|\bmail\s+-s\b|"
    r"https?://|\bpost\s+/|\bapi/[a-z]",
    re.I,
)


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(entry):
    """台账留痕（失败不阻断——判定不依赖台账）"""
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def load_rules():
    """与 route_guard_audit.load_rules 同构：失败=留痕+空规则（放行）"""
    try:
        with open(CFG, encoding="utf-8") as f:
            data = json.load(f)
        rules = {k: re.compile(v, re.I) for k, v in data.get("rules", {}).items()}
        if not rules:
            raise ValueError("rules 为空")
        return rules
    except Exception as e:
        log({"ts": now(), "event": "config_missing", "cfg": CFG, "err": str(e)})
        return {}


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0                      # stdin 失败放行
    rules = load_rules()
    if not rules:
        return 0                      # 无判据=放行（降级留痕在 config_missing）
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log({"ts": now(), "event": "stdin_unparsed", "n": len(raw), "err": str(e)})
        return 0                      # 解析失败放行·留痕
    tool = str(payload.get("tool_name", "?"))
    ti = payload.get("tool_input", {}) or {}
    # 键名归一化：R 族正则锚定 "path"/"target" 精确键名，而 Write/Edit 实际键为 file_path——
    # 归一化补齐（T2 自测实证漏网后补·⛔不改共享 config 正则，只在本端件做投影）
    if isinstance(ti, dict) and "file_path" in ti and "path" not in ti:
        ti = dict(ti)
        ti["path"] = ti["file_path"]
    blob = json.dumps(ti, ensure_ascii=False)
    for rule, pat in rules.items():
        if pat.search(blob):
            if rule == "R3_external" and not TRUE_EXFIL.search(blob):
                # 目录名误命中（如「安装发布」）→ 提示放行，⛔不阻断只读运维（v0.2 误拦收窄）
                print(
                    f"[traecn-pretool-guard] 提示：{tool} 命中 R3 但无外传工具词"
                    f"（疑目录名如「安装发布」）→ 放行留痕",
                    file=sys.stderr,
                )
                log({"ts": now(), "event": "r3_false_positive", "tool": tool})
                continue
            if rule in DENY_RULES:
                print(
                    f"[traecn-pretool-guard] 事前闸拦截：工具 {tool} 命中敏感判据 {rule}"
                    f"（不可逆/外传族·判据复用 route_guard_config·皮叔 2026-10-09 立法）。"
                    f"请改走安全等价路径（如 trash 不 rm·只读确认后分步执行）；"
                    f"确需原样执行请报你裁定。",
                    file=sys.stderr,
                )
                log({"ts": now(), "event": "deny", "tool": tool, "rule": rule})
                return 2               # 官方 PreToolUse deny 语义
            # WARN_RULES：提醒不拦
            print(
                f"[traecn-pretool-guard] 提醒：{tool} 命中核心文件写判据 {rule}"
                f"（提醒族不拦截·请确认已按铁律先读再改/备份在先）",
                file=sys.stderr,
            )
            log({"ts": now(), "event": "warn", "tool": tool, "rule": rule})
            return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log({"ts": now(), "event": "crash", "err": str(e)})
        sys.exit(0)                    # 未预见异常放行·留痕
