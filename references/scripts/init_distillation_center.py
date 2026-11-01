#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒸馏中心初始化脚本（共享·单一来源）

用途：新用户首次使用时，自动创建含表头的空蒸馏中心文件。
调用方：system-logger D4 / daily-buddy 月报第7步 / growth-box C6
设计依据：Skill架构规范 §1.1 防误层（用设计消除错误，不用检测捕获错误）
         指令编写规范 §5.7 产出物锁（把"检查"升级为"物理阻止"）
         多端共享核心文件写入门禁必须模式级（三个Skill统一调用，不各自为政）

Exit code语义：
  0 = 初始化成功（文件不存在，已创建）
  1 = 初始化失败（目录不可写/写入失败）
  2 = 文件已存在，跳过初始化（幂等）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass

import os
import sys
from datetime import datetime

DISTILLATION_CENTER_PATH = os.path.expanduser("[记忆共享中心]/记忆蒸馏/蒸馏中心.md")
DISTILLATION_DIR = os.path.dirname(DISTILLATION_CENTER_PATH)

TEMPLATE = """# 蒸馏中心

> 三套蒸馏系统的统一执行追踪索引。
> 不替代任何已有蒸馏文件，只记录"什么时候蒸馏了什么"。
> 每次蒸馏执行完成后，对应的 Skill 追加一条记录。

---

## 维护规则

1. 本文件由三个源头追加写入（各管一行）：
   - **系统日志蒸馏** → 写入 `📊 系统日志蒸馏` 行；并额外在月段内追加 `### 🔔 工作模式信号（YYYY-MM）` 子节（D2.5 产物·供 daily-buddy 月报 PULL）
   - **每日伙伴 · 日记月报** → 写入 `📓 日记月报` 行
   - **成长箱蒸馏**（别名：成长箱月度蒸馏·v1.1命名修正：成长箱是双向成长，"错误蒸馏"只覆盖负面）→ 写入 `🧠 成长箱蒸馏` 行（审查P2-3对齐：growth-box C6 写入串/终检串/存量数据三方均为"成长箱蒸馏"——模板原"成长箱月度蒸馏"与子串匹配冲突，统一到写入方权威·呈你追认）
2. 每行格式：`| 日期 | 类型 | ✅/❌ | 一句话摘要 | 下次执行日期 |`
3. 本文件每 30 天无更新 → TTL注册表亮🔴
4. 历史记录保留，不删不减
5. **工作模式信号子节格式**（系统日志蒸馏附加产出）：`### 🔔 工作模式信号（YYYY-MM）` + 固定 Schema 表（信号 | 可观测证据 | 路由目标 | 关联维度），仅含可观测事实、不含对你的评价；详见 system-logger `references/monthly-distillation.md` D2.5 / D4。daily-buddy 月报第1.1步 PULL 解析此子节并按路由并入评估维度。
6. 自定义蒸馏类型（如「📅 周蒸馏」）合法：行格式同规则2；「下次执行日期」填 YYYY-MM-DD 即纳入 awaken 巡检三级到期检测（周蒸馏建议节律=完成日+7天）；填文字或 — 则该行不参与检测（v1.2·WB反哺 FB-20260924-005 收口）

---

版本：v1.2 | 创建日期：{create_date} | 初始化方式：init_distillation_center.py 自动创建
"""


def main():
    # 检查文件是否已存在
    if os.path.exists(DISTILLATION_CENTER_PATH):
        print(f"[SKIP] 蒸馏中心已存在：{DISTILLATION_CENTER_PATH}")
        print(f"[EXIT] exit code 2 = 文件已存在，跳过初始化（幂等）")
        sys.exit(2)

    # 检查目录是否存在，不存在则创建
    if not os.path.exists(DISTILLATION_DIR):
        try:
            os.makedirs(DISTILLATION_DIR, exist_ok=True)
            print(f"[INFO] 已创建目录：{DISTILLATION_DIR}")
        except Exception as e:
            print(f"[FAIL] 创建目录失败：{DISTILLATION_DIR}，错误：{e}")
            print(f"[EXIT] exit code 1 = 初始化失败")
            sys.exit(1)

    # 创建含表头的空文件
    try:
        create_date = datetime.now().strftime("%Y-%m-%d")
        content = TEMPLATE.format(create_date=create_date)
        with open(DISTILLATION_CENTER_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] 蒸馏中心已初始化：{DISTILLATION_CENTER_PATH}")
        print(f"[INFO] 创建日期：{create_date}")
        print(f"[INFO] 模板版本：v1.1（含维护规则+命名修正）")
        print(f"[EXIT] exit code 0 = 初始化成功")
        sys.exit(0)
    except Exception as e:
        print(f"[FAIL] 写入文件失败：{DISTILLATION_CENTER_PATH}，错误：{e}")
        print(f"[EXIT] exit code 1 = 初始化失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
