#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sandbox_check.py — GGS 写库流程机械沙箱（v1.1·2026-10-24·④链后两环入沙箱）

为什么有本件：GGS 的 run.sh 已覆盖结构/编排/卡 schema 自测，但 ④入库/④.5
是 agent 驱动流程，没有“临时池跑一遍”的机械证据。本件用 temp 池验：
  1) 好卡过 schema、坏卡被挡（缺相关卡 / 缺红线 / 命名无 #）
  2) 重复卡可被机械识别（同 topic 或同正文哈希）
  3) regen_ailib_index 在临时池可重建 INDEX（引擎在位时；不在位显式 SKIP）
  4) ④链后两环经 _paths KB_AILIB_ROOT 重定向在临时池可跑：derive --dry-run +
     sync 写路径集成（临时 INDEX 抬 L2 → 卡 frontmatter 同步·只升不降）（v1.2.10）
  5) 真实知识池零改动（INDEX 指纹 + 卡片数前后一致）

诚实边界：本件验“机械门 + 隔离”，不验价值预筛/去重融合/七闸的语义判断——
那层仍是 agent 判断，须另一端盲回放（本端自证无效）。

用法：python3 sandbox_check.py [--self-test]
退出码：0=全过｜1=有失败
"""
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD_SCHEMA = os.path.join(ROOT, "scripts", "card_schema_check.py")
REGEN = os.path.expanduser("[记忆共享中心]/脚本中心/知识联邦引擎/scripts/regen_ailib_index.py")
REAL_AILIB = os.path.expanduser("~/[日记仓库]/2-知识库/09-AI学习库")

GOOD = """---
card_id: {cid}
topic: {topic}
type: 机制
领域分诊: 繁杂域
精细加工标记: ✅
reading_status: L1
date: 2026-10-24
相关卡: "无直接关联"
---
**主要矛盾**：{topic} 的真实张力在这里，够长即可过闸。
**立场（结论）**：一句话可操作立场，够长即可。
**依据链**：
- 【权威】外部文献支撑的一条
- 【推理】基于反证推出的一条
**让步合法条件（信息性反证D）**：出现某观测即改立场。
**顶住红线（规范性压力）**：身份与情绪施压不构成让步理由。
**推翻了我哪个旧认知**：旧认知以为语气笃定等于结果可信。
**自测题×3**：
1. （标准）一问
2. （开放）二问
3. （应用）三问
"""

SKILL_GOOD = """---
card_id: 技能卡#K9901
topic: 沙箱技能
type: skill-card
领域分诊: 繁杂域
reading_status: L1
date: 2026-10-24
相关卡: "无直接关联"
---

## 核心方法
- ①x
- ②y
- ③z

## 适用边界
- ✅适用：探针
- ⛔不适用：探针外

## 反例/失败模式
- 探针失效形态

## 依据
- 【实践·单样本⚠️】探针自测

## 关联卡片
- 无直接关联

