# GGS 发布自包含依赖清单（release-deps）

> 本文件是 SKILL.md v1.1.18「📦 发布自包含依赖清单」的逐字迁移件（2026-10-23 架构革命）。
> 性质：宿主系统层依赖登记；换机/开源发布按降级声明处理。主件留 3 行指针。


## 📦 发布自包含依赖清单（2026-09-15·自包含体检 Loop 登记）

> 依据：Skill架构规范 §11.5 开放引用原则 + §11.6 自包含 litmus + `skill_selfcontained_guard` 声明豁免机制。
> 性质：以下为**宿主系统层依赖的声明登记**——各消费处原文不改写；换机或开源发布时按降级声明处理。

**宿主共享引擎——知识联邦引擎**（消费处 SKILL.md §④入库管道+§⑤回写收口、references/topic-selection.md 池2碰撞候选队列、references/collision-consumption.md 批量筛选+收口验证环；缺失→入库管道熔断降级"脚本缺失，卡片仅落盘不重建INDEX/不回写队列"，collision_candidates.json 缺失→池2降级为空仅走池1，不阻塞）：

- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/derive_reading_status.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/regen_ailib_index.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/sync_card_frontmatter.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/concept_projection.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/lint_collision_card.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/sync_collision_queue.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/scan_card_citations.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/（收口验证环脚本目录）
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/concept_coverage_stats.py
- [记忆共享中心]/脚本中心/知识联邦引擎/collision_candidates.json
- [记忆共享中心]/数字分身/scripts/doenglingz_drift_check_remind.py
- [记忆共享中心]/脚本中心/build_spotpack.py
- [记忆共享中心]/脚本中心/记忆蒸馏/confidence_calibration_audit.py
- [记忆共享中心]/脚本中心/知识联邦引擎/scripts/cross_type_collision_scan.py（消费处 references/topic-selection.md 池3）
- [记忆共享中心]/脚本中心/search_kb.py（消费处 ④.5 七闸表闸1·真源带 TRUTH_OF 头；开发工具/知识联邦引擎 下为派生旧版）
- [记忆共享中心]/成就系统/scripts/check_concept_achievement.py（消费处 §⑤ 收口 step3.5）
- [记忆共享中心]/数字分身/scripts/count_card_topic.py（消费处 分层终审·新领域机械计数）
- [记忆共享中心]/数字分身/scripts/job_probation_check.py（消费处 JOB-001/JOB-004 多账原子登记）
- [记忆共享中心]/数字分身/scripts/job_audit_check.py（消费处 初审↔台账双向对账·⛔不建第二套）
- [记忆共享中心]/数字分身/scripts/auto_pass_audit.py（消费处 分层终审事后抽查）
- [记忆共享中心]/数字分身/scripts/batch_auto_pass.py（消费处 ④ 存量卡批量自动通过判定 ✅DO 硬命令）
> 🔻 **降级声明（v1.1.8 真值校正）**：知识联邦引擎及其脚本已以端用户最小集随安装包分发（件数以包面实装为准·本机 20 件），口径真源见 collision-consumption.md §二 降级声明段（该文件内文实存节）。仅当包内与本机该引擎目录**实际缺失**时，相关步骤才**跳过·不阻塞**。⛔不得把「随包」写成「不携带」（2026-10-12 clock-loop R1 实证=六处与实盘互斥）。

**宿主共享守卫件——脚本中心/守卫（作者侧·未随包分发）**（消费处 run.sh「global body integrity」段 + scripts/orchestration_check.sh 编排结构闸；缺失→两处执行位显式「SKIP·不阻塞」降级语句·v1.2.10 收口——原版漏登记致装机/换机 run.sh 必断最后一步，PAT-084 悬空引用族预防；anchor_reach_check.py 为本 Skill 自足副本不受影响）：

- [记忆共享中心]/脚本中心/skill_body_integrity_guard.py
- [记忆共享中心]/脚本中心/orchestration_gate.py

> **作者侧·未随包分发**：以上两件为作者机构建/体检工具；端用户缺失时 run.sh / orchestration_check.sh 两处执行位显式 SKIP·不阻塞。
