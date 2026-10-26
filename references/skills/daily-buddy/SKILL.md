---
name: daily-buddy
description: >
  每日伙伴核心工作流：早晨规划、进度记账、晚间复盘及多端同步。
  当用户说"日记/写日记/早上好/晨报/早报/开始规划"时——晨间规划；"开始专注/记录进度/完成了/记账"时——进度记账；"复盘/今晚复盘/今日复盘/今日总结/晚间总结/总结今天"时——晚间复盘；"睡眠数据"时——睡眠记录与检查（工作流C步骤1补齐）；"周报/月报/月总结/记忆蒸馏"时——周期报告；"同步日记"时——多端同步。
  NOT for 纯闲聊/文件操作/代码debug/系统文件架构与规格书维护（属工程任务，⛔非日记工作流——2026-08-29 实证：规格书瘦身任务被误命中本技能，已记录 abandon 信号）；"日记本在哪"等查询不触发。
compatibility: workbuddy, qclaw, trae, trae-solo, wukong, qoderwork, zcode
allowed-tools: [Read, Write, Bash, Grep]
dependencies: [scripts/create_skeleton.py, scripts/finalize_diary.py, scripts/achievement_tracker.py, scripts/update_diary_achievement.py, scripts/verify_achievement_seal.py, scripts/monthly_data_snapshot.py, scripts/verify_report_data.py, scripts/distill_containers.py, scripts/finalize_report.py]
author: 皮叔
source: self-built
upstream: [记忆共享中心]/技能配置/daily-buddy/
modifiable: true
version: "3.54.1"
license: MIT
complies_with: 文件格式规范 v2.0.0
normative_vocab: "RFC2119-equivalent (see 指令编写规范 §1.1)"
---

# 🤖 每日伙伴 (Daily Buddy)

> **设计哲学**：早晨规划→进度记账→晚间复盘→多端同步，闭环个人日报体系。
> **历史变更**：详见 `references/CHANGELOG.md`
> 🧭 **读法**：先看指路牌定位置，再按触发路由进对应工作流；工作流合同在文末终位区，执行时逐字照做。

## 🧭 指路牌（按节名指路·禁行号）

> 三纪律：①按节名指路，⛔行号（行号必漂）②每条带消费时刻 ③本节列出的节名集合≡实际 `## ` 节集合（`scripts/orchestration_gate.py` 常驻断言·防说谎）。

| 你要干什么 | 看哪节 |
|:--|:--|
| 核对强制条款（写任何输出前） | `## ⚠️ 铁律声明（执行时最高优先级）` |
| 判断该跑哪个工作流 | `## 🚦 触发与工作流路由` |
| 核对全局红线与常量 | `## 🛡️ 硬约束：P0 六条与常驻常量` |
| 核对禁止行为 | `## ⛔ 禁止行为` |
| 调脚本/核对四层契约/验收 | `## 🧰 契约与闸（脚本·四层·验收）` |
| 查路径变量 | `## 🔗 外部依赖变量表` |
| 找 reference 文件 | `## 📚 references/ 索引` |
| 核对质量与证据要求 | `## 📐 质量与证据声明` |
| 查 T5/预算/发布清单/安全 | `## 🔧 运维与安全（T5/预算/发布/安全）` |
| 执行晨间规划 | `## 🌅 工作流 A：早晨规划` |
| 执行进度记账 | `## 📝 工作流 B：进度记账` |
| 执行晚间复盘 | `## 🌙 工作流 C：晚间复盘` |
| 执行多端同步 | `## 🔄 工作流 D：多端同步` |
| 执行周报/月报 | `## 📊 工作流 E/F：周报与月报` |
| 写日记本体（模板） | `## 🏗️ SSOT 日记模板（创建日记时读）` |
| 改完本 Skill 要验收 | `## 🧪 修改后自检（机检入口）` |

## ⚠️ 铁律声明（执行时最高优先级）

> 🔴 本文件在每日伙伴 Skill 执行时优先级最高，context compression 不可覆盖
> 🔴 不是建议，是硬约束。不可跳过

**✅DO — 本Skill有6个工作流（A-F）。被触发后第一条回复✅DO声明当前执行的工作流。** 格式：`📋 每日伙伴 v{版本} · {工作流名}`。未声明=未触发。⛔DO NOT跳过——原因是多工作流下不声明会让用户不清楚跑的是哪个。

