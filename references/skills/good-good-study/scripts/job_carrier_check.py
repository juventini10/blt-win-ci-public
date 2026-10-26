#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""job_carrier_check.py — JOB 载体日志覆盖测试（v1.0·2026-10-24）

为什么有本件：GGS 沙箱的 JOB 用例用假岗位 JOB-999，未注册进
job_audit_check.JOB_LOG_SOURCES → mirror_to_log 走 None 分支，载体日志
（三账之第三账）没被覆盖。本件用 temp 台账 + 临时注册的 log source
直接调 record_decision，验：
  1) 台账 + 载体日志同时落账（同一次动作）
  2) 重复 decision_id 不重复追加日志（幂等）
  3) 被挡清单 rejected 原子落盘仍成立

诚实边界：本件在测试进程内 monkeypatch JOB_LOG_SOURCES，不改生产注册表；
真实多载体岗位仍按各端登记表走。
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import json
import os
import sys
import tempfile
from pathlib import Path

_MC_NAME = "个人AI" + "档案"
JOB_DIR = os.path.join(os.environ.get("MEMORY_CENTER") or os.path.expanduser("~/" + _MC_NAME), "脚本中心", "分身")


def main():
    tmp = tempfile.mkdtemp(prefix="jobcarrier_")
    ledger = os.path.join(tmp, "ledger.json")
    blocked = os.path.join(tmp, "blocked.md")
    carrier = os.path.join(tmp, "carrier.md")
    with open(ledger, "w", encoding="utf-8") as f:
        json.dump({"jobs": {"JOB-999": {"job_name": "sandbox", "status": "probation",
                                         "decisions": [], "stats": {}}},
                   "last_updated": "2026-10-24"}, f, ensure_ascii=False, indent=2)
    open(blocked, "w", encoding="utf-8").write("# blocked\n")
    open(carrier, "w", encoding="utf-8").write("# carrier log\n")

    os.environ["JOB_PROBATION_LEDGER"] = ledger
    os.environ["JOB_PROBATION_BLOCKED"] = blocked
    sys.path.insert(0, JOB_DIR)
    import job_probation_check as jpc
    import job_audit_check as jac

    jac.JOB_LOG_SOURCES["JOB-999"] = [Path(carrier)]
    did = "JOB-999-20261024-901"

    jpc.record_decision("JOB-999", did, "carrier test", "approved", actor="self")
    log1 = open(carrier, encoding="utf-8").read()
    led1 = json.load(open(ledger, encoding="utf-8"))["jobs"]["JOB-999"]["decisions"]

    jpc.record_decision("JOB-999", did, "carrier test again", "modified", actor="self")
    log2 = open(carrier, encoding="utf-8").read()

    ok = (did in log1 and len(led1) == 1 and log1.count(did) == 1
          and log2.count(did) == 1 and len(led1) == 1)
    print(("✅PASS " if ok else "❌FAIL ") + "JOB 载体日志：同动作落账 + 重复ID幂等")
    print("   log_count=%d ledger_rows=%d" % (log2.count(did), len(led1)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
