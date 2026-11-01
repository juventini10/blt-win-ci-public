#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·属 sucair Skill 内部产出物机检（与 note_validator.py/dedup_recall.py 同类，
# REG:      该二件亦无 §四注册表行）；本件无 settings.json hooks / STOP_GUARDS 挂载点可声明，
# REG:      硬填注册表会伪造 §3.0 ②「挂载实盘」——留痕豁免，判据来源=守卫编写规范 §3.0 登记四件套
"""
bp_quote_verify.py — 蓝图卡「引用真值 + 节锚可达」机检（v1.0.0 · 2026-10-27 批次1 建）

职责（蓝图卡重造任务卡 最终目标锚的两半句，各自机械可验）：
  ① 引文可回源：卡 body「## 依据」段里 「」/『』 包裹的引串，逐段必须能在 source_files
     所指源文件中找到（连续子串）——防「把 AI 的概括塞进引号冒充原文」。
  ② 节锚可达：frontmatter `source_files` 每项 `文件#节名` 的节名，必须在该文件中
     真实存在（标题行或加粗段首）——防「卡指不回原文具体节」（目标锚后半句空转）。

为什么做成常驻机检而非一次性核对：批次2/3 要放量到 30~50 张，人工逐条读回原文不可持续；
且 2026-10-27 批次1 实测证明「引文内含未标记省略」「概括词入引号」两类缺陷会真实发生。

判据口径（诚实边界）：
  - 比对前剥 markdown 表示层（** ` ~~ 与空白），⛔不做语义匹配——只验字面可回溯。
  - 引文按省略号（…/...）与破折号（——）切段逐段验，段内必须连续；
    ⇒ 卡内省略必须显式标记，未标记的省略=判红（schema §三「⛔不加工不引申」的机械执法）。
  - 段长 <6 字不参与判定（短语无辨识力，避免假红）。
  - 节锚匹配放宽：允许节名在标题行/加粗串中出现（原文常见「## 二、混合检索」被引作「二、混合检索」）。

用法：
  python3 bp_quote_verify.py <蓝图卡目录> [--source-root <记忆蓝图根>]
输出：逐卡 verdict + 缺陷清单；exit 0=全绿，1=有红（供 flow-read B5 门禁消费）。
"""
# Win console UTF-8 guard (auto by clock-loop 1.7.2)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass

import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from note_validator import parse_frontmatter

_MIN_SEG = 6  # 短于此长度的引文段不做判定（无辨识力）
_BAK_MARKS = ("回流前备份", "记忆琥珀", ".bak", "_archive", "归档", "备份")  # 同名多副本时排除的备份类路径标记


def _strip_presentational(s):
    """剥 markdown 表示层 + 空白：只比内容字面，不比排版。"""
    s = re.sub(r"\*\*|`|~~", "", s)
    s = re.sub(r"[\s\u3000]+", "", s)
    return s


def _split_elisions(raw):
    """按省略号/破折号切段——这两者在卡里表示「此处原文有省略」。"""
    parts = re.split(r"…{1,}|\.{3,}|——", raw)
    return [p for p in (_strip_presentational(x) for x in parts) if len(p) >= _MIN_SEG]


def _load_sources(fm, source_root):
    """按 source_files 的 `文件[#节]` 解析真实源文件全文；返回 (文件名→全文, 锚清单, 缺失)。"""
    texts, anchors, missing = {}, [], []
    for item in (fm.get("source_files") or []):
        ref = str(item)
        fname, _, anchor = ref.partition("#")
        fname = os.path.basename(fname.strip())
        if fname not in texts:
            found = glob.glob(os.path.join(os.path.expanduser(source_root), "**", fname), recursive=True)
            if not found:
                missing.append(fname)
                continue
            # 同名多副本时优先取活件：glob 顺序会把「回流前备份_*」类目录的旧件排在前面，
            # 导致整卡引文假红（2026-10-27 A4 片实证：守卫家族实例.md 备份 80KB/活件 121KB）。
            live = [p for p in found if not any(m in p for m in _BAK_MARKS)]
            found = live or found
            try:
                texts[fname] = open(found[0], encoding="utf-8").read()
            except OSError as e:
                missing.append("%s(读取失败:%s)" % (fname, e))
                continue
        if anchor.strip():
            anchors.append((fname, anchor.strip().lstrip("§")))
    return texts, anchors, missing


