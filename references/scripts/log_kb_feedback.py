#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_kb_feedback.py — 检索自进化 P0：召回质量反馈通道（feedback_log.jsonl 追加器）

用法:
  python3 log_kb_feedback.py "<task>" "<结果路径或标题>" "<反馈类型>" "[补充词,逗号分隔]"
  反馈类型: 这条没用 | 漏了X | 采纳
示例:
  python3 log_kb_feedback.py "写视频文案" "读书笔记/精力管理.md" "这条没用" ""
  python3 log_kb_feedback.py "写视频文案" "" "漏了X" "借势,主角"

设计: O_APPEND 内核原子追加（单 write ≤ PIPE_BUF，无 read-modify-write），与 memlog 同款并发安全。
      ⛔ 只追加不覆写；隔离验证用环境变量 KB_FEEDBACK_LOG 重定向到 /tmp。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys, os, json
from datetime import datetime

LOG = os.environ.get("KB_FEEDBACK_LOG",
                     os.path.expanduser("[记忆共享中心]/脚本中心/知识联邦引擎/logs/feedback_log.jsonl"))
FEEDBACK_TYPES = {"这条没用", "漏了X", "采纳"}


def main():
    if len(sys.argv) < 4:
        print("用法: log_kb_feedback.py <task> <结果路径> <反馈类型:这条没用|漏了X|采纳> [补充词,逗号分隔]")
        return 1
    task, result, ftype = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4].strip() else []
    if ftype not in FEEDBACK_TYPES:
        print(f"⚠️ 反馈类型须 ∈ {sorted(FEEDBACK_TYPES)}，收到: {ftype}")
        return 2
    rec = {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task,
        "result": result,
        "type": ftype,
        "extra_terms": [t.strip() for t in extra if t.strip()],
    }
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:  # O_APPEND 原子追加
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"✅ feedback 已记录 → {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
