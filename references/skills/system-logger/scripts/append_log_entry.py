#!/usr/bin/env python3
"""Append a system-log entry with a mechanically-captured timestamp.

Root-cause fix (system-logger v3.10.5): the `完成` timestamp used to be an
AI-declared free-text value, which could be wrong (L442 wrote 20:46 while the
file mtime was 14:35). The only correct value is the moment of the write,
which only the OS clock at append time knows. This script captures `date`
internally, fills the `完成` field, and appends — AI never touches the time
value, so it is physically impossible to write a fabricated timestamp.

Usage:
  printf '%s' "$ENTRY_BODY" | python3 append_log_entry.py --tool WorkBuddy [--logdir DIR] [--reflection]
  python3 append_log_entry.py --guard-line [--logdir DIR]   # 独立产出 changelog_guard 检测行（v3.10.24）

ENTRY_BODY must contain a line `- **完成**：<NOW>` (placeholder) OR omit the
`完成` field entirely (the script inserts it). A literal HH:MM in the 完成
line = bypass of the physical anchor -> exit 1 (refuse to write).

--guard-line (v3.10.24·2026-09-01·你"系统日志写半天"架构解耦): 默认写入路径
  不再同步内嵌 changelog_guard --check（全树扫描 ~7s 绑定每次写入=主凶）。
  改为独立模式：AI 在输出验证块前跑一次本模式，机械产出 guard_line 回显——
  填值权仍归脚本（AI 接触不到填值权·防假阴性疲劳设计不变），只改调用时机。
  输出: GUARD_LINE <值>

--reflection: 童灵思考标记（v3.10.15 新增·2026-08-26·脚本旧标 v3.10.8 系笔误·2026-09-01 Loop评估#7对齐CHANGELOG·v1.2 2026-09-05 反思→思考更名）
  当指定此参数时，在条目标题前添加 `[童灵思考]` 前缀。
  蒸馏管道会扫描此标记，按内容分流到 L2/L3/L6。
"""
# Win console UTF-8 guard (auto by clock-loop 1.7.2)
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import os
import time
import re
import subprocess
import sys
from datetime import datetime

LOGDIR_DEFAULT = os.path.expanduser("[记忆共享中心]/工作日志/系统日志")

# v3.12.0(2026-09-02·愿景①根治回复呈现层漂移): `--guard-line` 把 changelog_guard
# 检测值写入此缓存，写入路径的验证块读取它填 `📋 变更日志检测` 行——避免每次写入
# 重跑 7s 全树扫描（v3.10.24 解耦的代价），又让验证块 100% 脚本产出、AI 零构造权。
# v3.14.3(2026-09-18·QClaw·缓存新鲜度=年龄代理→被检对象身份验证·第一性根治):
#   病灶：v3.14.2 用"缓存年龄<10分钟"代理"缓存内容仍有效"——与 triwich_closeout_guard v1.2.0（mtime 时间差代理"本轮登记有没有"）
#   属**同一族缺陷**（拿代理信号冒充直接证据）。实证：08:36 算出"7 条候选未记"，08:45 写入时已修至 0，
#   但缓存年龄 9min<10min → 旧值被放行进验证块 → 系统日志固化了早已不成立的警告。
#   修法：缓存写入时**同时记录 changelog_guard.sh 与 变更日志.md 的 mtime+size 指纹**（即"检测所看过的东西"的身份），
#   读取时指纹不一即重算——年龄只做上限兵，指纹做新鲜度本体。解态：只有强制重算才拿得到旧值。
GUARD_CACHE = os.path.expanduser("~/.cache/systemlogger/guard_line.txt")

# —— 写入端留存的条目原文副本（2026-10-23·MiniMax Code 端·治尺轮）——
#   病根：条目被并发吞没后，人工恢复依赖「写入端会话回显原文」（步骤 5.8 第 3 优先级）
#   ⇒ 恢复依赖人记得 + 凭会话回显拼装 = 半记忆依赖 ⇒ 跨端/跨轮不可靠。
#   正解：**写入时即落一份原文副本** ⇒ 恢复变成机械实录回读（⛔不凭记忆重写）。
#   副本路径由 seal token 决定（确定性路径）⇒ 台账无须加列（⛔不扩列·不动前 6 列口径）。
#   副本目录在 ~/.cache（缓存面·非权威真源）：权威仍是系统日志文件本体。
ENTRY_COPY_DIR = os.environ.get("SYSLOG_ENTRY_CACHE") or os.path.join(
    os.path.dirname(GUARD_CACHE), "entries")
ENTRY_COPY_TTL_DAYS = 7


def _entry_copy_path(token):
    """副本路径 = 确定性映射（token → 路径）⇒ 回验段可独立定位，无需台账加列。"""
    return os.path.join(ENTRY_COPY_DIR, "%s.md" % token)


def _save_entry_copy(token, content):
    """写入条目原文副本（吞没后据此机械重建）。

    ⛔ 副本路径由 token 决定 · ⛔ 先写副本再追加正文 ⇒ 追加被吞时副本已存在。
    ⛔ 不含任何 AI 构造内容 = 写入那一刻的逐字原文（与追加内容同一变量）。
    """
    try:
        os.makedirs(ENTRY_COPY_DIR, exist_ok=True)
        p = _entry_copy_path(token)
        tmp = "%s.tmp.%d" % (p, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, p)
        return p
    except Exception:
        return None


def _prune_entry_copies(days=ENTRY_COPY_TTL_DAYS):
    """副本 TTL 清理（缓存面·非权威）。

    ⛔ 只删本目录内**文件名匹配 8 位 hex token**且 mtime 超期的文件 ⇒ 不误伤他物。
    ⛔ 保留期 7 天：覆盖「当日内吞没 + 次日修复」窗口（自愈只需近端副本）。
    """
    import re as _re
    _pat = _re.compile(r"^[0-9a-f]{8}\.md$")
    try:
        if not os.path.isdir(ENTRY_COPY_DIR):
            return 0
        cutoff = time.time() - days * 86400
        n = 0
        for fn in os.listdir(ENTRY_COPY_DIR):
            if not _pat.match(fn):
                continue
            p = os.path.join(ENTRY_COPY_DIR, fn)
            try:
                if os.path.isfile(p) and os.path.getmtime(p) < cutoff:
                    os.remove(p)
                    n += 1
            except OSError:
                pass
        return n
    except Exception:
        return 0


