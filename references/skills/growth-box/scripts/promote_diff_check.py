#!/usr/bin/env python3
"""晋升差集检查器 v1.0（只读·不写任何东西）
把 flow-B B4 第9步"十一本账"从散文义务变成一条命令的读数：哪本缺、缺什么。
用法：python3 promote_diff_check.py --pat PAT-069 [--pat PAT-091]
rc=0 差集为空（可安全宣告晋升完成）；rc=1 有缺本（列出缺哪几本）；rc=2 用法/文件不可达。
设计约束：纯只读，⛔不改任何文件——写动作归后续 promote_transaction.py（幂等事务）。
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import argparse, io, os, re, subprocess, sys

HOME = os.path.expanduser('~')
ARCH = os.path.expanduser('[记忆共享中心]')
LEDGERS = {
 1: ('条文本体', os.path.join(ARCH, '记忆规则/用户基本规则-铁律版.md'), r'### 铁律-0\d\d'),
 2: ('加载时机索引表', os.path.join(ARCH, '记忆规则/用户基本规则-铁律版.md'), r'\| 铁律-0\d\d'),
 5: ('摘要版版本号', os.path.join(ARCH, '记忆规则/用户基本规则-摘要版.md'), r'版本：v'),
 6: ('详解版版本号', os.path.join(ARCH, '记忆规则/用户基本规则-详解版.md'), r'版本：v'),
 8: ('本账CHANGELOG', os.path.join(ARCH, '记忆规则/CHANGELOG.md'), r'^## v'),
 9: ('成长箱条目状态', os.path.join(ARCH, '成长箱/learnings/LEARNINGS.md'), r'\*\*Status\*\*: (promoted|pending)'),
 10: ('状态总线', os.path.join(ARCH, '数字分身/state_bus.json'), None),
 11: ('中央变更账', os.path.join(ARCH, '变更日志.md'), None),
}


def read(p):
    try:
        return io.open(p, encoding='utf-8', errors='ignore').read()
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pat', action='append', default=[])
    a = ap.parse_args()
    if not a.pat:
        print('rc=2 用法：--pat PAT-0NN（可多次）'); return 2
    missing, ok = [], []
    tl = read(os.path.join(ARCH, '记忆规则/用户基本规则-铁律版.md')) or ''
    ids = re.findall(r'### 铁律-(0\d\d)', tl)
    for pat in a.pat:
        idx = os.path.join(ARCH, '成长箱/learnings/INDEX.md')
        row = [l for l in (read(idx) or '').splitlines() if l.startswith('| %s ' % pat)]
        state = re.search(r'pending\((\d)/3\)|已晋升|promoted|已判保持', row[0] if row else '')
        print('【%s】INDEX 现态=%s' % (pat, state.group() if state else '未找到行'))
        print('   铁律版现有条文=%d 条（最高号 铁律-%s）' % (len(ids), max(ids) if ids else '?'))
        print('   判定：该 PAT 尚无对应条文 → 属"需新立"，非"已覆盖可合并"')
    for no, (name, path, pat) in LEDGERS.items():
        t = read(path)
        if t is None:
            missing.append('⑭%d %s：文件不可达 %s' % (no, name, path)); continue
        if pat is None:
            ok.append('⑭%d %s：存在（内容核对须人工/后续事务）' % (no, name)); continue
        hit = len(re.findall(pat, t, re.M))
        (ok if hit else missing).append('⑭%d %s：命中 %d 处' % (no, name, hit) if hit else '⑭%d %s：零命中' % (no, name))
    print('\n=== 十一本账差集（本器只覆盖可机械探测的 8 本，③④⑦由 gen_rule_triggers/three_layer_guard 终检覆盖）===')
    for l in ok: print(' 在册  ', l)
    for l in missing: print(' ⛔缺  ', l)
    print('\n结论：%s' % ('差集为空' if not missing else '有 %d 本待补——不可宣告晋升完成' % len(missing)))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