**✅DO — 格式即法律、数据有出处、文件唯一性、时间真相、复盘真相源。**

**指令质量要求详见 `$SPEC`（指令编写规范.md）。**

## 🚦 触发与工作流路由

| 触发词 | 工作流 |
|:--|:--|
| "日记" / "写日记" | A-F 路由（按语境） |
| "晨报" / "早报" / "早上好" / "开始规划" | A 晨间规划 |
| "开始专注" / "记录进度" / "完成了" / "记账" | B 进度记账 |
| "复盘" / "今晚复盘" / "今日复盘" / "晚间总结" / "总结今天" / "今日总结" | C 晚间复盘 |
| "睡眠数据" | C 步骤1（睡眠数据采集） |
| "同步日记" | D 多端同步 |
| "周报" / "周报时间" | E 周报 |
| "月报" / "月总结" / "记忆蒸馏" / "月度记忆蒸馏" | F 月报 |

**不应该触发**："日记本在哪"/"看看昨天的日记"（查询意图，⛔写入流程）；纯代码debug；"总结一下这段代码"（宾语是代码不是一天）；用户说"不用写日记"。

**语境限定**：意图是"记录/生成内容"→触发；"查看/寻找/定位"→不触发。

**管辖权重叠**：日记写入唯一入口=本 Skill；系统日志记"AI做了什么"，本 Skill 记"个人的一天"（状态/睡眠/成就），两账不混。

**退出**：当前工作流执行完毕→自然退出；用户说"不写了""就这样"→即时退出。

## 🛡️ 硬约束：P0 六条与常驻常量

> 1. **格式即法律**：输出✅DO严格遵循 `references/diary-template.md` 的【SSOT 日记模板】，包含全部 HTML 注释标记（如 `<!-- SECTION: 模块名 -->`），严格保留标题层级。原因是格式漂移=跨天数据不可比对，模板一致性是周报/月报数据源可靠的前提。
> 2. **数据有出处**：每项数据从日记原文、`date` 输出、脚本结果或用户回答中提取。空值留空。原因是AI记忆可能过时或幻觉。
> 3. **文件唯一性**：每天只有 1 个文件 `YYYY-MM-DD.md`；已存在则追加/更新局部。原因是多文件=数据分散=同步冲突+统计遗漏。
> 4. **时间真相**：所有时间戳通过 `date` 命令获取。原因是AI推算时间=确定性计算走概率路径（内部记录 连错3天）。
> 5. **复盘真相源**：晚间建议从"实际完成区"取值，⛔不看"早晨计划区"。原因是计划=预期非事实。
> 6. **本文件唯一可信源**：`[记忆共享中心]/技能配置/daily-buddy/SKILL.md`；各平台为目录级软链，改权威源即全端生效。原因是多副本=版本漂移。

**📏 监控标准常量（全局统一）**

| 指标 | 标准值 | 偏差标记 |
|:--|:--|:--|
| 入睡时间 | 23:30 前 | 超过 → ⚠️ |
| 起床时间 | 07:30 前 | 超过 → ⚠️ |
| 睡眠时长 | ≥7h | <7h → ❌健康警示；<6h → 🔴严重警示 |
| 工作日番茄 | ≥16🍅 | <16🍅 → ⚠️ |
| 行为漂移阈值 | 连续3天同向偏差 | 触发L3行为层写入 |

**📅 记忆层 TTL**：L4 情境层 90天（到期提示季度复盘）｜L5 潜意识层 无上限、对质后30天无复发归档｜L1/L2/L3 6个月未review提示｜L4 预警 设立后60天提示校准。

**🐍 日期确定性（v3.12.1）**：`day_of_week` 是日期→星期的确定性函数，⛔禁止AI手写或推算。骨架必须调 `bash $SKILL_ROOT/scripts/dbbin.sh create_skeleton.py --date YYYY-MM-DD --out "$DIARY/YYYY-MM/YYYY-MM-DD.md"`（⛔漏 --out=只打 stdout 不落盘），`day_of_week` 由脚本注入，AI 从输出提取。违反=确定性计算走概率路径。

## ⛔ 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 跳过产出物锁 | 缺产物=后续步骤无法引用 |
| 2 | 跳过三段校验直接输出 | 检查不通过→输出残缺 |
| 3 | 代写今日感悟 | AI代写=剥夺反思 |
| 4 | 凭记忆写日记而非从原文提取 | 记忆可能有偏差 |
| 5 | 快照更新超出允许范围（CONTEXTUAL层·今日能量/SHADOW状态 + 头部时间戳 + 最近变更摘要/核心文件健康/成长箱速览/当前情境段·里程碑入口） | 越界写入污染其他区域 |

