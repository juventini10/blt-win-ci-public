#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_negative_mutate.py — 负例有牙常驻测试（B4 收编·2026-10-23）：九连变异（orchestration 五连 + parity 三连 + anchor 一连）+ 正例对照。
纪律：变异全在 /tmp 副本，活体零触碰；每例期望 rc=1（红）；未变异对照期望 rc=0（绿）。
任一变异不红=该闸没牙（本测试判 FAIL）；对照不绿=闸恒真误报（同判 FAIL）。"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import io, os, shutil, subprocess, sys, tempfile

GB = os.path.expanduser("[记忆共享中心]/技能配置/growth-box")
SCR = os.path.join(GB, "scripts")

def clone():
    d = tempfile.mkdtemp(prefix="gb-mut-")
    shutil.copytree(os.path.join(GB, "references"), os.path.join(d, "references"))
    shutil.copy(os.path.join(GB, "SKILL.md"), os.path.join(d, "SKILL.md"))
    return d

def skill(d):
    return os.path.join(d, "SKILL.md")

def edit(d, fn):
    p = skill(d)
    t = io.open(p, encoding="utf-8").read()
    t2 = fn(t)
    assert t2 != t, "变异未生效（替换串不命中）"
    io.open(p, "w", encoding="utf-8").write(t2)

def run(gate, d, extra=None):
    cmd = ["python3", os.path.join(SCR, gate), "--skill-root", d]
    if extra:
        cmd += extra
    return subprocess.run(cmd, capture_output=True, text=True).returncode

# ---- 九个变异函数 ----
def m_del(t):   # M1 删节：指路牌删"判断标准"行
    return t.replace("| 查状态语义/协作/安全/来源对照表 | `## 参考对照（判断标准·Skill 关系·安全对照·来源）` |\n", "")
def m_ghost(t):  # M2 幽灵节
    return t.replace("| 理解功能定位 |", "| 查不存在的节 | `## 幽灵节不存在` |\n| 查规范来源 |", 1)
def m_front(t):  # M3 模板前移：骨架节整体搬到铁律声明前（行首锚定⛔命中指路牌指针串——同坑第三回，本轮预先排雷）
    import re as _re
    s = _re.search(r"^## 📦 呈现层三块式骨架.*$", t, _re.M).start()
    e = _re.search(r"^## 🔌 强制 Read 熔断器.*$", t, _re.M).start()
    block = t[s:e]
    rest = t[:s] + t[e:]
    k = _re.search(r"^## ⚠️ 铁律声明.*$", rest, _re.M).start()
    return rest[:k] + block + rest[k:]
def m_lineno(t):  # M4 行号锚
    return t.replace("> 三纪律：①按节名指路", "> 细则见 L451 区间\n> 三纪律：①按节名指路", 1)
def m_near(t):  # M10 模板节被搬到 65-70% 区间（§13.1 成文≥70%·证 0.70 阈值有牙非装饰）
    import re as _re
    body=t
    heads=[m.start() for m in _re.finditer(r"^## ", body, _re.M)]
    s0=[h for h in heads if body[h:h+40].find("呈现层三块式骨架")>=0][0]
    e0=min([h for h in heads if h>s0], default=len(body))
    blk=body[s0:e0]; rest=body[:s0]+body[e0:]
    target=int(len(body.splitlines())*0.67)
    hs=[h for h in _re.finditer(r"^## .*$", rest, _re.M) if rest[:h.start()].count("\n")+1 >= target]
    k=hs[0].start() if hs else len(rest)
    return rest[:k]+blk+rest[k:]
def m_over(t):    # M5 超行（580 上限 → +300 行）
    return t + "\n".join("填充行 %d" % i for i in range(300))
def p_quad(t):    # M6 parity 四元组篡改
    return t.replace("A4／B5／C7／E14", "A4／B5／C8／E14", 1)
def p_oldform(t): # M7 旧形态回流（定住真实节行⛔误中指路牌反引号内同串）
    return t.replace("\n## 参考对照（判断标准·Skill 关系·安全对照·来源）\n", "\n## 参考对照（判断标准·Skill 关系·安全对照·来源）\n\n通知箱处理见流程C。\n", 1)
def p_route(t):   # M8 路由表步数篡改
    return t.replace("（共 4 步·全序见 flow-A.md）", "（共 5 步·全序见 flow-A.md）", 1)
def a_deadref(t): # M9 anchor 死引用（ASCII 名——PATH_PAT 字符类不含中文，用中文名会假绿=仪器陷阱）
    return t.replace("references/CHANGELOG.md", "references/NOPE-not-here.md")

CASES = [
    ("M1 删节", "orchestration_gate.py", m_del),
    ("M2 幽灵节", "orchestration_gate.py", m_ghost),
    ("M3 模板前移", "orchestration_gate.py", m_front),
    ("M4 行号锚", "orchestration_gate.py", m_lineno),
    ("M5 超行", "orchestration_gate.py", m_over),
    ("M10 模板@67%边界", "orchestration_gate.py", m_near),
    ("M6 四元组篡改", "parity_check.py", p_quad),
    ("M7 旧形态回流", "parity_check.py", p_oldform),
    ("M8 路由表篡改", "parity_check.py", p_route),
    ("M9 死引用", "anchor_reach_check.py", a_deadref),
]

fails = []
# 正例对照：三闸对未变异副本全绿
for gate in ("orchestration_gate.py", "anchor_reach_check.py", "parity_check.py"):
    d = clone()
    rc = run(gate, d)
    tag = "对照-%s" % gate
    if rc != 0:
        fails.append("%s 不绿（闸恒真/误报）rc=%d" % (tag, rc))
        print("🔴", tag)
    else:
        print("✅ %s rc=0" % tag)
    shutil.rmtree(d)

# 九连变异：对应闸必红
for name, gate, fn in CASES:
    d = clone()
    edit(d, fn)
    rc = run(gate, d)
    if rc != 1:
        fails.append("%s 未红（闸没牙）rc=%d" % (name, rc))
        print("🔴", name, "rc=%d" % rc)
    else:
        print("✅ %s → %s 判红 rc=1" % (name, gate))
    shutil.rmtree(d)

print("=" * 40)
if fails:
    print("NEG:FAIL %d 项：" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("NEG:OK 对照 3/3 绿 + 变异 %d/%d 红（双向牙齿检验通过）" % (len(CASES), len(CASES)))
