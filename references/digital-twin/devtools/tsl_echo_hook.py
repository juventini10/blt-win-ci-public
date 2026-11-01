#!/usr/bin/env python3
# TRUTH_OF: 脚本中心/tsl_echo_hook.py   # 真源声明·派生面须软链指向本件（v1.2.227 副本声明面）
# -*- coding: utf-8 -*-
# version: v1.1 → v1.2 → v1.3（2026-10-09 Qoder CN WB端TSL树时相根治任务卡·六改点⑤）
"""
tsl_echo_hook.py — TSL 树回显钩子（UserPromptSubmit·v1.3）
LRN-20260929-01 根治·闭环末环：
  Stop 钩子 tsl_tree_hook 机械产树至 ~/.workbuddy/tsl_last_tree.md
  → 本钩子（UserPromptSubmit）读树·未消费则 additionalContext 注入 → AI 被迫逐行 relay
  → 写 .consumed 标记（同 stamp 只注入一次）
产出（Stop）与呈现（UserPromptSubmit）均不经 AI 意志。

## v1.2 病根（2026-10-07·你「上岗回复老不按模板」根治·WB 端）

引擎源码实证（`app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs`）：
- `aggregateSettledResults`：`hookSpecificOutput = {...旧, ...新}` → **同 key 覆盖**
- `aggregateSettledResults`：`stdout = 旧 + "\n" + 新` → **拼接共存**
- UPS 消费：有 additionalContext → 覆盖赋值；否则走 stdout 拼接

⇒ **json envelope = 竞争（last wins）；裸文本 = 共存**。
WB 端 UPS 实挂 11 条钩子，多条同发 envelope ⇒ 排前面的注入块**结构性必被覆盖**（童灵块排第 4）。

旧形态另有一层污染：空闲时 `_emit("")   # v1.2：空闲零输出（⛔ 不再吐 `{}` 污染上下文）` 产出 `{}` → 引擎按 stdout 拼接时
**把字面量 `{}` 塞进模型上下文**（每轮一枚·非空上下文噪声）。

v1.2 修法：①输出形态委托 `hook_protocol` 单一真源（WB=text 裸文本）；
②空闲时**零输出**（⛔ 不再吐 `{}`），符合 `emit()` 空 ctx 只留痕不输出的既有语义。

## v1.3（2026-10-09 Qoder CN 任务卡·六改点⑤）：下回合注入语义根治
原 v1.2 把 **tsl_last_tree.md 树全文**注入下回合 → 与 Stop 钩子同 round 踢回路径**重复呈现**，
且树全篇出现在「非被踢回回合」＝违反 §3.9d 呈现点唯一性（树只该出现在被踢回那回合末段）。
v1.3 改：下回合 UPS **不再注入树本体**，仅当「上回合 fire 后仍缺树」（FIRE_STATE 存在且近期）时
注入**一行缺账提醒**（⛔每轮刷屏·提示后即清状态）。树全文唯一出现处＝被 Stop 钩子踢回的那一回合末段。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys as _sys, os as _os; _SCROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))); _SCROOT in _sys.path or _sys.path.insert(1, _SCROOT)  # sc-rootfix-20261014 域搬补路
import os, re, sys, json
from datetime import datetime  # v1.5-c：档位新鲜期判据需要（缺它=NameError被except吞=时间窗静默失效）

# 输出协议单一真源（2026-10-07·与注入钩子家族同源·WB 端必须 text）
_p = os.path.dirname(os.path.abspath(__file__))
if _p not in sys.path:
    sys.path.insert(0, _p)
try:
    import hook_protocol as _hp
except Exception:
    _hp = None


def _emit(ctx):
    """输出协议委托 hook_protocol 单一真源；空闲（空 ctx）零输出。"""
    if not ctx:
        return
    if _hp is not None:
        try:
            _hp.emit(ctx, payload={"hook_event_name": "UserPromptSubmit"},
                     argv=sys.argv[1:], event="UserPromptSubmit",
                     script="tsl_echo_hook.py")
            return
        except Exception:
            pass
    sys.stdout.write(ctx)


# v1.1（2026-09-30 by ZCode·与 tsl_tree_hook v1.2 同轮配对）：跨端适配三改——
#   ① TREE env 化（TSL_TREE_OUT·与 tree_hook 同名 env·ZCode 独立树槽·默认不变=WB 零回归）
#   ② 门控 session_d_tier：stdin UPS payload 的 session_id 过滤台账本会话最新行
#      （根除「全局最新行」跨端/跨会话串台·无 session_id 退全局=向后兼容）
#   ③ 树头 session 比对：树头带 session 且 ≠ 本会话 → 不回显（旧格式树头无 session=跳过比对·兼容）
TREE = os.environ.get("TSL_TREE_OUT") or os.path.join(os.path.expanduser("~"), ".workbuddy", "tsl_last_tree.md")
DONE = TREE + ".consumed"
STATE = os.environ.get("TSL_INJECT_STATE") or os.path.join(os.path.expanduser("~"), ".workbuddy", "doenglingz_inject_state.json")  # env=测试隔离缝（同 tsl_tree_hook v1.2）

# v1.3（2026-10-09）：FIRE_STATE 与 tree_hook 同源共享——记录「上回合是否 fire 后仍缺树」
FIRE_STATE = os.environ.get("TSL_FIRE_STATE") or os.path.join(os.path.expanduser("~"), ".workbuddy", "tsl_tree_fire_state.json")


def _stdin_session_id():
    try:
        if hasattr(sys.stdin, "reconfigure"): sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        d = json.loads(sys.stdin.read() or "{}")
        return d.get("session_id", "") if isinstance(d, dict) else ""
    except Exception:
        return ""


def _fire_state_get():
    try:
        with open(FIRE_STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _fire_state_clear():
    try:
        os.remove(FIRE_STATE)
    except Exception:
        pass


def _fire_recent(fs, window=600):
    if not isinstance(fs, dict):
        return False
    try:
        from datetime import datetime as _dt
        _ts = _dt.strptime(fs.get("ts", ""), "%Y-%m-%d %H:%M:%S")
        return (_dt.now() - _ts).total_seconds() <= window
    except Exception:
        return False


# 取档口径真源=分身/doenglingz_tier_read.py（2026-10-28 方案B）。本处=TSL专用变体：空sid→非D3·60min新鲜窗；与 tier_gate 的「空sid→全局兜底」版语义不同，⛔不可硬并（硬并会改门控语义/碰TSL关键路径）。改取档先改共享件并回归。
def session_d_tier(sid):
    """本会话最新档位——TSL 呈现义务仅 D3（08 §七·06 v1.89 档位门控）。
    sid 为空 → 退全局最新行（旧宿主兼容）；本会话无注入行 → 判非 D3（⛔不退全局·那正是串台源）。"""
    try:
        with open(STATE, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        # v1.5-b（与 tsl_tree_hook 同源·实测补刀）：无 sid 必须在进循环前短路。
        #   循环首句 `if sid and ...` 在 sid 为空时恒假 ⇒ 第一行档位直接返回，
        #   加在循环之后的 return "" 永远走不到。
        if not sid:
            return ""
        for line in reversed(lines):
            d = json.loads(line)
            # 🔴 2026-10-08 空值漏洞根治（与 tsl_tree_hook 同源同修）：
            #   原式第三条件 `d.get("session_id")` 空值时为假 ⇒ 空 sid 行绕过本会话过滤
            #   ⇒ 非 D3 回合被回判 D3（实测本机 161 行空 sid+D3 噪声）。判据**收窄**·⛔非放宽。
            if sid and d.get("session_id") != sid:
                continue
            if d.get("d_tier"):
                # v1.5-c（2026-10-27·与 tsl_tree_hook 同源同修·⛔两边分叉即双本账）：
                #   档位取「该会话历史最新」且无时间窗 ⇒ 会话曾 D3 过后，后续回合全被判 D3。
                #   加 60min 新鲜期：超期视为「本回合无档位证据」。阈值依据见 tree_hook 同段。
                try:
                    _t = datetime.strptime(str(d.get("ts"))[:19], "%Y-%m-%dT%H:%M:%S")
                    if (datetime.now() - _t).total_seconds() > 60 * 60:
                        return ""
                except Exception:
                    pass
                return d.get("d_tier")
        if sid:
            return ""
        # v1.5-b（与 tree_hook 同源）：无 sid 必须在进循环前短路——原式循环首句
        #   `if sid and ...` 在 sid 为空时恒假 ⇒ 第一行档位直接返回，后面的 return '' 走不到。
        return ""
    except Exception:
        pass
    return ""


def main():
    sid = _stdin_session_id()
    if session_d_tier(sid) != "D3":
        _emit("")   # v1.2：空闲零输出（⛔ 不再吐 `{}` 污染上下文）  # ⛔档位门控：仅 D3 回合注入 TSL 树
        return
    # v1.3（2026-10-09 Qoder 任务卡·六改点⑤）：下回合 UPS **不再注入树本体**
    # （§3.9d 呈现点唯一性：树全篇只出现在被 Stop 钩子踹回的那一回合末段）。
    # 仅当「上回合 fire 后仍缺树」（FIRE_STATE 存在·status∈{kicked,missing}·近期）时，
    # 注入**一行缺账提醒**（⛔每轮刷屏：提示后即清状态·下回合不再提示）。
    fs = _fire_state_get()
    if fs.get("status") in ("kicked", "missing") and _fire_recent(fs):
        ctx = ("⚠️ 上回合 D3 上岗回合 TSL 核验树未被 relay——Stop 钩子已机械产出并踢回，但末段仍无树。"
               "本回合末段请原样粘贴 TSL 核验树（⛔省略＝违反义务⑨·relay保真律·童灵在岗契约）。")
        _fire_state_clear()   # 只提示一次·⛔每轮刷屏
        _emit(ctx)
        return
    _emit("")   # v1.2：空闲零输出（⛔ 不再吐 `{}` 污染上下文）


if __name__ == "__main__":
    main()