## 🧰 契约与闸（脚本·四层·验收）

**✅DO 脚本调用规范**：一律经统一包装器 `dbbin.sh`（双保险·不需记得设环境变量）：
```
bash $SKILL_ROOT/scripts/dbbin.sh <script.py> [args...]
例：bash $SKILL_ROOT/scripts/dbbin.sh create_skeleton.py --date 2026-08-20 --out "$DIARY/2026-08/2026-08-20.md"
    bash $SKILL_ROOT/scripts/dbbin.sh finalize_diary.py --date 2026-08-20
```
⛔DO NOT 直接 `python3 scripts/xxx.py`——原因：可能落入沙箱假 python/假 HOME，导致空跑或成就模块错位（Hermes 沙箱 08-19/08-20 两次踩坑，已由 `dbenv` 脚本层自愈，调用层加 dbbin 为双保险）。

**四层契约**：输入=触发词→A-F 路由→date 真实时间→读日记；输出=五字段数据核对（date/tomato_count/sleep_duration/mood/task_summary·AI 执行层）+ SSOT 日记模板 + 完整性锁三段校验；行为=只读 Read+只写日记/快照/日志/SHADOW（白名单），行动倾向 `do_not_act_before_instructions`（例外：进度记账即时写入🟢自主、晚间复盘写入🟡确认）；演化=多端兼容，触发首行输出版本号并对比权威源（不一致采用权威源）。

**📦 可机器化验收（脚本即物理拦截·AI 只编排不手算）**

| 脚本 | 管什么 | 验收/何时 |
|:--|:--|:--|
| `create_skeleton.py` | 骨架生成（day_of_week 脚本注入） | exit 0+输出非空；工作流A |
| `finalize_diary.py` | 日记封口（完整性+次日骨架+概念进料门禁） | **exit 语义单一真相源=脚本头部**；核心：0=成功 / 3=当日无 ingest（`--skip-ingest` 有痕跳过）；工作流C 终步 |
| `monthly_data_snapshot.py` | 月报数据快照 | exit 0+快照JSON；F 第0步 |
| `verify_report_data.py` | 月报数据回读校验 | exit 0=22条规则全过；F 第1.9步 |
| `distill_containers.py` | 五容器回流骨架+校验 | exit 0=骨架齐备；`--verify` 校验；F 第6.5步 |
| `finalize_report.py` | 周/月报终检收口（三层物理拦截末层） | exit 0=封口；非0=拒收；F 第7步 / E 第7步 |
| `check_diary_titles.py` | 标题/日期一致性（QA·只读） | exit 0=校验完成 |
| `test_context_sync.py` | 周报×情境层联动（QA·只读） | 只读验证 |
| `achievement_tracker.py`（软链） | 成就检测 | 新成就→写 `成就证据/{日期}-{成就ID}.md`；须经 dbbin |
| `update_diary_achievement.py` | 日记成就模块更新 | 幂等可重复 |
| `verify_achievement_seal.py` | 成就封口签名校验 | 签名==当日真实数据→通过 |
| `$ACHIEVE_SCRIPTS/check_concept_achievement.py` | 概念碰撞成就对账 | 幂等可重复 |

> 🔗 软链归属：`scripts/achievement_tracker.py` 为软链→`[记忆共享中心]/成就系统/scripts/`（单一真源·双入口），⛔改独立副本=双本账。发布包构建时复制为普通文件。
> 🚦 exit 码族（单一真相源=`scripts/dbenv.py` docstring）：0=成功 / 1=参数错误 / 2=内容不完整 / 3=依赖文件缺失 / 4=依赖字段缺失 / 5/6/7=脚本特有扩展码（族表不越权定义·语义以各脚本头部为准，如 finalize_diary 5=参数错误/6=格式门禁） / 9=环境自检失败。

### 🛡️ Poka-Yoke 防误层（S级）

> 防误层让错误无法发生，而非检查错误是否发生。
> **为何不挂 hook（如实声明）**：脚本层已实装 3 项硬拦截（finalize_diary 六档 exit / create_skeleton 注入 day_of_week / verify_achievement_seal 签名校验）；番茄定值为 AI 执行层比对（**非脚本物理拦截·如实标注**）。故不重复挂 PreToolUse/PostToolUse hook，避免冗余与跨平台配置分裂。

