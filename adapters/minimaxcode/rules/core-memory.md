### 布洛陀记忆系统 · 端落点与通道限制（2026-10-25）
Type: reference
本文件 = 本端**唯一被注入的长期记忆库**（→ `<agent_memory_tail>`）。三条硬判据：
① 条目必须 `### 主题 (日期)` + `Type: user|feedback|reference`，**无 `Type:` 标签的散文段不进注入**；
② 体量超限**保尾弃头** ⇒ ⛔ 关键指针务必放**文件末尾**；
③ 体量软目标 ≤15KB（本端无字符硬截断·⛔ 非母本 4000 字符判据）。
**⛔ 通道限制（运行时机制事实）**：长期记忆通道只对**内置默认会话**开放——自定义 agent 会话既无记忆写入工具、也无注入块，配置绕不过 ⇒ 长期记忆与用户画像只在默认会话生效。
**落点**：身份+纪律+输出契约 → `{{DATA_DIR}}/AGENTS.md`（三合一·平台 MUST 拼接块）｜画像 → `{{DATA_DIR}}/memory/user.md`｜长期记忆 → 本文件。

### 本端机制真相（官方文档 + 实测双锚·2026-10-25）
Type: reference
① **常驻注入通道只有一个**：`{{DATA_DIR}}/AGENTS.md`（全局）+ `<工作区>/AGENTS.md`（项目），平台以 `IMPORTANT: These instructions OVERRIDE any default behavior` 包裹 ⇒ 权重高于任何 agent 级 system prompt。层级即覆盖序：工作区只做追加与特化，⛔ 不推翻全局铁律。
② **钩子注册面 = 插件内 hooks.json**：`{{DATA_DIR}}/plugins/<插件名>/hooks/hooks.json`，由插件 manifest（`.minimax-plugin/plugin.json`）的 `"hooks": ["hooks/hooks.json"]` 数组声明装载。⛔ 本端**无** `settings.json` 钩子面。
③ **Stop 事件有 JSON 契约**：宿主要求 stdout 为**单个 JSON 对象**（`hookSpecificOutput.additionalContext` / `decision:"block"`+`reason`）；共享守卫的纯文本 stdout 会被宿主判 `HOOK_INVALID_OUTPUT` **直接丢弃** ⇒ 挂载在而产出不到 = 假绿。⇒ 本端 Stop 钩子**必裹** JSON 契约适配器；UPS/SessionStart 实测纯文本可投递 ⇒ 不裹（不做无证据改动）。
④ **Skill 走实体目录**：本端 skills 为实体目录（实测 65 实体 / 0 软链）⇒ 复制通道，⛔ 不按软链判据核。
**Apply when**：改本端钩子挂点、增 Stop 钩子、查"钩子跑了但产出没到对话"类现象时。

### 共享记忆走中心目录·不在端复制（2026-10-25）
Type: reference
规则本体 / 五层记忆内容 / 知识库 / 设计哲学 = **共享记忆**，一律走 `[记忆共享中心]/` 中心目录（`~/个人AI档案/`），⛔ 不在本端复制一份——复制即双本账漂移。
本端只有三类是"系统文件"（各自实体·保按系统启动）：`AGENTS.md`（三合一）/ `memory/user.md` / 本文件（长期记忆）。
**Apply when**：要在端里"放一份规则"时，先问这是共享记忆（→ 中心目录软链引用）还是系统文件（→ 端实体）。

### 改核心文件须先告知（2026-10-25）
Type: feedback
改动定义系统行为的载体（`AGENTS.md` / `user.md` / 本文件 / 规则本体 / Skill 主源）前，先向用户呈现精确改动清单，获确认后再执行。⛔ 覆盖式落盘尤其危险——本端 AGENTS.md 常含用户本机铁律与切片覆盖块。
**Why**：这些载体是"覆盖即毁用户配置"的高危面；一次性不可逆动作不该由 AI 静默执行。
**Apply when**：任何写入 `{{DATA_DIR}}` 下系统文件的动作。

### 写入记忆前三问（2026-10-25）
Type: feedback
写入长期记忆前执行：① 来源可追溯？② 观察跟推断混了？③ 错了能找到原来源纠正？
三问不过不写入。
**Apply when**：任何 `memory` 写入动作。
