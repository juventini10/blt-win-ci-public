#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook_parity_audit.py —— 端内钩子与真源的同名分叉对账哨兵（只读检测·不覆盖任何文件）

为什么存在（2026-10-12 实证）：`~/.qoder-cn/hooks/` 与 `[记忆共享中心]/脚本中心/` 同名 .py 共 18 件，
其中 **11 件双向分叉**（两侧各有独有行），且其中 10 件正被 settings.json 直接当运行体调用。
这不是"忘了投影"（纯滞后件实测=0），是"两份实现各自演化"——任何单向覆盖都会丢行。
只要"同名两份"这个前提还在，每改一侧就再漂一次；本件把这件事从"没人知道"变成"每轮显形"，
与 harness_selfcheck.py 的 B 检查（真相源唯一性·禁裸副本）同族，只是补上 hooks 域这块空白。

四态判据（归一后比行：去空行、去纯注释行、逐行 strip）：
  PARITY   两侧行集相同（仅剩注释/空行差）  → ✅
  LAG      端独有=0、真源有新增            → 🔴 纯滞后（可安全同步：真源→端）
  AHEAD    真源独有=0、端有新增            → 🔴 端跑在前（应回流真源）
  DIVERGED 两侧各有独有行                  → 需归属登记；未登记=🔴
  ORPHAN   只在一侧存在                    → 不在本哨兵管辖内（仅报数）

归属登记（同目录 `hook_parity_registry.json`）降红条件＝四件齐 **且已定权**：
  authority（谁是权威文件）+ reason（为何分叉/为何不合并）+ verify_cmd（怎么复算）+ disposition
  disposition ∈ {merged, fork-owned} → 已定权，降为 ⚪
  disposition = pending-merge（或无此字段）→ **保持 🔴**——登记≠处置，写三行话不能把红洗白
缺任一件保持 🔴 —— "已挂账"不能靠一句话换豁免，那是判据自我豁免通道（2026-10-12 实证）。

用法：
    python3 hook_parity_audit.py                # 对账（exit 1=有未归属红灯）
    python3 hook_parity_audit.py --json         # 机器可读输出（供巡检/守卫消费）
    python3 hook_parity_audit.py --self-test    # 夹具自证：含"必须能红"的负例，防判据恒真

退出码：0=无未归属红灯 / 1=有 / 2=环境或用法异常
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse, json, os, re, sys, tempfile

H = os.path.expanduser("~")
END_HOOKS = os.path.join(H, ".qoder-cn", "hooks")
SRC_ROOT = os.path.join(H, "[记忆共享中心]", "开发工具")
REGISTRY = os.path.join(SRC_ROOT, "hook_parity_registry.json")
SETTINGS = os.path.join(H, ".qoder-cn", "settings.json")
PY_NAME = re.compile(r"([A-Za-z0-9_.\-]+\.py)")


def norm_lines(path):
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return None
    return [l.strip() for l in raw.splitlines() if l.strip() and not l.strip().startswith("#")]


# v1.1(2026-10-22·Qoder CN·皮叔令「拉清单」根治轮):对账对象纠错——原SRC_ROOT直寻开发工具,
#   walk 会先撞 blt-win-ci-workspace/public **构建产物**(deident+relocate+build链注入行·非真源),
#   拿构建件比端活文件→脱敏引用/路径占位/注入行全算"分叉"→6件红灯皆伪警(实证2026-10-22:
#   6件逐一diff 5件纯构建噪声+route_unknown_unknown"独有函数"实为三处皆有·唯构建快照没有)。
#   真源面=脚本中心(守卫/root/Skill路由引擎/scripts)+开发工具(⛔排除构建工作区)。
BUILD_COPY = ("blt-win-ci-workspace", "blt-win-ci-public", "记忆琥珀", "__pycache__")

