---
normative_vocab: "RFC2119-equivalent (see 指令编写规范 §1.1)"
---

# 来源与参考 — 唤醒记忆系统

> 本 Skill 的外部来源与发布依赖说明。

| 来源 | 可靠性 | 关键贡献 | 应用 |
|------|:---:|---------|------|
| **本Skill自身设计哲学** (2026-04-25) | 🟢 | 加载即校验、结构自锁、双模式路由 | 全篇 |
| **Skill架构规范 v6.2.2** | 🟢 | 四层契约+熔断器+T5对抗性+禁止行为 | 多轮合规迭代 |
| **IIT Gandhinagar论文** (2026) | 🟡 | 多步执行准确率随步骤数指数衰减 | 三步结构自锁 |
| **Anthropic Skills Complete Guide** | 🟡 | 渐进披露——SKILL.md自给自足+输出模板内嵌 | 输出格式示例 |
| **OWASP LLM Top 10** (2025) | 🟢 | 过度代理/敏感信息/提示泄露 | 安全声明 |

---

## 发布自包含依赖清单

> 依据：Skill架构规范 `pages/07-feedback-rules.md#§开放引用原则`（开放引用）+ 自包含 litmus + `skill_selfcontained_guard` 声明豁免机制。
> 性质：以下为**宿主系统层依赖与兄弟 Skill 脚本的声明登记**，各消费处原文不改写；换机或开源发布时按降级声明处理。

**作者侧发布工具链（健康探针，消费处 `self-healing.md §3.5`）**：`buluotuo-release-sync` 缺失 → 标 `N/A（发布者工具·未安装）`；`changelog_guard` 缺失 → 概览不加该行。均为合法终态非告警。

- `[记忆共享中心]/脚本中心/`
- `[记忆共享中心]/脚本中心/changelog_guard.sh`

**作者侧工具与兄弟 Skill 脚本（消费处 `dual-mode.md` 全量 1e 与自画像补跑）**：`restore-my-skills.sh` 失败 → 降级为报告失败信息不阻塞；`distill_containers.py` 失败 → 输出错误信息并建议手动检查，不阻塞。

- `[记忆共享中心]/技能配置/restore-my-skills.sh`
- `[记忆共享中心]/技能配置/daily-buddy/scripts/distill_containers.py`

**自动巡检宿主依赖（消费处 `patrol.md §3`）**：launchd 定时 + osascript 通知 + `~/buluotuo_bin/log/` 巡检日志。均为 macOS 系统能力与本机路径，非 macOS 端自动巡检不生效（不迁移，兼容性如实声明）；缺省时会话内巡检仍可用，不阻断主流程。
