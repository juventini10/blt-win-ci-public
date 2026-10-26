# adapters/minimaxcode — MiniMax Code 端适配器

> **端形态**：**Plugin Hook 端**。注册面 = `~/.minimax/plugins/bulutuo-guards/hooks/hooks.json`（由插件 manifest `.minimax-plugin/plugin.json` 的 `"hooks"` 数组声明装载），**不是** `settings.json`、**不是**独立 `hooks.json`、**不是** `cli/config.json`。
> **建档**：2026-10-25（实践记录见 `记忆蓝图/04_系统文件设计/安装包设计哲学/附录A参考实践-MiniMax Code端适配记录.md`）

---

## 一、能力速览（capability.yaml 单一真源）

| 键 | 值 | 依据 |
|---|---|---|
| config_root | `~/.minimax` | 本端 activeDataDir（⛔不硬编码·换 profile 即失效） |
| rules_inject | false | 本端无 `rules/` 目录面 |
| agents_full_inject | true | `AGENTS.md` 全局+工作区双层拼接（平台 MUST） |
| hooks_event | true | 插件 hooks.json 3 事件 / 17 条命令 |
| settings_json | false | 本端无 settings.json 钩子面 |
| hooks_registration_face | `minimax_plugin_hooks` | 安装器分派键（**新形态**·第 6 种注册面） |
| hooks_registration | `setup` | 安装器 ③ 跳过·防双写 |
| skill_symlink | false | 本端 skills 为**实体目录**（实测 65 实体 / 0 软链） |

## 二、目录结构

```
adapters/minimaxcode/
├── capability.yaml          # 能力矩阵 + hooks_surface + extra_hooks + twin_surface
├── setup.sh                 # 端部署入口（6 步）
├── rules/                   # 三合一载体模板（core-agents.md / core-user.md / core-memory.md）
├── templates/               # doenglingz-core-header.md（恒驻核头模板）
└── skills/                  # 童灵专属 2 件（实体直落，⛔不进共享技能配置）
```

## 三、名映射表（条文 12·承载名 ≠ 注入名·**本端三合一**）

| 承载名（rules/） | 本端注入名 | 通道 |
|---|---|---|
| `core-agents.md` | `AGENTS.md`（**SOUL + IDENTITY + 自定义指令 三合一**） | AGENTS.md 拼接块（平台 MUST） |
| `core-user.md` | `memory/user.md` | `<user_profile>` 只读块 |
| `core-memory.md` | `agents/mavis/memory/MEMORY.md` | `<agent_memory_tail>` 条目式注入 |

> ⚠️ 本端**三格同指一个文件**——平台拼接块只有一份 `AGENTS.md`，拆成三件即脱离平台机制（端哲学 02 §二 1:1 映射矩阵）。

## 四、安装分工（单一写点）

| 阶段 | 谁做 | 落点 |
|---|---|---|
| ① 系统文件三处 | 端 `setup.sh` | `AGENTS.md` / `memory/user.md` / `agents/mavis/memory/MEMORY.md` |
| ② Skill 实体 | 端 `setup.sh` | `~/.minimax/skills/`（端专属 2 件 + 通用复制） |
| ③ 钩子副本部署 | 安装器（ROSTER + extra_hooks） | `~/.minimax/hooks/` |
| ④ 钩子注册 | **端 `setup.sh`**（安装器按 capability 跳过） | 插件 `hooks/hooks.json` |
| ⑤ 自验证 | 端 `setup.sh` + 安装器 `--verify` | 逐件显形，⛔不谎报 |

设计判据：注册面只有一个写点（setup.sh）；安装器 ③ 只管落副本。⛔ 两处各写一半 = 双本账。

## 五、钩子口径（实盘 2026-10-25）

- **17 条命令 = UserPromptSubmit 6 + Stop 8 + SessionStart 3**。
- **Stop 的 8 条全部裹 `minimaxcode_hook_adapter.py`**——宿主 Plugin Hook 的 Stop 契约要求 stdout 为**单个 JSON 对象**，共享守卫的纯文本 stdout 会被宿主判 `HOOK_INVALID_OUTPUT` **直接丢弃**（挂载在·产出不到 = **假绿**）。⛔ 裸挂共享守卫＝静默失效。
- **UPS / SessionStart 不裹**——实测零 `HOOK_INVALID_OUTPUT`，纯文本可投递 ⇒ 不做无证据改动。
- 接入率分子按**被包脚本名**计（⛔不是命令条数·Stop 命令里有两个脚本）。

## 六、本端三条独有约束

| # | 约束 | 用户侧影响 |
|:--|:--|:--|
| C1 | `AGENTS.md` 单文件承载三格 | 改三件 = 改一个文件；⛔覆盖会毁用户本机铁律与切片覆盖块 |
| C2 | MEMORY 注入体是条目集合 | 模板须 `### 主题` + `Type:` 格式；⛔散文段不进注入；关键内容置尾（保尾弃头） |
| C3 | 长期记忆通道只对**内置默认会话**开放 | 选自定义 agent 会话 ⇒ 拿不到长期记忆与画像（平台机制·非本包缺陷） |

## 七、已知欠账（如实登记·⛔不藏）

1. **分身域 5 件本端未实挂**（`doenglingz_level_declare_guard` / `tsl_echo_hook` / `tsl_closeout_guard` / `tsl_tree_hook` / `doenglingz_skill_onduty_tier_promote`）——宿主 Plugin Hook 事件面无对应挂点证据 ⇒ 按 `twin_surface.gaps` 显形，⛔不谎称已支持。
2. 本端健康巡检走 `SessionStart` 钩子聚合器（`minimaxcode_health_aggregator.py`），⛔**无 launchd 定时巡逻**（声明 `launchd_patrol: n_a`）。
