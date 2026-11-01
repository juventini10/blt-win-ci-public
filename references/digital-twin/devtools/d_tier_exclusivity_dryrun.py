#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# REG: family=校验器|registry=记忆蓝图/04_系统文件设计/数字分身设计哲学/INDEX.md|board=记忆蓝图/04_系统文件设计/数字分身设计哲学/03-进度看板.md
"""d_tier_exclusivity_dryrun.py — D 轴档位互斥的机械回归（06 §1.6 互斥律的取证器）

为什么存在（2026-09-26·皮叔质证「你这个到底是 D1 还是 D2？真解决还是假的解决」）：
  09-23 那次「档位互斥律」只把 **D3↔D1** 做成互斥，D1↔D2 与 D3↔D2 两对从未处理；
  且注入器里有一条 09-20 的「排序裁决段」明文要求 D1 标签与 D2 报告**同现**——
  等于把叠加写成制度，还自称引用 §1.6 真源（而 §1.6 已在 09-23 改口）。
  当时的验证＝w1_vocab_dryrun 19/19＋"四例两向"，四例全在测 W1 触发词的召准，
  **无一例断言"同回合只出一个档"** ⇒ 测试面根本不覆盖该判据，全绿是必然，不是修好了。

判据（按段结构判别，⛔按词面）：注入器输出的每个空行分段里，D 档声明段至多 1 个。
  ⚠️ 词面判别会假报：D3 段的义务⓪正文里就写着『【童灵·D1 常驻模式…】』作为对照说明，
  grep 词面必然命中 D1——本件按「段落首行」定性，不吃词面（守卫编写规范 §3.5 同族）。

自带变异（§3.9 变异测试红线：探针必须可证伪）：把 `if not _d2:` 短路成 `if True:`，
  本件必须 FAIL；不变异则必须全绿。跑 `--mutant` 自检这一条。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
# 版本载体（与 doenglingz_inject_prompt.py 同律：版本以盘上常量为真源，⛔以文档手写号为准）
__version__ = "v1.4"  # v1.4(2026-10-30·K007 重落批·皮叔令「符合愿景最优解根治」)：新增词面腿粘滞常驻组 sticky_wordleg_checks 8 例（t1-t6 行为面＋m1/m2 代码面），把「粘滞源=事件腿 OR 词面腿」与「安静模式/闭眼执行 可退」焊进机制。⚠️本组原于 2026-10-28 17:13 落过一次（唯一物证=__pycache__ 同名 .pyc 内含 sticky_wordleg_checks×5/闭眼执行×6），21:13 那次整文件重写从 v1.3 旧芯落盘把改动抹掉且从未入库——CHANGELOG v2.75/06 §2.2.1/系统日志三处声称与盘上脱钩。本次由本端反汇编恢复形状重落，并据 01规范 §二·三十 向 w1_tier_regress 追加安全词语料。v1.3(2026-10-26·D2收敛配套)：D2 探测前缀同步为「【童灵域切片命中·」（仅层标题·正文已不灌）·06 §1.6 三态表 D2 行同步；v1.2(2026-10-24·贴 错根治批配套)：分类器双名兼容——确认块段首「启动确认块」→注入器已更名「启动确认指令」（存量4红根因·A/B 备份对照实证与注入器 v1.27 改动无关）；否定式逗号后缀用例 期望随切片词表现况刷新为 D2（否定判据本体=不升 D3 不变）。

# ── A5 去硬码（2026-10-18·来源唯一性迁移）：路径经 runtime_paths 单一出口 ──
#   ⛔ 字面 [记忆共享中心]/数字分身/... 硬码；键值改由 runtime_paths.json 供给（改根不改脚本）。
#   装载自给自足（自带 import，⛔依赖宿主已导入项）；realpath 取根——旧址长期为软链，
#   abspath 会返回软链路径使 dirname(dirname()) 错位（同 A4 判据）。
import os as _rp_os, sys as _rp_sys


def _rp_find_root(_d):
    """两态自适应上溯：作者端件在 <档案>/脚本中心/分身[/d4_behavior]，装机端件在 <MC>/数字分身/k2-slice-generator。
    逐级向上，每级试「该目录」与「该目录/脚本中心」两种落点，命中 runtime_paths.py 即返回（≤4 级）。
    ⛔写死上溯级数——2026-10-18 A5 就是写死两级，令 d4_behavior 层 22 支算到 脚本中心/分身 而装载必崩。"""
    for _ in range(4):
        for _c in (_d, _rp_os.path.join(_d, "脚本中心")):
            if _rp_os.path.isfile(_rp_os.path.join(_c, "runtime_paths.py")):
                return _c
        _up = _rp_os.path.dirname(_d)
        if _up == _d:
            break
        _d = _up
    return None


_RP_ROOT = _rp_find_root(_rp_os.path.dirname(_rp_os.path.realpath(__file__)))
if _RP_ROOT and _RP_ROOT not in _rp_sys.path:
    _rp_sys.path.insert(0, _RP_ROOT)
from runtime_paths import rp
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


# ── 被测脚本路径解析（2026-10-03·你「第一性原理根治」·治「验证器测的不是运行的那份」）──
# 病根实证：原式硬编码 `[记忆共享中心]/脚本中心/`，而 `runtime_paths.json` 的 `devtools`
#   指向 `脚本中心/`——两份 sha256 不同 ⇒ 回归器报「全绿」与运行态零关联。
#   同日实测：加病句断言后，旧件判 D3 / 真跑件判 D2，**两次都报全绿**。
# 判据（verifier_target_fidelity_guard.py）：路径必须解析自 runtime_paths。
# 降级：runtime_paths 不可读时按候选顺序探测 + stderr 显形，⛔不静默取旧件。
def _resolve_devtools(name):
    import json as _json
    rp = os.path.expanduser("~/.hermes/doenglingz/runtime_paths.json")
    base = None
    if os.path.isfile(rp):
        try:
            with open(rp, encoding="utf-8") as fh:
                base = _json.load(fh).get("devtools")
        except Exception:
            base = None
    cands = []
    if base:
        cands.append(os.path.join(base, name))
    cands += [
        os.path.expanduser("[记忆共享中心]/脚本中心/" + name),
        os.path.expanduser("[记忆共享中心]/脚本中心/" + name),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    sys.stderr.write("[WARN] %s 解析不到·候选=%s\n" % (name, cands))
    return cands[0]


TARGET = _resolve_devtools("doenglingz_inject_prompt.py")

# (用例名, prompt, 期望出现的档位段集合)
CASES = [
    ("纯闲聊→仅 D1", "今天天气不错随便聊聊", {"D1标签", "D1义务"}),
    ("无召唤+域词→仅 D2", "分析一下这个的本质为什么", {"D2义务"}),
    ("召唤+域词→仅 D3", "启动童灵，分析一下这个的本质为什么", {"D3段"}),
    ("复制 D1 标签来提问→仅 D2", "【童灵·D1 常驻模式（非全量，仅人格基底）】分析一下本质", {"D2义务"}),
    ("复制 D1 标签+召唤→仅 D3", "【童灵·D1 常驻模式（非全量，仅人格基底）】启动童灵，分析本质", {"D3段"}),
    ("短应答无切片→仅 D1", "嗯我知道了", {"D1标签", "D1义务"}),
    # 否定语境真阴性（2026-10-03·你「第一性原理根治」）：W1 v1.14 的召唤词宾语尾特判
    # 原式 `not tail and _is_trigger_tail` 只在「童灵」位于句尾时生效，病句里它跟逗号
    # ⇒ 特判失效 ⇒ 直呼抢先上岗 ⇒ 否定豁免被盖掉。此组为该类假绿的照妖镜。
    ("否定式提及+逗号后缀→不升 D3（10-03 病句·2026-10-24 期望刷新：切片词表现含'为什么'→正档=D2·否定判据本体=无 D3 段）", "我没有启动童灵，只是想问为什么", {"D2义务"}),
    ("否定式提及·原判例→仅 D1（10-01 病句）", "这一轮的对话我没有启动童灵啊", {"D1标签", "D1义务"}),
    ("否定式·助词隔开→仅 D1（10-03 扩窗病句）", "我不是在启动童灵，我是在问", {"D1标签", "D1义务"}),
    ("否定式·前半否定+后半直呼→D3（v1.14 保留判例）", "我没启动童灵。童灵，你来", {"D3段"}),
]
# 标签≡实盘两例（2026-09-26 三修·8要素⑧"词面命中≠内容真在场"）：需要夹具目录，单列于 SLICE_CASES
CASES_ALL = list(CASES) + [
    ("D7 命中且正文注入→D2（标签≡实盘）", "分析一下这个的本质为什么", {"D2义务"}),
    ("D8 命中但正文读不到→降 D1＋显形", "分析一下这个的本质为什么", {"D1标签", "D1义务"}),
]


TIER_OF = {"D1标签": "D1", "D1义务": "D1", "D2义务": "D2", "D3段": "D3"}
TIER_SEGS = set(TIER_OF)


def tiers_of(got):
    """段集合 -> 档位集合。D1 是「标签行＋义务段」两段一制，⛔不得按段数当档数。"""
    return {TIER_OF[x] for x in got if x in TIER_SEGS}


def seg_names(out):
    """按空行分段，用段首行给每段定性——⛔全文 grep。
    v1.3（2026-10-06）：确认块形态（注入器 v1.16·皮叔拍板「脚本拼装·AI 照抄」）——D1/D2/D3
    确认块段首行统一为「【启动确认块」，靠块内标签行区分档位；旧标签前缀保留=双名兼容
    （D2 域模式→切片模式·D3 上岗模式→全量模式·2026-10-06 正名）。"""
    got = set()
    for blk in out.split("\n\n"):
        s = blk.strip()
        if not s:
            continue
        if s.startswith("【启动确认块") or s.startswith("【启动确认指令"):
            if "【童灵·D3 全量模式】" in s or "【童灵·D3 上岗模式" in s:
                got.add("D3段")
            elif "【童灵·D1 常驻模式" in s:
                got.add("D1标签")
            elif "【童灵·D2 切片模式" in s or "【童灵·D2 域模式" in s:
                got.add("D2义务")
        elif s.startswith("【童灵·D3 上岗模式") or s.startswith("【童灵·D3 全量模式"):
            got.add("D3段")
        elif s.startswith("【童灵·D1 常驻模式"):
            got.add("D1标签")
        elif s.startswith("【童灵·D2 切片模式"):   # v1.31 D2 甲式单行正典（对齐注入器）
            got.add("D2义务")
        elif s.startswith("【童灵显示义务·强制】本回合为 D1"):
            got.add("D1义务")
        elif s.startswith("【童灵显示义务·强制】本回合档位＝D2"):
            got.add("D2义务")
        elif s.startswith("【童灵档位排序裁决】"):
            got.add("旧裁决段")
        elif s.startswith("【童灵域切片命中·"):
            got.add("D2义务")
    return got


def _fixture_slices(tmpdir, drop_layer):
    """复制真 slices/ 但删掉指定层——测"词表命中而正文读不到"时档位是否老实降回 D1。"""
    import shutil
    src = rp("twin_slices")
    d = os.path.join(tmpdir, "slices")
    shutil.copytree(src, d)
    os.remove(os.path.join(d, drop_layer + ".md"))
    return d


def run_target(script, prompt, env=None, extra=None):
    import os as _os
    e = dict(_os.environ)
    if env:
        e.update(env)
    cmd = [sys.executable, script, "--prompt", prompt, "--src", "dryrun"]
    if extra:
        cmd += list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    if r.returncode != 0:
        raise SystemExit("注入器非零退出：%s\n%s" % (r.returncode, r.stderr[:400]))
    out = r.stdout
    # v1.2 修复（2026-10-06·L5 MISS 根治轮顺手根治·存量红实锤）：注入器 WB 挂载态输出为
    # JSON 信封（hookSpecificOutput.additionalContext·单行·\n 转义）——旧解析器按裸文本
    # 空行分段 ⇒ 档位段恒=[] ⇒ 16 例全红（与本次改动无关的存量环境漂移：D1 用例输出路径
    # 与被测文本零交集仍红=隔离证明）。修法=信封在则解包取正文再分段，裸文本路径保留。
    try:
        import json as _j
        _d = _j.loads(out)
        if isinstance(_d, dict):
            _ctx = ((_d.get("hookSpecificOutput") or {}).get("additionalContext")) or ""
            if _ctx:
                out = _ctx
    except Exception:
        pass
    return out


def sweep(script):
    fails = []
    rows = []
    import tempfile
    fx = _fixture_slices(tempfile.mkdtemp(prefix="dtier_"), "L2_认知风格")
    for name, prompt, want in CASES_ALL:
        env = {"DONGLINGZ_SLICES_DIR": fx} if name.startswith("D8") else None
        out_raw = run_target(script, prompt, env)
        g = seg_names(out_raw)
        if name.startswith("D7") and "【童灵·D2 切片模式" not in out_raw and "【童灵域切片命中·" not in out_raw:
            bad_extra = ["D7 声称 D2 却没有切片正文"]
        elif name.startswith("D8") and "降级留痕" not in out_raw:
            bad_extra = ["D8 未显形降级留痕（读失败被静默吞）"]
        elif name.startswith("D8") and "童灵·D2" in out_raw:
            bad_extra = ["D8 仍出现 D2 声称＝标签与实盘不符"]
        else:
            bad_extra = []
        tiers = tiers_of(g)
        want_tiers = tiers_of(want)  # CASES 的 want 写的是段名，统一折算成档位再比
        bad = []
        if len(tiers) != 1:
            bad.append("同回合出 %d 个档：%s" % (len(tiers), sorted(tiers)))
        elif tiers != want_tiers:
            bad.append("应为 %s，实为 %s" % (sorted(want_tiers), sorted(tiers)))
        if "旧裁决段" in g:
            bad.append("旧排序裁决段复活（该段与 §1.6 互斥律方向相反）")
        # 档位包含关系：D2 须带命中切片声明（仅层标题·正文已不灌·2026-10-26 皮叔令）；D3 不重复贴基座
        if tiers == {"D2"} and not ({"D2义务"} <= g):
            bad.append("D2 缺命中切片声明（§1.6 收敛：D2＝命中切片声明·仅层标题·正文已删）")
        bad += bad_extra
        rows.append((name, sorted(tiers), bad))
        if bad:
            fails.append(name)
    return rows, fails


def drift_checks():
    """档位枚举单一真源 vs 三个消费端：06 三态表行、守卫正则、本件用例档位集合。"""
    out = []
    try:
        src = open(TARGET, encoding="utf-8").read()
        import ast as _ast
        tiers = _ast.literal_eval(re.search(r"^TIER_ORDER = \((.+?)\)", src, re.M).group(1))
    except Exception as e:
        return [("TIER_ORDER 可读且可解析", "FAIL", type(e).__name__)]
    ok_inj = "_tier_map" in src and "next((t for t in TIER_ORDER" in src
    out.append(("注入器按 TIER_ORDER 选档（非硬编码三处 if）", "OK" if ok_inj else "FAIL", ""))
    spec = os.path.expanduser("[记忆共享中心]/脚本中心/06-跨端适配规范.md")
    # v1.2 修复：脚本中心副本缺失时回退真源（记忆蓝图 04_系统文件设计/数字分身设计哲学/）——
    # 存量红实锤：脚本中心从未有此件（FileNotFoundError=漂移对账恒红）
    if not os.path.isfile(spec):
        spec = os.path.expanduser(
            "[记忆共享中心]/脚本中心/06-跨端适配规范.md")
    try:
        rows = re.findall(r"^\| (D[123]) ", open(spec, encoding="utf-8").read(), re.M)
        same = sorted(set(rows)) == sorted(tiers)
        out.append(("06 §1.6 三态表档位集合==TIER_ORDER", "OK" if same else "FAIL",
                    "表=%s 枚举=%s" % (sorted(set(rows)), sorted(tiers))))
    except Exception as e:
        out.append(("06 §1.6 三态表档位集合==TIER_ORDER", "FAIL", type(e).__name__))
    guard = _resolve_devtools("doenglingz_level_declare_guard.py")
    try:
        g = open(guard, encoding="utf-8").read()
        m = re.search(r"童灵·D\(\[([123]+)\]\)", g)   # ⛔[123] 只吃一个字符＝恒不命中（本轮第 3 次同型·靠自己的负例逮出）
        covered = bool(m) and sorted("D" + c for c in m.group(1)) == sorted(tiers)
        out.append(("守卫正则覆盖全部档位", "OK" if covered else "FAIL", ""))
    except Exception as e:
        out.append(("守卫正则覆盖全部档位", "FAIL", type(e).__name__))
    used = {t for _n, _p, want in CASES_ALL for t in tiers_of(want)}
    out.append(("本件用例档位集合==TIER_ORDER", "OK" if sorted(used) == sorted(tiers) else "FAIL",
                "用例=%s" % sorted(used)))
    return out


def make_mutant():
    """变异体：短路 D2 对 D1 的压制 → 本件必须抓到。"""
    src = open(TARGET, encoding="utf-8").read()
    # 变异 1：短路与否的档位判定（D2 不再压 D1）→ 必须抓到多档并存
    mut, n = re.subn(r"^        if not _d2:$", "        if True:", src, flags=re.M)
    # 变异 2：把"读不到正文也照贴 D2"改回去（标签与实盘解绑）→ 必须抓到 D8
    mut, n2 = re.subn(r"    _d2 = bool\(_injected\)", "    _d2 = bool(layers)", mut)
    if n != 1 or n2 != 1:
        raise SystemExit("变异点未命中（锚行漂移·本件与注入器需同步更新）n=%d n2=%d" % (n, n2))
    d = tempfile.mkdtemp(prefix="d_tier_mutant_")
    p = os.path.join(d, "doenglingz_inject_prompt.py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(mut)
    return p


def sticky_wordleg_checks():
    """词面腿粘滞常驻用例（2026-10-30·K007 重落·工单验收②④·形状恢复自 10-28 17:13 的 .pyc 反汇编）。

    病根（焊进机制⛔靠人记得）：粘滞函数原式（`_event_leg_d3_sticky`·注入器 v1.32 现名
    `_d3_sticky_legs`）只认 `mode==skill_event` 的 D3 笔，
    而词面腿「启动童灵」写的笔是 `mode=json, w1=True` → 进不了 180min 粘滞窗 → 逐轮清零重判
    （10-11 根治只搬了事件腿那半边）。
    断言分布：t1/t2 词面 D3 下轮须被粘滞撑起；t3 超窗负例不反噬；t4 跨 sid 不串档；
    t5 安全词（安静模式）可打断不锁死；t6 闭眼执行已退出安全词→不打断（2026-11-01 你裁）；m1/m2 代码面钉住泛化腿与词表收窄（防"实现漂回文档"）。
    夹具纪律：每例独立 `DOENGLINGZ_CONFIG_DIR` 临时目录——STATE_FILE 与 quiet flag 均隔离，
    ⛔不碰真台账，⛔共享 tmpcfg（flag 是 per-config-root 全局态，共享会让 t5 之后全体假绿）。
    ⛔词面判别（文件头同款坑）：按段首行定性。
    """
    import datetime as _dt
    import json as _j

    results = []
    SID = "dtier_sticky_"

    def fresh():
        d = tempfile.mkdtemp(prefix="dtier_sticky_cfg_")
        return d, {"DOENGLINGZ_CONFIG_DIR": d}

    def tiers_for(prompt, cfg_env, sid):
        out = run_target(TARGET, prompt, env=cfg_env, extra=["--session-id", sid])
        return seg_names(out)

    def last_row(cfgdir):
        p = os.path.join(cfgdir, "doenglingz_inject_state.json")
        try:
            lines = [l.strip() for l in open(p, encoding="utf-8") if l.strip()]
        except Exception:
            return {}
        for l in reversed(lines):
            try:
                return _j.loads(l)
            except Exception:
                continue
        return {}

    def rec(cfgdir, sid, tier="D3", w1=True, mode="json", minutes_ago=0):
        ts = (_dt.datetime.now() - _dt.timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
        with open(os.path.join(cfgdir, "doenglingz_inject_state.json"), "a", encoding="utf-8") as f:
            f.write(_j.dumps({"ts": ts, "w1": w1, "d3_sticky": False, "d_tier": tier,
                              "slices_injected": [], "slices_failed": [], "w3_layers": [],
                              "src": "dryrun", "mode": mode, "session_id": sid},
                             ensure_ascii=False) + "\n")

    def say(name, bad):
        results.append((name, "FAIL" if bad else "OK", bad or ""))

    # t1 词面腿召唤→D3
    cfg, env = fresh()
    g = tiers_for("启动童灵，分析一下这个的本质为什么", env, SID + "t1")
    say("t1 词面腿召唤→D3", "" if tiers_of(g) == {"D3"} else "应 D3 实为 %s" % sorted(tiers_of(g)))
    # t2 词面腿D3→下轮粘滞撑起 D3（K007 病形的正身）
    g2 = tiers_for("嗯我知道了", env, SID + "t1")
    bad = ""
    if tiers_of(g2) != {"D3"}:
        bad = "词面 D3 未粘滞，回落=%s（K007 病形复发）" % sorted(tiers_of(g2))
    else:
        row = last_row(cfg)
        if row.get("d3_sticky") is not True:
            bad = "末行 d3_sticky=%r（期望 True·粘滞须显式记录）" % row.get("d3_sticky")
        elif row.get("w1") is not False:
            bad = "末行 w1=%r（粘滞不算词面命中·不抹平两腿差异）" % row.get("w1")
    say("t2 词面腿D3→下轮粘滞撑起D3", bad)
    # t3 词面腿D3超窗→回落（窗口语义不得反噬成永久 D3）
    cfg, env = fresh()
    rec(cfg, SID + "t3", minutes_ago=181)
    g3 = tiers_for("嗯我知道了", env, SID + "t3")
    say("t3 词面腿D3超窗→回落",
        "" if tiers_of(g3) == {"D1"} else "超窗未回落仍粘滞=%s" % sorted(tiers_of(g3)))
    # t4 词面腿D3跨sid→不串档
    cfg, env = fresh()
    rec(cfg, SID + "t4_src", minutes_ago=0)
    g4 = tiers_for("嗯我知道了", env, "other_sid")
    say("t4 词面腿D3跨sid→不串档",
        "" if tiers_of(g4) == {"D1"} else "跨会话串档=%s" % sorted(tiers_of(g4)))
    # t5 安静模式打断粘滞→D1
    cfg, env = fresh()
    tiers_for("启动童灵", env, SID + "t5")
    g5 = tiers_for("安静模式", env, SID + "t5")
    say("t5 安静模式打断粘滞→D1",
        "" if tiers_of(g5) == {"D1"} else "安静模式未打断粘滞，仍=%s（锁死风险）" % sorted(tiers_of(g5)))
    # t6 闭眼执行已退出安全词→不打断粘滞（2026-11-01 你裁「现在就只有安静模式」·原期望 D1 翻转）
    cfg, env = fresh()
    tiers_for("启动童灵", env, SID + "t6")
    g6 = tiers_for("闭眼执行", env, SID + "t6")
    say("t6 闭眼执行退出安全词→粘滞保持 D3",
        "" if tiers_of(g6) == {"D3"} else "闭眼执行仍打断粘滞=%s（收窄未生效·检查 QUIET_ENTER_WORDS）" % sorted(tiers_of(g6)))
    # m1/m2 代码面：两条泛化腿必须在盘上（行为绿了但实现被回退＝下一轮必红的前置哨）
    src = open(TARGET, encoding="utf-8").read()
    _i = src.find("def _d3_sticky_legs")
    _j2 = src.find("\ndef ", _i + 10)
    fn = src[_i:_j2 if _j2 > 0 else len(src)]
    say("m1 粘滞函数含 w1 泛化（代码面）",
        "" if 'and not d.get("w1")' in fn else "粘滞函数缺 w1 泛化腿（回退只认 skill_event＝K007 复发）")
    _k = src.find("QUIET_ENTER_WORDS = (")
    _seg = src[_k:src.find(")", _k) + 1] if _k > 0 else ""
    say("m2 quiet门已收窄至安静模式（代码面·2026-11-01 你裁）",
        "" if (_k > 0 and "安静模式" in _seg and "闭眼执行" not in _seg)
        else "quiet 进入词表未收窄（闭眼执行仍在或安静模式缺失·收窄回退）")
    return results


def main():
    mutant = "--mutant" in sys.argv[1:]
    target = make_mutant() if mutant else TARGET
    rows, fails = sweep(target)
    dr = drift_checks()
    for name, st_, note in dr:
        print("  %s 漂移对账 %-34s %s" % ("✅" if st_ == "OK" else "❌", name, note))
    fails += ["drift:" + n for n, st_, _ in dr if st_ != "OK"]
    st = sticky_wordleg_checks()
    fails += ["sticky:" + n for n, st_, _ in st if st_ != "OK"]
    print("=== D 轴档位互斥回归（真源=06 §1.6 互斥律）%s ===" % ("·变异体" if mutant else ""))
    for name, tiers, bad in rows:
        print("  %s %-24s 档位段=%s%s" % ("✅" if not bad else "❌", name, tiers,
                                          "" if not bad else " ← " + "; ".join(bad)))
    print("=== 词面腿粘滞常驻组（K007·粘滞源=事件腿 OR 词面腿 w1=True）===")
    for name, st_, note in st:
        print("  %s %-24s %s" % ("✅" if st_ == "OK" else "❌", name, note))
    n_sweep_fail = len([f for f in fails if not f.startswith(("drift:", "sticky:"))])
    n_drift_fail = len([f for f in fails if f.startswith("drift:")])
    n_sticky_fail = len([f for f in fails if f.startswith("sticky:")])
    total = len(CASES_ALL) + len(dr) + len(st)
    passed = (len(CASES_ALL) - n_sweep_fail) + (len(dr) - n_drift_fail) + (len(st) - n_sticky_fail)
    print("合计 %d/%d 过（互斥 %d/%d·漂移对账 %d/%d·粘滞组 %d/%d·分母全部实算，⛔手写数）"
          % (passed, total, len(CASES_ALL) - n_sweep_fail, len(CASES_ALL),
             len(dr) - n_drift_fail, len(dr), len(st) - n_sticky_fail, len(st)))
    if mutant:
        ok = bool(fails)
        print("变异判定：%s（抓到 %d 例＝本探针可证伪；未抓到＝恒真探针，作废）"
              % ("✅ 变异被逮住" if ok else "❌ 变异未逮住", len(fails)))
        return 0 if ok else 1
    if fails:
        print("判定：❌ 存在多档并存/旧裁决残留/粘滞腿缺位 → ⛔不得落地（铁律-020）")
        return 1
    print("判定：✅ 全过；跑 --mutant 复验本探针可证伪性")
    return 0


if __name__ == "__main__":
    sys.exit(main())
