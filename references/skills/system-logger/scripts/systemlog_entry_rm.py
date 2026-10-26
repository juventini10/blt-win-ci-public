#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""systemlog_entry_rm.py — 系统日志条目删除唯一合法通道（v3.19.1·反模式13 的执法件）

为什么要有本件：手工删除条目（如去重删副本）会让该条目的 `- **seal**` 与文件本体断联，
append_log_entry 的自签回验随即永久报假 ❌（"疑被吞没"误导排查方向·假阴性疲劳吞真丢件）。
本件把"删条目"收敛为唯一通道，删除动作必须处置 seal：
  ① 默认 → 写 VOID 记录（~/.cache/systemlogger/seal_void.log）→ 回验自动认，不再假红；
  ② --migrate-to <存活条目标题片段> → 把 seal 注记回填到存活条目（去重合并场景）。
用法：
  python3 systemlog_entry_rm.py --title "<标题片段>" --reason "<为何删>" [--file 日志路径] [--migrate-to "<存活条目标题片段>"]
退出码：0=成功｜1=未命中/不唯一/写失败｜2=用法错误
诚实边界：本件保证"删除有留痕、seal 不失联"；⛔不判断删除本身是否该做（那是人的决定）。
"""
try:
    import sys; sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import argparse, os, re, subprocess, sys, time

__version__ = "v1.1"  # v1.1（2026-10-24·沙箱审计根治批）：①全程持 <logdir>/.systemlog.lock（旧版整文件重写裸奔·T12 实锤）②--migrate-to 先删后插重构根治 off-by-one 僵尸标题（T9 实锤）③迁移注记独立成行（旧行内拼接=单行双字段）④VOID 路径与 append 自检同推导（覆盖台账口径统一）⑤备份改锁内快照
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "systemlogger")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None, help="日志文件路径（默认今日）")
    ap.add_argument("--title", required=True, help="要删除条目的标题片段（须唯一命中一条 ### 条目）")
    ap.add_argument("--reason", required=True, help="删除原因（落 VOID 记录/迁移注记）")
    ap.add_argument("--migrate-to", default=None, help="把 seal 注记回填到该标题片段的存活条目（不传=记 VOID）")
    a = ap.parse_args()

    today = time.strftime("%Y-%m-%d")
    logfile = a.file or os.path.join(os.path.expanduser("~"), "[记忆共享中心]/工作日志/系统日志", "系统日志_%s.md" % today)
    if not os.path.exists(logfile):
        print("error: 文件不存在 %s" % logfile, file=sys.stderr); return 2

    from systemlog_lock import log_lock
    # v3.19.6：读行→备份→改→写全程持同一把 <logdir>/.systemlog.lock——本件是"整文件重写"通道，
    # 与 append(O_APPEND 追加)/reconcile(read→replace) 同源竞态（v3.17.7 封窗，本件 v3.19.1 开通道时
    # 漏挂锁；沙箱 T12 实锤：持锁期间 append 阻塞而 rm exit 0 跑完=裸奔）。reconcile 移锁外 spawn
    # （append 同例·防父子同锁死锁）。
    with log_lock(logfile):
        lines = open(logfile, encoding="utf-8", errors="replace").read().splitlines(True)

        starts = [i for i, l in enumerate(lines) if l.startswith("### ")]
        hits = [i for i in starts if a.title in lines[i]]
        if len(hits) != 1:
            print("error: 标题片段命中 %d 条（须唯一）：%s" % (len(hits), [lines[i].strip()[:40] for i in hits]), file=sys.stderr)
            return 1
        s0 = hits[0]
        nxt = [i for i in starts + [i for i, l in enumerate(lines) if l.startswith("## ") if i > s0] if i > s0]
        e0 = min(nxt) if nxt else len(lines)
        block = lines[s0:e0]
        while block and block[-1].strip() == "":
            block.pop()
        seal = None
        for l in block:
            m = re.search(r"-\s*\*\*seal\*\*\s*[:：]\s*([0-9a-fA-F]{8})", l)
            if m:
                seal = m.group(1); break

        # 备份（锁内快照——旧实现锁外快照可拿到竞态中间态）
        bak = logfile + time.strftime(".bak-rm-%Y%m%d%H%M%S")
        open(bak, "w", encoding="utf-8").write("".join(lines))

        if seal and a.migrate_to:
            surv = [i for i in starts if i != s0 and a.migrate_to in lines[i]]
            if len(surv) != 1:
                print("error: --migrate-to 命中 %d 条（须唯一）" % len(surv), file=sys.stderr); return 1
            # v3.19.6 重构：先删（当下坐标）→ 再在删除后的行集上重定位存活条目、注记独立成行插 seal 行后。
            # 旧实现按"注记插入了一行"平移被删块索引（s0+1/e0-1），但注记实为行内拼接=零平移 →
            # off-by-one 把标题行留在文件里成零字段僵尸条目（沙箱 T9 实锤·概览计数永久虚高）。
            del lines[s0:e0]
            starts2 = [i for i, l in enumerate(lines) if l.startswith("### ")]
            surv2 = [i for i in starts2 if a.migrate_to in lines[i]]
            if len(surv2) != 1:
                print("error: 删除后存活条目定位异常（%d 条）——内存态校验失败，未写盘·文件无损" % len(surv2), file=sys.stderr)
                return 1
            sv2 = surv2[0]
            se2 = min([i for i in starts2 + [i for i, l in enumerate(lines) if l.startswith("## ") if i > sv2] if i > sv2] or [len(lines)])
            note = "- **seal注记**：🟡 %s 迁移自删除副本（%s·%s）\n" % (seal, a.reason, time.strftime("%Y-%m-%d %H:%M"))
            ins = se2  # 存活条目无 seal 行 → 插块末尾
            for j in range(sv2, se2):
                if re.search(r"-\s*\*\*seal\*\*\s*[:：]", lines[j]):
                    ins = j + 1  # v3.19.6：注记独立成行（旧实现行内拼接=单行双字段形态病·沙箱 T9 实锤）
                    break
            lines.insert(ins, note)
        else:
            del lines[s0:e0]
            if seal:
                os.makedirs(CACHE, exist_ok=True)
                # v3.19.6 口径统一：VOID 路径与 append_log_entry 自检同推导——
                # SYSLOG_SEAL_VOID 显式覆盖 > 台账所在目录（SYSLOG_SEAL_LEDGER）> 默认缓存目录。
                # 旧实现单认 SYSLOG_SEAL_VOID，与 append 自检"从台账目录推导"两套口径，覆盖台账
                # 场景 VOID 认账失效（自签回验假红回归）。
                voidp = (os.environ.get("SYSLOG_SEAL_VOID")
                         or os.path.join(os.path.dirname(os.environ.get("SYSLOG_SEAL_LEDGER") or os.path.join(CACHE, "seal_ledger.log")),
                                         "seal_void.log"))
                with open(voidp, "a", encoding="utf-8") as vf:
                    vf.write("%s\t%s\t%s\t%s\t%s\n" % (seal, time.strftime("%Y-%m-%dT%H:%M"), a.reason,
                                                        os.path.basename(logfile), os.path.dirname(os.path.abspath(logfile))))

        open(logfile, "w", encoding="utf-8").write("".join(lines))
    rc_over = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "reconcile_overview.py"), logfile],
                             capture_output=True)
    print("RM-OK | 删除 1 条 | seal=%s 处置=%s | 备份=%s" % (seal or "-", ("迁移→" + a.migrate_to) if (seal and a.migrate_to) else ("VOID 记录" if seal else "无 seal"), os.path.basename(bak)))
    print("提示：概览已重算（rc=%d）。✅DO 立即 git commit 固化（步骤 3.4）。" % rc_over.returncode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
