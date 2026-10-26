#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_negative_tokens_parse.py — 否证 token 族「解析器 + token 语义」双向负例（v1.0 · 2026-10-25 童灵 D3 根治批）

为什么存在（P1 实锤的反哺件）：
  2026-10-25 clock-loop E 路径独立盲审发现：run.sh 的否证族循环原用 `IFS=<竖线> read -r pat reason`
  解析，而 token 本身就是含竖线的正则——在**第一个**竖线处被切断，退化 pat 令 grep 报错，
  错误又被 2>/dev/null 吞掉，于是"该条根本没执行"被算进"零命中"，闸自报 PASS = 假绿。
  v4.12.12 二次根治（独立复核 N-2）：v4.11 改的"末切"只救 pattern 侧含竖线，理由侧含竖线仍切歪
  （复核 M4 实证假红+理由错位）⇒ 数据格式迁 **TAB 分隔**，本套件随之把"末切正确"改钉为"TAB 正确"。
  同批还查出第8行 token 自身写错（双反斜杠在 ERE 里=行首单个反斜杠），既不拦真回流形态
  （表格行首接花括号象限名）又误命中无关行。
  ⇒ 病名「加锁未验锁」：闸有牙与否从来无人常驻验。本套件把"解析器正确 + 每条 token 真有牙"
  钉成常设断言，且**直接抽取 run.sh 现行循环体执行**（改坏实现→本套件即红，不许"改了没人逮"）。

判绿口径：末行含 "结果: N/N 通过 ✅"（run.sh 判绿正则要求，勿改措辞）
用法：python3 tests/test_negative_tokens_parse.py（已登记进 scripts/run.sh 的 SUITES）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNSH = ROOT / "scripts" / "run.sh"
NEG = ROOT / "scripts" / "negative_tokens.txt"

# 从 run.sh 抽取现行否证族循环体（不用副本——副本会随实现漂移成"测了个假东西"）
LOOP_RE = re.compile(r"(    NEG_HIT=0; NEG_RAN=0.*?\n    fi\n)", re.S)

DOMAINS = ["pages", "references/l1", "references/l2", "references/l3", "references/shared"]

results = []


def _extract_loop():
    src = RUNSH.read_text(encoding="utf-8")
    m = LOOP_RE.search(src)
    if not m:
        raise AssertionError("未能从 run.sh 抽取否证族循环体（实现被改形=本测试该红）")
    return m.group(1)


def _mk_tree(base):
    """造最小可扫域：run.sh 的否证段扫 SKILL.md + pages/ + references/{l1,l2,l3,shared}/
    每用例独立目录（⛔共用 base/tw——首版自曝：第二例起 mkdir 已存在直接崩）"""
    tw = base / ("case%d" % len(results))
    (tw / "scripts").mkdir(parents=True)
    (tw / "SKILL.md").write_text("# 干净样本\n本文件不含任何被否证的旧形态。\n", encoding="utf-8")
    for d in DOMAINS:
        p = tw / d
        p.mkdir(parents=True, exist_ok=True)
        (p / "sample.md").write_text("干净内容\n", encoding="utf-8")
    return tw


def _runner_script(base, name):
    loop = _extract_loop()
    sh = base / ("neg_slice_%s.sh" % name)
    sh.write_text(
        "#!/usr/bin/env bash\n"
        "set -u\n"
        'DIR="$1"; NEG_FILE="$2"\n'
        "FAIL=0\n"
        + loop
        + "\n"
        'if [ "$NEG_RAN" -eq 0 ] || [ "$NEG_HIT" -ne 0 ] || [ "$NEG_DEAD" -ne 0 ]; then exit 1; fi\n'
        "exit 0\n",
        encoding="utf-8")
    return sh


def _neg_variant(base, name, lines=None):
    f = base / name
    src = NEG.read_text(encoding="utf-8").splitlines()
    f.write_text("\n".join(lines if lines is not None else src) + "\n", encoding="utf-8")
    return f


