#!/usr/bin/env python3
"""
dedup_recall.py — Step 2.0 去重合并门·确定性召回脚本（v4.0.0 · Wave 3 建）

职责（方案§5.4 ①）：按 category + tags 交集检索 05-知识池 已有卡片，
输出小候选集供 AI 做 ADD/MERGE/SKIP 语义判断。
⛔不做语义判断——可规则化的交脚本，需判断的交模型。

用法：
  python3 dedup_recall.py <知识池根目录> --category <领域> --tags "词1,词2,..."
输出：候选卡列表（路径+card_id+title+tags 交集命中数），exit 0；无候选输出 EMPTY。

实体归一（G4 落项）：比较前全部归一化——小写 + 去空格/连字符/下划线，
「Agent 记忆 / Agent记忆 / agent memory」类变体命中同一候选集。
"""
# Win console UTF-8 guard (auto by clock-loop 1.7.2)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
import argparse, os, re, sys

# 单一 frontmatter 解析器来源：note_validator.parse_frontmatter（v4.2.0 · L9 修复）
# ⛔DO NOT 在此文件再写一份 parse_frontmatter——v4.2.0 前这里有一份分叉实现，
# 缺类型还原且多行数组处理有 bug，与 note_validator 漂移导致召回口径不一致。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from note_validator import parse_frontmatter

def normalize(s: str) -> str:
    """G4 实体归一：小写 + 剥空格/连字符/下划线。"""
    return re.sub(r'[\s\-_]+', '', s.lower())

def recall(pool_root: str, category: str, tags: list) -> list:
    """category 归一相等 且 tags 归一交集非空 → 候选。"""
    cat_n = normalize(category)
    tags_n = {normalize(t) for t in tags if t.strip()}
    hits = []
    for root, _, files in os.walk(pool_root):
        for f in files:
            if not f.endswith('.md') or f == 'INDEX.md':
                continue
            p = os.path.join(root, f)
            try:
                fm, _ = parse_frontmatter(open(p, encoding='utf-8').read())
            except Exception:
                continue
            if fm.get('type') != 'reading-card':
                continue
            if normalize(fm.get('category', '')) != cat_n:
                continue
            # tags 在 note_validator 解析后为 list（多行/行内数组），也兼容旧式逗号字符串
            raw_tags = fm.get('tags', [])
            if isinstance(raw_tags, str):
                card_tags = {normalize(t) for t in re.split(r'[,，\[\]]', raw_tags) if t.strip()}
            else:
                card_tags = {normalize(str(t)) for t in raw_tags if str(t).strip()}
            inter = tags_n & card_tags
            if inter:
                hits.append((p, fm.get('card_id', f), fm.get('title', ''), len(inter), sorted(inter)))
    hits.sort(key=lambda h: -h[3])
    return hits

def recall_blueprint(pool_root: str, domain: str, keywords: list) -> list:
    """蓝图卡候选召回（2026-10-27 批次1）：domain 归一相等 + 关键词子串命中。

    判据与读书卡不同源：blueprint-card 无 category/tags 字段（schema §二），
    检索键 = domain + title/summary/core_principles 拼接文本的子串交集——
    近似卡（同域同主题）按命中关键词数降序返回，供 AI 做 ADD/MERGE/SKIP 语义判断。
    """
    dom_n = normalize(domain)
    hits = []
    for root, _, files in os.walk(pool_root):
        for f in files:
            if not f.endswith('.md'):
                continue
            p = os.path.join(root, f)
            try:
                fm, _ = parse_frontmatter(open(p, encoding='utf-8').read())
            except Exception:
                continue
            if fm.get('type') != 'blueprint-card':
                continue
            if normalize(str(fm.get('domain', ''))) != dom_n:
                continue
            text = normalize(" ".join([str(fm.get('title', '')), str(fm.get('summary', '')),
                                        " ".join(str(x) for x in (fm.get('core_principles') or []))
                                        if isinstance(fm.get('core_principles'), list)
                                        else str(fm.get('core_principles', ''))]))
            inter = [k for k in keywords if normalize(k) and normalize(k) in text]
            if inter:
                hits.append((p, str(fm.get('card_id', f)), str(fm.get('title', '')), len(inter), inter))
    hits.sort(key=lambda h: -h[3])
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pool_root')
    ap.add_argument('--category', required=True)
    ap.add_argument('--tags', required=True, help='逗号分隔')
    ap.add_argument('--type', default='reading-card', choices=['reading-card', 'blueprint-card'],
                    help='blueprint-card 时 --category 语义=domain，--tags 语义=主题关键词（子串匹配）')
    ap.add_argument('--probe', action='store_true',
                    help='探针模式（bp_factory 验闸可用性专用）：不写 B2 凭证，⛔拿自检冒充产卡证据')
    a = ap.parse_args()
    tags = [t for t in re.split(r'[,，]', a.tags) if t.strip()]
    hits = (recall_blueprint(a.pool_root, a.category, tags) if a.type == 'blueprint-card'
            else recall(a.pool_root, a.category, tags))
    if not hits:
        print('EMPTY — 候选为空，全部 ADD（按 dedup-merge-gate.md ③）')
    else:
        print(f'候选 {len(hits)} 张（按 tags 交集命中数降序）：')
        for p, cid, title, n, inter in hits:
            print(f'  [{n}命中] {cid or title}  tags∩={inter}  ← {p}')
    # B2 凭证（2026-10-28 任务卡 §四十三-2：「应跑」升「不跑即出厂判红」的机械面）：
    #   只给 blueprint-card 写——读书卡路径零扰动（test_bp_semantic_dedup T3b 守）。
    #   bp_factory --ship 查此件存在+新鲜度（≤24h），无/过期=判红。
    if a.type == 'blueprint-card' and not a.probe:
        import json as _json, datetime as _dt
        ev = os.path.join(a.pool_root, '.b2_dedup_evidence.json')
        try:
            _tmp = ev + '.tmp.%d' % os.getpid()
            _json.dump({'at': _dt.datetime.now().isoformat(timespec='seconds'),
                        'domain': a.category, 'keywords': tags, 'hits': len(hits),
                        'pool_root': os.path.abspath(a.pool_root)},
                       open(_tmp, 'w', encoding='utf-8'), ensure_ascii=False)
            os.replace(_tmp, ev)
            print('🧾 B2 凭证已写：%s' % ev)
        except OSError as e:
            print('⚠️ B2 凭证写入失败（%s）——出厂闸门将因无凭证判红，请先修目录权限' % e)

if __name__ == '__main__':
    main()
