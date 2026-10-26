#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""minimaxcode_skill_link_reconciler.py — 端上 Skill 软链对账器（MiniMax Code 端专属）

为什么存在（2026-10-25 端形态归一·愿景裁决）：
  旧形态：``~/.minimax/skills`` 是**整目录软链** → ``<MC>/技能配置``（唯一真源）
    ⇒ 端专属 Skill 无处可落（往里写＝写进唯一真源 ⇒ 跨端可见 ⇒ 违反「端专属不进共享技能配置」）
    ⇒ 且端专属两件（童灵守护 / 童灵切片导航）＝本端童灵显式调用入口·traecn 端已装·本端缺
      ⇒ 端间能力不对等
  归一后（由 ``adapters/minimaxcode/setup.sh`` 的形态归一腿完成）：端上 skills = 普通目录；
  通用 Skill 逐件软链 → 真源；端专属 Skill 实体落端内。
    ⇒ 代价：真源新增 Skill 不再「自动可见」（整目录软链时代的红利没了）
    ⇒ **本件补这个缺口：会话启动时对账补链**（缺链则建 · 悬空链则清）

职责边界（⛔严守·不越权）：
  · 只管**通用件**（真源 ``技能配置/<name>``）：补缺软链 + 换错指 + 清悬空软链
  · ⛔ 不碰端专属实体目录（端专属是实体目录·不软链·不删）
  · ⛔ 不删真源任何内容（真源**只读**）
  · ⛔ 不动宿主其他配置（只动 ``<CFG>/skills/`` 这一层）

用法：
  ``minimaxcode_skill_link_reconciler.py``             # 对账 + 补链（默认·幂等）
  ``minimaxcode_skill_link_reconciler.py --report``     # 只读报告（不改任何东西）
  ``minimaxcode_skill_link_reconciler.py --self-test``  # 对偶夹具
