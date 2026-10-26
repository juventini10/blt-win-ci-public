#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""judgment_arbiter.py — GGS 双审裁决器（v1.0·2026-10-24）

为什么有本件：GGS v1.2.5 规定「双审任一项不一致→转用户确认」，但这条
仍靠执行者自觉比对。本件把两份盲审记录做机械裁决：
  1) 强制三项留痕（红线前置 / 四维同异 / 判定），缺项→转用户确认
  2) 两审前置或四维任一项不一致→转用户确认（⛔不自动融合）
  3) 两审一致时，按字段重算判定；重算与盲审判定不符→转用户确认
  4) 全部一致且自洽→输出该判定

诚实边界：本件不判“四维同异填得对不对”，只判两份记录是否一致/自洽；
语义判断仍由盲审承担。输入是 JSON 记录（见 --self-test 夹具）。

用法：
  python3 judgment_arbiter.py --a a.json --b b.json
  python3 judgment_arbiter.py --self-test
退出码：0=已裁决（含转用户确认）｜1=输入/格式错误
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import json
import sys

PRE_KEYS = ("topic_relevant", "complex_task")
DIM_KEYS = ("topic", "conclusion", "evidence", "toolbox")
DECISIONS = ("keep", "merge", "block", "user_confirm")


def _valid(r):
    if not isinstance(r, dict):
        return False, "不是对象"
    for k in ("candidate", "reviewer", "pre", "dims", "decision"):
        if k not in r:
            return False, "缺字段 %s" % k
    if not isinstance(r["pre"], dict) or not isinstance(r["dims"], dict):
        return False, "pre/dims 不是对象"
    for k in PRE_KEYS:
        if not isinstance(r["pre"].get(k), bool):
            return False, "pre.%s 非布尔" % k
    for k in DIM_KEYS:
        if r["dims"].get(k) not in ("same", "different"):
            return False, "dims.%s 非 same/different" % k
    if r["decision"] not in DECISIONS:
        return False, "decision 非法"
    return True, ""


def _derive(r):
    """按字段重算判定（不信任盲审标签）。"""
    if r["decision"] == "block":
        return "block"
    if r["pre"]["topic_relevant"] and r["pre"]["complex_task"] and r["dims"]["toolbox"] == "different":
        return "keep"
    n = sum(1 for k in DIM_KEYS if r["dims"][k] == "same")
    if n >= 3:
        return "merge"
    if n == 2:
        return "user_confirm"
    return "keep"


def arbitrate(a, b):
    for name, r in (("A", a), ("B", b)):
        ok, why = _valid(r)
        if not ok:
            return "user_confirm", "%s 记录不合格：%s → 转用户确认" % (name, why)
    if a["candidate"] != b["candidate"]:
        return "user_confirm", "两份记录候选不同（%s vs %s）→ 转用户确认" % (a["candidate"], b["candidate"])

    diffs = []
    for k in PRE_KEYS:
        if a["pre"][k] != b["pre"][k]:
            diffs.append("前置:%s" % k)
    for k in DIM_KEYS:
        if a["dims"][k] != b["dims"][k]:
            diffs.append("四维:%s" % k)
    if diffs:
        return "user_confirm", "双审不一致（%s）→ 转用户确认，⛔不自动融合" % "、".join(diffs)

    da, db = _derive(a), _derive(b)
    if da != db:
        return "user_confirm", "字段重算不一致（A=%s / B=%s）→ 转用户确认" % (da, db)
    if a["decision"] != da or b["decision"] != da:
        return "user_confirm", "盲审判定与字段重算不符（A=%s/B=%s/重算=%s）→ 转用户确认" % (
            a["decision"], b["decision"], da)
    return da, "双审一致且自洽 → %s" % da


def _fixture(candidate, reviewer, tr, ct, dims, decision):
    return {"candidate": candidate, "reviewer": reviewer,
            "pre": {"topic_relevant": tr, "complex_task": ct},
            "dims": dict(zip(DIM_KEYS, dims)), "decision": decision}


def self_test():
    cases = []
    # C1：两审一致，四维全异 → keep
    c1 = dict(tr=True, ct=False, dims=("different",) * 4, decision="keep")
    cases.append(("C1 双审一致 keep", arbitrate(_fixture("C1", "A", **c1), _fixture("C1", "B", **c1)), "keep"))
    # C2：两审一致，四维全同 → merge
    c2 = dict(tr=True, ct=False, dims=("same",) * 4, decision="merge")
    cases.append(("C2 双审一致 merge", arbitrate(_fixture("C2", "A", **c2), _fixture("C2", "B", **c2)), "merge"))
    # C3：两审一致 block
    c3 = dict(tr=False, ct=False, dims=("different",) * 4, decision="block")
    cases.append(("C3 双审一致 block", arbitrate(_fixture("C3", "A", **c3), _fixture("C3", "B", **c3)), "block"))
    # C4：真实分歧（A 保留 / B 融合）→ user_confirm
    a = _fixture("C4", "A", True, True, ("same", "same", "different", "different"), "keep")
    b = _fixture("C4", "B", True, False, ("same", "same", "same", "different"), "merge")
    cases.append(("C4 真实分歧→用户确认", arbitrate(a, b), "user_confirm"))
    # 缺留痕 → user_confirm
    bad = _fixture("C5", "A", True, True, ("same",) * 4, "merge")
    bad.pop("pre")
    cases.append(("缺留痕→用户确认", arbitrate(bad, _fixture("C5", "B", True, True, ("same",) * 4, "merge")), "user_confirm"))
    # 判定与字段不符 → user_confirm（四维全同却写 keep）
    wrong = _fixture("C6", "A", True, False, ("same",) * 4, "keep")
    cases.append(("判定与字段不符→用户确认", arbitrate(wrong, _fixture("C6", "B", True, False, ("same",) * 4, "keep")), "user_confirm"))

    ok = True
    for name, (got, why), want in cases:
        passed = got == want
        print(("✅PASS " if passed else "❌FAIL ") + name + " → %s（%s）" % (got, why))
        ok &= passed
    print("✅✅ 双审裁决器全过（%d 组）" % len(cases) if ok else "❌ 双审裁决器有失败")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if "--self-test" in a:
        return self_test()
    if "--a" not in a or "--b" not in a:
        print("用法: judgment_arbiter.py --a a.json --b b.json | --self-test", file=sys.stderr)
        return 1
    try:
        pa, pb = a[a.index("--a") + 1], a[a.index("--b") + 1]
        ra = json.load(open(pa, encoding="utf-8"))
        rb = json.load(open(pb, encoding="utf-8"))
    except Exception as e:
        print("❌ 读取失败：%s" % e, file=sys.stderr)
        return 1
    got, why = arbitrate(ra, rb)
    print("裁决：%s" % got)
    print("依据：%s" % why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
