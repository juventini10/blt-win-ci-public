#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 蓝图卡出厂编排件（与 note_validator/bp_quote_verify 同族，无 hook/STOP_GUARDS 挂载点可声明，
# REG:      硬填 §四注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
"""
bp_factory.py — 蓝图卡出厂流水线（一条命令跑完六闸 + 覆盖度台账 + 号段预留）

为什么存在（2026-10-27 批次1/2A 实证）：出厂原本要手工跑 5 条命令（lint→引文真值→向量增量→
serve 重启→真尺 selfcheck），我手工跑时真漏过两次（漏跑向量增量→新卡语义层不可达；漏补 CHANGELOG）。
能规则化的交脚本，需判断的交模型。

用法：
  python3 bp_factory.py                       # 只跑静态三闸（lint/真值/覆盖度）——最快
  python3 bp_factory.py --ship                # 全闸：静态 + 向量增量 + kb_serve 重启 + 真尺 + 去重门
  python3 bp_factory.py --reserve 20          # 申请 20 个连续 BC 号（写台账·多窗口并行不撞号）
  python3 bp_factory.py --coverage-only       # 只看覆盖度与分母口径
退出码：0=全绿；1=有红或用法错（--ship 时任一闸红即 1）。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from note_validator import parse_frontmatter  # 同源，⛔不重写解析器
from bp_quote_verify import verify_card

def _venv_py(fed):
    """.venv-st 解释器跨平台定位（2026-10-28 跨平台门禁修）：unix=bin/python，Win=Scripts\\python.exe。"""
    if os.name == "nt":
        return os.path.join(fed, ".venv-st", "Scripts", "python.exe")
    return os.path.join(fed, ".venv-st", "bin", "python")

HOME = os.path.expanduser("~")
CARD_DIR = os.path.join(HOME, "[日记仓库]", "2-知识库", "10-蓝图索引卡")
BP_ROOT = os.path.join(os.path.expanduser("[记忆共享中心]"), "记忆蓝图")
FED = os.path.join(os.path.expanduser("[记忆共享中心]"), "脚本中心", "知识联邦引擎")
LEDGER = os.path.join(CARD_DIR, ".bc_ledger.json")
INTRUSION_BASE = os.path.join(CARD_DIR, ".intrusion_baseline.json")


def _atomic_dump(path, obj):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)

# 覆盖度口径（唯一声明处·⛔在别处另算一套=双本账）：
#   分母 = 记忆蓝图/**/*.md，排除①备份类目录（路径段含 bak/备份/回流前/archive/存档/legacy/回收）
#         ②文件名含 CHANGELOG/INDEX/进度看板 的记账类件
#   分子 = blueprint-card 的 source_files 解析出的真实源文件（去重）
EXCL_DIR_RE = re.compile(r"bak|备份|回流前|archive|存档|归档|legacy|回收", re.I)  # 「归档」补入2026-10-28：与存档等价词表漏一形，11件归档旧版混入分母致覆盖率虚低（守卫规范「拼写族完备性」同族）
EXCL_FILE_RE = re.compile(r"CHANGELOG|INDEX|进度看板", re.I)


def design_files():
    out = []
    for r, ds, ns in os.walk(BP_ROOT):
        rel = r.replace(BP_ROOT, "")
        if any(EXCL_DIR_RE.search(d) for d in rel.split(os.sep) if d):
            continue
        for f in ns:
            if f.endswith(".md") and not EXCL_FILE_RE.search(f):
                out.append(os.path.join(r, f))
    return out


def covered_sources():
    cov = {}
    for p in glob.glob(os.path.join(CARD_DIR, "*.md")):
        try:
            fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        except Exception:
            continue
        if fm.get("type") != "blueprint-card":
            continue
        for it in (fm.get("source_files") or []):
            cov.setdefault(os.path.basename(str(it).split("#")[0]).strip(), []).append(os.path.basename(p))
    return cov


def coverage():
    files = design_files()
    tot_b = sum(os.path.getsize(f) for f in files)
    cov = covered_sources()
    hit = [f for f in files if os.path.basename(f) in cov]
    hit_b = sum(os.path.getsize(f) for f in hit)
    uncov = sorted(((os.path.getsize(f), f) for f in files if os.path.basename(f) not in cov), reverse=True)
    return {
        "口径": "记忆蓝图/**/*.md 排除备份类目录与 CHANGELOG/INDEX/进度看板（真源=bp_factory.design_files）",
        "数据截止日": datetime.date.today().isoformat(),
        "复算命令": "python3 " + os.path.join(HERE, "bp_factory.py") + " --coverage-only",
        "有效设计文件": len(files), "总字节": tot_b,
        "blueprint-card 数": sum(1 for p in glob.glob(os.path.join(CARD_DIR, "*.md"))
                                if 'type: blueprint-card' in open(p, encoding="utf-8").read()[:2000]),
        "已覆盖源文件": len(hit), "覆盖文件率%": round(len(hit) / max(1, len(files)) * 100, 1),
        "覆盖字节率%": round(hit_b / max(1, tot_b) * 100, 1),
        "未覆盖Top10(按字节KB)": [(round(s / 1024), os.path.relpath(f, BP_ROOT)[:52]) for s, f in uncov[:10]],
    }


def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, (p.stdout + p.stderr)


def step_lint():
    rc, out = run(["python3", os.path.join(HERE, "note_validator.py"), CARD_DIR])
    return ("✅" if rc == 0 else "⛔") + " 字段机检：" + (out.strip().splitlines()[-1][:90] if out.strip() else "无输出"), rc == 0


def step_verify():
    rc, out = run(["python3", os.path.join(HERE, "bp_quote_verify.py"), CARD_DIR])
    last = [l for l in out.splitlines() if "真值机检" in l]
    return ("✅" if rc == 0 else "⛔") + " 引文/节锚/关联：" + (last[-1][:110] if last else out.strip()[:90]), rc == 0


def step_reserve(n):
    led = json.load(open(LEDGER, encoding="utf-8")) if os.path.isfile(LEDGER) else {"issued": []}
    ids = []
    for p in glob.glob(os.path.join(CARD_DIR, "*.md")):
        fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        m = re.match(r"蓝图卡#BC(\d{4})", str(fm.get("card_id", "")))
        if m:
            ids.append(int(m.group(1)))
    mx = max(ids) if ids else 0
    # 台账里已预留但未落卡的号也要占位（防两窗口同抢）
    used = set(ids) | {int(x) for rec in led["issued"] for x in rec["range"]}
    free, k = [], mx
    while len(free) < n:
        k += 1
        if k not in used:
            free.append(k)
    lo, hi = free[0], free[-1]
    led["issued"].append({"range": list(range(lo, hi + 1)), "at": datetime.datetime.now().isoformat(timespec="seconds"),
                          "note": "bp_factory 预留·落卡后由 factory 核账"})
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False)
    return "📇 号段预留 BC%04d-BC%04d（%d 个）·台账 %s" % (lo, hi, n, os.path.basename(LEDGER)), True, (lo, hi)


def step_b2_evidence(evidence_path=None, now=None, max_age_s=24 * 3600):
    """B2 去重门凭证闸（任务卡 §四十三-2：「应跑」升「不跑即出厂判红」）。
    凭证由 dedup_recall --type blueprint-card 写；无件/超 24h/时间格式坏 = 判红。"""
    import datetime
    ev = evidence_path or os.path.join(CARD_DIR, ".b2_dedup_evidence.json")
    if not os.path.isfile(ev):
        return False, ("⛔ B2 去重门无凭证（从未跑或目录不对）——产卡前必须跑 dedup_recall，"
                       "不跑即判红（§四十根因：跳门致同判断双卡入库）")
    try:
        data = json.load(open(ev, encoding="utf-8"))
        t = datetime.datetime.fromisoformat(data["at"])
    except Exception as e:
        return False, "⛔ B2 凭证不可解析/无时间字段：%s" % e
    age = (datetime.datetime.now() if now is None else datetime.datetime.fromtimestamp(now)) - t
    if age.total_seconds() > max_age_s or age.total_seconds() < 0:
        return False, ("⛔ B2 凭证已过期（%s 前，>24h 不算数）——本轮新产的卡必须重新过去重门" %
                       _fmt_age(age.total_seconds()))
    return True, ("✅ B2 去重门凭证在册（%s 前·domain=%s·hits=%s）" %
                  (_fmt_age(age.total_seconds()), data.get("domain"), data.get("hits")))


def _fmt_age(sec):
    if sec < 3600:
        return "%d 分钟" % max(1, int(sec // 60))
    return "%.1f 小时" % (sec / 3600.0)


def step_semantic_dedup(py):
    """语义去重闸（§四十三-1）：新卡 vs 同文件既有卡 bge 余弦 ≥0.87 判红，对清单写抽检单第三节。
    解释器：优先 .venv-st（闸依赖模型）；跑不成判红不降级（PAT-058 仪器假绿同源防线）。"""
    script = os.path.join(HERE, "bp_semantic_dedup.py")
    if not os.path.isfile(script):
        return [("⛔ 语义去重闸件缺失：%s" % script, False)], False
    rc, out = run([py, script, CARD_DIR, "--json"])
    line = [l for l in out.splitlines() if l.startswith("{")]
    if rc == 0 and line:
        try:
            r = json.loads(line[-1])
            return [("✅ 语义去重闸：扫描 %d 对·零违规（阈值 0.87·§四十二标定）" % r.get("scanned", 0), True)], True
        except Exception:
            pass
    if rc == 1 and line:
        try:
            r = json.loads(line[-1])
            vs = r.get("violations", [])
            det = "；".join("%s↔%s %.3f" % (v["a"][4:-3], v["b"][4:-3], v["sim"]) for v in vs[:6])
            return [("🔴 语义去重闸：%d 对 ≥0.87（已写抽检单第三节·判罪权在人工，合并/改判后重跑出厂）：%s%s"
                     % (len(vs), det, "…" if len(vs) > 6 else ""), False)], False
        except Exception:
            pass
    tail = (out.strip().splitlines() or ["无输出"])[-1][:100]
    return [("⛔ 语义去重闸未跑成（rc=%d）：%s" % (rc, tail), False)], False


def step_ship():
    ok = True
    msgs = []
    py = _venv_py(FED)
    if not os.path.isfile(py):
        py = "python3"
        msgs.append(("🟡 .venv-st 缺失，向量/真尺/语义闸将以降级解释器跑（闸会判红不静默）", True))
    rc, out = run([py, "dedup_recall.py", CARD_DIR,
                   "--category", "检索", "--tags", "检索", "--type", "blueprint-card", "--probe"],
                  cwd=HERE)
    msgs.append((("✅" if rc == 0 else "⛔") + " 去重门可用：rc=%d" % rc, rc == 0)); ok &= rc == 0
    eok, emsg = step_b2_evidence()
    msgs.append((emsg, eok)); ok &= eok
    dts, dt_ok = step_semantic_dedup(py)
    msgs.extend(dts); ok &= dt_ok
    rc, out = run([py, "build_kb_vectors.py"], cwd=os.path.join(FED, "scripts"))
    line = [l for l in out.splitlines() if "向量库已更新" in l or "复用" in l]
    msgs.append((("✅" if rc == 0 else "⛔") + " 向量增量：" + (line[-1][:100] if line else out.strip()[:80]), rc == 0)); ok &= rc == 0
    rc2, _ = run(["launchctl", "kickstart", "-k", "gui/%d/com.buluotuo.kb-serve" % os.getuid()])
    msgs.append((("✅" if rc2 == 0 else "🟡") + " kb_serve 重启（运行态生效）：rc=%d" % rc2, True))  # 装机端可能无此服务→不判死
    rc3, out3 = run([py, "gate0_rewrite_ab.py", "--selfcheck"], cwd=os.path.join(FED, "scripts"))
    # 多轮取一致（2026-10-28 实测：同条件三遍恒等 14/21·0.545，但在摘除-还原/serve 重启窗口内读数会漂到 11/21）
    # ⇒ 读数须连跑两遍一致才采信；不一致判红并提示"有并发在改语料"，⛔拿一个不稳定的数当放行凭据
    out3b = run([py, os.path.join(FED, "scripts", "gate0_rewrite_ab.py"), "--selfcheck"])[1]
    exb = [l for l in out3b.splitlines() if "精确集" in l]
    ex = [l for l in out3.splitlines() if "精确集" in l]
    import re as _re
    _nd = _re.search(r"NDCG@5=([0-9.]+)", ex[0]) if ex else None
    ndv = float(_nd.group(1)) if _nd else 0.0
    FLOOR = 0.49  # 2026-10-27 登记：起点 0.510 留 0.02 抖动余量；同日实测只查 Recall 时 0.510→0.501 照样报绿
    good = bool(ex) and "14/21" in ex[0] and ndv >= FLOOR and exb == ex
    qd = os.path.join(CARD_DIR, "蓝图卡挤位待勾队列.md")
    # 豁免只认实验当轮写入的 gate_exempt 字段，⛔认文件里有没有 ⏳（过期台账=过期证据）
    pend = os.path.isfile(qd) and "gate_exempt: true" in open(qd, encoding="utf-8").read()
    msgs.append((("✅" if good else ("⚠️" if pend else "⛔")) + " 真尺（Recall+NDCG 双维·两遍一致才采信·地板 0.49）：" + (ex[0].strip()[:110] if ex else "读数缺失")
                 + ("" if good else ("｜退化题已进待勾队列 ⇒ 阻塞【批次交付】、不阻塞【生产线继续产卡】，勾完即解封" if pend else "｜无待勾台账 ⇒ 判红且阻塞生产（⛔默默放行）")), good))
    ok &= good
    return msgs, ok


PROBE = """
import json, os, sys
sys.path.insert(0, os.path.expanduser("[记忆共享中心]/脚本中心"))
import search_kb as skb
G = json.load(open(os.path.expanduser(
    "[记忆共享中心]/脚本中心/知识联邦引擎/scripts/eval_set.json")))["gate0"]
