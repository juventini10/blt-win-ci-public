#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_refs_integrity.py — 唤醒记忆系统引用完整性机检（v8.5.0 新增）

为什么存在：主体瘦身后所有细节都压在 references/，一旦锚点漂移或文件漏登记，
主体就把 AI 指到一个不存在的地方，且不报错（沉默断链）。本脚本把这条风险
从"靠人记得核对"降为"可跑可判红"。

检查四类（任一 FAIL → exit 1）：
  V1 文件可达：带目录前缀的 `xxx.md` 引用（references/、./、xxx/），目标必须存在；
              裸文件名（无目录前缀）可能是外部规范（如 Skill标准规范.md），跳过但**计数上屏**
              （v8.5.2：原实现把"找不到"与"外部引用"合并 continue，V1 从未真正判红）
  V2 节名可达：引用带 `§N` 时，目标文件须有同号标题（`## §N` / `### §N`）
  V3 索引齐：SKILL.md「全部顶层文件登记」段须覆盖 references/*.md 实存全集
  V4 依赖在盘：YAML dependencies 逐项校验（文件 exists / 目录 is_dir·v8.5.2 补目录型）

用法：python3 scripts/check_refs_integrity.py [--quiet]
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REF = BASE / "references"
SKILL = BASE / "SKILL.md"

REF_PAT = re.compile(r"([A-Za-z0-9_-]+\.md)(?:\s*§([0-9]+(?:\.[0-9]+)?))?")
HEAD_PAT = re.compile(r"^#{2,4}\s*§?\s*([0-9]+(?:\.[0-9]+)?)")


def md_files():
    return sorted(p for p in REF.glob("*.md"))


def headings(path: Path):
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEAD_PAT.match(line.strip())
        if m:
            out.add(m.group(1))
    return out


def _is_path_ref(text: str, start: int) -> bool:
    """该引用是否**声称自己在 references/ 下**（唯一判据：紧邻 token 恰为 references/）。

    v8.5.2 判据修正（第一版被自己的负例抓出）：原实现取前 16 字符窗口判 `endswith("/")`，
    会把「.../awaken-memory-system/SKILL.md」（绝对路径）与「pages/07-feedback-rules.md」
    （指向其他规范目录）一并误判成 references/ 下的引用 → 假红。
    真实语义只有一种：写作 `references/xxx.md` 才是本 Skill 的 references 引用；
    绝对路径与跨目录路径属外部引用，不归本脚本解析。
    """
    i = start
    while i > 0 and not text[i - 1].isspace():
        i -= 1
    token = text[i:start]
    # 判据=紧邻前缀以 references/ 结尾（覆盖 `references/x.md`、详见 references/x.md 两种写法）；
    # 绝对路径以 system/ 结尾、跨目录以 pages/ 结尾，均不命中 ⇒ 仍按外部引用跳过。
    return token.endswith("references/")


def main(argv=None):
    ap = argparse.ArgumentParser(description="唤醒记忆系统引用完整性机检")
    ap.add_argument("--quiet", action="store_true", help="只打印结论行")
    args = ap.parse_args(argv)

    fails = []
    scan = [SKILL] + md_files()
    head_cache = {}
    n_checked = 0
    n_bare_skipped = 0

    for path in scan:
        if path.name == "CHANGELOG.md" or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for m in REF_PAT.finditer(text):
            target, sec = m.group(1), m.group(2)
            tpath = REF / target
            is_path = _is_path_ref(text, m.start(1))
            if not tpath.is_file():
                n_checked += 1
                if is_path:
                    fails.append(f"V1 文件不可达: {path.name} → references/{target}（带路径前缀却不存在）")
                else:
                    n_bare_skipped += 1
                continue
            n_checked += 1
            if sec:
                if target not in head_cache:
                    head_cache[target] = headings(tpath)
                if sec not in head_cache[target]:
                    fails.append(f"V2 节名不可达: {path.name} → {target} §{sec}")
    if not args.quiet:
        print(f"V1 文件可达: 扫描 {len(scan)} 个 md / {n_checked} 条 .md 引用；"
              f"裸文件名跳过 {n_bare_skipped} 条（可能是外部规范）")

    # V3 索引齐
    skill_text = SKILL.read_text(encoding="utf-8")
    actual = {p.name for p in md_files()}
    missing = sorted(n for n in actual if f"`references/{n}`" not in skill_text)
    for n in missing:
        fails.append(f"V3 未登记顶层文件: references/{n}")

    # V4 依赖在盘（v8.5.2：按 YAML 列表逐项切分，目录型依赖同样校验）
    dep_line = next((l for l in skill_text.splitlines() if l.startswith("dependencies:")), "")
    raw = dep_line.split(":", 1)[1].strip()
    raw = raw.strip("[]")
    deps = [x.strip().strip("`").strip("'\"").strip() for x in raw.split(",")]
    deps = [d for d in deps if d]
    for d in deps:
        p = (BASE / d).resolve()
        ok = p.is_dir() if d.endswith("/") else p.exists()
        if not ok:
            kind = "目录" if d.endswith("/") else "文件"
            fails.append(f"V4 依赖缺失({kind}): {d}")

    if fails:
        print(f"❌ FAIL {len(fails)} 项")
        for f in fails:
            print("  -", f)
        return 1
    print(f"✅ PASS 引用完整性全绿（references {len(actual)} 个文件 / 依赖 {len(deps)} 项）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