def _anchor_exists(text, anchor):
    """节锚可达：剥表示层后，节名作为子串出现在任一行（含标题行/加粗串）。"""
    a = _strip_presentational(anchor)
    if not a:
        return True
    return any(a in _strip_presentational(l) for l in text.splitlines())


def verify_card(path, source_root, known_ids=frozenset()):
    text = open(path, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    if fm.get("type") != "blueprint-card":
        return None  # 非蓝图卡不归本件管
    issues = []

    srcs, anchors, missing = _load_sources(fm, source_root)
    for m in missing:
        issues.append("source_files 指向的文件不存在: %s" % m)
    for fname, anchor in anchors:
        full = srcs.get(fname)
        if full is not None and not _anchor_exists(full, anchor):
            issues.append("节锚不可达: %s#%s（该文件找不到此节名）" % (fname, anchor))
    blob = [_strip_presentational(v) for v in srcs.values()]

    # ③ 关联可达（2026-10-27 批次2A 实证补）：关联段引用的 蓝图卡#BCnnnn 必须在库内存在
    for ref in set(re.findall(r"BC(\d{4})", body)):
        want = "蓝图卡#BC" + ref
        if want not in known_ids:
            issues.append("关联指针不可达: %s（库内无此卡；未产的请写「待产」而非编号）" % want)

    m = re.search(r"^##\s*依据\s*$", body, re.M)
    if not m:
        issues.append("body 缺 ## 依据 段，引文无法机验")
    else:
        seg = body[m.end():]
        stop = re.search(r"^##\s", seg, re.M)
        seg = seg[:stop.start()] if stop else seg
        quotes = re.findall(r"[「『]([^」』]{6,})[」』]", seg)
        if not quotes:
            issues.append("依据段无 「」 引串（schema §三 要求含原文引用）")
        for q in quotes:
            for p in _split_elisions(q):
                if not any(p in v for v in blob):
                    issues.append("引文回源失败: 「%s…」缺片段=%s" % (q[:24], p[:44]))
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card_dir")
    ap.add_argument("--source-root", default=os.path.expanduser("[记忆共享中心]/记忆蓝图"))
    a = ap.parse_args()
    d = os.path.expanduser(a.card_dir)
    # ⛔不按文件名前缀筛卡——命名不规范的卡会静默漏检（与坑1「文件在、搜不到」同族病）；
    #   统一扫 *.md，由 verify_card 按 frontmatter type==blueprint-card 判定，跳过项计数可见。
    if os.path.isfile(d):
        files = [d]
    else:
        files = sorted(glob.glob(os.path.join(d, "*.md")))
    cards = files
    known = frozenset()
    for c in cards:
        try:
            fm0, _ = parse_frontmatter(open(c, encoding="utf-8").read())
        except Exception:
            continue
        if fm0.get("type") == "blueprint-card" and fm0.get("card_id"):
            known = known | {str(fm0["card_id"])}
    if not cards:
        print("⚠️ 目录内无 .md——本件判「未验证」而非「通过」（空集≠绿·防假绿）")
        return 1
    red = 0
    checked = 0   # 实验数（分母只算 blueprint-card，⛔把跳过项计入分母=假绿读数）
    skipped = []
    for c in cards:
        iss = verify_card(c, a.source_root, known)
        if iss is None:
            skipped.append(os.path.basename(c))
            continue
        checked += 1
        name = os.path.basename(c)
        if iss:
            red += 1
            print("⛔ %s" % name)
            for i in iss:
                print("   - %s" % i)
        else:
            print("✅ %s：引文全可回源 + 节锚全可达" % name)
    print("\n蓝图卡真值机检：%d/%d 绿（实验 %d 张·跳过非 blueprint-card %d 个%s）"
          % (checked - red, checked, checked, len(skipped),
             "：" + ", ".join(skipped[:5]) + ("…" if len(skipped) > 5 else "") if skipped else ""))
    if checked == 0:
        print("⚠️ 实验 0 张——没有卡可验时本件不得报绿（防空转假通过）")
        return 1
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