def _rebuild_orphan_seals(logfile, tokens):
    """用写入端留存的原文副本重建被吞条目（⛔不凭记忆重写）。

    返回 (已重建列表, 无副本可重建列表)。
    ⛔ 重建内容 = 副本逐字原文（含原 seal 行）⇒ 不产生新 seal、不改写事实。
    ⛔ 幂等：重建前确认该 seal 当前确不在文件里 ⇒ 绝不产生重复条目。
    ⛔ 持同一把锁 ⇒ 与 reconcile 的 replace 不交叠（⛔父进程不持锁时再 spawn reconcile）。
    """
    repaired, unrepairable = [], []
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from systemlog_lock import log_lock
    except Exception:
        return [], list(tokens)
    for tok in tokens:
        p = _entry_copy_path(tok)
        marker = "- **seal**：%s" % tok
        try:
            if not os.path.exists(p):
                unrepairable.append(tok)
                continue
            with open(p, encoding="utf-8") as f:
                content = f.read()
            if marker not in content:
                unrepairable.append(tok)  # 副本不含本 seal ⇒ 不是它的副本
                continue
            with log_lock(logfile):
                with open(logfile, encoding="utf-8", errors="replace") as f:
                    cur = f.read()
                if marker in cur:
                    continue  # 已被补（并发他方）⇒ 幂等跳过
                _insert_entry_into_group(logfile, cur, content)
            repaired.append(tok)
        except Exception:
            unrepairable.append(tok)
    return repaired, unrepairable


def _insert_entry_into_group(logfile, cur, content):
    """把重建的条目插回它应属的 `## <工具>` 组内（⛔不甩在文件末尾悬空）。

    归属真源 = 条目自带的 `- **工具**：X` 字段（与 reconcile 同口径）。

    规范结构（与 reconcile 产出逐字同形·实证今日日志）：
        `## <组头>` + 空行 + `### <条目标题>` + 空行 + 字段行… + `- **seal**：x`
    ⛔ 副本不含组头（否则文件里会出现第二张概览表 + 第二个组头·实证探针 T4 差 118 字节）
    ⛔ 重建后条目归位在组内（⛔不悬在文末）
    """
    m = re.search(r"^\s*-\s*\*\*工具\*\*\s*[:：]\s*(.+?)\s*$", content, re.M)
    tool = m.group(1).strip() if m else ""
    lines = cur.splitlines(keepends=True)
    if not tool:
        # 无工具字段 ⇒ 兜底追加到文末（⛔不猜归属·只保证条目不丢）
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(content)
        return
    hdr = re.compile(r"^## %s\s*$" % re.escape(tool))
    start = None
    for i, ln in enumerate(lines):
        if hdr.match(ln.rstrip("\n")):
            start = i
            break
    if start is None:
        # 组不存在 ⇒ 新建组头再放条目（⛔组头裸 `## X`·⛔不加 emoji/括号注释）
        tail = []
        while lines and lines[-1].strip() == "":
            tail.insert(0, lines.pop())
        new_lines = lines + ["", "## %s" % tool, "", content] + tail
        with open(logfile, "w", encoding="utf-8") as f:
            f.write("".join(new_lines))
        return
    # 组已存在 ⇒ 插到该组末尾（下一个 `## ` 之前）
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    seg = lines[start + 1:end]           # 组内现有内容（不含组头）
    # 规范结构：组头后隔一空行才进条目块（⛔组头与首条目之间必须有空行）
    if not seg or seg[0].strip() != "":
        seg = ["\n"] + seg
    else:
        seg = list(seg)
    # 去掉组内尾部空行（重建条目自带结尾）⇒ 避免末尾叠加空行
    # ⛔ 只删「条目块之后」的空行，⛔保留组头后的首个空行（上面已保证它在 seg[0]）
    while len(seg) > 1 and seg[-1].strip() == "":
        seg.pop()
    new_lines = lines[:start + 1] + seg + [content] + lines[end:]
    with open(logfile, "w", encoding="utf-8") as f:
        f.write("".join(new_lines))


def _guard_script_path():
    """changelog_guard.sh 定位（2026-10-14 根治谎报「未安装」）。

    病根：本件原写死 `开发工具/changelog-guard/changelog_guard.sh`，脚本中心根治阶段3首批
    把它搬进 `脚本中心/守卫/changelog-guard/` 后 os.path.exists 转 False → --guard-line 落
    "N/A（个人工具·未安装）"分支——十端共用的变更日志兜底层**静默降级**（真态=已装·移位）。
    判据：⛔单一写死路径=移位即假 N/A；按候选序取第一个存在件，旧址保留作回滚兼容。
    """
    for p in (
        os.path.expanduser("[记忆共享中心]/脚本中心/changelog_guard.sh"),
        os.path.expanduser("[记忆共享中心]/脚本中心/changelog-guard/changelog_guard.sh"),
    ):
        if os.path.exists(p):
            return p
    return None


def _guard_fingerprint():
    """签名=检测所依赖的两个输入的身份（guard 脚本 + 被检账本）。
    ⛔ 不用缓存自身年龄作新鲜度——那只是"多久前算的"，不回答"所算的东西变了没"。"""
    parts = []
    for p in (
        _guard_script_path() or "changelog_guard.sh:absent",
        os.path.expanduser("[记忆共享中心]/变更日志.md"),
    ):
        try:
            st = os.stat(p)
            parts.append("%s:%d:%d" % (os.path.basename(p), st.st_mtime_ns, st.st_size))
        except OSError:
            parts.append("%s:missing" % os.path.basename(p))
    return "|".join(parts)


def _write_guard_cache(val):
    try:
        d = os.path.dirname(GUARD_CACHE)
        os.makedirs(d, exist_ok=True)
        with open(GUARD_CACHE, "w", encoding="utf-8") as f:
            f.write(val.rstrip("\n") + "\n" + _guard_fingerprint() + "\n")
    except Exception:
        pass


