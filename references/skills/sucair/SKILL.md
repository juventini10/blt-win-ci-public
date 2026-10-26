---
name: sucair
emoji: 📖
trigger: "蒸馏这本书/蒸馏这个/蒸馏这篇文章/读这本书/帮我做笔记/帮我做读书笔记/提炼这本书/提炼这篇文章/拆解这本书/这本书的精华/把这篇做成卡片/把这篇加进知识库/把这段归档/归档到知识库/知识包/读书助手/5分钟精华"
description: >
  读书助手——蒸馏/读这本书/做笔记/提炼/拆解/精华/知识包。AI替你读，系统逼你学。
  触发词：蒸馏这本书/蒸馏这个/蒸馏这篇文章/读这本书/帮我做笔记/帮我做读书笔记/提炼这本书/提炼这篇文章/拆解这本书/这本书的精华/把这篇做成卡片/把这篇加进知识库/把这段归档/归档到知识库/知识包/读书助手/5分钟精华。
  单线程引擎：读一本书或一篇文章→生成知识包（精华+永久卡片+题库，按来源类型分档）→写入Obsidian知识池。
  不负责执行提醒/复习/分析——消费端由日记、Shall We Talk、月报各自触发。
  NOT for 纯闲聊、纯代码编辑、写书评/读后感（那是创作）。
compatibility: workbuddy, qclaw, trae, trae-work, wukong, qoderwork
allowed-tools: [Read, Write, Bash, Grep]
dependencies:
  - name: shall-we-talk
    version: "1.7.7"
    note: "前置配套——深度对话结束时同步读书成果到认知发现；钩子#11卡片质证回写；「阅读复习模式」消费 {书名}-题库.md（题库消费边）"
  - name: daily-buddy
    version: "3.54.0"
    note: "前置配套——读书笔记写入Obsidian知识池，由日记/月报消费端触发复习"
python_dependencies:
  - name: markitdown
    purpose: "Step 1 非MD格式文件→MD 格式归一化（scripts/fetch_source.py）"
    install: "pip install markitdown"
    fallback: "缺失时 .md/.markdown/.txt 直读降级（无需转换的源不被转换器阻塞）"
  - name: crawl4ai
    purpose: "Step 1 URL 抓取→MD（本地无头 Chromium，⛔不走云服务）"
    install: "pip install crawl4ai"
    fallback: "缺失时 URL 抓取不可用——脚本报错提示安装，改存本地文件再蒸"