| 防误机制 | Poka-Yoke 方法 | 防什么错 | 强度 |
|:--|:--|:--|:--|
| 五字段数据核对 | 清单法 | 数据缺失/字段错 | AI 执行层（弱一档·如实标注·物理拦截位=finalize_diary 完整性锁） |
| 番茄数定值校验 | 定值法 | 计数错 | AI 执行层（弱一档） |
| 步骤强依赖 | 步序法 | 跳步 | 最强（前步缺失=阻断） |
| 成就封口签名校验 | 接触法+定值法 | 检测被跳过/伪造 | 最强（签名不符=阻断） |

## 🔗 外部依赖变量表

> 变量化集中声明，避免散落硬编码；`$SKILL_ROOT` = `[记忆共享中心]/技能配置/daily-buddy/`。

| 变量 | 路径 | 何时用 |
|:--|:--|:--|
| `$SPEC` | `[记忆共享中心]/记忆蓝图/03_开发规范/指令编写规范.md` | 编写指令时 |
| `$ACHIEVE_SCRIPTS` | `[记忆共享中心]/成就系统/scripts/` | C 封口后 |
| `$GREATEST` | `[记忆共享中心]/最伟大的我/` | F 月报 |
| `$DISTILL` | `[记忆共享中心]/记忆蒸馏/蒸馏中心.md` | F 第1.1步 |
| `$DIARY` | `{{DIARY_ROOT}}`（含 `YYYY-MM/` 月层·与 create_skeleton 同源）；源端取值=`bash $SKILL_ROOT/scripts/dbbin.sh dbenv.py` 输出的 `DIARY_DIR` | A 存在性检查 |
| `$SYSTEM_LOG` | `[记忆共享中心]/工作日志/系统日志/` | C 封口后 |
| `$UNKNOWN` | `[记忆共享中心]/未知未知/` | C 反哺路由 |
| `$SITUATION` | `[记忆共享中心]/情境层/` | C 收尾 |
| `$HEURISTIC` | 知识池「✅核心启发」标签子集（虚拟集合·先扫✅标签卡→无则扫全池） | C 复盘引用 |
| `$KB_ENGINE` | `[记忆共享中心]/脚本中心/知识联邦引擎/` | C 引用 |

> 🔻 降级声明：知识联邦引擎及其脚本属发布者工具，端用户最小集随包分发；无此引擎时相关步骤跳过·不阻塞。

## 📚 references/ 索引

| 文件 | 内容 | 加载时机 |
|------|------|---------|
| `diary-template.md` | SSOT 日记模板（12 SECTION） | 写/更新日记 |
| `工作流C-晚间复盘.md` | 晚间复盘 SOP（步骤1-9） | 工作流C |
| `sleep-module.md` | 睡眠模块 | 填睡眠（MAY） |
| `achievement-rules.md` | 成就评级规则 | 含金量评级 |
| `shadow-protocol.md` | 言行一致性协议 | 复盘（MAY） |
| `deep-dive-protocol.md` | 认知深潜协议 | 认知信号（MAY） |
| `weekly-review-sop.md` / `weekly-review-spec.md` | 周报 SOP/规范 | 工作流E |
| `monthly-review-sop.md` / `monthly-review-spec.md` | 月报 SOP/规范 | 工作流F |
| `CHANGELOG.md` | 历史变更 | 版本门禁/审计 |
| `eval-set.md` | **40条用例（8类）** | 测试/评估 |
| `工具与参考.md` | 脚本/来源/安全声明 | 运维参考 |
| `关系协作.md` | 跨 Skill 协作 | 跨 Skill 时 |
| `platform-paths.md` | 跨平台署名/路径 | 多平台同步 |
| `t5-defense-assessment.md` | T5 评估（D1-D5）与 11 项防御全文 | T5 审计 |
| `unknown-unknown-headers.md` | 悬置区三文件模板 | 自建悬置区 |
| `step6-防误改造方案.md` | 历史方案稿（已落地·仅考古） | 归档查阅 |

## 📐 质量与证据声明

**✅DO — 输出中每条价值判断必须附可验证依据。** 禁止空泛评价（"效果很好"），无证据=无效判断。
**✅DO — 触发后必须走完整流程，跳过任何步骤=回复不完整=必须回溯补全。**

