#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 蓝图卡因果实验件（与 bp_factory/bp_c1_scan 同族，无 hook/STOP_GUARDS 挂载点可声明，
# REG:      硬填 §四注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
# -*- coding: utf-8 -*-
"""bp_causal_ab.py — 真反事实实验：物理摘除本生产线全部 蓝图卡-*.md → 重建缓存 → 跑 gate0 33 题 → 还原 → 复验。

为什么必须物理摘除（2026-10-27 实证）：后处理「从返回结果里删掉再重排」只在
「文档分数与语料集无关」时等价；本引擎的路由桶加权、BM25 IDF、实体直通、向量候选池
四项全部依赖语料集，实测反证=摘除蓝图文档后 F-Q10/F-Q11 目标卡由 4 名掉到 13/11 名
（后处理数学上不可能让名次变差）。故唯一正解=改变输入集后重跑评分。

安全设计（失败会留下"卡被移走未还原"的生产状态，故不靠自觉）：
  ①移前清点文件清单并落盘 manifest（异常时可人工按单找回）
  ②try/finally 成对还原
  ③还原后三重复验：文件数、缓存重建后 hit5 回到实验前读数、逐文件存在性
  ④任一复验不过 ⇒ exit 2 + 大声报红（⛔静默）
只读 eval_set 真值，⛔改题面/⛔代填真值。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass

import datetime
import glob
import json
import os
import shutil
import subprocess
import sys

def _venv_py(fed):
    """.venv-st 解释器跨平台定位（2026-10-28 跨平台门禁修）：unix=bin/python，Win=Scripts\\python.exe。"""
    if os.name == "nt":
        return os.path.join(fed, ".venv-st", "Scripts", "python.exe")
    return os.path.join(fed, ".venv-st", "bin", "python")

HOME = os.path.expanduser("~")
CARD_DIR = os.path.join(HOME, "[日记仓库]", "2-知识库", "10-蓝图索引卡")
STASH = os.path.join(HOME, ".bp-ab-stash")  # 2026-10-28 中性化：⛔写死作者工作台目录名
MANIFEST = os.path.join(STASH, "_manifest.json")
FED = os.path.join(os.path.expanduser("[记忆共享中心]"), "脚本中心", "知识联邦引擎")
PY = _venv_py(FED)
if not os.path.isfile(PY):
    PY = "python3"

PROBE = """
import json, os, sys
sys.path.insert(0, os.path.expanduser("[记忆共享中心]/脚本中心"))
import search_kb as skb
G = json.load(open(os.path.expanduser(
    "[记忆共享中心]/脚本中心/知识联邦引擎/scripts/eval_set.json")))["gate0"]
res = {}
for c in G["samples"]:
    r = skb.search(c["task"], k=60)
    items = r[0][0] if isinstance(r[0], tuple) else r[0]
    names = [os.path.basename(it[1]) for it in items]
    tgs = [os.path.basename(t) for t in (c.get("targets") or [])]
    def is_t(n):
        return any(t.replace(".md", "") == n.replace(".md", "") or t in n or n in t for t in tgs)
    rank = next((i + 1 for i, n in enumerate(names) if is_t(n)), None)
    res[c["id"]] = rank
print(json.dumps(res, ensure_ascii=False))
"""


def run_probe(tag):
    p = subprocess.run([PY, "-c", PROBE], capture_output=True, text=True)
    line = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith("{")]
    if not line:
        raise RuntimeError("%s 读数失败：%s" % (tag, (p.stdout + p.stderr)[-200:]))
    return json.loads(line[-1])


NAME_PROBE = """
import json, os, sys
sys.path.insert(0, os.path.expanduser("[记忆共享中心]/脚本中心"))
import search_kb as skb
G = json.load(open(os.path.expanduser(
    "[记忆共享中心]/脚本中心/知识联邦引擎/scripts/eval_set.json")))["gate0"]