"""
import argparse
import json
import os
import sys
import time

try:
    import sys as _s
    _s.stdout.reconfigure(encoding="utf-8")
    _s.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _resolve_mc():
    """记忆中心根（自推导·⛔不硬编码作者路径）"""
    env = os.environ.get("BULUOTUO_MC") or os.environ.get("BULUOTUO_MEMORY_CENTER")
    if env and os.path.isdir(env):
        return env
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        if os.path.basename(d) == "脚本中心":
            return os.path.dirname(d)
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return os.path.expanduser("~")


def _skills_src(mc):
    env = os.environ.get("BULUOTUO_SKILLS_DIR")
    if env and os.path.isdir(env):
        return env
    return os.path.join(mc, "技能配置")


def _skills_dst():
    cfg = os.environ.get("MINIMAX_CONFIG_DIR") or os.environ.get("MINIMAX_DATA_DIR")
    if not cfg:
        cfg = os.path.expanduser("~/.minimax")
    return os.path.join(cfg, "skills")


def _common_skills(src):
    """真源里的通用件集合 = 真源**所有可解析项**（⛔不按「是不是 skill」筛）。

    ⚠️ 2026-10-25 治尺（口径不一致＝尺的盲区）：
       原判据＝「目录且根级有 SKILL.md」⇒ 把
       ①技能包（SKILL.md 在**子目录**：andrej-karpathy-skills / taste-skill）
       ②工程目录（ai-website-cloner-template / mcp-server / ow-bridge）
       ③非目录运维件（.sh / .txt）
       全判成「真源没有 ⇒ 悬空 ⇒ 该清」⇒ 会**误清 13 条合法链**。
       而 setup.sh 的建链口径是「真源全量项」⇒ 两件口径打架（一个建一个清）。
       ⇒ 统一为**存在性口径**：真源里有这个项 ⇒ 就是该有的链；真源里彻底没有 ⇒ 才是悬空。
       ⛔ 断链项（-e 为假）不纳入（端上链过去也是断链）。
    """
    out = {}
    if not os.path.isdir(src):
        return out
    for name in sorted(os.listdir(src)):
        # ⛔ 排除隐藏项（.DS_Store / .git 等·系统与编辑器垃圾）⇒ 不进件集（否则端上多一垃圾链）
        if name.startswith("."):
            continue
        p = os.path.join(src, name)
        if os.path.exists(p):
            out[name] = p
    return out


def _plan(src, dst):
    """返回 (缺失待建, 指向错待换, 悬空待清, 端专属实体跳过数)"""
    want = _common_skills(src)
    missing, wrong, dangling, keep = [], [], [], 0
    if not os.path.isdir(dst):
        return list(want.keys()), [], [], keep
    for name in os.listdir(dst):
        p = os.path.join(dst, name)
        if not os.path.islink(p):
            keep += 1            # 端专属实体目录 / 用户私件 ⇒ ⛔不动
            continue
        tgt = os.path.realpath(p)
        if name in want:
            if tgt != os.path.realpath(want[name]):
                wrong.append(name)
        else:
            dangling.append(name)  # 真源已无此件 ⇒ 悬空链
    for name in want:
        if not os.path.islink(os.path.join(dst, name)) and not os.path.isdir(os.path.join(dst, name)):
            missing.append(name)
    return missing, wrong, dangling, keep


def apply_reconcile(src, dst, dry=False):
    if os.path.islink(dst):
        # 整目录软链形态 ⇒ 本件不适用（建链会落进真源）⇒ ⛔直接不动作
        return {"missing": [], "wrong": [], "dangling": [], "kept": 0,
                "made": [], "fixed": [], "removed": [], "applied": False,
                "skipped": "端上 skills 是整目录软链·形态归一未完成"}
    missing, wrong, dangling, keep = _plan(src, dst)
    if dry:
        return {"missing": missing, "wrong": wrong, "dangling": dangling,
                "kept": keep, "applied": False}
    made, fixed, removed = [], [], []
    for name in missing:
        try:
            os.symlink(os.path.join(src, name), os.path.join(dst, name))
            made.append(name)
        except OSError:
            pass
    for name in wrong:
        p = os.path.join(dst, name)
        try:
            os.unlink(p)
            os.symlink(os.path.join(src, name), p)
            fixed.append(name)
        except OSError:
            pass
    for name in dangling:
        p = os.path.join(dst, name)
        try:
            if os.path.islink(p) and not os.path.exists(p):
                os.unlink(p)
                removed.append(name)
        except OSError:
            pass
    return {"missing": missing, "wrong": wrong, "dangling": dangling,
            "kept": keep, "made": made, "fixed": fixed, "removed": removed,
            "applied": True}


def _selftest():
    """对偶夹具：5 例（缺链建·指向错换·悬空清·端专属实体不动·整目录软链形态跳过）"""
    import shutil
    import tempfile
    ok = True

    def case(name, fn):
        nonlocal ok
        try:
            r = fn()
        except Exception as e:  # noqa
            r = False
            print("  ❌ %s 异常: %s" % (name, e))
        if r:
            print("  ✅ %s" % name)
        else:
            ok = False
            print("  ❌ %s" % name)

    def mk():
        base = tempfile.mkdtemp(prefix="mcslr_")
        src = os.path.join(base, "src")
        dst = os.path.join(base, "dst")
        os.makedirs(src)
        os.makedirs(dst)
        for n in ("alpha", "beta"):
            d = os.path.join(src, n)
            os.makedirs(d)
            open(os.path.join(d, "SKILL.md"), "w").write("---\nname: %s\n---\n" % n)
        return base, src, dst

    def c1():
        base, src, dst = mk()
        try:
            res = apply_reconcile(src, dst)
            return res["made"] == ["alpha", "beta"] and os.path.islink(os.path.join(dst, "alpha"))
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def c2():
        base, src, dst = mk()
        try:
            os.makedirs(os.path.join(src, "gamma"))
            open(os.path.join(src, "gamma", "SKILL.md"), "w").write("x")
            os.symlink(os.path.join(src, "beta"), os.path.join(dst, "alpha"))
            res = apply_reconcile(src, dst)
            return res["fixed"] == ["alpha"] and os.path.realpath(os.path.join(dst, "alpha")).endswith("alpha")
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def c3():
        base, src, dst = mk()
        try:
            os.symlink(os.path.join(src, "ghost"), os.path.join(dst, "ghost"))
            res = apply_reconcile(src, dst)
            return res["removed"] == ["ghost"] and not os.path.lexists(os.path.join(dst, "ghost"))
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def c4():
        base, src, dst = mk()
        try:
            os.makedirs(os.path.join(dst, "端专属件"))
            open(os.path.join(dst, "端专属件", "SKILL.md"), "w").write("x")
            apply_reconcile(src, dst)
            return os.path.isdir(os.path.join(dst, "端专属件")) and not os.path.islink(os.path.join(dst, "端专属件"))
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def c5():
        base, src, dst = mk()
        try:
            shutil.rmtree(dst, ignore_errors=True)
            os.symlink(src, dst)
            res = apply_reconcile(src, dst)
            # 整目录软链形态 ⇒ 本件不适用 ⇒ 不建链（由 setup.sh 形态归一腿负责）
            return res["made"] == []
        finally:
            shutil.rmtree(base, ignore_errors=True)

    print("🧪 minimaxcode_skill_link_reconciler 自测")
    case("缺链→建链", c1)
    case("指向错→换指", c2)
    case("悬空链→清理", c3)
    case("端专属实体目录→不动", c4)
    case("整目录软链形态→不建链", c5)
    print("🟢 自测全绿" if ok else "🔴 自测有失败")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="只读报告·不改任何东西")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _selftest()
    mc = _resolve_mc()
    src = _skills_src(mc)
    dst = _skills_dst()
    if os.path.islink(dst):
        res = {"skipped": "端上 skills 是整目录软链·形态归一未完成（请跑 adapters/minimaxcode/setup.sh）"}
        if a.json:
            print(json.dumps(res, ensure_ascii=False))
        else:
            print("⏭️ 端上 skills 是整目录软链·形态归一未完成·本件不适用")
        return 0
    res = apply_reconcile(src, dst, dry=a.report)
    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    elif res.get("applied"):
        n = len(res.get("made", [])) + len(res.get("fixed", [])) + len(res.get("removed", []))
        if n:
            print("🔗 Skill 链接对账：补链 %d · 换指 %d · 清悬空 %d（端专属实体 %d 件未动）"
                  % (len(res.get("made", [])), len(res.get("fixed", [])),
                     len(res.get("removed", [])), res.get("kept", 0)))
        # 无变化 ⇒ 静默（⛔不产噪音：SessionStart 钩子每会话都跑）
    else:
        print("🔗 Skill 链接对账（只读）：缺链 %d · 指向错 %d · 悬空 %d · 端专属实体 %d"
              % (len(res["missing"]), len(res["wrong"]), len(res["dangling"]), res["kept"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
