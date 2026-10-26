---
name: eval-migration-map
description: SWT 36 用例 × 现位 × 校验 token 迁移对账（v1.7.0 架构革命）
normative_vocab: "RFC2119-equivalent (see 指令编写规范 §1.1)"
---

# SWT Eval 迁移对账（v1.7.0）

> 规范依据：Skill架构规范 v6.0.1 `pages/08-progressive-loading.md` 迁移纪律 #5——分家后必出「断言×现位×校验token」迁移表，token 在场性由 `scripts/eval_anchor_check.py` 常驻校验。⛔表说了没验=第二本账。

| 组 | 用例 | 现位 | 校验 token |
|:--|:--|:--|:--|
| 触发/不触发 | #1-#8 | 主件 §触发条件 | 深度对话 / 聊聊我 / 不应触发 |
| 数据源 | #9-#11 | `flow-talk.md §启动门禁与数据读取` + 主件 Step1 | 6 源 / ≥2 / 降级 |
| 追问深度 | #12-#16 | `flow-talk.md §追问引擎` | 维度N / 锚点 / 矛盾 |
| 声明/收获门 | #17-#19b | 主件 Step3（声明模板/四层表）+ `flow-talk.md` | 四行 / 收获门 / 觉察型 |
| 沉淀/退出 | #20-#28 | 主件 Step4 紧凑表 + `flow-sediment.md` | 六道锁 / 反馈段 / 奥德赛 |
| 标注 | #29-#31 | 主件 Step3 标注格式 + `flow-talk.md` | 第X问 / 深度X/4 |
| 按需加载 | #32 | 主件 references 索引 + 三片 flow gates | flow-talk / 指针 |
| 双轨 | #33-#36 | `flow-talk.md §双角色` | 双轨 / 3次 / 豁免 |

**边界**：组级对账 + token 常驻校验=机械面；语义一致仍人眼（规范同条）。⛔不宣称 token 齐=行为全对。

**与 eval_anchor_check.py CHECKS 的关系（2026-10-27 对齐注·评估台账#14）**：本表「校验 token」列=用例组关键词（语义层·人工对账用）；机械常驻校验的 token 全集=`scripts/eval_anchor_check.py` 的 CHECKS 26 项（锚点 token·如「启动门禁/双角色/锁一/[深度X/4·层名]」）。两列不同层：前者验「用例组覆盖哪些机制」，后者验「机制声明在现位文件中在场」——⛔混同读数。#37-46（2026-10-27 补）不在本表对账范围（本表只对账 v1.7.0 迁移的 36 旧例）。