def _read_guard_cache():
    """v3.14.3 第一性根治（2026-09-18·QClaw）：指纹验证优先于年龄。
    病灶：旧版只问"缓存多久前算的"（年龄代理），不问"所算的东西变了没"（直接证据）——
    与 triwich_closeout_guard v1.2.0（mtime 代理登记）同一族。实证：08:36 的"7 条"在已修至 0 后
    仍被年龄 TTL 放行进验证块（9min<10min）。
    新序：①读缓存行 ②指纹不一致（含旧格式无指纹行）→立即重算 ③指纹一致→年龄仅作上限兜底。"""
    try:
        if os.path.exists(GUARD_CACHE):
            with open(GUARD_CACHE, encoding="utf-8") as f:
                raw = f.read().strip().split("\n")
            val = raw[0].strip() if raw else ""
            cached_fp = raw[1].strip() if len(raw) > 1 else ""
            if cached_fp != _guard_fingerprint():
                fresh = run_guard_line()
                if fresh:
                    _write_guard_cache(fresh)
                    return fresh
                return "⚠️ guard_line 自动重算失败（输入已变·审查F2升级）——手动跑 `append_log_entry.py --guard-line` 核实"
            age = time.time() - os.path.getmtime(GUARD_CACHE)
            if age > 600:
                v2 = run_guard_line()
                if v2:
                    _write_guard_cache(v2)
                    return v2
                return "⚠️ guard_line 自动重算失败（原缓存>%d分钟·审查F2升级）——手动跑 `append_log_entry.py --guard-line` 核实" % (600 // 60)
            return val
    except Exception:
        pass
    return None


def run_guard_line():
    """机械产出 changelog_guard 检测行（v3.10.24 从写入路径独立出来）。

    AI 只能回显本函数返回值，不能自填——v3.10.7 防假阴性疲劳设计保留，
    仅调用时机从"每次写入"改为"验证块输出前（每会话 1 次）"。
    """
    guard_line = ""
    guard_script = _guard_script_path()
    if guard_script and os.path.exists(guard_script):
        out = err = ""
        try:
            try:
                cp = subprocess.run(
                    ["bash", guard_script, "--check"], capture_output=True, timeout=90
                )
                out = cp.stdout.decode("utf-8", "replace").strip()
                err = cp.stderr.decode("utf-8", "replace").strip()
            except subprocess.TimeoutExpired:
                guard_line = "⚠️ changelog_guard --check 超时 90s 未返回（AI 需手动跑 --check 核实）"
            if not guard_line:
                import json as _json
                j = _json.loads(out)
                n = int(j.get("candidates", 0))
                guard_line = "✅ 全部已记" if n == 0 else "⚠️ %d 条候选未记录（整行红框高亮）" % n
        except Exception as e:
            reason = "%s: %s" % (type(e).__name__, str(e)[:120])
            if err:
                reason += " | stderr: %s" % err.splitlines()[0][:160]
            guard_line = "⚠️ changelog_guard 执行失败（原因=%s·AI 需手动跑 --check 核实）" % reason
    else:
        guard_line = "N/A（个人工具·未安装）"
    return guard_line


def repair_orphans_mode(logdir):
    """独立巡检模式（v3.20.0·2026-10-23·MiniMax Code 端·治尺轮）。

    背景：孤儿 seal 的自动修复此前只能被动挂在写入路径（下次写入时才触发）⇒
    「当天最后一条被吞没」永远等不到修复。独立模式让修复**不依赖任何后续写入**
    ⇒ 可挂定时任务（愿景①全自动化：机制自动运转，不依赖人记得）。

    判据口径与写入路径完全一致：签发账本枚数 vs 文件内命中数，扣掉 VOID（去重删副本）。
    ⛔ 无副本的残余只报不猜（⛔凭记忆重写=编造）。
    """
    dt = datetime.now()
    today = dt.strftime("%Y-%m-%d")
    logfile = os.path.join(logdir, "系统日志_%s.md" % today)
    if not os.path.exists(logfile):
        print("ℹ️ 当日日志不存在（%s）——无可巡检项" % os.path.basename(logfile))
        return 0
    lg = os.environ.get("SYSLOG_SEAL_LEDGER") or os.path.join(os.path.dirname(GUARD_CACHE), "seal_ledger.log")
    mine = []
    if os.path.exists(lg):
        with open(lg, encoding="utf-8", errors="replace") as sf:
            for l in sf:
                c = l.rstrip("\n").split("\t")
                if (len(c) >= 5 and c[2] == os.path.basename(logfile) and str(today) in c[1]
                        and c[4] == os.path.dirname(os.path.abspath(logfile))):
                    mine.append(c[0])
    with open(logfile, encoding="utf-8", errors="replace") as ff:
        body = ff.read()
    void = set()
    vp = os.path.join(os.path.dirname(lg), "seal_void.log")
    if os.path.exists(vp):
        with open(vp, encoding="utf-8", errors="replace") as vf:
            for v in vf:
                vc = v.rstrip("\n").split("\t")
                if len(vc) >= 4 and vc[3] == os.path.basename(logfile):
                    void.add(vc[0])
    lost = [x for x in mine if x not in body and x not in void]
    if not lost:
        print("✅ 孤儿巡检：%d 枚已签发 seal 全部在文件里（无吞没）" % len(mine))
        return 0
    repaired, unfixed = _rebuild_orphan_seals(logfile, lost)
    if repaired:
        try:
            subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "reconcile_overview.py"), logfile],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
    print("⚠️ 孤儿巡检：%d/%d 枚已签发却不在文件里（疑被并发整文件回写吞没）" % (len(lost), len(mine)))
    if repaired:
        print("✅ 已用写入端原文副本自动重建 %d 枚：%s" % (len(repaired), repaired))
    if unfixed:
        print("❌ %d 枚无原文副本（写入端跑的是旧版脚本）⇒ 需人工按步骤 5.8 用会话回显原文重建，"
              "⛔凭记忆重写：%s" % (len(unfixed), unfixed))
    return 1 if unfixed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=False, help="tool name (normalized allowlist value)")
    ap.add_argument("--logdir", default=LOGDIR_DEFAULT)
    ap.add_argument("--allow-dup", action="store_true",
                    help="v3.19.1: 显式放行同标题短窗重复追加（默认拒写防双签发·反模式13 触发源闸）")
    ap.add_argument("--reflection", action="store_true",
                    help="添加 [童灵思考] 前缀（童灵→童灵心智活动汇报·蒸馏管道扫描标记）")
    ap.add_argument("--guard-line", action="store_true",
                    help="v3.10.24: 独立产出 changelog_guard 检测行（不写条目）——验证块输出前调用")
    ap.add_argument("--verify-reply", metavar="REPLY_FILE",
                    help="v3.13.0: 检测 AI 回复是否包含流程完成令牌（🔖 流程完成令牌：{hash}）。"
                         "传入回复文本文件路径，或用 - 从 stdin 读取。exit 0=包含令牌（流程完成），"
                         "exit 1=不包含令牌（流程未完成，需重新 relay 验证块）。")
    ap.add_argument("--repair-orphans", action="store_true",
                    help="v3.20.0: 独立巡检模式——扫描当日日志的签发账本，机械重建被并发吞没的条目"
                         "（用写入端留存的原文副本·⛔不凭记忆重写）。可挂 cron 定期跑。")
    args = ap.parse_args()

    if args.guard_line:
        val = run_guard_line()
        _write_guard_cache(val)
        print("GUARD_LINE %s" % val)
        return 0

    if args.verify_reply:
        return verify_reply_token(args.verify_reply)
    if args.repair_orphans:
        return repair_orphans_mode(args.logdir)
    if not args.tool:
        print("error: --tool 必填（--guard-line 模式除外）", file=sys.stderr)
        return 2

    # 输入面物理校验（v3.10.9·2026-08-27）：--tool 决定 `## <Tool>` 组头与概览行键，
    # 此前零校验=任意字符串直接进结构层（概览脏行的输入面缺口）。唯一真源=normalize_tool。
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import normalize_tool as nt
    if args.tool not in nt.ALLOWLIST:
        key = nt.norm_key(args.tool)
        cand = {nt.VARIANTS.get(key, key)} | {a for a in nt.ALLOWLIST if nt.norm_key(a) == key}
        canon = next(iter(cand & nt.ALLOWLIST), None)
        if not canon:
            print(f"error: --tool {args.tool!r} 不在 {len(nt.ALLOWLIST)} 规范名 allowlist 且无法归一"
                  f"——按 SKILL.md「工具名规范」节归一后重跑（拒写，不生成脏行）", file=sys.stderr)
            return 1
        args.tool = canon

    dt = datetime.now()
    now_hm = dt.strftime("%H:%M")
    today = dt.strftime("%Y-%m-%d")

    body = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not body.strip():
        print("error: empty entry body on stdin", file=sys.stderr)
        return 2

    # 童灵思考标记（v3.10.15 新增·v1.2 2026-09-05 更名：反思→思考·你裁定认错偏置）
    if args.reflection:
        # 在第一个 ### 标题后添加 [童灵思考] 前缀
        body = re.sub(r"(^###\s+)", r"\1[童灵思考] ", body, count=1, flags=re.M)
        # 如果没有 ### 标题，在第一个 ## 标题后添加
        if not re.search(r"^###\s+", body, re.M):
            # ⚠️ 2026-10-02 段名归一（你指正）：兜底标题原写「童灵认知深化」，与 2026-09-05
            #   你裁定的唯一段名「童灵思考」不一致 → 同一份系统日志里出现两套段名。
            #   判据：蒸馏按前缀 [童灵思考] 扫描（L96·标题内容不参与判据），故改标题不改功能，
            #   但段名统一是规范要求——「名字即货币」（§二·十七同源判据）。
            body = re.sub(r"(^##\s+.*\n)", r"\1\n### [童灵思考] 童灵思考（本日）\n", body, count=1, flags=re.M)
        # 审查F13修复：两个标题都没有时标记无效——必须显式警告而非静默（防标记与内容不符）
        if not re.search(r"^###\s+|^##\s+", body, re.M):
            # v3.16.0（2026-09-11·第18端接入漏网根治）：原实现仅告警 → 改**机械兜底自动补标题**。
            # 漏网实证：AI 传裸文本（无任何标题）→ [童灵思考] 未注入 → 蒸馏分流静默不命中（假绿式漏网）。
            # 全自动化方向（愿景①）：脚本自己补标题，不依赖 AI 记得写 ###。
            body = "### [童灵思考] 童灵思考（%s）\n\n%s" % (today, body.lstrip("\n"))
            print("ℹ️ --reflection：条目体无标题 → 已机械补「### [童灵思考] 童灵思考」标题（防漏网兜底·段名与 2026-09-05 裁定一致）", file=sys.stderr)

    # Bypass guard: a literal time in the 完成 line instead of <NOW>.
    comp = re.search(r"^\s*-\s*\*\*完成\*\*\s*[:：]\s*(.+)$", body, re.M)  # v3.16.0 r1-C6：全/半角冒号并拒（原只拦全角=半角伪造时间可落盘成双行）
    if comp and comp.group(1).strip() != "<NOW>":
        print(
            "error: 完成 field contains literal time '%s' — must use <NOW> "
            "(the script owns the timestamp; a literal value bypasses the physical anchor)"
            % comp.group(1).strip(),
            file=sys.stderr,
        )
        return 1

    # Fill the placeholder (if AI wrote <NOW>) or insert if omitted.
    body = body.replace("<NOW>", now_hm)
    # v3.15.1(2026-09-10·跨组错位根治)：条目须携带 `- **工具**：<规范名>`——下游
    # reconcile_overview.py 的组位归一以此为**唯一归属真源**（缺字段=归不了位·不猜）。
    # 机制与「完成」完全一致：缺则补、有则不动；⛔不改任何既有行内容，⛔不动追加姿势。
    _has_tool = bool(re.search(r"^\s*-\s*\*\*工具\*\*\s*[:：]", body, re.M))  # 批4 r3-K2 [:：]统一
    _has_done = bool(re.search(r"^\s*-\s*\*\*完成\*\*\s*[:：]", body, re.M))  # v3.16.0批3 r2-C6：[:：]统一（原只认全角=半角<NOW>过L211后在此漏判成双行）
    _new = []
    if not _has_tool:
        _new.append("- **工具**：%s" % args.tool)
    elif not re.search(r"^\s*-\s*\*\*工具\*\*\s*[:：]\s*%s\s*$" % re.escape(args.tool), body, re.M):
        # v3.17.9（2026-10-21·Qoder CN·任务卡2026-10-21-静默隐身检测与日志变体根治·组C）：
        #   病形=原「有则不动」只判字段在不在、不判值合不合规——条目体自写 `- **工具**：qodercn`
        #   照原样落盘成变体值（今日 09:18 他窗 ## qodercn 变体组头的上游入口）。下游
        #   resolve_tool_field 已有变体映射（归组面自愈），入口封口后变体永不进盘=发生器根治。
        #   改写面=全部工具字段行（正常仅一条；多条=脏数据一并统一）；冒号形态随原行不变。
        body = re.sub(r"^(\s*-\s*\*\*工具\*\*\s*[:：]).*$", r"\g<1>%s" % args.tool, body, flags=re.M)
        print("ℹ️ v3.17.9 入口封口：条目体工具字段值与 --tool 规范名不符→已机械改写为 %s（不拒写·值归一）" % args.tool, file=sys.stderr)
    if not _has_done:
        _new.append("- **完成**：%s" % now_hm)
    # v3.17.7（2026-10-21·Qoder CN·任务卡2026-10-21-append-log静默丢字段盲区）：
    #   病形=旧两路注入（粗体字段锚/###标题锚）对「## 标题+非粗体bullet」全不中，
    #   re.sub 静默返回原文→工具/完成没注入也不报错→reconcile（归属真源=工具字段·切块锚=^###）
    #   归不了位→条目悬在他端组头下（10:16 实证·写后告警报了但拦不住）。
    #   修法=三级机械保证：①无###先锚保底（标题层级矫正/首行补题，承 v3.16.0 --reflection 补标题先例）
    #   ②字段注入不依赖 body 恰好有锚 ③写前自证闸=补不成即拒写，⛔事后挂账。
    if not re.search(r"^### ", body, re.M):
        _th = re.search(r"^#{2,6} +(\S.*)$", body, re.M)
        if _th:
            body = body[:_th.start()] + "### " + _th.group(1) + body[_th.end():]
            print("ℹ️ v3.17.7 机械兜底：条目体用非###标题（reconcile切块锚=###）→标题层级矫正，题文不变", file=sys.stderr)
        elif body.strip():
            _fl = re.search(r"^\s*(\S.*)$", body, re.M)
            _first = _fl.group(1).strip()
            if re.match(r"^-\s*\*\*[^*]+\*\*\s*[:：]", _first):
                # v3.19.6（沙箱 T6 实锤）：首行是字段行→⛔不吞作标题——旧行为首行整体吃进标题，
                # 字段行静默消失（落盘 7/8 + 标题变"- **类型**：分析"垃圾值）。兜底应"补"不该"吃"：
                # 生成中性可追溯标题，字段原样保全。
                body = "### 未命名条目（%s）\n\n%s" % (now_hm, body.lstrip("\n"))
                print("ℹ️ v3.19.6 兜底修正：条目体无标题且首行是字段行→不吞作标题（防字段丢失）·生成中性标题，字段保全", file=sys.stderr)
            else:
                body = "### " + _first[:60] + "\n\n" + body[_fl.end():].lstrip("\n")
                print("ℹ️ v3.17.7 机械兜底：条目体无任何标题→首行补 ### 标题（截60字）", file=sys.stderr)
    if _new:
        _ins = "".join(s + "\n" for s in _new)
        # 插入点=**首个既有字段行之前**（而非紧跟标题）——避免标题下的空行被留在字段中间，
        # 同时让「工具→完成→其余」贴近单条记录模板顺序。
        _anchor = re.search(r"^- \*\*[^*]+\*\*[:：]", body, re.M)  # 同上 [:：]统一
        if _anchor:
            body = body[:_anchor.start()] + _ins + body[_anchor.start():]
        else:
            _h3l = re.search(r"^###.*$", body, re.M)  # v3.17.7：原 re.sub 无###时静默不插——改显式分支（仍无题=进下方拒写闸）
            if _h3l:
                body = body[:_h3l.end()] + "\n" + _ins + body[_h3l.end():].lstrip("\n")
    # v3.17.7 写前自证闸：条目三要素（###标题/工具/完成）缺一即拒写（仪器故障与判据红分态同族）
    if not (re.search(r"^### ", body, re.M)
            and re.search(r"^\s*-\s*\*\*工具\*\*\s*[:：]", body, re.M)
            and re.search(r"^\s*-\s*\*\*完成\*\*\s*[:：]", body, re.M)):
        print("error: 条目体无法机械补全（空/畸形）→ 拒写。⛔不产出悬空错位条目。模板：首行 `### 标题` + `- **类型**：…` 等粗体字段行，工具/完成由脚本代填", file=sys.stderr)
        return 2

    logfile = os.path.join(args.logdir, "系统日志_%s.md" % today)

    # v3.19.1 防双写闸（Poka-Yoke 设计端·反模式13 触发源根治：双签发→去重删副本→seal 断联）：
    #   同文件存在同标题条目且完成时间 ≤10 分钟 → 拒写；确属新任务同名 → --allow-dup 显式放行。
    if os.path.exists(logfile):  # allow_dup 也进块：只跳拒写不跳检测，两态都要留痕（v3.19.2 自测逮出：整块跳过=allow 无痕=校准数据缺半边）
        _m_title = re.search(r"^### (.+)$", body, re.M)
        if _m_title:
            _t = _m_title.group(1).strip()
            try:
                with open(logfile, encoding="utf-8", errors="replace") as _df:
                    _lines = _df.read().splitlines()
            except OSError:
                _lines = []
            _hit = None
            for _i, _l in enumerate(_lines):
                if _l.strip() == "### " + _t:
                    for _j in range(_i + 1, min(_i + 16, len(_lines))):
                        _m2 = re.match(r"^-\s*\*\*完成\*\*\s*[:：]\s*(\d{2}):(\d{2})", _lines[_j])
                        if _m2:
                            _hit = _m2.group(1) + ":" + _m2.group(2)
                            break
                    if _hit:
                        break
            if _hit:
                _h2m = int(_hit[:2]) * 60 + int(_hit[3:])
                _nowm = int(now_hm[:2]) * 60 + int(now_hm[3:])
                _delta = _nowm - _h2m
                if 0 <= _delta <= 10:
                    # v3.19.2 数据留痕：两态均落 dup_gate.jsonl——窗口阈值校准靠实盘数据不靠人记得（愿景①③）
                    try:
                        import json as _json
                        with open(os.path.join(os.path.dirname(GUARD_CACHE), "dup_gate.jsonl"), "a", encoding="utf-8") as _dg:
                            _dg.write(_json.dumps({"ev": "allow" if args.allow_dup else "reject",
                                                    "ts": "%s %s" % (today, now_hm), "gap_min": _delta,
                                                    "title": _t[:50], "tool": args.tool}, ensure_ascii=False) + "\n")
                    except OSError:
                        pass  # 留痕失败不阻塞主流程（同 seal_ledger 口径）
                    if not args.allow_dup:
                        print("error: 同标题条目 %d 分钟前已写入（完成 %s）→ 拒写防双签发（反模式13 触发源闸）。"
                              "确属新任务同名：加 --allow-dup 显式放行。" % (_delta, _hit), file=sys.stderr)
                        return 3

    # Grouping: tool group header must be unique in the whole file (v3.10.6 根治:
    # tail-window 判定缺陷——组头在文件中部时末尾窗口看不到，误加重复组头，8/12 连犯两次).
    # 判定基准=全文扫描该工具组头是否已存在：存在→并入（不加组头）；不存在→新建组头。
    header = ""
    if os.path.exists(logfile):
        with open(logfile, encoding="utf-8") as f:
            text = f.read()
        group_exists = bool(re.search(rf"^## {re.escape(args.tool)}\s*$", text, re.M))
        if not group_exists:
            header = "## %s\n\n" % args.tool
    else:
        header = (
            "# 系统日志 %s\n\n"
            "## 今日概览\n\n"
            "| 工具 | 任务数 | 关键成果 |\n"
            "|------|--------|---------|\n"
            "| %s | 0 |  |\n\n"
            "## %s\n\n"
        ) % (today, args.tool, args.tool)

    # v3.14.0(2026-09-21·皮叔令「数字分身信誉度最高级别任务」): 令牌内嵌进条目本体——
    #   修 v3.13.0 两缺陷：①签发值只落 last_token.txt 一枚，下次写入即被覆盖 → 历史令牌
    #   全部不可事后验签（2026-09-21 实测：当日 6 枚令牌 grep 日志 0 命中·签发值已被覆盖）；
    #   ②令牌不进日志文件 → 只能证明「某次脚本运行发生过」，不能证明「哪轮·哪条」。
    #   现在：每条条目自带 seal 行（落盘·逐条独立·可事后审计）；签发账本 seal_ledger.log
    #   改为 append-only 追加（保留历史）。
    import hashlib as _hl, secrets as _sk
    _seed = "%s%s%s%s" % (today, now_hm, args.tool, _sk.token_hex(8))
    token_hash = _hl.sha256(_seed.encode("utf-8")).hexdigest()[:8]
    # 条目本体（不含 header）= 重建时需要逐字回读的最小单元。
    # ⛔ header（概览表 + `## 工具` 组头）**不入副本**——重建时若把 header 一起追加，
    #   文件里会出现第二张概览表 + 第二个组头（实证·探针 T4 差 118 字节）。
    #   组头归属由 reconcile 按条目自带的「工具」字段建组/归位（归属真源=工具字段）。
    entry_body = body.rstrip("\n") + "\n" + "- **seal**：%s\n" % token_hash
    content = header + entry_body
    try:
        _cache_dir = os.path.dirname(GUARD_CACHE)
        os.makedirs(_cache_dir, exist_ok=True)
        with open(os.path.join(_cache_dir, "last_token.txt"), "w", encoding="utf-8") as _tf:
            _tf.write(token_hash)
        # 端间版本可观测（2026-10-23·MiniMax Code 端·治尺轮）：台账行尾加一列
        #   **本脚本内容指纹** ⇒ 事后可机械判定「各端副本是不是同一版」
        #   （hash 不同 = 版本漂移·⛔不必维护版本号·⛔不依赖人记得同步）
        #   ⛔ 只在行尾追加一列·⛔前 6 列一字不动 ⇒ 旧解析器（取第 1 段比对）不受影响
        try:
            with open(os.path.abspath(__file__), "rb") as _sfp:
                _script_fp = _hl.sha256(_sfp.read()).hexdigest()[:8]
        except OSError:
            _script_fp = "unknown"
        with open(os.environ.get("SYSLOG_SEAL_LEDGER") or os.path.join(_cache_dir, "seal_ledger.log"), "a", encoding="utf-8") as _lf:
            _lf.write("%s\t%sT%s\t%s\t%s\t%s\t%s\n" % (token_hash, today, now_hm, os.path.basename(logfile), args.tool, os.path.dirname(os.path.abspath(logfile)), _script_fp))
    except Exception:
        pass  # 落盘失败不阻塞写入主流程；verify 时按"无签发记录"降级处理

    # —— 写入端留存的条目原文副本（2026-10-23·MiniMax Code 端·治尺轮）——
    #   ⛔ 必须在 append **之前**落副本：条目被并发吞没时，副本仍在本机 ⇒ 可机械重建。
    #   ⛔ 副本 = 追加内容的逐字原文（含原 seal 行）⇒ 重建不改写事实、不产生新 seal。
    #   ⚠️ 副本目录在 ~/.cache（缓存面）：机器重装/清缓存后副本不在 ⇒ 回验降级为人工路径（诚实降级）。
    if _save_entry_copy(token_hash, entry_body) is None:
        # v3.19.6：副本落盘失败显形（旧实现静默吞）——副本是吞没自愈的重建依据，断链无人知=自愈静默失效
        print("⚠️ 条目原文副本落盘失败（吞没自愈的重建依据缺失·主流程继续）——请检查 %s 可写性" % ENTRY_COPY_DIR, file=sys.stderr)
    _prune_entry_copies()

    # O_APPEND atomic append — concurrent writers never overwrite each other.
    # 加共享锁：与 reconcile 的 read→replace 互斥，防并发 append 被 os.replace 换 inode 吞掉
    from systemlog_lock import log_lock
    with log_lock(logfile):
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(content)

    # Mechanical overview reconcile (best effort; never blocks the append).
    # stdout 静默——避免子进程诊断行污染 AI 捕获的 stdout（stdout 只应为验证块）。
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "reconcile_overview.py"), logfile],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        if r.returncode != 0:
            # 审查F14修复：不阻塞主流程，但失败信号必须可见（不再静默吞）
            print("⚠️ reconcile 未收敛（exit %d）——概览计数可能滞后，建议手动跑 reconcile_overview.py 查看详情" % r.returncode, file=sys.stderr)
    except Exception as e:
        print("⚠️ reconcile 调用异常：%s（概览计数可能滞后）" % e, file=sys.stderr)

    # —— 吞没自愈（2026-10-23·MiniMax Code 端·治尺轮·根治跨端并发丢条）——
    #   病根：端间副本版本漂移 ⇒ 他端若跑**未取锁的旧版**脚本，其 append 可落在
    #   reconcile 的 read→replace 窗口内被换 inode 吞掉（实证 2026-10-23 16:20
    #   Qoder CN 端条目：seal 已签发却不在文件里 ⇒ 孤儿 seal ⇒ 当天后续写入持续误报）。
    #   正解：append 后**回读自验**——自己的 seal 必须在文件里；不在 ⇒ 补写。
    #   ⛔ 补写前先确认当前文件里确实没有本 seal ⇒ 绝不产生重复条目
    #   ⛔ 补写持同一把锁 ⇒ 与 reconcile 的 replace 不交叠
    #   ⚠️ 残余窗口：未取锁的他端 reconcile 若在本次自验之后才动手 ⇒ 仍可能吞本条
    #     ⇒ 端间副本版本对齐（各端都跑带锁版）才是根治面·已出核对单
    _seal_marker = "- **seal**：%s" % token_hash
    for _try in range(3):
        try:
            with open(logfile, encoding="utf-8", errors="replace") as _rf:
                _cur = _rf.read()
        except OSError:
            _cur = ""
        if _seal_marker in _cur:
            break
        with log_lock(logfile):
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(content)
        print("⚠️ 吞没自愈：追加内容未见于文件（疑被并发 replace 吞没）——补写第 %d 次" % (_try + 1), file=sys.stderr)
    else:
        print("⚠️ 吞没自愈：补写 3 次仍未确认落盘（seal=%s）——该条可能缺失，请人工核对" % token_hash, file=sys.stderr)

    # v3.10.24(2026-09-01·你"系统日志写半天"架构解耦): changelog_guard 检测行
    # 不再在写入路径同步内嵌（全树扫描 ~7s×每次写入=主凶）——改由 AI 在验证块
    # 输出前跑 `--guard-line` 独立模式（每会话 1 次）机械产出。填值权仍归脚本。
    # 见 run_guard_line()。

    # 调试行写 stderr（机器消费者用），stdout 只出验证块供 AI 逐字 relay
    sys.stderr.write("APPENDED %s\n" % logfile)
    sys.stderr.write("TIME %s %s\n" % (today, now_hm))
    if args.reflection:
        sys.stderr.write("REFLECTION true\n")
    sys.stderr.write("---ENTRY---\n")
    sys.stderr.write(content + "\n")

    # v3.12.0 回复验证块：脚本机械产出，AI 只许逐字 relay（防误·设计消除错误）。
    # 漂移在架构上不可能——AI 接触不到任何格式构造权。
    emit_verify_block(logfile, today, now_hm, args.tool, body, token_hash)
    return 0


