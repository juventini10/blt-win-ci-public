#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""distill_due_core 负例测试（v8.3.3 补记 v8.3.1 声明的 5/5 负例实物·clock-loop E路径Loop逮补）

锚定 CHANGELOG v8.3.1 五条证据，today 钉死确定性可跑（不依赖真实台账内容）。
运行：python3 -m unittest test_distill_core -v
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import datetime
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "distill_due_core", Path(__file__).resolve().parent / "distill_due_core.py")
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

TODAY = datetime.date(2026, 10, 3)
TYPES = {"🧠 成长箱蒸馏": {"match": "成长箱蒸馏"},
         "📓 日记月报": {"match": "日记月报"},
         "📊 系统日志蒸馏": {"match": "系统日志蒸馏"},
         "🔄 统一蒸馏管道": {"match": "统一蒸馏管道"}}


def row(d, t, nxt):
    return "| %s | %s | 产物 | 摘要 | %s |" % (d, t, nxt)


class TestDistillCore(unittest.TestCase):

    def test_01_month_segment_multirow_take_last(self):
        """负例1·月段内多行取最后一行（旧due_check取第一行病·成长箱误报根因）"""
        content = "\n".join([row("2026-10-01", "🧠 成长箱蒸馏", "2026-12-31"),
                              row("2026-10-02", "🧠 成长箱蒸馏", "2026-11-01")])
        self.assertEqual(core.extract_expected(content, TYPES),
                         {"🧠 成长箱蒸馏": "2026-11-01"})

    def test_02_onetime_dash_silent(self):
        """负例2·一次性任务 `—` 静默，且⛔不许倒序回扫把执行日误当下次日"""
        only = row("2026-10-02", "🔄 统一蒸馏管道（3月补蒸馏）", "—")
        self.assertEqual(core.extract_expected(only, TYPES), {})
        with_valid = row("2026-09-30", "🔄 统一蒸馏管道", "2026-11-01") + "\n" + only
        self.assertEqual(core.extract_expected(with_valid, TYPES),
                         {"🔄 统一蒸馏管道": "2026-11-01"})

    def test_03_todo_region_excluded(self):
        """负例3·调度器自生成TODO区剔除（自读自写粘滞→假逾期）"""
        content = ("<!-- DISTILLATION-TODO:START -->\n"
                   + row("2026-10-03", "📓 日记月报", "2026-09-15")
                   + "\n<!-- DISTILLATION-TODO:END -->")
        self.assertEqual(core.extract_expected(content, TYPES), {})
        self.assertEqual(core.check_overdue(content, TYPES, TODAY), [])

    def test_04_cross_month_blindspot_eliminated(self):
        """负例4·旧月段独有类型仍可取到（scheduler旧版只扫最新月段盲区根治）"""
        content = ("# 2026-10\n" + row("2026-10-01", "🧠 成长箱蒸馏", "2026-11-01")
                   + "\n# 2026-09\n" + row("2026-09-05", "📊 系统日志蒸馏", "2026-11-01"))
        self.assertEqual(core.extract_expected(content, TYPES),
                         {"🧠 成长箱蒸馏": "2026-11-01", "📊 系统日志蒸馏": "2026-11-01"})

    def test_05_positive_four_types_zero_overdue(self):
        """正例·真实台账口径四类型全 2026-11-01 → today(10-03) 零逾期；括号后缀归并主类(5类假象不复发)"""
        content = "\n".join([row("2026-10-01", "🧠 成长箱蒸馏", "2026-11-01"),
                              row("2026-10-01", "📓 日记月报", "2026-11-01"),
                              row("2026-10-01", "📊 系统日志蒸馏", "2026-11-01"),
                              row("2026-10-01", "🔄 统一蒸馏管道（终审落地+勘误）", "2026-11-01")])
        self.assertEqual(core.check_overdue(content, TYPES, TODAY), [])
        self.assertEqual(len(core.extract_expected(content, TYPES)), 4)

    # ── v8.5.5 对偶夹具（2026-11-02·你「启动月度蒸馏=能做的全做完」根因修复）────────
    # 反向验证纪律（铁律-021①）：只测正例＝把尺变瞎。必须配对：
    #   负例＝他物冒充必绿（摘要提到本类型名 ≠ 本类型的账行）
    #   正例＝真声明必红（真账行不被新判据误杀）

    def test_06_dual_negative_other_type_mentions_this_one(self):
        """负例6·他行摘要提到本类型名 ⇒ 不得被当成本类型的账行

        2026-11-02 真盘实锤：`2026-11-01 | 📓 日记月报 | ✅ | …系统日志蒸馏… | 2026-12-01`
        这一行摘要含「系统日志蒸馏」六字 → 旧判据（整行 substring）把它误归给
        「📊 系统日志蒸馏」并取走末字段 2026-12-01 ⇒ 该类型整体隐身。

        ⚠️ 行序必须还原真盘（2026-11-02 自纠）：日记月报行在**文档中更靠后**，
        倒序扫描才先撞上它 → 误归才会发生。夹具若把它排前面，变异体不复现原病
        ⇒ 变异检验假绿（尺空转）。本用例行序 = 真盘行序（系统日志行在前·日记月报行在后）。
        """
        content = "\n".join([
            row("2026-10-01", "📊 系统日志蒸馏", "2026-11-01"),
            row("2026-11-01", "📓 日记月报", "2026-12-01"),
        ])
        got = core.extract_expected(content, TYPES)
        # 📊 系统日志蒸馏 必须取自己那行（2026-11-01），⛔ 不许拿日记月报的 2026-12-01
        self.assertEqual(got.get("📊 系统日志蒸馏"), "2026-11-01")
        self.assertEqual(got.get("📓 日记月报"), "2026-12-01")
        self.assertEqual(len(got), 2)

    def test_07_dual_positive_real_row_not_killed(self):
        """正例7·真声明不被新判据误杀（emoji 前缀/括号后缀都要能取到）"""
        content = "\n".join([
            row("2026-10-01", "🔄 统一蒸馏管道（终审落地+勘误）", "2026-11-01"),
            row("2026-10-01", "🧠 成长箱蒸馏", "2026-11-01"),
        ])
        got = core.extract_expected(content, TYPES)
        self.assertEqual(got.get("🔄 统一蒸馏管道"), "2026-11-01")
        self.assertEqual(got.get("🧠 成长箱蒸馏"), "2026-11-01")

    def test_08_mutation_old_judgement_is_caught(self):
        """变异检验·把判据改回「整行 substring」必须让负例6变红（证尺没空转）

        夹具用**真盘原文**（[记忆共享中心]/记忆蒸馏/蒸馏中心.md）——2026-11-02 自纠：
        最小夹具无法还原真盘的完整扫描条件（变异体在最小夹具上不复现原病），
        ⇒ 用真盘原文才是硬证据；真盘路径不存在时跳过（⛔不静默通过）。
        ⛔ **2026-11-03 二次自纠·「用真盘原文」≠「用真盘的值」**：
        11-03 实测两次假红，根因层层递进——
          ①第一次：断言写死 `"2026-11-01"`，而真盘「📊 系统日志蒸馏」11-03 已销账
            ⇒ 其「预期下次」滚到 **2026-12-01** ⇒ 夹具绑的是**会变的真盘快照**。
            （先试「期望值实读真盘当前行」——但引出②）
          ②第二次：真盘**所有类型的「预期下次」在月首都滚到同一天**（12-01）⇒
            变异体靠「整行 substring 扫到冒充行」取到的值**恰好与正确答案相同**
            ⇒ **变异体不再显形** ⇒ 变异检验假绿（尺空转）。
            病根＝**原病（取到别的类型的值）在「所有类型同值」时症状自然隐身**
            ⇒ 用真盘原文当夹具，证据强度**随真盘状态波动**。
        **正解（本次落地）**：夹具取真盘的**行序 + 冒充源 + 行形态**（这是真盘原文
        不可替代的部分——最小夹具复现不出「倒序扫描撞上冒充行就 break」的路径），
        但**值用可控的区分值**（各类型的「预期下次」取互不相同的日期）⇒
        ①真判据必取到自己那行的值 ②变异体必取到冒充行的值 ⇒ 两值不等 ⇒
        变异体**恒显形**，不随真盘状态波动。
        真盘原文仍读（证行序与冒充源来自实盘·非手编），但**不拿它的值当断言**。
        """
        center = Path('[记忆共享中心]') / "记忆蒸馏" / "蒸馏中心.md"
        if not center.exists():
            self.skipTest("真盘蒸馏中心不可达·变异检验跳过（⛔不静默通过）")
        real = center.read_text(encoding="utf-8")
        src = Path(core.__file__).read_text(encoding="utf-8")

        # ── 夹具构造：取真盘的**行序 + 冒充源 + 行形态**，值用**可分辨值** ──
        #   ⛔ 值不可用真盘的值（真盘月首各类型同值⇒变异体症状隐身·见 docstring ②）
        #   ⛔ 行序/冒充源必须来自真盘（最小夹具复现不出「倒序撞冒充行就 break」路径）
        EXPECT = "2099-01-01"   # 📊 自己的值
        DECOY = "2099-12-31"   # 冒充源（日记月报行）的值
        # 构造要点：夹具须让**倒序扫描先撞冒充源** ⇒ 文件序上冒充源行在**下方**。
        #   真盘 11-03 状态：📊 11-03 行在 📓 11-01 冒充行**上方** ⇒ 倒序先撞自己
        #   ⇒ 原病在真盘上**已潜伏不显形**（这正是「拿真盘的值当断言」不可靠的原因）。
        #   故从真盘取「某条 📊 行 + 其下方那条含「系统日志蒸馏」的 📓 行」这一对，
        #   保留真盘日期/类型/行形态，值换成可分辨值 ⇒ 变异体**恒显形**。
        own_row = None      # 候选的 📊 账行（文件序上方）
        decoy_row = None    # 候选的冒充源 📓 账行（文件序下方）
        for ln in real.splitlines():
            if not ln.startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) < 5 or not core.ROW_DATE_RE.match(cells[0]):
                continue
            tnorm = core.normalize_type(cells[1])
            if tnorm == "📊 系统日志蒸馏":
                own_row = cells
                continue
            if tnorm == "📓 日记月报" and "系统日志蒸馏" in ln:
                decoy_row = cells
                break
        if own_row is None or decoy_row is None:
            self.skipTest("真盘当前无「📊 账行 + 其下方摘要含系统日志蒸馏的 📓 冒充行」配对"
                          "·变异检验跳过（⛔不静默通过）")
        fixture = "\n".join([
            "| %s | %s | ✅ | 摘要 | %s |" % (own_row[0], own_row[1], EXPECT),
            "| %s | %s | ✅ | 本月含系统日志蒸馏摘要 | %s |" % (decoy_row[0], decoy_row[1], DECOY),
        ])
        # 变异：把主判据的「类型列双向包含」换成「整行 substring」（=原病判据）。
        #   ⛔ 必须连 else 分支整体替换——只改一行会留下 match_in_row 兼容分支，
        #   变异体走另一条路径 → 原病不复现 → 变异检验假绿（尺空转·2026-11-02 自纠）。
        old_block = (
            '                _hay = normalize_type(raw_type) if do_norm else raw_type\n'
            '                _needle = normalize_type(needle) if do_norm else needle\n'
            '                if _hay != _needle and _needle not in _hay and _hay not in _needle:\n'
            '                    continue')
        new_block = (
            '                if needle not in line:\n'
            '                    continue')
        mutated = src.replace(old_block, new_block)
        self.assertNotEqual(mutated, src, "变异未命中·判据文本与预期不符·测试空转")
        ns = {}
        exec(compile(mutated, "mutated_core", "exec"), ns)
        mutated_got = ns["extract_expected"](fixture, TYPES)
        # 变异体必须复现原病：📊 系统日志蒸馏 取到**冒充行**的值（而非自己那行）。
        #   原病有两种表现，⛔断言须覆盖两者（病根是「取到别人的行」，具体是
        #   ①取到冒充行的值 ②整体从结果中消失——两种都算失去鉴别力）：
        #   · 变异体取到 DECOY（冒充行值）→ 取错值
        #   · 变异体取到 None（该类型在结果里消失）→ 隐身
        #   ⛔ 只接受「既不等于 EXPECT、也不等于 None」以外的正常结果。
        mutated_val = mutated_got.get("📊 系统日志蒸馏")
        self.assertTrue(
            mutated_val is None or mutated_val == DECOY,
            "变异体未复现原病·负例6失去鉴别力（尺空转）·变异体取到=%r" % (mutated_val,))
        # 真判据必须取到自己那行的值（正向确认，避免变异检验自说自话）
        self.assertEqual(core.extract_expected(fixture, TYPES).get("📊 系统日志蒸馏"),
                         EXPECT, "真判据取错值·负例6断言需重审")


if __name__ == "__main__":
    unittest.main(verbosity=2)
