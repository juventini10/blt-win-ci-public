#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""path_integrity_check.py — 装机产物路径完整性检查器 v2（2026-10-10 十一轮·双拼病门禁）

用法：
    python3 path_integrity_check.py --root <记忆共享中心或包根> [--pkg-template] [--quiet]

检查项（命中任一 = exit 1）：
  1) 双拼形态（运行时调用形）：expanduser( 或引号内紧跟的 波浪号+双斜杠绝对路径
     / 波浪号+盘符冒号 形态——病形本体（expanduser 静默失效·Fail-Silent）。
     prose 注释/文档描述病形不算（行级判据 + 显式豁免标记，防自伤假阳性）。
  2) 占位符残留：装机面仍含未替换的占位符 token（安装器漏替换）
  3) 畸形前缀：波浪号斜杠紧贴占位符（包模板层病灶·--pkg-template 主判此项）
  4) 段重复畸形：路径/常量段异常重复（REPEAT_SEG 行级·2026-10-10 十一轮补类）

⛔ 判据构造纪律（本文件源码会被安装器 _fill / mirror relocate/deident 改写）：
  - 占位符 token 用 chr() 动态构造 ⇒ _fill 替换不到本判据（防"检查器自己被治成假绿"）
  - 先例同构：pkg_cleanliness_check.py TILDE_PAT
