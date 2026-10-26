#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""traecn_transcript_adapter.py — Trae CN 端 transcript 适配器 v0.2（2026-10-09）

【为什么存在】
  脚本哲学 04·Hook 清单中 4 件正文类守卫（route_audit / route_guard_audit /
  audit_search_kb / feedback_detect）+ rule_three_layer_guard 的 ④-动态，stdin 契约
  = {"transcript_path": <CC式 JSONL>}；而 Trae CN 官方 Stop 载荷是
  last_assistant_message / text_content（正文直给·无 transcript 文件）。
  → 按 Hermes `_hermes_transcript_adapter` 先例（04 接入说明·db→jsonl 喂 stdin 契约·
  共脚本零改动·端适配承载），本件做两件事：
    ① 幂等记录会话消息 → CC 式 JSONL
    ② --run 转换 stdin 为 {"transcript_path"} 喂共脚本并归一 rc

【纪律】
  - 钩子面 rc 纪律（守卫编写规范 §3.5 L361）：本件与被喂共脚本对外 rc **恒 0**，
    检红走红行 + 台账留痕；rc≠0 专留真崩也转为台账（Trae Stop exit2=block，
    ⛔绝不用非零退出码——防把审计变成"阻断停轮"）。
  - 幂等：flock + 尾行比对（role+text 同 → 跳过），同轮 4 个 --run 并行也只写一条。
  - 异常全放行（exit 0）·子超时 45s 独立降级 · 留痕 traecn_adapter.log（可追查）。
  - 落盘：[记忆共享中心]/Trae记忆/transcripts/<session_id>.jsonl（端专属记忆目录·非 /tmp）。

【用法】
  记录腿（UPS·prompt=user；Stop·last_assistant_message|text_content=assistant）:
    echo '<payload>' | python3 traecn_transcript_adapter.py
  喂食腿（Stop 守卫链）:
    echo '<payload>' | python3 traecn_transcript_adapter.py \
        --run <共脚本路径> [--src traecn]
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys, os, json, re, subprocess, tempfile, time

try:
    import fcntl
except ImportError:  # Windows 无 fcntl：降级无锁（幂等靠尾行比对·钩子串行调用）
    fcntl = None

TR_DIR = os.path.expanduser("[记忆共享中心]/Trae记忆/transcripts")
LOG = os.path.expanduser("[记忆共享中心]/Trae记忆/hooks-probe/traecn_adapter.log")
CHILD_TIMEOUT = 45


def log(msg):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))
    except Exception:
        pass


def safe_sid(sid):
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(sid or "unknown"))[:80]


def flatten(v):
    if isinstance(v, str):
        return v
    return json.dumps(v, ensure_ascii=False)


def ensure_entry(path, role, text):
    """flock + 尾行比对幂等追加 CC 式 {"role","message":{"content":[{type:text}]}}"""
    if not text:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lock = path + ".lock"
    with open(lock, "a") as lf:
        if fcntl:
            fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            tail = ""
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                with open(path, encoding="utf-8") as f:
                    lines = [l for l in f.read().splitlines() if l.strip()]
                    tail = lines[-1] if lines else ""
            if tail:
                try:
                    td = json.loads(tail)
                    t_role = (td.get("role") or "").lower()
                    t_content = td.get("message", {}).get("content")
                    if isinstance(t_content, list):
                        t_text = "".join(
                            b.get("text", "") for b in t_content
                            if isinstance(b, dict) and b.get("type") == "text")
                    else:
                        t_text = flatten(t_content)
                    if t_role == role and t_text == text:
                        return  # 幂等命中
                except Exception:
                    pass
            entry = {"role": role,
                     "message": {"content": [{"type": "text", "text": text}]}}
            with open(path, "a", encoding="utf-8") as f:
                if fcntl:
                    fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        finally:
            if fcntl:
                fcntl.flock(lf, fcntl.LOCK_UN)


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    sid = safe_sid(payload.get("session_id"))
    path = os.path.join(TR_DIR, sid + ".jsonl")

    # ① 记录（UPS=用户 · Stop=助手）
    prompt = payload.get("prompt")
    if isinstance(prompt, str) and prompt.strip():
        ensure_entry(path, "user", prompt)
    last = payload.get("last_assistant_message") or payload.get("text_content")
    if last:
        ensure_entry(path, "assistant", flatten(last))

    # ② --run 转换 stdin 喂共脚本
    if "--run" in sys.argv:
        i = sys.argv.index("--run")
        try:
            script = sys.argv[i + 1]
        except IndexError:
            return 0
        cmd = [sys.executable, script]
        if "--src" in sys.argv:
            j = sys.argv.index("--src")
            try:
                cmd += ["--src", sys.argv[j + 1]]
            except IndexError:
                pass
        try:
            # v0.2（2026-10-09 童灵全链接入）：合并原 payload + transcript_path——
            #   原式只喂 transcript_path ⇒ session_id/last_assistant_message 被剥，
            #   tsl_closeout_guard 的档位过滤（sid 过滤本会话）读不到 ⇒ 退全局最新行=串台源。
            #   子脚本均 .get() 取键，多余键无害；--src 仍按 argv 显式透传。
            p = subprocess.run(
                cmd, input=json.dumps({**payload, "transcript_path": path}),
                capture_output=True, text=True, timeout=CHILD_TIMEOUT)
            if p.stdout:
                sys.stdout.write(p.stdout)
            if p.returncode != 0 or (p.stderr or "").strip():
                log("CHILD rc=%s %s | stderr=%s | stdout_tail=%s" % (
                    p.returncode, os.path.basename(script),
                    (p.stderr or "")[-300:], (p.stdout or "")[-200:]))
        except subprocess.TimeoutExpired:
            log("TIMEOUT %ds %s" % (CHILD_TIMEOUT, os.path.basename(script)))
        except Exception as e:
            log("ERROR %s: %s" % (os.path.basename(script), e))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # 钩子面异常全放行
        log("FATAL %s" % e)
        sys.exit(0)
