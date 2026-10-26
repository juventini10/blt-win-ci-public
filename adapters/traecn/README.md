# adapters/traecn — Trae CN 端适配器

> **端形态**：标准 hook 端。注册面 = `~/.trae-cn/hooks.json`（6 事件），**不是** `settings.json`、**不是** `cli/config.json`。
> **建档**：2026-10-25（Trae Work 退役·双端合并单端；实践记录见 `记忆蓝图/04_系统文件设计/安装包设计哲学/附录A参考实践-Trae CN端适配记录.md`）

---

## 一、能力速览（capability.yaml 单一真源）

| 键 | 值 | 依据 |
|---|---|---|
| config_root | `~/.trae-cn` | 产品 `dataFolderName` |
| rules_inject | true | `user_rules/` 常驻注入 |
| hooks_event | true | `hooks.json` 六事件 |
| settings_json | false | 无 settings.json 面 |
| hooks_registration_face | `hooks_json` | 安装器分派键 |
| hooks_registration | `setup` | 安装器 ③ 跳过·防双写 |
| skill_symlink | true | 通用 Skill 软链 + 专属实体 |

## 二、目录结构

```
adapters/traecn/
├── capability.yaml          # 能力矩阵 + hooks_surface + extra_hooks
├── setup.sh                 # 端部署入口（5 步）
├── rules/                   # 五系统文件承载名（core-*.md）
├── templates/               # doenglingz-core-header.md（恒驻核头模板）
└── skills/                  # 童灵专属 2 件（实体直落，⛔不进共享技能配置）
```

## 三、名映射表（条文 12·承载名 ≠ 注入名）

| 承载名（rules/） | 本端注入名（user_rules/） |
|---|---|
| `core-soul.md` | `SOUL.md` |
| `core-identity.md` | `IDENTITY.md` |
| `core-user.md` | `USER.md` |
| `core-memory.md` | `MEMORY.md` |
| `execution-guidelines.md` | `trae_solo_rules.md` |
| `intent-signature-check.md` | 同名直落 |

Skill 承载名：`doenglingz-guard` → `布洛陀-童灵守护`；`doenglingz-slice-nav` → `布洛陀-童灵切片导航`。

## 四、安装分工（单一写点）

| 阶段 | 谁做 | 落点 |
|---|---|---|
| ① rules + 分身核 + Skill | 端 `setup.sh` | `~/.trae-cn/user_rules/`、`skills/` |
| ② 钩子副本部署 | 安装器（ROSTER + extra_hooks） | `~/.trae-cn/hooks/` |
| ③ 钩子注册 | **端 `setup.sh`**（安装器按 capability 跳过） | `~/.trae-cn/hooks.json` |
| ④ 自验证 | 端 `setup.sh` + 安装器 `--verify` | 逐件显形，⛔不谎报 |

设计判据：注册面只有一个写点（setup.sh）；安装器 ② 只管落副本。⛔ 两处各写一半 = 双本账。

## 五、钩子口径（实盘 2026-10-25）

- **31 条命令 = 25 功能钩子 + 6 条 `hooks-probe/probe.sh` 探针**。
- 探针属作者侧观测面，⛔不进包、⛔不计接入率分子。
- Stop 的 6 条（`route_audit` / `route_guard_audit` / `audit_search_kb` / `feedback_detect` / `rule_three_layer_guard` / `tsl_closeout_guard`）经 `traecn_transcript_adapter.py --run` 委派——命令体保留 wrapper，⛔按裸命令注册（否则转录解析断链）。

## 六、已知欠账（如实登记·⛔不藏）

1. `traecode_title_namer.py` 等旧名遗留（更名前的文件名/参数），改名须查全引用面后统一迁移。
2. `platform_adaptation_check.py` 作者侧日检属发版门禁（依赖作者日志目录），⛔不随包；`launchd_patrol` 声明为 `n_a`。