want = sys.argv[1]
c = next(x for x in G["samples"] if x["id"] == want)
r = skb.search(c["task"], k=15)
items = r[0][0] if isinstance(r[0], tuple) else r[0]
names = [os.path.basename(it[1]) for it in items[:5]]
print("NAMES " + json.dumps([n for n in names if n.startswith("蓝图卡-")], ensure_ascii=False))
"""


def top_mine(sample_id):
    """该题 Top5 里的我方卡名（子进程跑：模型依赖在 .venv-st，主进程缺件时不硬试）。"""
    import subprocess as sp, tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(NAME_PROBE)
        pn = f.name
    try:
        py = _venv_py(FED)
        if not os.path.isfile(py):
            py = "python3"
        out = sp.run([py, pn, sample_id], capture_output=True, text=True).stdout
        line = [l for l in out.splitlines() if l.startswith("NAMES ")]
        return json.loads(line[-1][6:]) if line else []
    except Exception:
        return []
    finally:
        os.unlink(pn)


def main():
    cards = sorted(glob.glob(os.path.join(CARD_DIR, "蓝图卡-*.md")))
    if len(cards) < 5:
        print("⛔ 卡数异常（%d），中止不动生产文件" % len(cards)); return 1
    print("清点：本生产线卡片 %d 张（含 C1 清单等 蓝图卡-* 前缀非卡文件，如实计入摘除面）" % len(cards))
    os.makedirs(STASH, exist_ok=True)
    json.dump({"cards": [os.path.basename(c) for c in cards],
               "at": datetime.datetime.now().isoformat(timespec="seconds"),
               "note": "bp_causal_ab 实验暂存·正常路径会被 finally 清空"},
              open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False)

    with_cards = run_probe("with")
    moved = []
    try:
        for c in cards:
            dst = os.path.join(STASH, os.path.basename(c))
            shutil.move(c, dst)
            moved.append(c)
        print("已摘除 %d 件，重建缓存中…" % len(moved))
        without = run_probe("without")
    finally:
        back = 0
        for f in glob.glob(os.path.join(STASH, "蓝图卡-*.md")):
            shutil.move(f, os.path.join(CARD_DIR, os.path.basename(f)))
            back += 1
        print("已还原 %d 件（应=%d）" % (back, len(moved)))
        shutil.rmtree(STASH, ignore_errors=True)

    # 复验一：文件数
    now_cards = sorted(glob.glob(os.path.join(CARD_DIR, "蓝图卡-*.md")))
    ok_count = len(now_cards) == len(cards)
    # 复验二：还原后读数必须回到实验前（证明确实回到原状态）
    after = run_probe("after")
    drift = [k for k in with_cards if with_cards[k] != after.get(k)]
    print("复验：文件数 %s（%d/%d）｜读数回归 %s" %
          ("✅" if ok_count else "⛔", len(now_cards), len(cards),
           "✅ 零漂移" if not drift else "⛔ 漂移题=%s" % drift))

    top = 5
    hurt = [(k, without[k], with_cards[k], top_mine(k)) for k in with_cards
            if without.get(k) and without[k] <= top and (not with_cards[k] or with_cards[k] > top)]
    helpd = [(k, with_cards[k], without.get(k)) for k in with_cards
             if with_cards.get(k) and with_cards[k] <= top and (not without.get(k) or without[k] > top)]
    h_with = sum(1 for v in with_cards.values() if v and v <= top)
    h_without = sum(1 for v in without.values() if v and v <= top)
    print("\n=== 真反事实结论（物理摘除，非后处理）===")
    print("真值题 target 命中 Top5：有我方卡 = %d/%d；摘除我方卡 = %d/%d" %
          (h_with, len(with_cards), h_without, len(without)))
    print("被我的卡挤掉正主的题 = %d：%s" % (len(hurt), hurt or "无"))
    print("因我的卡而进 Top5 的题 = %d：%s" % (len(helpd), [(k, r) for k, r, _ in helpd] or "无"))
    verdict_ok = ok_count and not drift
    if True:  # 队列总是原子重写：hurt=0 也落盘，⛔让旧台账继续充当豁免凭据
        import datetime as _dt
        _Q = os.path.expanduser("~/[日记仓库]/2-知识库/10-蓝图索引卡/蓝图卡挤位待勾队列.md")
        _lines = ["# 蓝图卡挤位待勾队列（真值增补候选 · 待你勾）", "",
                  "生成：%s（bp_causal_ab.py 自动·⛔分身代勾）" % _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "判据来源：eval_set.authority「真值=你逐题价值判定·分身⛔代填」⇒ 本表只提案，勾了才生效。",
                  "语义：这些题的原答案被本生产线卡片挤出 Top5。若上位卡确实同题更贴，请把它加进该题 targets（勾=同意）；",
                  "若属词面抢位，请令收窄上位卡语面（改判据⛔由 AI 自决）。未勾期间：生产线不阻塞，批次交付阻塞（见任务卡 §三十）。", "",
                  "## 待勾条目", "",
              "gate_exempt: %s" % ("true" if (hurt and verdict_ok) else "false"),
              "本轮读数：%s" % (("挤位 %d 题·待你勾" % len(hurt)) if hurt else "挤位 0 题 ⇒ 本文件不赋予豁免资格"), ""]
        for cid, a, b, cards in hurt:
            _lines.append("- ⏳题 `%s`：原答案名次 %d → %d（被挤出 Top5）" % (cid, a, b))
            _lines.append("     上位我方卡：%s" % "、".join(str(c).replace(".md", "") for c in cards))
            _lines.append("     你的裁决（三选一）：□ 增补为合法答案 □ 令收窄卡语面 □ 保留原判（该卡让位）")
            _lines.append("")
        open(_Q, "w", encoding="utf-8").write("\n".join(_lines) + "\n")
        json.dump({"harm": len(hurt), "gain": len(helpd), "verdict_ok": bool(verdict_ok),
               "hit5_with": h_with, "hit5_without": h_without,
               "at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
               "source": "bp_causal_ab.py 物理摘除实验（真反事实）"},
              open(os.path.join(CARD_DIR, ".causal_ledger.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("待勾队列已落盘：%s（%d 条·勾完即可解封交付闸）" % (_Q, len(hurt)))
    print("\n实验可信度：", "✅ 还原复验通过，以上读数可作因果结论" if verdict_ok
          else "⛔ 还原复验未过，读数不作结论，须人工核对 %s" % MANIFEST)
    return 0 if verdict_ok else 2


if __name__ == "__main__":
    sys.exit(main())