TOP, FAR = 5, 60          # FAR=取回窗口（够大才能做「拿掉我方卡后重排」的反事实）


def names(task):
    r = skb.search(task, k=FAR)
    items = r[0][0] if isinstance(r[0], tuple) else r[0]
    return [os.path.basename(it[1]) for it in items]


hit5 = 0
harm = 0
causal = []
gain = 0
for c in G["samples"]:
    tgs = [os.path.basename(t) for t in (c.get("targets") or [])]

    def is_t(n):
        return any(t.replace(".md", "") == n.replace(".md", "") or t in n or n in t for t in tgs)

    nm = names(c["task"])
    rank = next((i + 1 for i, n in enumerate(nm) if is_t(n)), None)
    if rank and rank <= TOP:
        hit5 += 1
        continue
    if not tgs:
        continue
    mine = [n for n in nm[:TOP] if n.startswith("蓝图卡-")]
    if mine:
        harm += 1
    # 反事实：拿掉我方全部蓝图卡后重排（近似——BM25 IDF 不重算，40/4469 影响可忽略并如实标注）
    wo = [n for n in nm if not n.startswith("蓝图卡-")]
    r_wo = next((i + 1 for i, n in enumerate(wo) if is_t(n)), None)
    if r_wo and r_wo <= TOP and rank and rank > TOP:
        causal.append((c["id"], r_wo, rank, mine[:2]))
    if rank and rank <= TOP and (not r_wo or r_wo > TOP):
        gain += 1