author: 皮叔
source: self-built
upstream: [记忆共享中心]/技能配置/sucair/
modifiable: true
version: "4.17.0"
license: MIT
complies_with: 文件格式规范(⛔不写版本号·以源 frontmatter 为唯一真相源=#142)
normative_vocab: "RFC2119-equivalent (see 指令编写规范 §1.1)"
---

# 📖 读书助手 — AI替你读，系统逼你学

> **设计哲学**：AI替你读（5分钟精华+永久卡片+题库），系统逼你学（消费端由日记/Shall We Talk/月报触发）。
> **历史变更**：详见 `references/CHANGELOG.md`
> 🔴 本文件在读书助手 Skill 执行时优先级最高，context compression 不可覆盖
> 🔴 不是建议，是硬约束。不可跳过

---


## 🧭 指路牌（按节名指路·禁行号）

| 你要干什么 | 看哪节 |
|:--|:--|
| 开工先看不可跳过的硬约束 | `## ⚠️ 铁律声明` |
| 判断输出是否有据可查 | `## 📐 质量与证据声明` |
| 确认本 Skill 的输入/输出/行为/演化边界 | `## 四层契约` |
| 审计对抗性防御（11条全文在附件） | `## 🛡️ T5对抗性防御声明` |
| 看防错三法的执行位与验证法 | `## 🛡️ Poka-Yoke防误层（S级）` |
| 判断要不要二次确认 | `## 行动倾向` |
| 确认本 Skill 做哪三件事 | `## 功能定位` |
| 判断该不该触发 | `## 触发条件` |
| 查设计取舍的历史理由 | `## 📋 Alternatives Considered` |
| 开工第一步：跑熔断器并读执行本体 | `## 执行流程` |
| 查谁能读写知识池 | `## 知识池读写权限` |
| 查 L1-L4 状态由谁更新 | `## reading_status 四级` |
| 查绝对不能做的事 | `## 禁止行为（纯五级标注）` |
| 查上下游与互斥分工 | `## 与其他 Skill 的关系` |
| 查学术来源映射 | `## 来源与参考` |
| 查附件清单与加载时机 | `## references/ 目录索引` |
| 输出前最后核对呈现模板 | `## 📦 蒸馏输出模板` |

---
## ⚠️ 铁律声明

**✅DO — 本Skill是单线程读写引擎。只负责"读一本书→生成知识包→写入知识池"。不负责推送/提醒/复习/分析。** ⛔DO NOT自己主动弹出"该复习了"——原因是复习由日记驱动的Shall We Talk触发，本Skill不应抢占控制权。

> 注：「生成并落盘题库文件」属于"生成知识包→写入知识池"的生产职责（消费边由 Shall We Talk「阅读复习模式」读取），不属"复习/推送/提醒"——本Skill仍不抢控制权，只负责把可消费的题库文件交出去。

**✅DO — 永久卡片✅DO拆成独立原子文件。** ⛔DO NOT把整本书的内容塞进一个文件——原因是一个800行的文件你看不完也不会回看。一张卡片=一个概念，一页看完。

**✅DO — 如实标记阅读状态。** reading_status字段为四级（L1-L4），如实标记。⛔DO NOT粉饰——原因是实事求是是用户的铁律。

**指令质量要求详见下方「📐 质量与证据声明」段及 §四层契约。**

---

## 📐 质量与证据声明

**✅DO — 输出中的每条价值判断必须附带可验证的依据。** 禁止空泛评价（如"效果很好""非常有价值"）。无证据=无效判断。

**✅DO — 本Skill被触发后必须走完整流程，跳过任何步骤=回复不完整=必须回溯补全。**

---

## 四层契约

| 契约层 | 定义 |
|:---:|------|
| 输入契约 | 用户说"读这本书"/"蒸馏这篇文章" + **源**文件路径（书/文章/论文/推文串）或 URL → 启动 |
| 输出契约 | 知识包：精华 + 永久卡片 + 题库——**数量（卡片/精华字数/题库）由三明智涌现**（C1枚举→C2归并→C3验证），以 references/config.yaml 分档表为结构参考（⛔不硬编码上限） + 知识池索引更新 |
| 行为契约 | 只读书籍文件+只写Obsidian知识池+更新索引；行动倾向：default_to_action |
| 演化契约 | `01-读书笔记/` = legacy 停放区（存量旧笔记不动，新书不再写入）。新书全部产出写 `05-知识池/{书名}/` 书文件夹（精华+卡片平铺同夹·文件名保留书名前缀·以 config.yaml 为准；旧"去书名前缀"口径已废弃）。核心启发库渐进迁移 | 



## 🛡️ T5对抗性防御声明

> 十一项声明全文（不可绕过/权限边界/CoT反污染/语义不变性/间接注入/旧格式/多Skill冲突/Context溢出/工具隔离/循环调用/抗渐进侵蚀）见 `references/t5-defense-assessment.md#§T5对抗性防御声明`——执行时按需加载，截断必回源；外置只搬位置，条款效力不变。
## 🛡️ Poka-Yoke防误层（S级）

### 接触式防错（Contact Method）

- **锚点**：05-知识池实存条目（写卡前实体归一 G4 + category+tags 交集检索）——候选空则 ADD/非空则三选一
- **执行位**：Step 2.0 写卡前门禁（实体归一+交集检索）
- **可验证性**：dedup_recall.py 确定性召回（scripts/dedup_recall.py）；⛔静默 SKIP 禁止（三决策必须计入完成确认）

### 定值式防错（Fixed-Value Method）

- **锚点**：分档结构参考（references/config.yaml 分档表·⛔不硬编码数字上限；卡片数/精华字数/题库均由三明智涌现）+ 卡片正文≤600 字（config 永久卡片上限·**机检真源=note_validator.CARD_BODY_MAX 常量**，config.yaml 分档表为人类可读投影——改数两处同步·2026-09-01 清零批#8 真源反转；机检兜底：note_validator `check_body_length` 生成自检+lint 双生效）
- **执行位**：Step 3-4（精华字数/卡片数/每卡上限）
- **可验证性**：完整性锁三查（数字源两处对账：600 上限数字真源=note_validator.CARD_BODY_MAX 常量·机检执法位；references/config.yaml 分档表=人类可读结构投影——2026-09-01 清零批#8 真源反转口径，⛔不硬编码第三处）

### 步序式防错（Motion-Step Method）

- **锚点**：单线程引擎 Step1→2→3→4 强依赖（读→拆→写→确认），上步未完成不可执行下步
- **执行位**：四步链全程+完成确认
- **可验证性**：产出物锁（知识包三件套缺件=未完成）；⛔不抢消费端控制权（范围边界铁律·语义锚）

## 行动倾向

**default_to_action** —— 用户说"读这本书"→立即读取→生成知识包→写入。不需要二次确认。

---

## 功能定位

不是"生成一本漂亮的笔记"，是"把一本书拆成你能一口一口吃的知识颗粒"。做三件事：

1. **读取源**：完整读取书（PDF/EPUB/TXT）或文章/论文/推文串（MD/TXT/HTML/URL）等格式
2. **生成知识包**：5分钟精华 + 永久卡片 + 题库
3. **写入知识池**：Obsidian `05-知识池/` 目录

---

## 触发条件

### 管辖权重叠
| 重叠类型 | 处理规则 |
|:---------|:---------|
| 触发词重叠 | second-brain（已于 2026-08-07 归档·依 D4 拍板）的"摄入/把这篇文章加进知识库"触发词随归档废止，文章蒸馏归本 Skill 独占；与 good-good-study 的边界见 §与其他 Skill 的关系 |
| 功能重叠 | 与Shall We Talk无直接功能重叠（读书助手管知识输入，Shall We Talk管自我认知）；与每日伙伴联动→读书产出的"本周阅读"回写入日记 |
| 退出条件 | 知识包写入完成→自然退出。用户说"先记到这里"→简写后退出 |

### 应该触发

| 触发词 | 场景 |
|--------|------|
| "读这本书" / "蒸馏这本书" / "提炼这本书" / "帮我做读书笔记" / "帮我做笔记" / "读书助手"（直呼Skill名） | 用户提供书籍文件路径，请求生成知识包 |
| "拆解这本书" / "知识包" | 用户要求将书籍拆解为知识颗粒 |
| "这本书的精华" / "5分钟精华" | 用户请求书籍精华摘要 |
| "蒸馏这篇文章" / "提炼这篇文章" | 用户提供文章文件路径或 URL（source_type=article-long/article-short） |
| "把这篇做成卡片" / "蒸馏这个" | 用户提供任意源（文/论文/推文串），请求蒸馏成卡片 |
| "把这篇加进知识库" / "把这段归档" / "归档到知识库" | 原 second-brain 触发词（含"归档"变体）·归档后由本 Skill 承接 |

### 不应该触发

| 场景 | 原因 |
|------|------|
| 用户只是提到一本书但未要求处理 | ☑SHOULD等待用户明确指令再启动 |
| 用户要求写书评/读后感 | 书评是创作，不是知识拆解 |
| 用户要求复习已读内容 | 复习由Shall We Talk触发，本Skill不负责 |
| 没有源文件路径或 URL | MAY询问路径，但不应凭空启动 |

---

## 📋 Alternatives Considered

> 设计决策记录见 `references/CHANGELOG.md` v4.1.0 条目"设计决策记录"


## 执行流程

> 单线程四步链：Step 1 识别源类型+读取 → Step 2前置 C1穷举 → Step 2.0 去重合并门 → Step 2 生成知识包 → C3 批判三问 → Step 3 写入知识池 → Step 4 完成确认。
> **执行本体（含自检清单与文件产物模板）已逐字下沉 `references/flow-read.md`；主文件只留熔断器与路由。**

🔌 **强制 Read 熔断器（先于任何步骤）**：
1. `python3 scripts/flow_read_gate.py` 必须 exit 0；
2. 随后 Read `references/flow-read.md` **全文**再执行；
3. 任一失败 → 🔴 中止本流程并回报「flow-read.md 不合格」，⛔ 不凭记忆裸奔、⛔ 不自行补写该文件后继续（补写＝伪造产出物，同 triwich Step0 熔断器口径）。

| 阶段 | 产出 | 本体（flow-read.md） |
|:--|:--|:--|
| Step 1 识别源类型+读取 | 源内容 + source_type | `references/flow-read.md#§识别源类型` |
| Step 2 前置 C1 穷举 | C1 清单落盘 | `references/flow-read.md#§源卡片穷举` |
| Step 2.0 去重合并门 | ADD/MERGE/SKIP/CONFLICT | `references/flow-read.md#§去重合并门` |
| Step 2 生成知识包 | 精华+卡片+题库 | `references/flow-read.md#§生成知识包` |
| C3 批判三问 | 三问通过标记 | `references/flow-read.md#§批判三问` |
| Step 3 写入知识池 | 卡片落盘+INDEX | `references/flow-read.md#§写入知识池` |
| Step 4 完成确认 | 确认摘要 | `references/flow-read.md#§完成确认` |

---
## 知识池读写权限

| 操作 | 谁可以做 |
|------|:---:|
| 写入新卡片 | 只有读书助手 |
| 更新卡片reading_status | Shall We Talk触发时 |
| 读取知识池（匹配/分析） | 日记/Shall We Talk/月报/成就 |
| 读取知识池（灵感匹配） | 每日伙伴·灵感闪现模块 |

**读书助手不读自己的产出去做分析——分析归月报。**

---

## reading_status 四级

| 级别 | 状态 | 谁更新 | 含义 |
|:--:|------|:---:|------|
| L1 | `AI已提炼` | 读书助手（Step 4自动） | AI读完了，卡片在等你 |
| L2 | `你已阅读` | Shall We Talk（日记触发） | 你在日记写了读了这本书 |
| L3 | `已应用` | Shall We Talk（日记触发） | 日记感悟匹配到这张卡片 |
| L4 | `已内化` | Shall We Talk（对话确认） | 你能用自己的话讲了 |

---

## 禁止行为（纯五级标注）

本段不再使用枚举编号。每条为独立约束：

⛔DO NOT生成一个超长笔记文件——原因是旧模板已废除，你从来没看完过。✅DO生成独立原子卡片文件（数量由三明智涌现：C1枚举→C2归并→C3验证，书不设数字上下限），正文≤600 字（机检真源=note_validator.CARD_BODY_MAX·config.yaml 投影·改数两处同步）。

⛔DO NOT 凭空凑数/注水（每张卡须是 C1 枚举出的独立原子概念、100%基于原文）——防注水靠 C3 批判验证，不靠数字上限。✅DO 数量由三明智涌现（C1枚举→C2归并→C3验证），书不设数字上下限。

⛔DO NOT静默 SKIP/CONFLICT——原因是 SKIP/CONFLICT 不报告=用户无法知道哪些知识被判定重复或立场冲突，计数失真=去重门形同虚设。✅DO去重三决策（ADD/MERGE/SKIP；SPLIT 为 MERGE 对称按需触发）与 CONFLICT 立场决策（独立·非第4态）全部计入 Step 4 完成确认。

⛔DO NOT捏造原文内容——原因是提炼层必须100%基于原文（Fail-Closed安全哲学）。✅DO缺失数据标注"未找到"而非脑补。

⛔DO NOT用旧的 `reading_status="已读完"`——原因是已替换为四级状态（L1-L4）。✅DO新笔记用新格式，旧笔记不动。

⛔DO NOT读书助手读自己的产出去做分析——原因是分析归月报，职责分离。✅DO只写入、不读回分析。

---

## 与其他 Skill 的关系

| Skill | 关系 | 说明 |
|-------|------|------|
| Shall We Talk | 下游 | 日记写了"读了《X》"→Shall We Talk「阅读复习模式」自动触发；读知识池卡片(reading_status L1/L2)+`{书名}-题库.md`→抽due题→出题→判定→回写卡片frontmatter(reading_status升级·按读书卡片schema§6.2)+题库间隔参数(SM-2-lite)；#11卡片质证仅作深度对话中顺带的知识点确认 |
| 每日伙伴 | 下游 | 灵感闪现匹配扩展到知识池 |
| 月报 | 下游 | 阅读分析——北极星·质证升级数/引用率/品类分布/反图书馆指数（live 唯一分析消费端） |
| **good-good-study（好好学习）** | **互斥分工** | **"读具体一本书"归读书助手；"领域学习无书/给我学X的路径"归好好学习 B线（与 good-good-study SKILL.md 边界表述一致·⛔不锚版本号#142）。读书计划/书单/延展网络类需求以 good-good-study 侧声明为权威，本 Skill 不越界承接** |
| 认知边界探测协议 | 平行 | 15个阅读认知偏差角度 |

> **三库联邦关系备注（软引用）**：本 Skill 产出（知识池精华+卡片）是知识联邦的输入源之一，库角色与编号以《学习引擎/08-三库联邦设计.md》为准（不在本文写死——防设计演化后本段过期）。live 分析消费端仍为月报；08 工程化落地后概念层蒸馏自动接管本Skill产出（蒸馏方为独立进程，本Skill无需改动，与"不读回分析"铁律不冲突）。⛔现阶段不得宣称概念层已在消费本Skill产出。

---

## 来源与参考

> 学术来源映射表见 `references/academic-sources.md`（7条来源×贡献×可靠性）

---

> 本 Skill 是读书助手 · 五层记忆系统知识摄入层
> 设计者：皮叔 | 开源协议：MIT

## references/ 目录索引

| 文件 | 用途 | 加载时机 |
|------|------|:---:|
| `CHANGELOG.md` | 历史版本变更记录 | 查询时 |
| `platform-paths.md` | 平台路径共享模板（9 Skill 共用·2026-08-11 复审补入索引） | 跨 Skill 路径对齐时 |
| `config.yaml` | 路径配置+质量阈值+source_type分档表 | Step1启动时 |
| `dedup-merge-gate.md` | Step 2.0 去重合并门执行细则（实体归一/召回/MERGE规范） | Step2.0执行时 |
| `eval-set.md` | 评估测试用例集（36 条用例·应触发T1-T11/不应触发N1-N5/运行时R1-R20） | loop评估时 |
| `note-template.md` | ⚠️ 已废弃·旧长笔记模板（v3.0 重构后废除·仅历史存档·⛔不得用于生成） | 查询历史时（不用于生成） |
| `t5-defense-assessment.md` | T5攻击面5维度评估记录 + 11条声明全文 | T5审计时 |
| `flow-read.md` | 执行本体（Step1-4+自检清单·SKILL.md 逐字迁移件） | 每次执行前（熔断器放行后） |
| `academic-sources.md` | 学术来源与参考映射表（7条） | 设计溯源时 |
| scripts/note_validator.py | 合规「规则单源」：笔记/卡片 frontmatter 校验 + 卡片正文≤600字（check_body_length）+ 题库校验（validate_quizbank）+ 产物机检（lint）+ 条件必填（source_type 驱动）+ INDEX 一致性校验（--index-check） | 写入前自检/写后机检 |
| scripts/dedup_recall.py | Step 2.0 确定性召回：category+tags 交集检索（G4实体归一内置） | Step2.0写卡前 |
| scripts/assign_kb_no.py | kb_no 机器编号发号与台账同步（--allocate 领号 / --sync 补漏+刷账+对账） | Step2.2领号 / Step3写入后 |
| scripts/fetch_source.py | Step 1 格式归一化：URL抓取(crawl4ai本地)+文件转MD(markitdown)，⛔不走云服务 | Step1源为URL/非MD格式时 |
| scripts/flow_read_gate.py | 强制 Read 熔断器：flow-read.md 在位/够长/四锚齐，exit 1=禁止执行 | 每次执行前 |
| scripts/anchor_reach_check.py | 引用可达性：路径 + `path#§锚点`（通用件副本） | 施工末/发版 |
| scripts/ocr_scan.py | 扫描件 A 路：RapidOCR 双跑+结构闸；`--probe` 能力探测选路（A/A2/B·见 flow-read 0.1） | Step1 扫描件时 |
| scripts/ocr_vision.swift | 扫描件 A2 路：macOS 原生 Vision OCR 源码（swiftc 编译二进制调用·零第三方依赖） | A2 路执行时 |
| references/ocr-corrections.json | OCR 专名纠错表（只收已回原图确认条目） | 扫描件 OCR 时 |
| scripts/test_sucair.py | G2 自动回归载体：`cd scripts && python3 -m unittest test_sucair`（14 例） | scripts/references 任一改动后 |
| tests/ | 触发词正负例用例（trigger-positive.md / trigger-negative.md） | 触发判定验证时 |

> 类型专属 schema（`笔记schema.md` / `读书卡片schema.md`）位于 `[记忆共享中心]/记忆蓝图/03_开发规范/schemas/`，是笔记/卡片 frontmatter 的合规权威源（层3）。`scripts/note_validator.py` 的 `NOTE_FIELDS` / `CARD_FIELDS` 是机器真源，字段集与这两份 schema 一一对应；reading_status 值域 L1-L4 由 schema 约束（全 Skill 通用互操作），业务语义以本文件「reading_status 四级」表为准（2026-08-12 用户拍板统一：schema=What，Skill=What-it-means——schema 侧旧语义"未读/在读/精读"已清除）。读书卡片schema 当前版本为 v1.3.4（含立场扩展层·单态渐进模型 + 源泛化：source_type 分档 book/paper/article-long/article-short/thread）。**题库 schema 权威源已落地**：`记忆蓝图/03_开发规范/schemas/题库schema.md` v1.0.0。

> 本 Skill 是 **五层记忆系统 · 布洛陀版本 v1.0** 的一部分
> 设计者：皮叔 | 开源协议：MIT

## 📦 蒸馏输出模板

> 呈现合同（L2 在场律）：输出前最后读到，逐字填槽，⛔不另造格式。执行本体的步骤见 `references/flow-read.md`。

### 5分钟精华模板（Step 2.1 产出）

```markdown
---
title: 《书名》精华摘要
type: note
status: active
version: v1.0.0
date: YYYY-MM-DD          # 创建日（ISO），禁用 date_created
summary: 《书名》5分钟精华核心观点   # ≤40字
source: 输入PDF路径 或 生成器标识
author: 用户                # 笔记维护者（非书作者）
book: 《书名》
book_author: 作者         # 书作者，独立于 author
reading_status: L1        # L1=AI已提炼/L2=你已阅读/L3=已应用/L4=已内化（详见 `## reading_status 四级` 表）
template_type: A
complies_with: 笔记schema v1.0.0
---

## ⚔️ 核心争论/主要矛盾
[这本书核心张力或学术界/作者未关闭的问题——1-2句。例：「主要矛盾：涌现秩序是设计出来的还是进化出来的」。此字段站第一屏=入口灵魂（Adler：读任何书先找它在回答什么问题；库恩：反常处=信息熵最高处），也为后续立场升级提供认知钩子。]

## 📖 一句话
[这本书说的什么，≤30字]

## 🎯 3个核心观点
1. [观点1，≤100字]
2. [观点2，≤100字]
3. [观点3，≤100字]

## ⚡ 1个现在就用的行动
[读完这本书，明天就做的一件小事]

## 🗺️ 框架图
[垂直单列树（├──/└── 文件树风格）——全书逻辑结构。⛔DO NOT 用多列水平并排ASCII树——原因是中文字符占双宽，跨行水平对齐在不同字体/环境下必错位（多环境实测）；垂直树每行自包含、无跨行对齐需求，任何环境不乱]
```

### 完成确认模板（Step 4 产出）

```
📖 《书名》/《文章标题》已拆解（source_type: book/article-long/...）

├── 📖 5分钟精华：{涌现字数}字（结构完整=⚔️矛盾+🎯3核心观点+⚡1行动 即达标，无总字硬上限）
├── 🃏 {涌现张数}张永久卡片：已存入知识池
├── 🔀 去重：ADD n / MERGE m / SKIP k + CONFLICT c（各自显式计数·CONFLICT 为独立立场决策非去重第4态，⛔不静默）
├── ❓ 题库：已生成（默写 n / 应用 n / 逻辑链 n——实际题数必填，⛔DO NOT 写“由三明智涌现”代替具体数字——原因是题库“内部维护”不可验证，具体题数是唯一留痕；短文/推文串写"不出题（信息密度不足）"，⛔不留空）
└── 🔗 索引：已更新
```