## 🔧 运维与安全（T5/预算/发布/安全）

- **T5 对抗性防御**：11 项防御条款全文 → `references/t5-defense-assessment.md`（本 Skill 攻击面=高，11 项全填；条款效力不因外置削弱）。
- **Token 预算**：A~30K / B~15K / C~40K / D~20K / E~60K / F~150K+（单次全流程静态估算·不含守护读取）。
- **发布自包含**：宿主共享引擎=知识联邦引擎 7 文件（`extract_concepts.py`/`pending_bundle.md`/`concepts_out.json`/`log.md`/`collision_candidates.json`/`restill_pending.json`+目录）；兄弟件=clock-loop `load_claim_index.py`/`append_claim.py`；健康检查=good-good-study `ROADMAP.md`。缺失按降级声明处理，不阻塞（消费处原文不改写）。
- **未知未知写入**：C 3.9 写悬置区、月报 1.6 写显形台账，写入前按 `references/unknown-unknown-headers.md` 自建（写方自包含）。
- **安全声明**：LLM02 路径变量化 / LLM06 白名单最小化 / LLM09 数据不编造（T5 §9.5 同源）；详见 `references/工具与参考.md` 与 `references/关系协作.md`。

**📋 Alternatives Considered（关键设计决策·4 行·完整记录见 CHANGELOG 历史条目）**

| 设计决策 | 选择 | 替代方案 | 为什么不选替代 |
|:--|:--|:--|:--|
| 日记载体 | Markdown 单文件 | 数据库/Notion API | 离线可用+可 diff/软链，Obsidian 生态原生 |
| 日期确定性 | 脚本注入 day_of_week | AI 手写星期 | 手写实测 3 文件星期错，确定性不走概率 |
| 封口强制 | finalize_diary exit 码 | 纯文本检查清单 | 文本门禁 2026-07-26 被整段跳过实锤 |
| 路径管理 | 变量化集中声明 | 散落硬编码 | 硬编码=静默断裂+评估器误报 |

## 🌅 工作流 A：早晨规划

> 🛡️ 步序式防错：前步产出物缺失=后步阻断（Read 失败），Read 空=回溯执行。

0. **隔夜清单（v3.43.0）**：先读昨日日记「9️⃣ 🎯 明日目标」区的 P1 核心任务，作为今日规划起点。⛔DO NOT 从空白重新规划（丢弃隔夜清单=每晚「9️⃣」白写=闭环断裂）。
   - 📖 顺序：Read `$DIARY/YYYY-MM/昨日.md` → 提取「明日P1核心任务」3 行。
   - 🔌 熔断器：昨日日记不存在 / 无该区 / 区为空 → 跳过隔夜清单进步骤1（不阻塞）。
   - 📍 排序：隔夜清单作 P1 基准，可调整/替换，但✅DO先展示"昨晚定的 3 件"给用户确认再动。
1. **获取信息**：运行 `date` 对齐今日日期（年/月/日/星期，⛔不凭记忆推算）；日历=日期对齐，非系统日历事件。
   - 💡 每月1号提醒：`date +%d`=="01" → 提示执行「生成月报」（回复"生成月报"立即执行 / "稍后"跳过）。
   - 💡 每周一提醒：`date +%u`=="1" → 提示执行「生成周报」（同上一问）。
   - 💡 错误候选提醒（每天）：读 `[记忆共享中心]/成长箱/错误候选待确认.md`，有⏳候选（≤5条）则列出并问"记到成长箱/跳过"；无则静默。⛔DO NOT 自动写入成长箱（记录与否归用户判断）。
2. **未完成结转**：读昨日【未完成】项，问用户是否加入今日（需确认优先级和🍅数，不自动搬运）。
3. **80/20 规划**：引导定今日目标，强制分 P1（最重要1-2件）与 P2（量力），每个目标☑SHOULD有 `X🍅` 预估。
4. **创建/更新日记**：检查 `$DIARY/YYYY-MM/YYYY-MM-DD.md`；不存在则 `bash $SKILL_ROOT/scripts/dbbin.sh create_skeleton.py --date YYYY-MM-DD --out "$DIARY/YYYY-MM/YYYY-MM-DD.md"`（day_of_week 脚本注入·脚本幂等），把目标填入 `## 1️⃣ 🎯 今日工作`。