def run_case(name, mutate_tree, expect_rc, base, neg_file=None):
    tw = _mk_tree(base)
    if mutate_tree:
        mutate_tree(tw)
    sh = _runner_script(base, tw.name)
    nf = neg_file or _neg_variant(base, "neg_used.txt")
    r = subprocess.run(["bash", str(sh), str(tw / "scripts"), str(nf)],
                       capture_output=True, text=True, timeout=180)
    ok = r.returncode == expect_rc
    results.append(ok)
    print("[{r}] {n}: exit={e} 期望={x}".format(r="PASS" if ok else "FAIL", n=name,
                                               e=r.returncode, x=expect_rc))
    if not ok:
        print("   stdout:", (r.stdout or "").strip().splitlines()[:3])
        print("   stderr:", (r.stderr or "").strip().splitlines()[:3])


def _inject_skill(line):
    def _m(tw):
        p = tw / "SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + line + "\n", encoding="utf-8")
    return _m


def _all_comments(base):
    return _neg_variant(base, "neg_allcomment.txt",
                        lines=["# 只有注释，无可执行 token", "", "# 另一条注释"])


def _pin_no_first_split(_):
    """病根防回归：run.sh 现文本必须不再含「以竖线作 IFS 的 read」形态。"""
    src = RUNSH.read_text(encoding="utf-8")
    if re.search(r"while\s+IFS='?\|'?\s+read", src):
        raise AssertionError("run.sh 退回 IFS 首切=假绿病根复活")


def _show_split_semantics():
    """对照实验（只读）：证明竖线分隔必截断、TAB 分隔无损——钉住"为什么非换分隔符不可"。"""
    src = NEG.read_text(encoding="utf-8").splitlines()
    data = [l for l in src if l.strip() and not l.lstrip().startswith("#")]
    line3 = data[1]                                    # 第3行 token（pattern 内含竖线）
    tab_pat = line3.split("\t")[0]                     # 现行 TAB 语义
    ok_tab = tab_pat.strip().startswith("\\|") and "下一步·决策" in tab_pat
    results.append(ok_tab)
    print("[%s] TAB 语义无损: pat=[%s]" % ("PASS" if ok_tab else "FAIL", tab_pat))
    ok_sep = all("\t" in l for l in data)
    results.append(ok_sep)
    print("[%s] 数据格式已全量迁 TAB（%d/%d 行含制表符）" % (
        "PASS" if ok_sep else "FAIL", sum(1 for l in data if "\t" in l), len(data)))


def _reason_with_pipe(base):
    """N-2 直接哨兵：理由段含竖线，不得再被切进 pattern（旧竖线分隔下会假红+理由错位）。"""
    src = NEG.read_text(encoding="utf-8").splitlines()
    probe = "下一步·决策\t理由里带竖线|例如「A|B」这种写法"
    return _neg_variant(base, "neg_pipe_reason.txt", lines=src[:1] + [probe])


def main():
    _pin_no_first_split(None)  # 形态断言（抛异常即红）
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run_case("合规态必绿", None, 0, base)
        run_case("下一步旧按钮标签回流必红",
                 _inject_skill("| 1 | 下一步·决策 | 默认推荐 |"), 1, base)
        run_case("认知格旧表形态回流必红",
                 _inject_skill("| {已知已知} | 旧表第一行 | 内容 |"), 1, base)
        run_case("无关反斜杠行不误命中（第8行校正验证）",
                 _inject_skill("\\{已知已知} 非表格行首"), 0, base)
        run_case("族零条可执行必红", None, 1, base, neg_file=_all_comments(base))
        # N-2 哨兵：token 行理由段含竖线时，pattern 必须仍只取制表符前段（旧竖线分隔会连理由一起吞进正则）
        run_case("理由段含竖线不得切歪pattern",
                 _inject_skill("| 1 | 下一步·决策 | x |"), 1, base, neg_file=_reason_with_pipe(base))
        _show_split_semantics()
    n = sum(results)
    ok = n == len(results)
    print("结果: {n}/{t} 通过 {s}".format(n=n, t=len(results), s="✅" if ok else "❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