def find_src(name, src_root=SRC_ROOT):
    roots = [src_root,
             os.path.join(H, "[记忆共享中心]", "脚本中心", "守卫"),
             os.path.join(H, "[记忆共享中心]", "脚本中心", "Skill路由引擎", "scripts"),
             os.path.join(H, "[记忆共享中心]", "脚本中心")]
    for root in roots:
        direct = os.path.join(root, name)
        if os.path.exists(direct) and not any(b in direct for b in BUILD_COPY):
            return direct
        for r, _, fs in os.walk(root):
            if any(b in r for b in BUILD_COPY):
                continue
            if name in fs:
                return os.path.join(r, name)
    return None


def live_refs():
    """settings.json 里被直接当运行体调用的端内钩子文件名集合。"""
    out = set()
    try:
        blob = json.dumps(json.load(open(SETTINGS, encoding="utf-8")), ensure_ascii=False)
    except Exception:
        return out
    for p in PY_NAME.findall(blob):
        if os.path.exists(os.path.join(END_HOOKS, p)):
            out.add(p)
    return out


def classify(end_path, src_path):
    a, b = norm_lines(end_path), norm_lines(src_path)
    if a is None or b is None:
        return "ORPHAN", 0, 0
    sa, sb = set(a), set(b)
    only_end, only_src = len(sa - sb), len(sb - sa)
    if only_end == 0 and only_src == 0:
        return "PARITY", 0, 0
    if only_end == 0:
        return "LAG", only_end, only_src
    if only_src == 0:
        return "AHEAD", only_end, only_src
    return "DIVERGED", only_end, only_src


def registry(path=REGISTRY):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


CLOSED_DISPOSITION = ("merged", "fork-owned")   # 只有已定权的才允许降红；pending-merge 保持红


def owned(rec):
    """四件齐且 disposition 已定权才算已归属——防"写条登记就把红洗成⚪"。"""
    if not isinstance(rec, dict):
        return False
    if str(rec.get("disposition") or "").strip() not in CLOSED_DISPOSITION:
        return False
    return all(str(rec.get(k) or "").strip() for k in ("authority", "reason", "verify_cmd"))


def scan(end_hooks=END_HOOKS, src_root=SRC_ROOT, reg=None):
    reg = registry() if reg is None else reg
    rows = []
    if not os.path.isdir(end_hooks):
        return None
    for name in sorted(os.listdir(end_hooks)):
        if not name.endswith(".py"):
            continue
        sp = find_src(name, src_root)
        if sp is None:
            continue
        st, oe, osrc = classify(os.path.join(end_hooks, name), sp)
        rows.append({"name": name, "state": st, "end_only": oe, "src_only": osrc,
                     "end": os.path.join(end_hooks, name), "src": sp,
                     "registered": owned(reg.get(name)), "reg": reg.get(name)})
    return rows


def check(end_hooks=END_HOOKS, src_root=SRC_ROOT, reg=None, verbose=True, live=None, quiet_states=("PARITY",)):
    live = live_refs() if live is None else live
    rows = scan(end_hooks, src_root, reg)
    if rows is None:
        sys.stderr.write("环境异常：端内钩子目录不存在 %s\n" % end_hooks)
        return 2, []
    reds, counts = [], {}
    if verbose:
        print("📐 端内钩子 × 真源 同名分叉对账（只读·不覆盖任何文件）")
        print("   端目录 %s ｜ 真源 %s" % (end_hooks.replace(H, "~"), src_root.replace(H, "~")))
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
        if r["state"] in quiet_states:
            continue
        if r["registered"]:
            mark = "⚪已归属"
        elif r["state"] == "ORPHAN":
            mark = "ℹ️"
        else:
            mark = "🔴"
            reds.append(r)
        if verbose:
            extra = " ⚠️正被调用" if r["name"] in live else "（死副本）"
            print("   %s %-34s %-9s 端独有%-4d 源独有%-4d%s" % (mark, r["name"], r["state"],
                                                                  r["end_only"], r["src_only"], extra))
    if verbose:
        print("   汇总：%s" % counts)
        print("   未归属红灯 %d 件%s" % (len(reds), "（降红需四件齐且已定权：authority+reason+verify_cmd+disposition∈{merged,fork-owned}）" if reds else ""))
    return (1 if reds else 0), reds