> 🔌 熔断器（骨架生成·外部跑脚本）
> ├─ 成功条件：create_skeleton.py exit 0 且输出非空
> ├─ 失败处理：中止
> ├─ 可修正参数：日期参数/环境（检查 dbbin 与 python）
> ├─ 重试次数：1
> └─ 降级方案：停止创建，输出错误并建议手动创建或检查环境
> ⛔DO NOT 用 AI 手写骨架替代（day_of_week 可能推错）。

## 📝 工作流 B：进度记账

> 💡 用户自行计时，AI 只记账。🍅 = 约半小时工作量的记账单位。

1. **意图声明**："开始专注：{任务名}" → 确认记录并等待完成报告（不计时、不提醒、不打断心流）。
2. **进度记录**：用户报告进度（如"剪辑完成了 2🍅"）→ 精准捕捉任务名与实际🍅数。
3. **即时写入**：打开今日日记 `## 1️⃣ 🎯 今日工作` 表，把数量累加到「实际」列，更新「状态」列（完成✅/进行⏳）。每次报告后立刻写盘；复盘发现漏记→回溯补全。
4. **简短确认**：一句话（例："✅ 已记账：视频剪辑累计 4🍅。"）。

> 🔌 熔断器（日记文件缺失·外部读文件）
> ├─ 成功条件：今日日记存在且 Read 非空
> ├─ 失败处理：中止
> ├─ 可修正参数：路径→检查日期与 `$DIARY` 目录
> ├─ 重试次数：1
> └─ 降级方案：提示"今日日记尚未创建，是否先执行早晨规划（工作流A）？"
> ⛔DO NOT 自动创建空日记并写入（缺骨架=后续复盘数据断裂）。

**定值校验（定值法）**：`sum(工作段) == tomato_count`，不等=拒绝写入（AI 执行层比对·强度弱于脚本拦截，如实标注）。
**写盘前检查点**：数据完整性（任务名匹配+🍅有用户出处）｜白名单｜路径变量化｜局部更新非全量重写。

## 🌙 工作流 C：晚间复盘

> 此流程极其关键，✅DO按 1-9 顺序执行（含 5.5 概念抽取管道·步骤9最终输出8模块：年度进度/今日评级/今日数据/今日工作/今日感悟/新增概念卡/伙伴建议/明日目标）。完整步骤 → `references/工作流C-晚间复盘.md`。
> 🔌 缺档/补录（v3.52.7）：日记不存在 → 先跑工作流 A 步骤4 同命令建骨架，再进 1-9；补录时概念进料用 `--ingest-date` 指向实际抽取日；建议写完跑 `finalize_diary.py --check-advice`。

**📦 日记封口（强制终步·任何路径完成日记均须执行）**
```
bash $SKILL_ROOT/scripts/dbbin.sh finalize_diary.py --date YYYY-MM-DD
```
脚本原子化完成：完整性校验 + 生成次日骨架 + 续接锚点 + 输出确认 JSON。AI 的最终输出✅DO包含「日记封口确认」块，灵感原文取自脚本 JSON（⛔不凭记忆）：
```
📋 日记封口确认
├── 今日：{today} ✓ ({today_rating})
├── 次日骨架：{tomorrow_skeleton} ✓
├── 灵感就位：「{tomorrow_inspiration}」
├── 续接锚点：{tomorrow_anchor}
├── 年度进度：{year_progress}
└── 概念进料：{concept_ingest}（来自封口脚本JSON·v3.20.1）
```
🔒 概念进料门禁已下沉脚本层（v3.20.1）：当日无 ingest 条目→exit 3 拒绝封口（`--skip-ingest` 有痕跳过）；⛔DO NOT AI 自行编写该行（文本层门禁 2026-07-26 被整段跳过实锤）。

**🎯 概念卡价值预筛（v3.49.0）**：概念卡写入概念库前由童灵预筛——个人感悟卡看认知增量，技术架构卡看复用价值；挡同义反复/空话/一次性问题，留推翻旧认知/新模式/可复用方案；重复卡先提价值合并再归档；主题熟悉→第一性原理先，不熟悉→抽象建模先。预筛记录追加 `[记忆共享中心]/数字分身/steps/step3-first-review-log.md` 概念卡预筛段（⛔不占 JOB-001 推翻率分母）。⛔查格式/⛔替皮叔做终审。