"""
import argparse
import os
import re
import sys

PLACEHOLDER = chr(0x5B) + "记忆共享中心" + chr(0x5D)      # 左方括号 + 词 + 右方括号
TILDE_PREFIXED = chr(0x7E) + chr(0x2F) + PLACEHOLDER      # 波浪号斜杠 + 占位符
Q = "[" + chr(39) + chr(34) + "]+"               # 单双引号字符类（chr 构造避转义）
BAD_CALL = re.compile(
    "expanduser\\(" + Q + "\\s*" + chr(0x7E) + "(/[A-Za-z]:[/\\\\]|//)"
    "|" + Q + chr(0x7E) + "[A-Za-z]:[/\\\\]"
)
# 2026-10-21 反哺(上游反馈Bug1·李生Win)：{{X_ROOT}} 填充值已含模板后缀→装机产物 "A/B/A/B" 段重复双拼。   # PATH-INTEGRITY-EXEMPT 判据自形/病形引用行，非装机产物
#   区别于运行时双拼(BAD_CALL·expanduser/波浪号形)。限产物面判，--pkg-template 跳过(模板层无重复+prose病形示例不误报)。
# 2026-10-25 根治（Trae CN 入包轮·「段重复」类假红 42 件实证）：原式只要求"任一含斜杠的两段串重复"，
#   实测把 HTML 标记（`div></div>`×N、`{{VAL}}</td><td>{{VAL}}`）与相对路径 `../../..` 一并判成
#   "路径段重复" ⇒ 判据名（路径段）与实测量域（任意文本）不相交（假红逼人改文案＝比漏报更坏）。
#   收紧为「路径段字符集」：段内 ⛔ 空白/尖括号/花括号/圆括号/方括号/引号/反引号/斜杠/等号/反斜杠；
#   `..`/`.` 纯点段（合法相对路径）不计病形。⛔ 未动 CHANGELOG 例外、未动扫描域、未动 EXEMPT 机制。
_SEGCH = r"[^\s<>{}()\[\]\"'`/=\\]"   # 路径段字符集（单一处定义）
REPEAT_SEG = re.compile(r"(" + _SEGCH + r"+/" + _SEGCH + r"+)/\1")   # PATH-INTEGRITY-EXEMPT 判据自形/病形引用行，非装机产物
# 2026-10-25 域修正（承 2026-10-12 `double` 类「⛔不判 .md/.json prose」先例·条文19 声明式域）：
#   段重复病形的实物侧＝**值/调用形**（py/sh/ps1/json/yaml/html）；`.md` 里写 `A/B/A/B` 是   # PATH-INTEGRITY-EXEMPT 病形引用行
#   叙述/示例（系统日志、任务卡、设计规范 13 件实测），属记录面而非装机产物 ⇒ 移出判据域。
#   ⛔ 不是"正则改窄凑绿"：判据式未动，只声明它管哪类文件（与 CHANGELOG 例外同一理由的推广）。
REPEAT_EXT = {".py", ".sh", ".ps1", ".json", ".yaml", ".yml", ".html"}
EXEMPT = "PATH-INTEGRITY-EXEMPT"                          # 行级显式豁免标记
TEXT_EXT = {".md", ".py", ".sh", ".ps1", ".yaml", ".yml", ".json", ".txt", ".html"}
# .venv/venv/node_modules=第三方依赖（site-packages 自带病形引用·非装机产物）；
# .venv-st=知识联邦引擎自带 site-packages（2026-10-25 Trae CN 入包轮：fill_syntax_scan 早已豁免它，
#   本器漏列＝同族不一致 ⇒ 42 件里有 4 件来自第三方依赖源码·非装机产物）
# _wip=端用户暂存区（2026-10-23 V2.2.9 Win 反馈 P2-5：实测 _wip 单项 844 件噪声掩盖真命中）
SKIP_DIRS = {".git", "__pycache__", ".package-lock", "记忆琥珀", "logs", "_archive",
             ".snapshots", ".guard", ".patrol",
             ".venv", ".venv-st", "venv", "_wip", "node_modules"}


def _is_disease_repeat(line):
    """段重复病形判定：命中且重复段非纯点段 ⇒ 病形（`../../..` 是合法相对路径，不是双拼）。"""
    m = REPEAT_SEG.search(line)
    if not m:
        return False
    a, b = m.group(1).split("/")
    return a.strip(".") != "" and b.strip(".") != ""


def _is_skipped_dir(name):
    """目录豁免判定：常量表命中，或 `.venv` 族（.venv/.venv-st/.venv-semantic…＝第三方依赖）。

    2026-10-25 Trae CN 入包轮：原实现只列 `.venv`/`.venv-st` 两个**具体名**，实测 MC 里还有
    `.venv-semantic` ⇒ 按名穷举必漏（同族第 N 次）⇒ 改按**族前缀**判，一次断根。
    """
    return name in SKIP_DIRS or name.startswith(".venv")


def scan(root, only_dirs=None, ph_files=None):
    hits = {"double": [], "placeholder": [], "tilde_prefixed": [], "repeat": []}
    for dp, dn, fn in os.walk(root):
        _rel = os.path.relpath(dp, root)
        parts = set(dp.replace("\\", "/").split("/"))
        if parts & SKIP_DIRS or any(_is_skipped_dir(x) for x in parts):
            dn[:] = [d for d in dn if d not in SKIP_DIRS and not _is_skipped_dir(d)]
            continue
        if only_dirs and not any(_rel == d or _rel.startswith(d + os.sep) for d in only_dirs):
            # 声明域=「只扫这些 root 子目录」（2026-10-12 域修正·条文19 实现=声明）：
            # root 直挂文件=白名单外跳过 fn，但 ⛔不可剪 dn（首版把 root 剪死=维护假绿，负例T17当场抓获）
            if _rel == ".":
                fn[:] = []
            else:
                dn[:] = []
                continue
        for f in fn:
            if os.path.splitext(f)[1].lower() not in TEXT_EXT:
                continue
            p = os.path.join(dp, f)
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            rel = os.path.relpath(p, root)
            _exe = os.path.splitext(f)[1].lower() in {".py", ".sh", ".ps1"}
            for ln in t.splitlines():
                if EXEMPT in ln:
                    continue
                if BAD_CALL.search(ln) and _exe:  # double=运行时调用形⇒⛔不判 .md/.json 等 prose（2026-10-12 域修正·历史台账引用不可改亦不该判）
                    hits["double"].append(rel)
                    break
            if (ph_files is None or rel in ph_files) and PLACEHOLDER in t:
                hits["placeholder"].append(rel)
            if TILDE_PREFIXED in t and (ph_files is None or rel in ph_files):
                # 2026-10-12 域修正·条文19 实现=声明：tilde 类与占位符类同受 --placeholder-files
                # 管辖（R4 扫描域收窄声明=双参数成对；原实现漏这一腿⇒作者机 MC 病案登记 prose 全爆红，
                # 装机态白名单件照判不损失）；行级 PATH-INTEGRITY-EXEMPT 同步生效
                for _ln in t.splitlines():
                    if TILDE_PREFIXED in _ln and EXEMPT not in _ln:
                        hits["tilde_prefixed"].append(rel)
                        break
            # CHANGELOG 是历史文本：引用历史病形（如「曾渲染出 A/B/A/B 双段」）是记录本身，   # PATH-INTEGRITY-EXEMPT 病形引用行
            # 不是当前产物里的路径重复（2026-10-23 V2.2.10 Win 真机 T15/T16 误报实证：
            # daily-buddy CHANGELOG L61 描述 $DIARY 双段渲染被 REPEAT_SEG 误判）。
            if os.path.splitext(f)[1].lower() in REPEAT_EXT and f.lower() != "changelog.md":
                for _ln in t.splitlines():
                    if EXEMPT in _ln:
                        continue
                    if _is_disease_repeat(_ln):
                        hits["repeat"].append(rel)
                        break
    return hits


def main():
    ap = argparse.ArgumentParser(description="装机产物路径完整性（双拼病门禁·只读）")
    ap.add_argument("--root", required=True, help="记忆共享中心或包根")
    ap.add_argument("--quiet", action="store_true", help="只输出总判定")
    ap.add_argument("--pkg-template", action="store_true",
                    help="包模板层模式：只判畸形前缀（占位符未替换=出厂原态、prose 病形示例不算）")
    ap.add_argument("--only-dirs", default=None,
                    help="只扫这些 root 子目录（逗号分隔·空=全树）——装机产物面白名单")
    ap.add_argument("--placeholder-files", default=None,
                    help="占位符残留只查这些文件（相对 root 或绝对路径·逗号分隔；空=全树）——直拷类设计含占位符不误报")
    args = ap.parse_args()
    root = os.path.expanduser(args.root)
    if not os.path.isdir(root):
        print("[FAIL] 根目录不存在: %s" % root, file=sys.stderr)
        return 2
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    hits = scan(root,
                only_dirs=[d for d in args.only_dirs.split(",") if d] if args.only_dirs else None,
                ph_files=set(args.placeholder_files.split(",")) if args.placeholder_files else None)
    if args.pkg_template:
        hits["placeholder"] = []
        hits["double"] = []
        hits["repeat"] = []
    total = sum(len(v) for v in hits.values())
    if total and not args.quiet:
        for k, label in (("double", "双拼形态产物(运行时调用形)"),
                         ("placeholder", "占位符残留(未替换)"),
                         ("tilde_prefixed", "畸形前缀(波浪号紧贴占位符)"),
                         ("repeat", "段重复畸形(路径段异常重复)")):
            if hits[k]:
                print("  [FAIL] %s: %d 件" % (label, len(hits[k])))
                for r in hits[k][:8]:
                    print("         - %s" % r)
                if len(hits[k]) > 8:
                    print("         ... 另有 %d 件" % (len(hits[k]) - 8))
    if total == 0:
        print("  [PASS] 路径完整性: 无双拼/无占位符残留/无畸形前缀/无段重复")
        return 0
    print("  [FAIL] 路径完整性: 共 %d 件命中" % total)
    return 1


if __name__ == "__main__":
    sys.exit(main())
