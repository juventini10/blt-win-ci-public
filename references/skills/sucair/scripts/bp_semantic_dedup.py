#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 蓝图卡语义去重闸（与 bp_factory/bp_quote_verify 同族，无 hook/STOP_GUARDS 挂载点可声明，
# REG:      硬填 §四注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
"""
bp_semantic_dedup.py — 蓝图卡语义去重闸（新卡 vs 同源文件既有卡，bge 余弦 ≥阈值 判红）

为什么存在（2026-10-28 任务卡 §四十/§四十三-1 实证）：字段机检/引文门/节锚门全绿也拦不住
两条卡说同一件事——「以卡数替代检索增益」这条目标锚禁令在机制上曾是空的。琥珀 5 对重复
（0.866~0.943）靠人工相似度核对才隔离，本件把它变成出厂必过的闸。

打分尺（唯一，⛔另造一套=双本账）：
  文本面 = search_kb.build_docs() 的蓝图卡检索面（title+文件名+source_files+core_principles
           +summary+tags+正文前600）——与检索消费者同一对象，闸判的正是检索会撞车的那些对；
  模型 = 与向量库同款的 bge 量化模型（.venv-st + onnx int8），余弦相似度。
  实证依据：§四十二 阈值 0.87 在此尺下可分（同判断组 0.866~0.943 / 同文件对照中位 ~0.73）。

用法：
  python3 bp_semantic_dedup.py [卡目录]                 # 全库同文件对扫描·增量嵌（首跑慢）
  python3 bp_semantic_dedup.py --json                   # 机器可读输出（bp_factory --ship 消费）
  python3 bp_semantic_dedup.py --set <卡> --to <卡>     # 变异自检用（内存替换 frontmatter 面，不落盘）
退出码：0=零违规｜1=有 ≥阈值 的对（写/更新 疑似重复抽检单第三节）｜2=环境不可用/用法错。
诚实边界：本件只证"语义高度相似"，⛔判"是重复"——同节多卡合法，判罪权在人工抽检单，
闸的职责是把它们摆到出厂名单上，拦在 trust 升档之前。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import argparse
import datetime
import hashlib
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
def _venv_py(fed):
    """.venv-st 解释器跨平台定位（2026-10-28 跨平台门禁修）：unix=bin/python，Win=Scripts\\python.exe。"""
    if os.name == "nt":
        return os.path.join(fed, ".venv-st", "Scripts", "python.exe")
    return os.path.join(fed, ".venv-st", "bin", "python")

HOME = os.path.expanduser("~")
CARD_DIR_DEFAULT = os.path.join(HOME, "[日记仓库]", "2-知识库", "10-蓝图索引卡")
FED = os.path.join(os.path.expanduser("[记忆共享中心]"), "脚本中心", "知识联邦引擎")
QUANT_DIR = os.path.join(FED, "models", "bge-large-zh-v1.5-qint8-avx2")
VENV_PY = _venv_py(FED)
MODEL_NAME = os.environ.get("KB_MODEL") or "BAAI/bge-large-zh-v1.5"

THRESHOLD = 0.87  # §四十二 标定·2026-10-28 重标定复核见任务卡 §四十四
EVIDENCE_NAME = ".b2_dedup_evidence.json"
AUDIT_SECTION3 = "## 三、出厂闸名单"  # 本件只维护抽检单第三节，⛔动一/二节人工区


def read_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def write_json(path, obj):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)


def _face(raw, base):
    """蓝图卡检索面（模板真源=search_kb.py L1159-1187 的 text 拼装，改那边须同步本函数并重标定）。

    为什么不在运行 import search_kb.build_docs 取面：build_docs 只扫全局 BLUEPRINT_INDEX_DIR，
    临时子库（夹具/隔离目录）取不到卡——首轮 T1/T6 因此拿空集当通过（2026-10-28 夹具抓到）。
    解析器仍用 note_validator.parse_frontmatter（全 Skill 单一解析器纪律，与 dedup_recall 同源）。"""
    from note_validator import parse_frontmatter
    fm, body = parse_frontmatter(raw)
    if fm.get("type") != "blueprint-card":
        return None

    def lst(key):
        v = fm.get(key, [])
        if isinstance(v, list):
            return [str(x) for x in v]
        return [str(v)] if str(v).strip() else []
    title = str(fm.get("title", base.replace(".md", "")))
    summary = str(fm.get("summary", ""))
    return (title + " " + os.path.splitext(base)[0] + " "
            + " ".join(lst("source_files")) + " "
            + " ".join(lst("core_principles")) + " " + summary + " "
            + " ".join(lst("tags")) + " " + re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)[:600])


def library_docs(card_dir):
    """卡目录里的 blueprint-card 检索面文本 {绝对路径: text}。"""
    card_dir = os.path.abspath(card_dir)
    out = {}
    for b in sorted(os.listdir(card_dir)):
        if not b.endswith(".md") or b.startswith("00-"):
            continue
        p = os.path.join(card_dir, b)
        try:
            raw = open(p, encoding="utf-8").read()
        except OSError:
            continue
        if "type: blueprint-card" not in raw[:2000]:
            continue
        t = _face(raw, b)
        if t:
            out[p] = t
    return out


def source_keys(card_dir):
    """每张卡的源文件名集合（同文件判据键）。复用 note_validator 唯一解析器。"""
    from note_validator import parse_frontmatter
    out = {}
    for b in sorted(os.listdir(card_dir)):
        if not b.endswith(".md") or not b.startswith("蓝图卡-"):
            continue
        p = os.path.join(card_dir, b)
        try:
            fm, _ = parse_frontmatter(open(p, encoding="utf-8").read())
        except Exception:
            continue
        if fm.get("type") != "blueprint-card":
            continue
        keys = set()
        for it in (fm.get("source_files") or []):
            keys.add(os.path.basename(str(it).split("#")[0]).strip())
        out[b] = keys
    return out


def _load_model():
    from sentence_transformers import SentenceTransformer
    if os.path.isdir(QUANT_DIR) and os.path.isfile(os.path.join(QUANT_DIR, "onnx", "model_qint8_avx2.onnx")):
        return SentenceTransformer(QUANT_DIR, backend="onnx",
                                   model_kwargs={"file_name": "onnx/model_qint8_avx2.onnx",
                                                 "provider": "CPUExecutionProvider"},
                                   local_files_only=True)
    return SentenceTransformer(MODEL_NAME, local_files_only=True)


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def embed_texts(texts, vec_cache_path=None, model=None):
    """文本→向量，md5(text) 键缓存（与 kb 向量库同款幂等模式）。返回 {text: vec}。"""
    cache = read_json(vec_cache_path, {}) if vec_cache_path else {}
    todo = []
    for t in set(texts):
        if hashlib.md5(t.encode("utf-8")).hexdigest() not in cache:
            todo.append(t)
    if todo:
        m = model or _load_model()
        vecs = m.encode(todo, normalize_embeddings=True, batch_size=32)
        for t, v in zip(todo, vecs):
            cache[hashlib.md5(t.encode("utf-8")).hexdigest()] = [float(x) for x in v]
        if vec_cache_path:
            write_json(vec_cache_path, cache)
    return {t: cache[hashlib.md5(t.encode("utf-8")).hexdigest()] for t in set(texts)}


def adjudicated_pairs(sheet_path):
    """抽检单第四节「裁决判例」里的豁免对（仅裁次=非重复的行；MERGE 对不豁免——其隔离卡回库时应照拦）。

    豁免的合法性=人工判例在册（皮叔 2026-10-28 授权轮），⛔机器自判——判例文件丢失则豁免清零（fail-closed）。"""
    adj = set()
    try:
        text = open(sheet_path, encoding="utf-8").read()
    except Exception:
        return adj
    m = re.search(r"^## 四、裁决判例.*?(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return adj
    for line in m.group(0).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or "非重复" not in cells[1]:
            continue
        names = []
        for part in cells[0].split("/"):
            q = part.strip()
            if not q:
                continue
            if not q.startswith("蓝图卡-"):
                q = "蓝图卡-" + q
            names.append(q if q.endswith(".md") else q + ".md")
        if len(names) == 2:
            adj.add(tuple(sorted(names)))
    return adj


def gate(card_dir, threshold=THRESHOLD, vec_cache=None, ledger=None, dry_run=False, mutate=None):
    """全库同文件两两余弦 ≥threshold ⇒ violations（只报同文件对，跨节同文件也报·人工判）。

    mutate: {"卡文件名": 替换后的完整检索面文本}——T6 变异夹具用，⛔落盘。
    返回 {"violations": [(path_a, path_b, sim)], "scanned": n, "embedded": m, "threshold": t}
    """
    docs = library_docs(card_dir)
    if not docs:
        return {"violations": [], "scanned": 0, "embedded": 0, "threshold": threshold,
                "note": "目录内无 blueprint-card（空库≠通过，调用方按需判红）"}
    names = {os.path.basename(p): p for p in docs}
    texts = dict(docs)
    if mutate:
        for b, t in mutate.items():
            if b in names:
                texts[names[b]] = t
    sk = source_keys(card_dir)
    # 同文件分组（按源文件名），组内两两配对
    grp = {}
    for b, keys in sk.items():
        for k in keys:
            grp.setdefault(k, []).append(b)
    pairs = set()
    for ps in grp.values():
        ps = [b for b in ps if b in names]
        for a, c in itertools.combinations(sorted(ps), 2):
            pairs.add((names[a], names[c]))
    vecs = embed_texts([texts[p] for p in names.values()], vec_cache_path=vec_cache)
    adj = adjudicated_pairs(os.path.join(card_dir, "疑似重复抽检单.md"))
    violations = []
    seen = set()
    for pa, pc in sorted(pairs):
        key = tuple(sorted([os.path.basename(pa), os.path.basename(pc)]))
        if key in seen:
            continue  # 同卡对可属多个源文件组，按卡对去重报一次
        seen.add(key)
        s = _cos(vecs[texts[pa]], vecs[texts[pc]])
        if s >= threshold and key not in adj:
            violations.append((pa, pc, round(s, 3)))
    res = {"violations": violations, "scanned": len(seen),
           "exempted": len([k for k in seen if k in adj]),
           "embedded": len([t for t in texts.values()]), "threshold": threshold}
    if ledger and not dry_run:
        led = read_json(ledger, {"cards": {}})
        led["cards"] = {b: hashlib.md5(texts[p].encode("utf-8")).hexdigest()
                        for b, p in names.items()}
        led["at"] = datetime.datetime.now().isoformat(timespec="seconds")
        led["last_violations"] = len(violations)
        write_json(ledger, led)
    return res


def known_pairs_from_audit_sheet(sheet_path):
    """抽检单一/二节表格里已登记的卡对（键=两文件名排序元组）。

    表形制（实盘）：3 列「相似度 | 文件 | 卡A / 卡B」，卡名带 `-` 前缀简写且可能省略
    「蓝图卡-」头——首轮解析按 4 列拆以 `startswith('-')` 取格，解出 0 对拿空集当已知
    （2026-10-28 T2 输出现场抓到，当场修正加回归断言）。"""
    known = set()
    try:
        text = open(sheet_path, encoding="utf-8").read()
    except Exception:
        return known
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.match(r"^0\.\d+$", cells[0]):
            continue
        names = []
        for part in cells[2].split("/"):
            p = part.strip().lstrip("-").strip()
            if not p:
                continue
            if not p.startswith("蓝图卡-"):
                p = "蓝图卡-" + p
            names.append(p if p.endswith(".md") else p + ".md")
        for x, y in itertools.combinations(sorted(names), 2):
            known.add((x, y))
    return known


def samefile_sample_below(card_dir, slack=0.05, threshold=THRESHOLD, vec_cache=None, ledger=None):
    """返回读数低于 (threshold-slack) 的同文件对（T6 选例用）。[(path_a, path_b, sim)] 降序。"""
    return _all_pairs_below(card_dir, threshold - slack, vec_cache=vec_cache, ledger=ledger)


def _all_pairs_below(card_dir, upper, vec_cache=None, ledger=None):
    docs = library_docs(card_dir)
    names = {os.path.basename(p): p for p in docs}
    sk = source_keys(card_dir)
    grp = {}
    for b, keys in sk.items():
        for k in keys:
            grp.setdefault(k, []).append(b)
    pairs = set()
    for ps in grp.values():
        ps = [b for b in ps if b in names]
        for a, c in itertools.combinations(sorted(ps), 2):
            pairs.add((names[a], names[c]))
    vecs = embed_texts(list(docs.values()), vec_cache_path=vec_cache)
    out = []
    for pa, pc in sorted(pairs):
        s = _cos(vecs[docs[pa]], vecs[docs[pc]])
        if s <= upper:
            out.append((pa, pc, round(s, 3)))
    out.sort(key=lambda r: -r[2])
    return out


def update_audit_section3(card_dir, violations):
    """把闸报对写入抽检单第三节（覆盖式·只动本节气泡，⛔碰一/二节人工区）。"""
    sheet = os.path.join(card_dir, "疑似重复抽检单.md")
    head3 = "%s（bp_semantic_dedup 自动维护·覆盖式·判罪权在人工）" % AUDIT_SECTION3
    lines = [head3, "", "| 相似度 | 两张卡 |", "|--:|:--|"]
    for pa, pc, s in sorted(violations, key=lambda r: -r[2]):
        lines.append("| %.3f | %s / %s |" % (s, os.path.basename(pa), os.path.basename(pc)))
    if not violations:
        lines.append("| — | （本轮零违规） |")
    block = "\n".join(lines) + "\n"
    text = open(sheet, encoding="utf-8").read() if os.path.isfile(sheet) else "# 疑似重复抽检单\n"
    pat = re.compile(r"^%s（.*?(?=^## |\Z)" % re.escape(AUDIT_SECTION3), re.S | re.M)
    if pat.search(text):
        new = pat.sub(block, text)
    else:
        new = text.rstrip() + "\n\n---\n\n" + block
    tmp = sheet + ".tmp.%d" % os.getpid()
    open(tmp, "w", encoding="utf-8").write(new)
    os.replace(tmp, sheet)
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card_dir", nargs="?", default=CARD_DIR_DEFAULT)
    ap.add_argument("--threshold", type=float, default=None,
                    help="改判据须 --set-threshold-with-reason 同段齐给（防手滑阈值漂移），单独给报错")
    ap.add_argument("--reason", default=None, help="与 --threshold 成对：改阈值的实证理由")
    ap.add_argument("--set", dest="mut_set", help="变异自检：目标卡文件名")
    ap.add_argument("--to", dest="mut_to", help="变异自检：借用其面的另一卡文件名")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    thr = THRESHOLD
    if a.threshold is not None:
        if not a.reason:
            print("⛔ 改阈值必须同给 --reason（实证依据），否则视为手滑", file=sys.stderr)
            return 2
        thr = a.threshold
    if bool(a.mut_set) != bool(a.mut_to):
        print("⛔ --set/--to 必须成对", file=sys.stderr)
        return 2
    mutate = None
    if a.mut_set:
        docs = library_docs(a.card_dir)
        names = {os.path.basename(p): p for p in docs}
        if a.mut_set not in names or a.mut_to not in names:
            print("⛔ 变异目标卡不在库内：%s / %s" % (a.mut_set, a.mut_to), file=sys.stderr)
            return 2
        mutate = {a.mut_set: docs[names[a.mut_to]]}
    vec_cache = os.path.join(a.card_dir, ".dedup_vecs.json")
    ledger = os.path.join(a.card_dir, ".dedup_ledger.json")
    res = gate(a.card_dir, threshold=thr, vec_cache=vec_cache, ledger=ledger, mutate=mutate)
    vls = res["violations"]
    if not a.json:
        print("扫描 %d 对｜阈值 %.2f｜违规 %d" % (res["scanned"], thr, len(vls)))
        for x, y, s in vls:
            print("  %.3f  %s / %s" % (s, os.path.basename(x), os.path.basename(y)))
    else:
        out = dict(res)
        out["violations"] = [{"a": os.path.basename(x), "b": os.path.basename(y), "sim": s}
                             for x, y, s in vls]
        print(json.dumps(out, ensure_ascii=False))
    if vls:
        update_audit_section3(a.card_dir, vls)
        return 1
    return 0


if __name__ == "__main__":
    if os.path.basename(sys.executable).lower() not in ("python", "python.exe") or "venv-st" not in sys.executable:
        # 允许被 bp_factory 以 venv python 子进程调用；直接裸跑时提示正确的解释器
        if not os.path.isdir(os.path.dirname(VENV_PY)):
            print("⚠️ .venv-st 不在位，闸无法加载模型（判红不静默）", file=sys.stderr)
            sys.exit(2)
        if "--allow-venv-check" not in sys.argv:
            print("⛔ 本件须在 .venv-st 解释器下运行：%s" % VENV_PY, file=sys.stderr)
            sys.exit(2)
    sys.exit(main())
