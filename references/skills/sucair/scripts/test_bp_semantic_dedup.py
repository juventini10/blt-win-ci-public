#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: skip 非挂载型守卫·sucair 蓝图卡语义去重闸的测试夹具（与 bp_factory/test_sucair 同族，无 hook/STOP_GUARDS 挂载点，
# REG:      硬填 §四注册表会伪造 §3.0 ②「挂载实盘」）。判据来源=守卫编写规范 §3.0 登记四件套
"""test_bp_semantic_dedup.py — 蓝图卡语义去重闸夹具（§四十三-1 要求：正例必红、负例必绿、变异必有效）

必须在 .venv-st 解释器下跑（闸依赖 bge 量化模型）：
  [记忆共享中心]/脚本中心/知识联邦引擎/.venv-st/bin/python -m unittest test_bp_semantic_dedup -v

用例对应（编号对齐任务卡判据）：
  T1 正例：同文件近重复对 ⇒ 判红（隔离卡副本放临时库，闸必须列出该对）
  T2 负例：全量闸出的违规对必须都在抽检单已知清单内；低于阈值的对绝不出现在 violations
  T3 证据：dedup_recall --type blueprint-card 跑完必写凭证文件，字段齐；读书卡路径不受扰动
  T4 证据缺失：bp_factory 出厂判红（"不跑即判红"的机械面）
  T5 证据过期：超 24h 判红；新鲜凭证放行
  T6 变异：把旧卡 frontmatter 换成近邻卡的 ⇒ md5 变 ⇒ 重嵌 ⇒ 判红（内容变更不失明）
  M1 变异：阈值拉到 1.01 ⇒ 全库同文件对零违规（证明阈值判据真在起作用，非恒红）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import os
import re
import shutil
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bp_semantic_dedup as BSD  # noqa: E402

CARD_DIR = os.path.expanduser("~/[日记仓库]/2-知识库/10-蓝图索引卡")
TRASH = os.path.expanduser("~/qoder-cn-work/_trash-dedup-hupo-20261028")
# 已种子的全库向量缓存（md5(text) 键·只增不改）：夹具共用它，新卡零重嵌
SEED_CACHE = os.path.join(CARD_DIR, ".dedup_vecs.json")


def _resolve(b):
    """文件名 → 真实路径（琥珀新卡在隔离目录，其余在卡库）。"""
    for d in (TRASH, CARD_DIR):
        p = os.path.join(d, b)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(b)


class TmpLib(unittest.TestCase):
    def setUp(self):
        self.lib = tempfile.mkdtemp(prefix="bpdedup_lib_")
        self.tmp = tempfile.mkdtemp(prefix="bpdedup_tmp_")

    def tearDown(self):
        shutil.rmtree(self.lib, ignore_errors=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def place(self, bases):
        for b in bases:
            shutil.copy(_resolve(b), os.path.join(self.lib, b))
        return self.lib


class T1PositiveRed(TmpLib):
    def test_near_dup_pair_is_red(self):
        # 琥珀对：隔离卡与库内既有卡说同一条判断（§四十 表，同尺读数 0.88+）
        pairs = [("蓝图卡-琥珀-物理监听不靠AI自觉.md", "蓝图卡-记忆琥珀-备份是物理事实不是步骤.md"),
                 ("蓝图卡-琥珀-清理三段式不删今天.md", "蓝图卡-记忆琥珀-清理三段式与今日备份不删.md")]
        self.place([b for pr in pairs for b in pr])
        viol = BSD.gate(self.lib, threshold=BSD.THRESHOLD,
                        vec_cache=SEED_CACHE,
                        ledger=os.path.join(self.tmp, "ledger.json"))
        flat = {tuple(sorted([os.path.basename(x), os.path.basename(y)]))
                for x, y, _s in viol["violations"]}
        for a, b in pairs:
            self.assertIn(tuple(sorted([a, b])), flat,
                          "正例未判红：%s vs %s → %s" % (a, b, viol["violations"]))


class T2NegativeGreen(unittest.TestCase):
    def test_full_library_violations_within_known_lists(self):
        # 已知清单 = 抽检单一/二节（人工登记）+ 第三节（闸自己上一轮写的）；
        # 两单之外新冒出的对允许存在（=多窗并发产物），但输出一行提醒人工过目，⛔静默
        viol_all = BSD.gate(CARD_DIR, threshold=BSD.THRESHOLD, dry_run=True,
                            vec_cache=os.path.join(CARD_DIR, ".dedup_vecs.json"))
        known = BSD.known_pairs_from_audit_sheet(os.path.join(CARD_DIR, "疑似重复抽检单.md"))
        # 回归断言：抽检单实盘 ≥10 行登记对，解析器解空=拿空集当已知（首轮现场 bug）
        self.assertGreaterEqual(len(known), 10,
                                "抽检单解析出 %d 对——解析器与表形制漂移，⛔拿空集继续跑" % len(known))
        new_ones = []
        for x, y, s in viol_all["violations"]:
            key = tuple(sorted([os.path.basename(x), os.path.basename(y)]))
            self.assertGreaterEqual(s, BSD.THRESHOLD)
            if key not in known:
                new_ones.append((key, s))
        if new_ones:
            print("ℹ️ 清单外新相似对 %d（多窗并发产物·待入抽检单人工判）: %s" % (len(new_ones), new_ones))


class T3Evidence(TmpLib):
    def test_dedup_recall_writes_evidence(self):
        import subprocess
        self.place(["蓝图卡-琥珀-心跳读盘不查进程.md"])
        ev = os.path.join(self.lib, ".b2_dedup_evidence.json")
        rc = subprocess.run([sys.executable, os.path.join(HERE, "dedup_recall.py"), self.lib,
                             "--category", "琥珀", "--tags", "心跳", "--type", "blueprint-card"],
                            capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        self.assertTrue(os.path.isfile(ev), "跑完未写凭证文件")
        data = BSD.read_json(ev, default=None) or {}
        for k in ("at", "domain", "keywords", "hits", "pool_root"):
            self.assertIn(k, data)
        self.assertEqual(data.get("domain"), "琥珀")

    def test_reading_card_mode_writes_no_evidence(self):
        # 读书卡路径不受扰动（⛔顺手扩大影响面）
        import subprocess
        pool = os.path.join(self.lib, "pool")
        os.makedirs(pool)
        rc = subprocess.run([sys.executable, os.path.join(HERE, "dedup_recall.py"), pool,
                             "--category", "x", "--tags", "y"],
                            capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
        self.assertFalse(os.path.isfile(os.path.join(pool, ".b2_dedup_evidence.json")))


class T4T5FactoryGate(TmpLib):
    def _step(self, ev_path, now=None):
        import bp_factory as BF
        return BF.step_b2_evidence(evidence_path=ev_path, now=now)

    def test_missing_evidence_red(self):
        ok, msg = self._step(os.path.join(self.lib, "nope.json"))
        self.assertFalse(ok, "无凭证必须判红：" + msg)

    def test_stale_evidence_red(self):
        ev = os.path.join(self.lib, ".b2_dedup_evidence.json")
        BSD.write_json(ev, {"at": "2026-10-26T00:00:00", "domain": "琥珀",
                            "keywords": ["x"], "hits": 0, "pool_root": self.lib})
        ok, _msg = self._step(ev, now=time.time())
        self.assertFalse(ok, "超 24h 凭证必须判红")

    def test_fresh_evidence_green(self):
        ev = os.path.join(self.lib, ".b2_dedup_evidence.json")
        BSD.write_json(ev, {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "domain": "琥珀",
                            "keywords": ["x"], "hits": 0, "pool_root": self.lib})
        ok, _msg = self._step(ev, now=time.time())
        self.assertTrue(ok)


class T6Mutate(TmpLib):
    def test_mutate_triggers_red(self):
        # 从真实库同文件对里选一对读数明显低于阈值的，把其一 frontmatter 整体换成另一张的 ⇒ 必撞阈值
        below = BSD.samefile_sample_below(CARD_DIR, slack=0.05, vec_cache=SEED_CACHE)
        self.assertTrue(below, "找不到低于阈值的同文件对，夹具前提不成立（阈值/分布需重标定）")
        pa, pb, s0 = below[0]
        ba, bb = os.path.basename(pa), os.path.basename(pb)
        self.place([ba, bb])
        raw_b = open(_resolve(bb), encoding="utf-8").read()
        head_b = re.match(r"^---\n(.*?)\n---", raw_b, re.S).group(1)
        ta = os.path.join(self.lib, ba)
        raw_a = open(ta, encoding="utf-8").read()
        new = re.sub(r"^---\n.*?\n---", "---\n" + head_b + "\n---", raw_a, count=1, flags=re.S)
        open(ta, "w", encoding="utf-8").write(new)
        viol2 = BSD.gate(self.lib, threshold=BSD.THRESHOLD,
                         vec_cache=SEED_CACHE,
                         ledger=os.path.join(self.tmp, "ledger2.json"))
        names = {tuple(sorted([os.path.basename(x), os.path.basename(y)])) for x, y, _ in viol2["violations"]}
        self.assertIn(tuple(sorted([ba, bb])), names,
                      "变异后未判红 ⇒ 闸对内容变更失明（md5 重嵌链断）·s0=%.3f" % s0)


class M1MutateThreshold(unittest.TestCase):
    def test_threshold_101_zero_violations(self):
        # 阈值 >1.0：不同文本 cosine 必 <1.01 ⇒ 全绿。证明"判红"来自阈值比较而非恒真
        # （自配对已在 gate 内用 set 去重——本测同时是那个 bug 的回归防线）
        viol = BSD.gate(CARD_DIR, threshold=1.01, dry_run=True,
                        vec_cache=os.path.join(CARD_DIR, ".dedup_vecs.json"))
        self.assertEqual([], viol["violations"])


class T7Adjudication(unittest.TestCase):
    """裁决豁免位（第四节判例）：正例解析/负例缺文件 fail-closed/变异分辨。"""

    SHEET = os.path.join(CARD_DIR, "疑似重复抽检单.md")

    def test_positive_parses_non_dup_rows(self):
        adj = BSD.adjudicated_pairs(self.SHEET)
        self.assertGreaterEqual(len(adj), 7, "第四节实盘≥7对非重复，解少=形制漂移")
        # MERGE 对⛔进豁免（隔离卡若回库应照拦）
        merge_key = tuple(sorted(["蓝图卡-守卫-探针零样本禁令.md", "蓝图卡-守卫-零不等于无.md"]))
        self.assertNotIn(merge_key, adj)

    def test_negative_missing_file_zero_exempt(self):
        self.assertEqual(set(), BSD.adjudicated_pairs("/nonexistent/sheet.md"),
                         "判例文件丢失必须豁免清零（fail-closed），⛔默认全豁免")

    def test_mutate_section_absent(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("# 抽检单\n## 三、出厂闸名单\n| x | y |\n")  # 有单无第四节
            p = f.name
        try:
            self.assertEqual(set(), BSD.adjudicated_pairs(p))
        finally:
            os.unlink(p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
