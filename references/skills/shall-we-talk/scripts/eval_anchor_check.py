#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_anchor_check.py — SWT eval 迁移 token 常驻校验（v1.7.0·规范§08迁移纪律#5）

只证「关键断言 token 仍在现位」，不证语义全对；语义仍由 eval + 人眼承担。
用法：python3 eval_anchor_check.py [--self-test]
退出码：0=全在｜1=缺件/缺 token｜2=用法
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
CHECKS = [
    ("SKILL.md", "铁律"), ("SKILL.md", "触发条件"), ("SKILL.md", "四层契约"),
    ("SKILL.md", "六道锁"), ("SKILL.md", "禁止行为"), ("SKILL.md", "T5"),
    ("SKILL.md", "问题生成声明"), ("SKILL.md", "[深度X/4·层名]"), ("SKILL.md", "收获门"),
    ("references/flow-talk.md", "启动门禁"), ("references/flow-talk.md", "追问引擎"),
    ("references/flow-talk.md", "双角色"), ("references/flow-talk.md", "盘点点机制"),
    ("references/flow-talk.md", "对话控制台与接力结构"), ("references/flow-talk.md", "重力判定"),
    ("references/flow-talk.md", "行为方式模型"), ("references/flow-talk.md", "Layer1.5"),
    ("references/flow-sediment.md", "锁一"), ("references/flow-sediment.md", "锁六"),
    ("references/flow-sediment.md", "Step 4.5"), ("references/flow-sediment.md", "终身记忆"),
    ("references/flow-review.md", "阅读复习模式"), ("references/flow-review.md", "间隔参数"),
    ("references/flow-review.md", "无题库降级"),
    ("references/t5-defense-assessment.md", "## 🛡️ T5对抗性防御声明"),
    ("references/t5-defense-assessment.md", "### 11. 抗渐进侵蚀声明"),
]


def check(root):
    bad = []
    for rel, tok in CHECKS:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            bad.append("%s 缺失" % rel); continue
        if tok not in open(p, encoding="utf-8", errors="ignore").read():
            bad.append("%s 缺 token「%s」" % (rel, tok))
    return bad


def _self_test():
    import tempfile
    root = tempfile.mkdtemp(prefix="evalanchor_")
    for rel, tok in CHECKS:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(tok + "\n")
    p1 = check(root)
    print(("✅" if not p1 else "❌") + " P1 全 token 在场 → 通过")
    # 负例：删掉一个 token
    p = os.path.join(root, CHECKS[0][0])
    txt = open(p, encoding="utf-8").read().replace(CHECKS[0][1], "")
    open(p, "w", encoding="utf-8").write(txt)
    p2 = check(root)
    print(("✅" if p2 else "❌") + " N1 删 token 必须被抓（bad=%d）" % len(p2))
    ok = (not p1) and bool(p2)
    print("✅✅ --self-test 全过" if ok else "❌ --self-test 有项不过")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv[1:]:
        return _self_test()
    if sys.argv[1:]:
        print("error: 未知参数", file=sys.stderr); return 2
    bad = check(ROOT)
    if bad:
        print("❌ eval 迁移 token 校验：%d 项缺失" % len(bad))
        for b in bad: print("   ·", b)
        return 1
    print("✅ eval 迁移 token 全在（%d 项）" % len(CHECKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
