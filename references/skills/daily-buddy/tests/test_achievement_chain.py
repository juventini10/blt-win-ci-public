#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成就链四态回归（跨平台·本地与 GitHub CI 同一份脚本）

用法：
  python3 test_achievement_chain.py --pkg <安装包根目录>            # 测补丁后（发版态）
  python3 test_achievement_chain.py --pkg <安装包根目录> --no-patch  # 测补丁前（现网态）

退出码：0=全绿；1=有用例失败；2=环境不满足（夹具缺失）
"""
import argparse, os, shutil, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

REPL = {
    "[记忆共享中心]": None,   # 运行时填
    "[日记仓库]": None,
    "[日记子目录]": "1-每日计划/01-日记",
}
TPL = "# {d}\n\n<!-- SECTION: ACHIEVEMENTS -->\n- 本日新增达成：待定\n<!-- /SECTION -->\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True, help="安装包根目录（含 references/）")
    ap.add_argument("--no-patch", action="store_true", help="不应用 P0 补丁，测现网态")
    ap.add_argument("--date", default=date.today().isoformat(), help="测试用日期，默认今天")
    a = ap.parse_args()

    PKG = Path(a.pkg).resolve()
    skill_src = PKG / "references/skills/daily-buddy"
    ach_src = PKG / "references/成就系统/scripts"
    if not skill_src.is_dir() or not ach_src.is_dir():
        print(f"❌ 夹具缺失：{skill_src} 或 {ach_src}")
        return 2

    TMP = Path(tempfile.mkdtemp(prefix="ach_chain_"))
    HOME = TMP / "home"
    MC = HOME / "[记忆共享中心]"
    skill = HOME / ".workbuddy/skills/daily-buddy"
    skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_src, skill)
    ach = MC / "成就系统/scripts"
    ach.mkdir(parents=True, exist_ok=True)
    for f in ach_src.glob("*.py"):
        shutil.copy2(f, ach / f.name)
    # 运行时数据（若包内带）——本用例只测守卫链，不覆盖"首次无 json 初始化"场景
    _json = ach_src / "achievement_data.json"
    if _json.exists():
        shutil.copy2(_json, ach / _json.name)

    upd = skill / "scripts/update_diary_achievement.py"
    # 不在此处打补丁：包内文件应已是发版态（补丁已合入）。
    # 「补丁前/后对照」的区分力证据见 REPORT.md，此处只测包内现状，零外部依赖。
    if a.no_patch:
        print("[提示] --no-patch 已废弃（补丁已合入包内），本次按包内现状测")

    repl = {"[记忆共享中心]": str(MC),
            "[日记仓库]": str(HOME / "[日记仓库]"),
            "[日记子目录]": "1-每日计划/01-日记"}
    for p in list(skill.rglob("*.py")) + list(ach.glob("*.py")):
        t = p.read_text(encoding="utf-8")
        t2 = t
        for k, v in repl.items():
            t2 = t2.replace(k, v)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")

    env = dict(os.environ, HOME=str(HOME), DB_HOME=str(HOME),
               PYTHONIOENCODING="utf-8")
    probe = subprocess.run(
        [sys.executable, "-c",
         f"import sys;sys.path.insert(0,{str(skill / 'scripts')!r});import dbenv;print(dbenv.DIARY_DIR)"],
        capture_output=True, text=True, env=env)
    diary_dir = Path(probe.stdout.strip())
    if str(TMP) not in str(diary_dir):
        print(f"❌ 日记目录逃出沙箱：{diary_dir}（stdout={probe.stdout!r} stderr={probe.stderr[:300]!r}）")
        return 2

    diary = diary_dir / a.date[:7] / f"{a.date}.md"
    diary.parent.mkdir(parents=True, exist_ok=True)
    diary.write_text(TPL.format(d=a.date), encoding="utf-8")

    target = skill / "scripts/achievement_tracker.py"
    real = ach / "achievement_tracker.py"
    real_bytes = real.read_bytes()

    def run(label, expect_block):
        r = subprocess.run([sys.executable, str(upd), "--date", a.date],
                           capture_output=True, text=True, env=env, cwd=str(skill))
        err = [l for l in (r.stderr or "").strip().splitlines() if l.strip()]
        out = (r.stdout or "").strip().splitlines()
        line = [l for l in diary.read_text(encoding="utf-8").splitlines() if "本日新增达成" in l]
        rewritten = bool(line) and "待定" not in line[0]
        tracker_ran = any("成就检测原始输出" in l or "newly_unlocked" in l for l in out)
        blocked = bool(err)
        good = (blocked == expect_block) and (rewritten != expect_block) and (tracker_ran != expect_block)
        print(f"  {'PASS' if good else 'FAIL'} | {label} | exit={r.returncode} 拦截={blocked} "
              f"tracker={tracker_ran} 改写={rewritten}")
        if not good:
            if err:
                print(f"       stderr: {err[0][:160]}")
            print(f"       stdout尾3行: {out[-3:] if out else '(空)'}")
        diary.write_text(TPL.format(d=a.date), encoding="utf-8")
        return good

    print(f"\n=== 成就链四态回归（{'补丁后' if not a.no_patch else '补丁前/现网'}）===")
    res = []
    res.append(run("A 实体副本(用户实际形态)", expect_block=a.no_patch))

    target.unlink()
    try:
        target.symlink_to(real)
        res.append(run("B 软链→真源", expect_block=False))
    except OSError as e:
        print(f"  SKIP | B 软链→真源 | 本环境不支持建链（{e.__class__.__name__}）")

    target.unlink()
    target.write_bytes(b"")
    res.append(run("C 0字节普通文件(Windows建链失败终态)", expect_block=a.no_patch))

    target.unlink()
    wrong = HOME / "wrong_tracker.py"
    wrong.write_bytes(real_bytes)
    try:
        target.symlink_to(wrong)
        res.append(run("D 负例·软链指错", expect_block=True))
    except OSError as e:
        print(f"  SKIP | D 负例·软链指错 | 本环境不支持建链（{e.__class__.__name__}）")

    total = len(res)
    ok = sum(res)
    print(f"\n结果: {ok}/{total} 符合预期 → {'全绿' if ok == total else '有失败'}")
    print(f"[沙箱] {TMP}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