def emit_verify_block(logfile, today, now_hm, tool, body, token_hash):
    """机械产出回复验证块（diff 块）。AI 只许逐字 relay，接触不到构造权。

    段2 的全部行（📍文件/⏰时间/🔧工具/📋校验/📋变更日志检测/🔖流程完成令牌）均由脚本算值填，
    与 flow-write.md 步骤5 模板逐字一致。设计消除错误：AI 无法改写/表格化/增删任何行。

    v3.13.0(2026-09-02·回复完整性令牌机制): 验证块末尾新增「🔖 流程完成令牌」——
    唯一 hash（sha256(time+random)前8位），AI 不能伪造。SKILL.md 声明：系统日志流程完成的
    唯一标志是回复末尾包含此令牌。没有令牌=流程未完成=AI 必须重新 relay 验证块。
    --verify-reply 模式检测回复是否包含此令牌。
    """
    import hashlib
    import secrets
    fname = os.path.basename(logfile)
    # 数据一致性：重读文件确认刚写入的条目存在
    consistency = "✅ 数据一致性：通过"
    try:
        with open(logfile, encoding="utf-8") as f:
            txt = f.read()
        if not re.search(rf"^- \*\*完成\*\*[:：]\s*{re.escape(now_hm)}$", txt, re.M):  # 批4 r3-K2 回读同型+\s*（冒号后带空格值曾假红·全角同修）
            consistency = "⚠️ 数据一致性：写入后回读未命中（请人工核对）"
    except Exception:
        consistency = "⚠️ 数据一致性：回读失败（请人工核对）"
    # 格式完整性：统计字段行数（期望 8）
    n_fields = len(re.findall(r"^- \*\*[^*]+\*\*[:：]", body, re.M))  # 批4 r3-K2 计数字段同型
    if n_fields >= 8:
        fmt = "✅ 格式完整性：%d 字段齐全（≥8 基础门槛·含扩展）" % n_fields
    else:
        fmt = "⚠️ 格式完整性：%d/8 基础字段不足（必备字段缺失·与扩展字段无关）" % n_fields
    # 变更日志检测：读 --guard-line 写入的缓存
    gv = _read_guard_cache()
    if gv is None:
        changelog = "⚠️ guard_line 未跑（先跑 `append_log_entry.py --guard-line` 填值）"
    else:
        changelog = gv
    # v3.17.3 自签 seal 回验（2026-10-12 成长箱 Loop 实证：本端 21:00 写入成功的条目，
    #   21:05 被另一窗口的"读全文→写回"吞掉——O_APPEND 防得住追加并发、防不住整文件重写，
    #   塌缩熔断阈值 >30% 也报不出（当日只丢 1 条）。现按签发账本逐枚回查，丢了就在验证块喊出来。）
    seals_line = "✅ 自签 seal 回验：通过"
    try:
        _lg = os.environ.get("SYSLOG_SEAL_LEDGER") or os.path.join(os.path.dirname(GUARD_CACHE), "seal_ledger.log")
        _mine = []
        if os.path.exists(_lg):
            with open(_lg, encoding="utf-8", errors="replace") as _sf:
                for _l in _sf:
                    _c = _l.rstrip("\n").split("\t")
                    if (len(_c) >= 5 and _c[2] == os.path.basename(logfile) and str(today) in _c[1]
                            and _c[4] == os.path.dirname(os.path.abspath(logfile))):
                        _mine.append(_c[0])
        with open(logfile, encoding="utf-8", errors="replace") as _ff:
            _body = _ff.read()
        _void = set()
        _vp = os.path.join(os.path.dirname(_lg), "seal_void.log")
        if os.path.exists(_vp):
            with open(_vp, encoding="utf-8", errors="replace") as _vf:
                for _v in _vf:
                    _vc = _v.rstrip("\n").split("\t")
                    if len(_vc) >= 4 and _vc[3] == os.path.basename(logfile):
                        _void.add(_vc[0])
        _lost = [x for x in _mine if x not in _body and x not in _void]
        if _lost:
            # —— 自动重建（2026-10-23·MiniMax Code 端·治尺轮）——
            #   病根：孤儿 seal 的恢复依赖「写入端会话回显原文」（人工/记忆依赖·跨端不可靠）。
            #   正解：写入端留有原文副本 ⇒ 恢复 = 机械回读副本 ⇒ 不凭记忆重写。
            #   ⛔ 重建前确认该 seal 确不在文件里（幂等）· ⛔ 持同一把锁。
            #   ⚠️ 残余（无副本）：写入端跑的是旧版脚本（没留副本）⇒ 只能人工·如实报出。
            _repaired, _unfixed = _rebuild_orphan_seals(logfile, _lost)
            if _repaired:
                with open(logfile, encoding="utf-8", errors="replace") as _ff2:
                    _body = _ff2.read()
                _unfixed = [x for x in _unfixed if x not in _body]
                # 重建后需重跑 reconcile 让概览计数与分组归位（⛔父进程不持锁时再 spawn）
                try:
                    subprocess.run(
                        [sys.executable, os.path.join(os.path.dirname(__file__), "reconcile_overview.py"), logfile],
                        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                except Exception:
                    pass
            if _repaired and _unfixed:
                # v3.19.6：双态并存时合并呈现——旧实现 ❌ 行整体覆盖 ✅ 行，重建成果被吞（验证块只见 ❌）
                seals_line = ("⚠️ 自签 seal 回验：已按原文副本自动重建 %d 枚（%s）；另有 %d 枚无副本须人工按步骤 5.8 重建（%s）"
                              "——⛔凭记忆重写；若确属去重删副本：systemlog_entry_rm.py 留 VOID 记录（本检自动认）"
                              % (len(_repaired), _repaired[:6], len(_unfixed), _unfixed[:6]))
            elif _repaired:
                seals_line = ("✅ 自签 seal 回验：已按写入端原文副本自动重建 %d 枚被吞条目（%s）"
                              % (len(_repaired), _repaired[:6]))
            elif _unfixed:
                seals_line = ("❌ 自签 seal 回验：%d/%d 枚已签发却不在文件里（疑被并发整文件回写吞没）%s"
                              " —— 写入端无原文副本（该端跑的是旧版脚本）⇒ 按步骤 5.8 用会话回显原文重建，"
                              "⛔凭记忆重写；若确属去重删副本：systemlog_entry_rm.py 留 VOID 记录（本检自动认）"
                              % (len(_unfixed), len(_mine), _unfixed[:6]))
            else:
                seals_line = ("❌ 自签 seal 回验：%d/%d 枚已签发却不在文件里（疑被并发整文件回写吞没）%s"
                              " —— 按步骤 5.8 用会话回显原文重建，⛔凭记忆重写；若确属去重删副本："
                              "systemlog_entry_rm.py 留 VOID 记录（本检自动认）" % (len(_lost), len(_mine), _lost[:6]))
    except Exception as _e:
        seals_line = "⚪ 自签 seal 回验：未执行（%s）" % type(_e).__name__
    # v3.14.0：令牌已在写入前生成，并已内嵌进条目（- **seal**：行）+ 记入 seal_ledger.log
    #   （append-only）。此处只负责把同一枚值打进验证块——保证「条目内 seal ≡ 回复令牌」。
    print("📝 系统日志已写入")
    print("━━━━━━━━━━━━━━━")
    print()
    print("📍 文件：%s" % fname)
    print()
    print("⏰ 时间：%s %s" % (today, now_hm))
    print()
    print("🔧 工具：%s" % tool)
    print()
    print("📋 校验状态：")
    print(consistency)
    print(fmt)
    print("✅ 机械校验：完成行回读一致 + 字段结构检查（假设验证=AI步骤4.3自检项·脚本未代验·审查F3如实化）")
    print(seals_line)
    print()
    print("📋 变更日志检测：%s" % changelog)
    print()
    print("🔖 流程完成令牌：%s" % token_hash)


def verify_reply_token(reply_path):
    """v3.13.0: 检测 AI 回复是否包含流程完成令牌。

    流程完成令牌格式：`🔖 流程完成令牌：{8位hash}`
    - 包含令牌 → exit 0（流程完成）
    - 不包含令牌 → exit 1（流程未完成，需重新 relay 验证块）

    这是防错层兜底（事后检测），不是防误层根治（事前消除）。
    防误层根治是：flow-write.md 步骤5 声明「系统日志流程完成的唯一标志是回复末尾包含此令牌」，
    把 relay 验证块从「行为要求」升级为「流程完成的必要条件」。

    诚实边界：纯 AI 环境不存在「绝对物理杜绝」——AI 仍然可以选择不 relay 验证块，
    只是这样流程就不算完成。--verify-reply 需要 AI 自觉跑，AI 可以不跑。
    可达的最优形态：绕过成本 > 遵守成本 + 绕过留痕。
    """
    if reply_path == "-":
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    else:
        try:
            with open(os.path.expanduser(reply_path), encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print("error: 无法读取回复文件 %s: %s" % (reply_path, e), file=sys.stderr)
            return 2

    # 检测流程完成令牌：🔖 流程完成令牌：{8位十六进制hash}
    token_pattern = r"🔖\s*流程完成令牌[：:]\s*([0-9a-f]{8})"
    m = re.search(token_pattern, text)
    if m:
        token = m.group(1)
        # 审查F1：与最近签发值比对（格式合法 ≠ 本会话签发）
        issued = None
        try:
            token_store = os.path.join(os.path.dirname(GUARD_CACHE), "last_token.txt")
            if os.path.exists(token_store):
                with open(token_store, encoding="utf-8") as tf:
                    issued = tf.read().strip()
        except Exception:
            issued = None
        _ledger_hit = None
        try:
            # v3.19.6（沙箱 T2e 实锤）：与写入路径(L603)/自签回验(L719)/巡检(L332)同口径认
            # SYSLOG_SEAL_LEDGER 覆盖——旧版读死默认路径，覆盖账本里的合法令牌被误报"伪造"。
            _lp = os.environ.get("SYSLOG_SEAL_LEDGER") or os.path.join(os.path.dirname(GUARD_CACHE), "seal_ledger.log")
            if os.path.exists(_lp):
                for _line in open(_lp, encoding="utf-8"):
                    if _line.split("\t", 1)[0].strip() == token:
                        _ledger_hit = _line.rstrip("\n")
                        break
        except Exception:
            _ledger_hit = None
        if issued == token:
            print("✅ 回复完整性：通过（令牌=%s·与本会话签发值一致·验签✓）" % token)
            print("📋 系统日志流程完成。")
            return 0
        if _ledger_hit:
            print("✅ 回复完整性：通过（令牌=%s·命中签发账本 seal_ledger·v3.14.0 历史可验）" % token)
            print("   账本行：%s" % _ledger_hit)
            print("📋 系统日志流程完成。")
            return 0
        elif issued is None:
            print("⚠️ 回复完整性：无本会话签发记录（签发值落盘缺失或系统异常）——无法验签，请人工核对日志文件·审查F1", file=sys.stderr)
            return 1
        else:
            print("⚠️ 回复完整性：令牌格式合法但与本会话最近签发值不符（伪造或跨会话）·审查F1验签", file=sys.stderr)
            print("📌 处置：确认是否本会话产出——是则人工核对日志文件后放行，否则重新 relay 验证块。", file=sys.stderr)
            return 1
    else:
        print("❌ 回复完整性：未通过（缺少流程完成令牌）", file=sys.stderr)
        print("⚠️ 系统日志流程未完成——AI 回复中未检测到「🔖 流程完成令牌：{hash}」。", file=sys.stderr)
        print("📌 可能原因：", file=sys.stderr)
        print("  1. AI 自创了回复格式，跳过了验证块的逐字 relay", file=sys.stderr)
        print("  2. 验证块被表格化/改写/增删了行", file=sys.stderr)
        print("  3. append_log_entry.py 版本过旧（< v3.13.0），未产出令牌", file=sys.stderr)
        print("📌 修复：重新逐字 relay append_log_entry.py stdout 末尾的验证块（含🔖流程完成令牌行）。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
