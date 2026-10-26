#!/usr/bin/env python3
# version: v1.0
r"""minimaxcode_title_namer.py — MiniMax Code 端适配器：UserPromptSubmit 自动命名对话标题。

规则（你立 2026-09-09，SSOT=~/.workbuddy/MEMORY.md「对话标题命名规则」）:
    标题格式 = YYMMDD | 类型 | 主题
    日期 = 北京时区实际创建日期（取会话 created_at_ms·⛔不用当前时间冒充）
    类型 ∈ {功能,设计,修复,优化,发布,探索,文档,研究,日记,周报,月报}
    主题 = 首条 prompt 简洁概括（≤20 字·断点回退）

## 定位（端适配器·第 21 端·MiniMax Code）

⛔ 本文件**只做两件事**：定位会话 + 落库。
⛔ 公共原语（classify / extract_theme / make_title / bj_date_from_ms）**只 import 不复制**
   —— 复制 = 端内副本不随原语升级 = 同一规则两个版本 = 双本账漂移。
   真源 = [记忆共享中心]/脚本中心/session_title_utils.py（与 技能配置/session-title-namer/scripts/
   同内容·sha256 一致·对外发布走后者）。

## 本端机制事实（2026-10-23·运行时源码级实测·非印象）

| # | 事实 | 证据锚 |
|:--|:--|:--|
| M1 | 标题落库面 = `local_runtime_sessions.title`（列）+ `extra_data_json.titleSource` | sqlite `.schema` + 实测行 |
| M2 | 宿主自动起名 = `mutateSession(sid,{title,titleSource:'auto'},undefined,{title:expectedTitle,source:'default'})` | app.asar `createTitleCommitter` |
| M3 | 宿主起名带 **CAS 守卫**：`current.title≠expectedTitle.title` **或** `current.titleSource≠'default'` → 抛 `SessionTitleConflictError` | app.asar `DrizzleSessionRepository.update` |
| M4 | 用户手动命名 ⇔ `titleSource='manual'`（`normalizeSessionMutation` 对任何 title 变更默认置 manual） | app.asar + 实测行（`mavis session update` 写出的行 = manual） |
| M5 | 检索面 = FTS `title_terms`（`c`+codepoint hex·NFKC+trim+lower·空格分隔） | app.asar `toSessionSearchTerms` + 实测 FTS 行 |
| M6 | 无外部 HTTP/CLI 写入口（41980=本地 LLM 代理·17788 无路由） | curl 实测 |
| M7 | hook 载荷 = stdin JSON，含 `session_id` / `prompt` / `transcript_path` / `cwd` | 官方 `references/local-plugin-hooks.md` |

### ⇒ 关键结论：**不需要母本那种「后台夺回守卫」**

母本 WB 的宿主 AI 起名发生在钩子写入之后几秒 → WB 必须 spawn 后台进程轮询夺回（v0.6）。
本端宿主起名是 **CAS 条件更新**：本件把 `title` 与 `titleSource='manual'` 一起写入后——
  · 宿主若在写入前读=title_null → CAS 的 title 比对失配 → 抛冲突 → 宿主起名被拒；
  · 宿主若在写入后读=title_ ours → CAS 的 source 比对（'manual'≠'default'）失配 → 抛冲突 → 被拒。
⇒ 两种时序宿主都拿不到写权，**一次写入即终局**，无后台进程、无轮询、无抢写窗口。

### ⇒ 「不覆盖用户手动命名」用运行时自己的字段判，不靠时间窗猜

判据 = `titleSource='manual'`（M4）。该值同时覆盖两种情形：
  · 用户手动命名 → 跳过（⛔不覆盖用户显式意志）
  · 本件上一轮已命名 → 跳过（幂等，不重复改写）
另加一道格式签名兜底：标题已符合 `^\d{6} \| ` → 跳过（即便 titleSource 被改回 auto 也不重写主题）。

## 守卫清单（每条配两向探针·自测逐条验证"只有它能拦"）

| 守卫 | 拦什么 | 判据来源 |
|:--|:--|:--|
| G1 archived | 已归档会话不写 | 运行时 `archived` 列 |
| G2 kind | 非 conversation（task/cron/peek/channel）不写 | 运行时 `session_kind` 列 |
| G3 child | 有 parent 的子会话不写（本端子会话标题由任务描述生成） | 运行时 `parent_session_id` 列 |
| G4 manual | titleSource='manual' 不写（用户手动命名 / 本件已命名） | 运行时 `titleSource` 字段 |
| G5 signature | 标题已是 `YYMMDD \| ` 格式不写 | 本件格式签名 |

## 两问记录（§二·十八）

**第一问·禁设核对**：已读 §二·七「退役/永久关闭行」+ §3.4·扩（呈现格式禁拦律等否决族）——
本件**不撞任何否决族**：它不是呈现面拦截器（不拦用户输入·不改 prompt·不判内容合规），
不是已退役件复活（`reply_format_guard` 同族未触碰），⛔ 不新建「判据族守卫」，
只做**元数据写入**（会话标题），与母本 `session_title_namer` 族同质同位。

**第二问·量三数**：
  · **N1 = 1**（本端标题至今为宿主 LLM 摘要·无统一格式·与皮叔 2026-09-09 立的命名规则脱节）> 0 → 允许立项。
  · **N2 = 0**（无形态错位：本件只读会话元数据·不判定正文语义·标题文本由公共原语出）。
  · **N3 = 0**（无仪器假阳性：本件不产出红/黄判定·只写元数据·自测为两向探针）。

## 安全设计

  · **退出码语义**：hook 形态 **rc 恒 0**（装饰性功能绝不断对话·⛔任何异常都静默降级·失败留痕日志）；
    `--self-test` 形态 rc 0/1（自测是独立面·不是 hook 面）。
  · **stdout 恒空**：hook 只做副作用·不输出结构化响应（官方契约：side-effect hook 应无 stdout）。
  · **不硬编码数据根**：⛔禁写死 `~/.minimax`（换 profile 即失效）——按
    `transcript_path` → 环境变量 → 候选目录 逐个 **exists + 会话行存在** 双校验定位 DB。
  · **只写两列**：title + extra_data_json.$.titleSource（其余 extra_data_json 原样保留）。
  · **⛔不碰 updated_at_ms**：改它会把会话顶到侧栏最前＝打乱你的会话顺序。

## 用法

    # 钩子形态（由 Plugin hooks.json 调用·绝对路径引用本件）
    echo '{"session_id":"mvs_xxx","prompt":"修复搜索超时"}' | python3 minimaxcode_title_namer.py

    # 只看生成结果不写库
    python3 minimaxcode_title_namer.py --dry-run --prompt "修复搜索超时问题"

    # 自测（两向探针·每条守卫验证"只有它能拦"）
    python3 minimaxcode_title_namer.py --self-test
"""