def self_test():
    """夹具：正例判绿 + 三种必须能红（未登记分叉/纯滞后/登记缺件）+ 三件齐降红。"""
    ok = fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if cond:
            ok += 1
        else:
            fail += 1

    tmp = tempfile.mkdtemp(prefix="hookparity_")
    end, src = os.path.join(tmp, "hooks"), os.path.join(tmp, "devtools")
    os.makedirs(end); os.makedirs(src)
    open(os.path.join(src, "a_guard.py"), "w").write("x = 1\ny = 2\nz = 3\n")
    open(os.path.join(end, "a_guard.py"), "w").write("x = 1\nEND_ONLY = 9\n")            # DIVERGED
    open(os.path.join(src, "b_guard.py"), "w").write("p = 1\nq = 2\n")
    open(os.path.join(end, "b_guard.py"), "w").write("p = 1\n")                          # LAG
    open(os.path.join(src, "c_guard.py"), "w").write("k = 1\n")
    open(os.path.join(end, "c_guard.py"), "w").write("k = 1\n# 注释差而已\n")             # PARITY
    rc, reds = check(end, src, reg={}, verbose=False, live=set())
    got = {r["name"] for r in reds}
    chk("T1 分叉+滞后未登记 → 必红", rc == 1 and {"a_guard.py", "b_guard.py"} <= got)
    chk("T2 同源件不误报（防过度报警）", "c_guard.py" not in got)
    rc2, reds2 = check(end, src, reg={"a_guard.py": {"authority": "x"}}, verbose=False, live=set())
    chk("T3 登记缺 reason/verify_cmd → 仍必红（一句话不算豁免）",
        rc2 == 1 and "a_guard.py" in {r["name"] for r in reds2})
    full = {"a_guard.py": {"authority": src + "/a_guard.py", "reason": "端适配增量·已实测双向差异",
                           "verify_cmd": "python3 hook_parity_audit.py --json"}}
    rc3, reds3 = check(end, src, reg=full, verbose=False, live=set())
    chk("T4 三件齐但无 disposition（未定权）→ 仍必红（登记≠处置）",
        rc3 == 1 and "a_guard.py" in {r["name"] for r in reds3})
    closed = {"a_guard.py": {**full["a_guard.py"], "disposition": "fork-owned"},
              "b_guard.py": {"authority": src + "/b_guard.py", "reason": "纯滞后已同步真源→端",
                              "verify_cmd": "python3 hook_parity_audit.py", "disposition": "merged"}}
    rc4, reds4 = check(end, src, reg=closed, verbose=False, live=set())
    chk("T5 四件齐且已定权 → 降为已归属·rc 转绿",
        rc4 == 0 and not reds4)
    pend = {"a_guard.py": {**full["a_guard.py"], "disposition": "pending-merge"}}
    rc5, reds5 = check(end, src, reg=pend, verbose=False, live=set())
    chk("T6 pending-merge 即使写满三件 → 仍必红（待合并不是已处置）",
        "a_guard.py" in {r["name"] for r in reds5})
    rows = scan(end, src, reg={})
    states = {r["state"] for r in rows}
    chk("T7 夹具有牙：分叉/滞后/同源三态确实被区分（否则本哨兵恒真）",
        {"DIVERGED", "LAG", "PARITY"} <= states)
    print("自测结果：%d 通过 / %d 失败" % (ok, fail))
    return 0 if fail == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="端内钩子与真源同名分叉对账（只读·不覆盖）")
    ap.add_argument("--self-test", action="store_true", help="夹具自证（含必须能红的负例）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    rc, reds = check(verbose=not a.json)
    if a.json:
        print(json.dumps({"rc": rc, "red": [{k: r[k] for k in ("name", "state", "end_only", "src_only")}
                                             for r in reds]}, ensure_ascii=False, indent=1))
    sys.exit(rc)


if __name__ == "__main__":
    main()