print("HIT5", hit5, "OF", len(G["samples"]))
print("COEXIST", harm)
print("GAIN", gain)
for cid, a, b, o in causal:
    print("CAUSAL", cid, a, b, o)
"""


def step_intrusion(topn=5):
    """越位闸：我的 蓝图卡-* 占住 gate0 既有 33 题（真值=你逐题勾）Top-N 且非该题 target ⇒ 越位。
    只读 eval_set，⛔不改题面不代填真值。用途：放量前的安全尺——越位数上涨说明卡语面与他域题
    重叠，该收窄措辞而不是加卡（2026-10-27 批次2B 实测：BC0007 挤 F-Q12 目标卡至 7 名）。"""
    import tempfile
    py = _venv_py(FED)
    if not os.path.isfile(py):
        py = "python3"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(PROBE)
        probe = f.name
    try:
        rc, out = run([py, probe, str(topn)])
    finally:
        os.unlink(probe)
    if rc != 0 or "HIT5" not in out:
        tail = (out.strip().splitlines() or ["无输出"])[-1]
        return [("⛔ 越位闸未跑成：" + tail[:80], False)], False
    lines = out.splitlines()
    hl = [l for l in lines if l.startswith("HIT5")]
    hit, tot = (int(hl[0].split()[1]), int(hl[0].split()[3])) if hl else (0, 0)
    co = int(([l for l in lines if l.startswith("COEXIST")] or ["0 0"])[0].split()[1])
    gn = int(([l for l in lines if l.startswith("GAIN")] or ["0 0"])[0].split()[1])
    causal = [l for l in lines if l.startswith("CAUSAL")]
    msg = ("🎯 越位闸（同现层）：真值题 target 命中 Top5 = %d/%d｜同现=我方卡占住未命中题 %d 个"
           "｜因果数请跑 bp_causal_ab.py 取（本件内后处理因果算法已作废，恒零读数不配当判据）"
           % (hit, tot, co))
    if causal:
        msg += chr(10) + "   " + " | ".join(l[7:].strip() for l in causal[:4])
    msg += chr(10) + "   ⛔ 因果层判据作废：后处理重排的前提（其余分数不变）已被自家数据证伪——"
    "去掉蓝图文档后 F-Q10/F-Q11 目标卡由 4 名掉至 13/11 名，说明路由加权/IDF/实体直通皆依赖语料集。"
    "真反事实须物理摘除卡片文件后重建 doc 缓存再跑（方法已登记任务卡 §十五），在此之前本闸只认同现层；"
    "注：GAIN 亦不可测——后处理摘除只可能让其余文档名次变好，结构上永远报 0，⛔拿它当'我的卡没帮忙'的证据"
    # 判据＝物理因果台账（PAT-052 代理信号不占判据位）。同现数只作监控展示：
    # 2026-10-28 实测同现 1→6 而真反事实 harm=0，若以同现判红会误杀已验证无害的放量，且让最弱档证据决定放行
    try:
        cj = json.load(open(os.path.join(CARD_DIR, ".causal_ledger.json"), encoding="utf-8"))
    except Exception:
        cj = None
    if cj is None:
        msg += chr(10) + "   ⛔ 无因果台账（未跑 bp_causal_ab.py）⇒ 判红；⛔用同现数替代"
        ok_intr = False
    elif not cj.get("verdict_ok"):
        msg += chr(10) + "   ⛔ 因果实验复验未过（读数不可复现，常见于摘除-还原/serve 重启窗口有并发）⇒ 判红"
        ok_intr = False
    elif cj.get("harm", 0) > 0:
        msg += chr(10) + "   🔴 因果 harm=%s ⇒ 已生成待勾队列，阻塞【批次交付】不阻塞【生产线】（待你勾）" % cj["harm"]
        ok_intr = True
    else:
        msg += chr(10) + "   ✅ 因果台账 harm=0、gain=%s（hit5 %s→%s）⇒ 净增益且零挤位" % (
            cj.get("gain"), cj.get("hit5_without"), cj.get("hit5_with"))
        ok_intr = True
    _atomic_dump(INTRUSION_BASE, {"coexist_monitor_only": co, "causal": cj if cj else "absent",
                                  "hit5": hit,
                                  "at": datetime.datetime.now().isoformat(timespec="seconds"),
                                  "note": "同现数仅供监控（判据位已交因果台账）；本文件记录趋势，⛔参与放行"})
    return [(msg, True)], ok_intr



def gaps(top_n=12):
    """缺口台账：每个设计文件已有几张细颗粒卡 + 字节，并给出「下一片」工单（自动领号+定点读命令）。
    为什么需要：批次3 要放量，但「读片→产卡→出厂」的机械编排此前每轮由 AI 手搓生成器，
    那是可规则化的活（选文件/算覆盖/领号/拼命令），该交脚本；AI 只留判断部分（哪条是独立设计判断）。"""
    import collections
    files = design_files()
    per = collections.Counter()
    for p in glob.glob(os.path.join(CARD_DIR, "*.md")):
        try:
            fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        except Exception:
            continue
        if fm.get("type") != "blueprint-card":
            continue
        for it in (fm.get("source_files") or []):
            per[os.path.basename(str(it).split("#")[0]).strip()] += 1
    rows = []
    for f in files:
        b = os.path.basename(f)
        sz = os.path.getsize(f)
        n = per.get(b, 0)
        rows.append({"path": f, "base": b, "bytes": sz, "cards": n,
                     "est": max(1, round(sz / 30000)),        # 约 3 万字节 1 条判断（任务卡 §一 粒度）
                     "dirs": len({1})})
    _cards_seen = len({os.path.basename(p) for p in glob.glob(os.path.join(CARD_DIR, "*.md"))
                       if "type: blueprint-card" in open(p, encoding="utf-8", errors="ignore").read()[:2000]})
    covered = [r for r in rows if r["cards"] > 0]
    todo = sorted([r for r in rows if r["cards"] == 0], key=lambda r: -r["bytes"])
    part = [r for r in covered if r["cards"] < r["est"]]
    # 两口径并列，⛔混用（max(1,·) 下限会把小文件放大成一张，与任务卡按字节均摊不同尺）
    total_est_floor = sum(r["est"] for r in rows)                     # 口径二：每文件至少 1 张
    total_est_bytes = round(sum(r["bytes"] for r in rows) / 30000)   # 口径一：任务卡 §一 约 3 万字节 1 条判断
    have = sum(r["cards"] for r in covered)
    nxt = todo[0] if todo else None
    out = {"文件全集": len(rows), "已产卡(唯一卡数)": _cards_seen, "卡次(按源文件计)": have,
           "应有卡_按字节均摊": total_est_bytes, "应有卡_每文件至少1张": total_est_floor,
           "缺口_按字节均摊": total_est_bytes - _cards_seen, "缺口_含下限": total_est_floor - _cards_seen,
           "口径说明": "字节均摊=任务卡§一原尺(总字节/3万)；含下限=每文件至少1张，两者差额即碎文件的兜底量，⛔拿二者互证",
           "零卡文件": len(todo), "部分覆盖待补": len(part),
           "下一片": None if not nxt else {"文件": os.path.relpath(nxt["path"], BP_ROOT),
                                        "KB": nxt["bytes"] // 1024, "估需卡": nxt["est"],
                                        "领号命令": "python3 %s --reserve %d" % (os.path.join(HERE, "bp_factory.py"), nxt["est"]),
                                        "候选预筛": "python3 %s \"%s\" --gap --budget-kb 40" % (os.path.join(HERE, "bp_c1_scan.py"), nxt["path"]),
                                        "出厂命令": "python3 %s --ship" % os.path.join(HERE, "bp_factory.py")}}
    if top_n:
        out["零卡最大前10"] = [(os.path.relpath(r["path"], BP_ROOT)[:46], r["bytes"] // 1024, r["est"]) for r in todo[:10]]
        out["部分覆盖待补前10"] = [(os.path.relpath(r["path"], BP_ROOT)[:46], r["cards"], r["est"]) for r in sorted(part, key=lambda r: r["cards"] - r["est"])[:10]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ship", action="store_true", help="含向量/serve/真尺（慢·出厂前跑）")
    ap.add_argument("--gaps", action="store_true", help="缺口台账与下一片工单（批次3 放量用）")
    ap.add_argument("--coverage-only", action="store_true")
    ap.add_argument("--reserve", type=int, default=0, help="申请 N 个连续 BC 号并写台账")
    a = ap.parse_args()

    if a.gaps:
        import pprint
        pprint.pprint(gaps(), sort_dicts=False, width=118)
        return 0
    if a.coverage_only:
        for k, v in coverage().items():
            print("%-22s %s" % (k, v))
        return 0
    if a.reserve:
        m, ok, _ = step_reserve(a.reserve)
        print(m)
        return 0 if ok else 1

    all_ok = True
    m1, ok1 = step_lint(); print(m1); all_ok &= ok1
    m2, ok2 = step_verify(); print(m2); all_ok &= ok2
    cv = coverage()
    print("📊 覆盖度：blueprint-card %d 张 → 源文件 %d/%d 个（%.1f%%），字节覆盖 %.1f%%｜数据截止 %s"
          % (cv["blueprint-card 数"], cv["已覆盖源文件"], cv["有效设计文件"],
             cv["覆盖文件率%"], cv["覆盖字节率%"], cv["数据截止日"]))
    print("   口径：" + cv["口径"])
    print("   未覆盖最大件：" + "; ".join("%s(%dKB)" % (n, s) for s, n in cv["未覆盖Top10(按字节KB)"][:4]))
    if a.ship:
        ship_msgs, ok_ship = step_ship()
        intr, clean = step_intrusion()
        for line, ok in intr:
            print(line); all_ok &= (ok and clean)
        for line, ok in ship_msgs:
            print(line); all_ok &= ok
    print("\n出厂判定：", "✅ 全绿，可交付" if all_ok else "⛔ 有闸未过，禁止交付/升 trust")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