from __future__ import annotations
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass

import importlib.util
import json
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

SCRIPT_VERSION = "1.0"
HOOK_TITLE_RE = re.compile(r"^\d{6} \| ")

# ── 公共原语加载（⛔ 只 import 不复制） ──────────────────────────────────────
def _load_primitive():
    """定位并加载公共原语。返回 (module, path_str)。找不到抛异常（上层 rc 恒 0 静默）。"""
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "开发工具" / "session_title_utils.py",   # 04-跨端接入指南 §92 指定的真源
        here.parent / "session_title_utils.py",                     # 同目录副本（sha 一致·兜底）
    ]
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("session_title_utils", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, str(path)
    raise RuntimeError("public primitive session_title_utils.py not found")


# ── 数据根定位（⛔ 不硬编码） ───────────────────────────────────────────────
def _candidate_data_dirs(payload: dict) -> list[Path]:
    out: list[Path] = []

    def add(path) -> None:
        if path is None:
            return
        p = Path(path)
        if p not in out:
            out.append(p)

    # ① transcript_path 形如 <dataDir>/v2/sessions/YYYY/MM/DD/<sid>/messages.jsonl
    tp = payload.get("transcript_path")
    if isinstance(tp, str) and tp:
        parts = Path(tp).parts
        for i, seg in enumerate(parts):
            if seg == "v2" and i + 1 < len(parts) and parts[i + 1] == "sessions":
                add(Path(*parts[:i]))
                break

    # ② 运行时环境变量
    for env in ("MINIMAX_DATA_DIR", "MINIMAX_HOME", "MINIMAX_AGENT_DATA_DIR"):
        value = os.environ.get(env)
        if value:
            add(Path(value).expanduser())

    # ③ 候选目录（逐个 exists + 行存在双校验·⛔不盲信第一个）
    home = Path.home()
    add(home / ".minimax")
    add(home / ".minimax-agent-cn")
    return out


def _find_db(payload: dict, session_id: str):
    """返回可写 DB 路径。判据 = 文件存在 **且** 该 session 行在该库里（防跨 profile 误写）。"""
    for data_dir in _candidate_data_dirs(payload):
        db = data_dir / "v2" / "sqlite" / "runtime-state.sqlite"
        if not db.is_file():
            continue
        try:
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
            try:
                row = con.execute(
                    "SELECT 1 FROM local_runtime_sessions WHERE session_id=?", (session_id,)
                ).fetchone()
            finally:
                con.close()
        except Exception:
            continue
        if row:
            return db
    return None


# ── 会话读取 ────────────────────────────────────────────────────────────────
_COLUMNS = (
    "title, extra_data_json, session_kind, parent_session_id, archived, "
    "created_at_ms, agent_name, workspace_dir, purpose, status, session_type"
)


def _read_session(con, session_id: str):
    row = con.execute(
        f"SELECT {_COLUMNS} FROM local_runtime_sessions "
        "WHERE session_id=? AND columnar_version=3",
        (session_id,),
    ).fetchone()
    if row is None:
        return None
    keys = ("title", "extra_data_json", "session_kind", "parent_session_id", "archived",
            "created_at_ms", "agent_name", "workspace_dir", "purpose", "status", "session_type")
    return dict(zip(keys, row))


def _title_source(row: dict) -> str:
    try:
        extra = json.loads(row.get("extra_data_json") or "{}")
    except Exception:
        return ""
    value = extra.get("titleSource")
    return value if isinstance(value, str) else ""


# ── 守卫（每条独立可关·供两向探针验证） ─────────────────────────────────────
def _g_archived(row) -> bool:
    return int(row.get("archived") or 0) == 1


def _g_kind(row) -> bool:
    return (row.get("session_kind") or "") != "conversation"


def _g_child(row) -> bool:
    return bool(row.get("parent_session_id"))


def _g_manual(row) -> bool:
    return _title_source(row) == "manual"


def _g_signature(row) -> bool:
    title = row.get("title") or ""
    return bool(HOOK_TITLE_RE.match(title))


GUARDS = {
    "archived": _g_archived,
    "kind": _g_kind,
    "child": _g_child,
    "manual": _g_manual,
    "signature": _g_signature,
}


# ── FTS 同步（复刻运行时 writeSessionSearchDocument·app.asar） ───────────────
def _terms(value) -> str:
    """运行时 toSessionSearchTerms 的等价实现：NFKC → trim → lower → 每码点 'c'+hex。"""
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip().lower()
    return " ".join("c%x" % ord(ch) for ch in text)


def _sync_fts(con, row: dict, session_id: str, new_title: str) -> bool:
    try:
        con.execute(
            "INSERT INTO local_runtime_session_fts_keys(session_id) VALUES(?) "
            "ON CONFLICT DO NOTHING",
            (session_id,),
        )
        key = con.execute(
            "SELECT fts_rowid FROM local_runtime_session_fts_keys WHERE session_id=?",
            (session_id,),
        ).fetchone()
        if not key:
            return False
        rowid = key[0]
        con.execute("DELETE FROM local_runtime_sessions_fts WHERE rowid=?", (rowid,))
        con.execute(
            "INSERT INTO local_runtime_sessions_fts("
            "rowid, session_id, session_id_terms, agent_name_terms, title_terms, "
            "workspace_dir_terms, purpose_terms, status_terms, session_type_terms"
            ") VALUES (?,?,?,?,?,?,?,?,?)",
            (rowid, session_id, _terms(session_id), _terms(row.get("agent_name")),
             _terms(new_title), _terms(row.get("workspace_dir")), _terms(row.get("purpose")),
             _terms(row.get("status")), _terms(row.get("session_type"))),
        )
        return True
    except Exception:
        return False


# ── 核心：落库 ──────────────────────────────────────────────────────────────
def apply_title(con, session_id: str, prompt: str, disable=()) -> tuple[str, str | None]:
    """返回 (结果码, 标题或 None)。结果码 = named / skip:<守卫名> / skip:not_found …"""
    row = _read_session(con, session_id)
    if row is None:
        return "skip:not_found", None

    for name, guard in GUARDS.items():
        if name in disable:
            continue
        if guard(row):
            return f"skip:{name}", None

    primitive, _ = _load_primitive()
    created = row.get("created_at_ms")
    if not isinstance(created, int) or created <= 0:
        created = int(datetime.now().timestamp() * 1000)
    title = primitive.make_title(prompt, created)

    cur = con.execute(
        "UPDATE local_runtime_sessions "
        "SET title=?, extra_data_json=json_set(COALESCE(extra_data_json,'{}'),'$.titleSource','manual') "
        "WHERE session_id=? AND columnar_version=3",
        (title, session_id),
    )
    if cur.rowcount != 1:
        con.rollback()
        return "skip:no_update", None

    fts_ok = _sync_fts(con, row, session_id, title)
    con.commit()
    return ("named" if fts_ok else "named_no_fts"), title


# ── 日志 ────────────────────────────────────────────────────────────────────
def _log(message: str) -> None:
    data_dir = os.environ.get("PLUGIN_DATA")
    if not data_dir:
        return
    try:
        path = Path(data_dir) / "minimaxcode_title_namer.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
    except Exception:
        pass


# ── hook 形态 ───────────────────────────────────────────────────────────────
def hook_mode() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except Exception:
        return 0
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        _log("skip: bad_json")
        return 0
    if not isinstance(payload, dict):
        return 0

    session_id = str(payload.get("session_id") or "").strip()
    prompt = str(payload.get("prompt") or "").strip()
    if not session_id or not prompt:
        _log(f"skip: no_session_id_or_prompt sid={session_id!r}")
        return 0

    try:
        db = _find_db(payload, session_id)
        if db is None:
            _log(f"skip: db_not_found sid={session_id}")
            return 0
        con = sqlite3.connect(str(db), timeout=5)
        try:
            con.execute("PRAGMA busy_timeout=5000")
            result, title = apply_title(con, session_id, prompt)
        finally:
            con.close()
        _log(f"{result} sid={session_id} title={title!r}")
    except Exception as exc:
        _log(f"error sid={session_id}: {type(exc).__name__}: {exc}")
    return 0


# ── 自测（两向探针） ────────────────────────────────────────────────────────
_FIXTURE_SCHEMA = """
CREATE TABLE local_runtime_sessions (
  session_id TEXT PRIMARY KEY, record_json TEXT NOT NULL DEFAULT '{}',
  updated_at_ms INTEGER NOT NULL DEFAULT 0, columnar_version INTEGER NOT NULL DEFAULT 3,
  agent_name TEXT, runtime TEXT, session_type TEXT, status TEXT,
  archived INTEGER NOT NULL DEFAULT 0, visibility TEXT NOT NULL DEFAULT 'visible',
  session_kind TEXT NOT NULL DEFAULT 'conversation', purpose TEXT,
  parent_session_id TEXT, title TEXT, created_at_ms INTEGER,
  workspace_dir TEXT, extra_data_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE local_runtime_session_fts_keys (
  fts_rowid INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_fts_keys_sid ON local_runtime_session_fts_keys(session_id);
CREATE VIRTUAL TABLE local_runtime_sessions_fts USING fts5(
  session_id UNINDEXED, session_id_terms, agent_name_terms, title_terms,
  workspace_dir_terms, purpose_terms, status_terms, session_type_terms,
  tokenize = 'unicode61'
);
"""

_FIXTURES = {
    "sid_ok": dict(session_kind="conversation", parent_session_id=None, archived=0,
                   title=None, title_source=None),
    "sid_manual": dict(session_kind="conversation", parent_session_id=None, archived=0,
                       title="我手动起的名字", title_source="manual"),
    "sid_task": dict(session_kind="task", parent_session_id=None, archived=0,
                     title=None, title_source=None),
    "sid_child": dict(session_kind="conversation", parent_session_id="mvs_parent",
                      archived=0, title=None, title_source=None),
    "sid_archived": dict(session_kind="conversation", parent_session_id=None, archived=1,
                         title=None, title_source=None),
    "sid_signed": dict(session_kind="conversation", parent_session_id=None, archived=0,
                       title="261023 | 功能 | 已有格式标题", title_source="auto"),
}

_CREATED_MS = 1792718928222


def _build_fixture(con, sid: str, spec: dict) -> None:
    extra = json.dumps({"titleSource": spec["title_source"]} if spec["title_source"] else {},
                       ensure_ascii=False, separators=(",", ":"))
    con.execute(
        "INSERT INTO local_runtime_sessions(session_id, record_json, updated_at_ms, columnar_version,"
        " agent_name, runtime, session_type, status, archived, visibility, session_kind, purpose,"
        " parent_session_id, title, created_at_ms, extra_data_json)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (sid, "{}", 0, 3, "mavis", "pi-agent", "branch", "started", spec["archived"], "visible",
         spec["session_kind"], None, spec["parent_session_id"], spec["title"], _CREATED_MS, extra),
    )