**🏆 概念碰撞成就对账（v3.35.0）**：封口后跑 `bash $SKILL_ROOT/scripts/dbbin.sh $ACHIEVE_SCRIPTS/check_concept_achievement.py`（详见 `references/工作流C-晚间复盘.md` 步骤6.5）。

**定值校验**：`sum(工作段) == tomato_count`，不等=拒绝。
**完整性锁**：SECTION 全集核验（日常 11·含里程碑日 12，含🔟伙伴建议）+含金量评定｜版本号声明｜日记原文+date+脚本结果｜完成率/健康警示｜次日骨架已生成（finalize exit 0 + 封口确认块）｜概念进料行取自脚本 JSON。

## 🔄 工作流 D：多端同步

1. 检查是否存在 `<!-- MOBILE_GENERATED -->` 或「【注】本日记基于手机时间生成」的待校验日记。
   > 🔌 熔断器（无待校验日记）
   > ├─ 成功条件：当日目录存在带 MOBILE_GENERATED 标记的日记
   > ├─ 失败处理：跳过
   > └─ 降级方案：输出"当前无需校验的手机日记"，D 正常退出
   > ⛔DO NOT 对已有 PC_VERIFIED 标记的日记重复校验。
2. **对比修复**：手机时间→电脑实时时间；检查 SECTION 是否齐全（日常骨架 11·含里程碑日 12）；核对完成率等数据逻辑。
3. **追加校验记录**：`<!-- PC_VERIFIED: YYYY-MM-DD HH:MM -->` 【电脑同步校验记录】…✅ 通过校验。
   - 完整性锁：PC_VERIFIED 标记+校验记录｜版本声明｜date 输出+SECTION 清单｜通过/不通过判定。

> 五字段核对（AI 执行层·v3.54.0 如实标注）：同步前逐项核对 date/tomato_count/sleep_duration/mood/task_summary 五字段有值且类型正确，缺失/不符=拒绝同步并回补。本步骤无脚本拦截（D 为低频冷路径·不为此新建校验件），物理拦截位=finalize_diary 完整性锁（C 终步）。

## 📊 工作流 E/F：周报与月报

- **E 周报**：完整 SOP → `references/weekly-review-sop.md`。核心：数据采集→情境层→成就更新→生成周报(8模块)→**终检收口（`finalize_report.py --type weekly` 物理拦截）**→情境层更新→记忆层联动。
- **F 月报**：完整 SOP → `references/monthly-review-sop.md` + `monthly-review-spec.md`。核心：月报生成→系统日志客观数据+日记提取纠偏→**系统日志工作模式信号 PULL（第1.1步）**→L2回流校验→SHADOW月度统计→L4情境层→L1底线审计→日志归档→**第6.5步五容器回流（distill_containers.py）→第7步终检+蒸馏中心登记（finalize_report.py 三层物理拦截）**。
- ⚠️ 月报含待确认内容时，对话末用醒目框汇总（对齐三明智结论块格式），不确认不生效。
- ⚠️ 三级级联锁（产出物锁+上步校验锁+报告终检锁）强制嵌入每步。
- 🏆 成就→最伟大的我联动两通道：成就证据自动写入 + 月报第6.5.5步系统建设成果蒸馏。

## 🏗️ SSOT 日记模板（创建日记时读）

> 📌 完整模板在 `references/diary-template.md`（SECTION 全集 12 = 10 编号模块（含🔟伙伴建议）+ 📊里程碑（有才显示·日常骨架不含）+ 🌀悬置；**日常骨架=11 个 SECTION**），创建/更新日记时✅DO Read，逐字照填。

## 🧪 修改后自检（机检入口）

- **一键机检**：`bash $SKILL_ROOT/scripts/run.sh`（结构闸/引用闸/模板形态闸/既有脚本自检）——全绿才算改完，⛔不以口头"已检查"替代。

> ⚠️ **机检件归属声明（2026-10-26）**：本节所列 `run.sh`／`orchestration_check.sh`／`run_gate_selftest.sh`／`test_retire_anchor.sh` 属**作者侧** QA 机检件，**未随本安装包分发**——端用户侧无需执行、也执行不到；改动这些脚本的验收在发布者工具链内进行（登记表 `author-qa-exclude.json`）。
- version ≡ `references/CHANGELOG.md` 最新条目；references 索引≡实际文件；eval-set 40 条零新增红。
- 所有 cross-file 引用以 `references/` 开头；脚本调用一律 `dbbin.sh`。
