#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clutter_check.py — 包内杂物闸（v1.0 · 2026-10-25 clock-loop E 路径独立盲审 P5 根治）

TRUTH_OF: 杂物判据清单唯一真源=本文件常量（⛔不在别处复制）。
为什么存在：
  2026-10-25 独立盲审查出包内有 .DS_Store（顶层 + references/）与 scripts/__pycache__，
  且 skill_eval 的 file_clutter 判 0.4（candidate-found）——而 run.sh 十二闸**对此零覆盖**：
  杂物只在"被评估"时才被发现，平时新增无人拦=回流无保护。本闸把它变成常驻判据。
判据（只读·⛔不删任何东西——清理动作归人/归 trash，本件只显形）：
  第一查【杂物】①系统垃圾 .DS_Store/Thumbs.db ②编译缓存 __pycache__/*.pyc ③零字节 .md/.py
  第二查【审计链跟踪态】scripts/{seal,followup_ledger,scan_ledger}.log 与 steps 键文件必须仍在 git 跟踪态。
    为什么不交给 .gitignore 管：`!` 只是意图留痕，一旦这些件被 untrack，ignore 会让它们永久静默不再入库，
    且没有任何判据为此变红——换机即断封口哈希链、守卫 S4 台账对账失去数据源。
    非 git 环境（发布包/装机态）如实 SKIP，⛔不假绿也不假红。
用法：python3 scripts/clutter_check.py [--skill-root DIR] [--selftest]
退出码：0=干净 / 1=检出杂物 / 2=参数或路径错误
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import os
import shutil
import sys
import tempfile

NAME = "clutter_check.py v1.3"
JUNK_NAMES = {".DS_Store", "Thumbs.db", ".directory"}
JUNK_DIRS = {"__pycache__", ".pytest_cache"}
ZERO_EXT = (".md", ".py")


def scan(root):
    """返回 [(相对路径, 类别)]；⛔跳过 .git（版本库自有件不归本闸管）。"""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if ".git" in dirnames:
            dirnames.remove(".git")
        for d in list(dirnames):
            if d in JUNK_DIRS:
                found.append((os.path.join(rel_dir, d) if rel_dir != "." else d, "编译缓存目录"))
        for f in filenames:
            p = os.path.join(dirpath, f)
            rel = os.path.join(rel_dir, f) if rel_dir != "." else f
            if f in JUNK_NAMES:
                found.append((rel, "系统垃圾"))
                continue
            if f.endswith(".pyc"):
                found.append((rel, "编译缓存件"))
                continue
            if f.endswith(ZERO_EXT):
                try:
                    if os.path.getsize(p) == 0:
                        found.append((rel, "零字节文件"))
                except OSError:
                    found.append((rel, "不可读(计红)"))
    return found


def check(root):
    """主查＝杂物 + 审计链跟踪态，两项合一退出码（run.sh 单点调用不变，扩查不改接线）。"""
    if not os.path.isdir(root):
        print("CLUTTER:ERROR 包根不可达 %s" % root)
        return 2
    found = scan(root)
    rc = 0
    if found:
        print("CLUTTER:FAIL 包内检出 %d 项运行时/系统杂物（⛔不该随包分发·清理归 trash 不归本闸）：" % len(found))
        for rel, kind in sorted(found):
            print("   %s ← %s" % (rel, kind))
        rc = 1
    else:
        print("CLUTTER:OK 包内无系统垃圾/编译缓存/零字节件")
    t_rc, t_lines = check_tracking(root)
    for line in t_lines:
        print(line)
    return 1 if (rc or t_rc) else 0


# ── 第二查：审计链跟踪态（杂物清完不等于账本活着）──
# 病名：.gitignore 的 `!` 只是意图留痕，不是强制闸。seal.log / followup_ledger.log / scan_ledger.log
# 与 steps 键文件一旦被 untrack，ignore 规则会让它们**永久静默不再入库**（且 check-ignore 对已跟踪件短路，
# 人在的时候根本看不出问题），结果=封口哈希链与守卫 S4 台账对账脱离容灾面，没有任何一栏为此变红。
TRACK_MUST = ["scripts/seal.log", "scripts/followup_ledger.log", "scripts/scan_ledger.log"]
TRACK_GLOB = "steps/step0-determination-*.md"
# 反方向（独立复核 D-1）：甲类【可再生命】必须**不在**跟踪态。ignore 对已跟踪件短路＝脱离时无人报警，
# 出库动作也因此"做过又被塞回来"而无人知。双向都判：漏进与漏出同罪。
NOT_TRACK = (".landing_baseline", ".briefing_baseline", ".seal_fingerprint",
             ".DS_Store", ".pyc", ".pytest_cache")
# v1.3 挪出包后同族正判据：这些件本就不该出现在包内任何位置（在=落点漂移回潮）
IN_PACKAGE_FORBIDDEN = (".landing_baseline", ".briefing_baseline", ".seal_fingerprint")


def git_root_of(path):
    d = os.path.abspath(path)
    while d and d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def _walk_all(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for f in filenames:
            yield os.path.relpath(os.path.join(dirpath, f), root)


def check_tracking(root):
    """返回 (rc, 行列表)。非 git 环境（发布包/装机态）→ SKIP 不假绿；git 不可用 → 判红不静默。"""
    inpkg = sorted(p for p in _walk_all(root) for x in IN_PACKAGE_FORBIDDEN if x in p)
    if inpkg:
        return (1, ["FAIL 运行时态件仍在 Skill 包内（v2.16 起默认落点=~/.cache/triwich/）：%s"
                    % "、".join(inpkg[:6])])
    import subprocess
    if not git_root_of(root):
        return (0, ["⚪ 跟踪态断言 SKIP：非 git 环境（发布包/装机态无 .git）"])
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--"], cwd=root,
                             capture_output=True, text=True, timeout=60)
    except Exception as e:
        return (1, ["FAIL 跟踪态断言不可执行：%s（⛔不得当作通过）" % e])
    if out.returncode != 0:
        return (1, ["FAIL 跟踪态断言 git 失败 rc=%d %s"
                    % (out.returncode, (out.stderr or "").strip()[:80])])
    tracked = set(x for x in out.stdout.split("\0") if x)
    files = [p for p in TRACK_MUST if os.path.isfile(os.path.join(root, p))]
    import glob as _g
    files += sorted(os.path.relpath(x, root) for x in _g.glob(os.path.join(root, TRACK_GLOB)))
    if not files:
        return (0, ["⚪ 跟踪态断言：本机无审计链件可查（新装/发布态正常）"])
    back = sorted({p for p in tracked for x in NOT_TRACK if x in p})
    if back:
        return (1, ["FAIL 可再生命混入跟踪态（.gitignore 对已跟踪件不生效，需 git rm --cached 出库）：%s"
                    % "、".join(back[:6])])
    miss = [p for p in files if p not in tracked]
    if miss:
        return (1, ["FAIL 审计链件脱离跟踪态（封口链与 S4 对账将脱离容灾面·需 git add 回来）：%s"
                    % "、".join(miss[:6])])
    return (0, ["TRACK:OK 审计链件在跟踪态（台账+键文件共 %d 件）" % len(files)])


def selftest():
    """双向自检（对齐"新锁必自带负例"——P1 同批教训：无负例的锁等于没锁）。"""
    ok = True
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "pkg")
        os.makedirs(os.path.join(base, "scripts"))
        os.makedirs(os.path.join(base, "references"))
        open(os.path.join(base, "SKILL.md"), "w").write("# 干净\n")
        rc = check(base)
        print("[%s] 合规态必绿: exit=%d 期望=0" % ("PASS" if rc == 0 else "FAIL", rc))
        ok &= rc == 0

        open(os.path.join(base, ".DS_Store"), "w").write("junk")
        rc = check(base)
        print("[%s] 系统垃圾必红: exit=%d 期望=1" % ("PASS" if rc == 1 else "FAIL", rc))
        ok &= rc == 1

        os.remove(os.path.join(base, ".DS_Store"))
        os.makedirs(os.path.join(base, "scripts", "__pycache__"))
        open(os.path.join(base, "scripts", "__pycache__", "a.pyc"), "w").write("x")
        rc = check(base)
        print("[%s] 编译缓存必红: exit=%d 期望=1" % ("PASS" if rc == 1 else "FAIL", rc))
        ok &= rc == 1

        shutil.rmtree(os.path.join(base, "scripts", "__pycache__"))
        open(os.path.join(base, "references", "ghost.md"), "w").close()
        rc = check(base)
        print("[%s] 零字节件必红: exit=%d 期望=1" % ("PASS" if rc == 1 else "FAIL", rc))
        ok &= rc == 1

        os.remove(os.path.join(base, "references", "ghost.md"))
        # 第二查负例 A：无 .git 的合成目录不得误报（发布/装机态合法 SKIP）
        tr_rc, tr_lines = check_tracking(base)
        ok_a = tr_rc == 0
        print("[%s] 非 git 态不误报: rc=%d %s" % ("PASS" if ok_a else "FAIL", tr_rc, tr_lines[0][:44]))
        ok &= ok_a
        # 第二查负例 B：真 git 仓里把台账件 untrack → 必须判红（这条不给负例就是纸闸）
        import subprocess
        repo = os.path.join(td, "repo")
        os.makedirs(os.path.join(repo, "scripts"))
        open(os.path.join(repo, "scripts", "seal.log"), "w").write("x\n")
        open(os.path.join(repo, "SKILL.md"), "w").write("# t\n")
        try:
            for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "i"]):
                subprocess.run(cmd, cwd=repo, check=True, capture_output=True, timeout=60)
            ok_on = check_tracking(repo)[0] == 0
            subprocess.run(["git", "rm", "--cached", "-q", "--", "scripts/seal.log"],
                           cwd=repo, check=True, capture_output=True, timeout=60)
            r_off, l_off = check_tracking(repo)
            ok_b = ok_on and r_off == 1 and "脱离跟踪态" in l_off[0]
            print("[%s] 跟踪↔脱跟踪双向: 在跟踪判绿=%s / untrack 判红=%s" % ("PASS" if ok_b else "FAIL", ok_on, r_off))
        except Exception as e:
            ok_b = False
            print("[FAIL] 第二查负例 B 夹具不可跑：%s" % str(e)[:70])
        ok &= ok_b
        rc = check(os.path.join(td, "nope"))
        print("[%s] 包根不可达必显形: exit=%d 期望=2" % ("PASS" if rc == 2 else "FAIL", rc))
        ok &= rc == 2
    print("SELFTEST:%s" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--selftest", action="store_true", help="夹具双向自检（run.sh 常驻调用）")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return check(os.path.abspath(a.skill_root))


if __name__ == "__main__":
    sys.exit(main())
