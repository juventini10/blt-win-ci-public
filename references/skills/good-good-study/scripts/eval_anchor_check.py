#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_anchor_check.py — GGS 架构迁移 token 常驻校验（v1.2.0·规范§08迁移纪律#5）"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
CHECKS = [
    ("SKILL.md","铁律"),("SKILL.md","触发条件"),("SKILL.md","四层契约"),
    ("SKILL.md","禁止行为"),("SKILL.md","T5"),("SKILL.md","Poka-Yoke"),("SKILL.md","产出模板"),
    ("references/a-line-lineup.md","JOB-001"),("references/a-line-lineup.md","分层终审"),
    ("references/a-line-lineup.md","去重/融合验收"),
    ("references/skill-card-pipeline.md","JOB-004"),("references/skill-card-pipeline.md","七闸"),
    ("references/skill-card-pipeline.md","候选格式"),
    ("references/release-deps.md","知识联邦引擎"),
    ("references/t5-defense-assessment.md","## 🛡️ T5对抗性防御声明"),
    ("references/t5-defense-assessment.md","### 11. 抗渐进侵蚀声明"),
]
def check(root):
    bad=[]
    for rel,tok in CHECKS:
        p=os.path.join(root,rel)
        if not os.path.isfile(p): bad.append(rel+" 缺失"); continue
        if tok not in open(p,encoding="utf-8",errors="ignore").read():
            bad.append("%s 缺 token「%s」" % (rel,tok))
    return bad
def _self_test():
    import tempfile
    root=tempfile.mkdtemp(prefix="ggsanchor_")
    for rel,tok in CHECKS:
        p=os.path.join(root,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,"a",encoding="utf-8").write(tok+"\n")
    p1=check(root)
    p=os.path.join(root,CHECKS[0][0]); txt=open(p,encoding="utf-8").read().replace(CHECKS[0][1],"")
    open(p,"w",encoding="utf-8").write(txt)
    p2=check(root)
    ok=(not p1) and bool(p2)
    print(("✅" if not p1 else "❌")+" P1 全 token 在场 → 通过")
    print(("✅" if p2 else "❌")+" N1 删 token 必须被抓（bad=%d）" % len(p2))
    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1
def main():
    if "--self-test" in sys.argv[1:]: return _self_test()
    bad=check(ROOT)
    if bad:
        print("❌ eval 迁移 token 校验：%d 项缺失" % len(bad))
        for b in bad: print("   ·",b)
        return 1
    print("✅ eval 迁移 token 全在（%d 项）" % len(CHECKS)); return 0
if __name__=="__main__": sys.exit(main())