def self_test() -> int:
    failures: list[str] = []
    primitive, _ = _load_primitive()
    con = sqlite3.connect(":memory:")
    con.executescript(_FIXTURE_SCHEMA)
    for sid, spec in _FIXTURES.items():
        _build_fixture(con, sid, spec)
    con.commit()

    prompt = "把布洛陀脚本体系接入 MiniMax Code 端并跑通验证"

    # T1 正向：能写 + 格式正确 + titleSource 落 manual + FTS 同步可检索
    result, title = apply_title(con, "sid_ok", prompt)
    if result != "named":
        failures.append(f"T1 result={result} (期望 named)")
    elif not re.match(r"^\d{6} \| \S+ \| \S+", title or ""):
        failures.append(f"T1 标题格式不合规: {title!r}")
    elif title.split(" | ")[0] != primitive.bj_date_from_ms(_CREATED_MS):
        failures.append(f"T1 日期不是创建日期: {title!r}")
    row = _read_session(con, "sid_ok")
    if _title_source(row) != "manual":
        failures.append(f"T1 titleSource={_title_source(row)!r} (期望 manual)")
    fts = con.execute(
        "SELECT title_terms FROM local_runtime_sessions_fts WHERE session_id='sid_ok'"
    ).fetchone()
    if not fts or fts[0] != _terms(title):
        failures.append("T1 FTS title_terms 未同步")
    else:
        match = con.execute(
            "SELECT session_id FROM local_runtime_sessions_fts "
            "WHERE local_runtime_sessions_fts MATCH ?",
            (f'"{_terms(title)}"',),
        ).fetchall()
        if not match:
            failures.append("T1 FTS MATCH 检索不到新标题")

    # T2~T6 两条守卫：正常路径应拦
    expected_skips = {
        "sid_manual": "manual",
        "sid_task": "kind",
        "sid_child": "child",
        "sid_archived": "archived",
        "sid_signed": "signature",
    }
    for sid, guard in expected_skips.items():
        before = _read_session(con, sid)["title"]
        result, _ = apply_title(con, sid, prompt)
        if result != f"skip:{guard}":
            failures.append(f"{sid} result={result} (期望 skip:{guard})")
        after = _read_session(con, sid)["title"]
        if after != before:
            failures.append(f"{sid} 标题被改写: {before!r} -> {after!r}")

    # 两向探针：逐条守卫验证"只有它能拦"——关掉它必须放行（否则该判据恒真=假绿）
    for sid, guard in expected_skips.items():
        result, _ = apply_title(con, sid, prompt, disable=(guard,))
        if result.startswith("skip:"):
            failures.append(f"PROBE:FAIL {guard} 关掉后仍被拦（判据恒真·假绿）")

    # T7 幂等：再跑一次同一会话 → 应被拦（首个命中的守卫=manual·本件已写过的行）
    result, _ = apply_title(con, "sid_ok", prompt)
    if result not in ("skip:manual", "skip:signature"):
        failures.append(f"T7 幂等失败 result={result} (期望 skip:manual/skip:signature)")

    con.close()

    total = 2 + len(expected_skips) * 2 + 1
    if failures:
        print(f"SELF-TEST: FAIL({len(failures)})/{total}")
        for item in failures:
            print(f"  ✗ {item}")
        return 1
    print(f"SELF-TEST: OK {total}/{total} · MUT:OK（{len(expected_skips)} 条守卫关掉即放行·判据可杀）")
    return 0


# ── dry-run ─────────────────────────────────────────────────────────────────
def dry_run(prompt: str) -> int:
    primitive, _ = _load_primitive()
    created = int(datetime.now().timestamp() * 1000)
    print(primitive.make_title(prompt, created))
    return 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] == "--self-test":
        try:
            return self_test()
        except Exception as exc:
            print(f"SELF-TEST: FAIL({type(exc).__name__}: {exc})")
            return 1
    if args and args[0] == "--dry-run":
        prompt = ""
        i = 1
        while i < len(args):
            if args[i] == "--prompt" and i + 1 < len(args):
                prompt = args[i + 1]
                i += 2
            else:
                i += 1
        try:
            return dry_run(prompt)
        except Exception as exc:
            print(f"DRY-RUN: FAIL({type(exc).__name__}: {exc})")
            return 1
    try:
        return hook_mode()
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