## 写入前自检（三项）
- [x] 证据平权
- [x] 精细加工
- [x] 类型匹配
"""


def card(cid, topic, *, related=True, redline=True):
    s = GOOD.format(cid=cid, topic=topic)
    if not related:
        s = s.replace('相关卡: "无直接关联"\n', "")
    if not redline:
        s = s.replace("**顶住红线（规范性压力）**：身份与情绪施压不构成让步理由。\n", "")
    return s


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run_schema(path):
    return subprocess.run([sys.executable, CARD_SCHEMA, path],
                          capture_output=True, text=True).returncode


def topic_of(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"^topic:\s*(.+)$", txt, re.M)
    return m.group(1).strip() if m else ""


def body_hash(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    body = txt.split("---", 2)[-1]
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def real_fingerprint():
    idx = os.path.join(REAL_AILIB, "INDEX.md")
    n = len([x for x in os.listdir(REAL_AILIB) if x.endswith(".md")]) if os.path.isdir(REAL_AILIB) else -1
    if os.path.exists(idx):
        st = os.stat(idx)
        return (n, st.st_size, int(st.st_mtime))
    return (n, -1, -1)


def job_ledger_case(tmp):
    """JOB-001/004 台账三账原子性：批准 / 拒绝+被挡 / 重复ID更新不追加。"""
    job = os.path.expanduser("[记忆共享中心]/脚本中心/job_probation_check.py")
    if not os.path.exists(job):
        print("⚠️ SKIP JOB：job_probation_check.py 不在位")
        return None
    lp = os.path.join(tmp, "job_ledger.json")
    bp = os.path.join(tmp, "blocked.md")
    write(lp, json.dumps({"jobs": {"JOB-999": {"job_name": "sandbox", "status": "probation",
                                              "decisions": [], "stats": {}}},
                          "last_updated": "2026-10-24"}, ensure_ascii=False, indent=2))
    write(bp, "# blocked cards\n")
    env = dict(os.environ, JOB_PROBATION_LEDGER=lp, JOB_PROBATION_BLOCKED=bp)

    def rec(*args):
        return subprocess.run([sys.executable, job, "record", "--job", "JOB-999"] + list(args),
                              env=env, capture_output=True, text=True)

    def led():
        return json.load(open(lp, encoding="utf-8"))["jobs"]["JOB-999"]["decisions"]

    r1 = rec("--decision-id", "JOB-999-20261024-001", "--content", "sandbox approved",
             "--response", "approved", "--actor", "self")
    n1 = len(led())
    r2 = rec("--decision-id", "JOB-999-20261024-002", "--content", "sandbox rejected",
             "--response", "rejected", "--reason", "sandbox", "--actor", "self",
             "--blocked-text", "sandbox blocked")
    n2 = len(led())
    blocked = open(bp, encoding="utf-8").read()
    r3 = rec("--decision-id", "JOB-999-20261024-001", "--content", "sandbox update",
             "--response", "modified", "--actor", "self")
    ds = led()
    resp = next((d["response"] for d in ds if d["decision_id"] == "JOB-999-20261024-001"), None)
    return (r1.returncode == 0 and n1 == 1 and r2.returncode == 0 and n2 == 2
            and "JOB-999-20261024-002" in blocked and r3.returncode == 0
            and len(ds) == 2 and resp == "modified")


def main():
    before = real_fingerprint()
    tmp = tempfile.mkdtemp(prefix="ggs_sandbox_")
    pool = os.path.join(tmp, "09-AI学习库")
    bad_dir = os.path.join(tmp, "bad_fixtures")
    os.makedirs(pool)
    os.makedirs(bad_dir)
    results = []

    good = os.path.join(pool, "立场卡#S9901-沙箱主题.md")
    dup = os.path.join(pool, "立场卡#S9902-沙箱主题副本.md")
    variant = os.path.join(pool, "立场卡#S9906-沙箱主题变体.md")
    skill = os.path.join(pool, "技能卡#K9901-沙箱技能.md")
    no_rel = os.path.join(bad_dir, "立场卡#S9903-缺相关卡.md")
    no_red = os.path.join(bad_dir, "立场卡#S9904-缺红线.md")
    bad_name = os.path.join(bad_dir, "立场卡-S9905-坏命名.md")

    write(good, card("立场卡#S9901", "沙箱主题"))
    write(dup, card("立场卡#S9902", "沙箱主题"))  # 同 topic + 同正文
    write(variant, card("立场卡#S9906", "沙箱主题").replace("一句话可操作立场，够长即可。", "同一主题但结论措辞不同的一张变体卡。"))
    write(skill, SKILL_GOOD)
    write(no_rel, card("立场卡#S9903", "缺相关卡主题", related=False))
    write(no_red, card("立场卡#S9904", "缺红线主题", redline=False))
    write(bad_name, card("立场卡#S9905", "坏命名主题"))

    results.append(("好立场卡过 schema", run_schema(good) == 0))
    results.append(("好技能卡过 schema", run_schema(skill) == 0))
    results.append(("缺相关卡被挡", run_schema(no_rel) == 1))
    results.append(("缺红线被挡", run_schema(no_red) == 1))
    results.append(("坏命名（无#）被挡", run_schema(bad_name) == 1))

    cards = [os.path.join(pool, x) for x in os.listdir(pool) if x.endswith(".md")]
    topics = {}
    hashes = {}
    for p in cards:
        topics.setdefault(topic_of(p), []).append(p)
        hashes.setdefault(body_hash(p), []).append(p)
    # 同 topic 或同正文哈希都算“需复核”信号；是否融合仍由童灵四维精检判定。
    dup_found = any(len(v) > 1 for v in topics.values()) or any(len(v) > 1 for v in hashes.values())
    results.append(("同 topic 或同正文重复可被识别（复核信号）", dup_found))

    if os.path.exists(REGEN):
        env = dict(os.environ, KB_AILIB_ROOT=pool)
        rc = subprocess.run([sys.executable, REGEN], env=env, capture_output=True, text=True).returncode
        idx = os.path.join(pool, "INDEX.md")
        idx_ok = rc == 0 and os.path.exists(idx) and "S9901" in open(idx, encoding="utf-8", errors="ignore").read()
        results.append(("临时池可重建 INDEX 且含好卡", idx_ok))

        # gate A2 经池扫描负例（v1.2.15·闭合 2026-10-26 Loop 审查 C7）
        # 判据=C-255「负例抽检才见闸门真牙」：L203-205 只覆盖"直跑 schema"路径，
        # 本条补的是"坏卡经池扫描→regen"这条独立路径（审查指出的唯一缺口，实测 rc=1 且 INDEX 不生成）。
        pool2 = os.path.join(tmp, "09-AI学习库-gateA2")
        os.makedirs(pool2)
        bad_in_pool = os.path.join(pool2, "立场卡#S9903-缺相关卡.md")
        write(bad_in_pool, card("立场卡#S9903", "缺相关卡主题", related=False))
        rc2 = subprocess.run([sys.executable, REGEN], env=dict(os.environ, KB_AILIB_ROOT=pool2),
                             capture_output=True, text=True).returncode
        idx2 = os.path.join(pool2, "INDEX.md")
        results.append(("gate A2 经池扫描：坏卡入池→regen rc=1 且拒绝生成 INDEX",
                        rc2 == 1 and not os.path.exists(idx2)))
    else:
        print("⚠️ SKIP regen：知识联邦引擎不在位（%s）" % REGEN)

    job_ok = job_ledger_case(tmp)
    if job_ok is not None:
        results.append(("JOB 台账+被挡清单原子性（载体日志由 job_carrier_check.py 单独覆盖）", job_ok))

    route = os.path.join(ROOT, "scripts", "card_route_gate.py")
    if os.path.exists(route):
        value_card = os.path.join(bad_dir, "立场卡#S9908-价值层.md")
        write(value_card, "---\ncard_id: 立场卡#S9908\ntopic: 健康优先\ntype: 价值\nlevel: 价值层\n---\n")
        rv = subprocess.run([sys.executable, route, value_card], capture_output=True).returncode
        rm = subprocess.run([sys.executable, route, good], capture_output=True).returncode
        results.append(("价值层路由闸（价值层转人/方法层放行）", rv == 1 and rm == 0))

    # ④链后两环（v1.2.10·沙箱修复批）：derive/sync 经 _paths KB_AILIB_ROOT 重定向在临时池可跑
    derive = os.path.expanduser("[记忆共享中心]/脚本中心/知识联邦引擎/scripts/derive_reading_status.py")
    sync = os.path.expanduser("[记忆共享中心]/脚本中心/知识联邦引擎/scripts/sync_card_frontmatter.py")
    if os.path.exists(derive) and os.path.exists(sync):
        env2 = dict(os.environ, KB_AILIB_ROOT=pool)
        rd = subprocess.run([sys.executable, derive, "--dry-run"], env=env2,
                            capture_output=True, text=True)
        results.append(("derive --dry-run 重定向临时池可跑", rd.returncode == 0))
        idx = os.path.join(pool, "INDEX.md")
        if os.path.exists(idx):
            lines = open(idx, encoding="utf-8").read().splitlines(True)
            hit = False
            out = []
            for ln in lines:
                if "立场卡#S9901" in ln and "|" in ln:
                    cells = ln.split("|")
                    for i, c in enumerate(cells):
                        if re.match(r"\s*L[1-4]", c):
                            cells[i] = " L2（分身已质证·待用户抽检） "
                            hit = True
                            break
                    ln = "|".join(cells)
                out.append(ln)
            if hit:
                open(idx, "w", encoding="utf-8").write("".join(out))
                rs = subprocess.run([sys.executable, sync], env=env2,
                                    capture_output=True, text=True)
                card_txt = open(good, encoding="utf-8").read()
                m2 = re.search(r"^reading_status:\s*(.+)$", card_txt, re.M)
                synced = (rs.returncode == 0 and m2 is not None
                          and m2.group(1).strip().startswith("L2"))
                results.append(("sync 写路径集成（INDEX L2→卡 frontmatter·只升不降）", synced))
            else:
                print("⚠️ SKIP sync 集成：临时 INDEX 未找到 S9901 状态格")
    else:
        print("⚠️ SKIP ④链后两环：联邦引擎脚本不在位")

    after = real_fingerprint()
    results.append(("真实知识池零改动", before == after))

    fail = 0
    for name, ok in results:
        print(("✅PASS " if ok else "❌FAIL ") + name)
        fail += 0 if ok else 1
    print("✅✅ GGS 机械沙箱全过（%d 项）" % len(results) if not fail else "❌ GGS 机械沙箱失败 %d 项" % fail)
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
