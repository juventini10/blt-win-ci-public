#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""panel_snapshot.py v1.1.0 — 愿景看板 v4.1（单页分区下钻·三主题可切换）

v1.1.0（2026-10-25·皮叔令「三个都可以，点一个切换一个模板」·三主题系统）：
  - 形态升级：单主题 → 三主题共存可切换——theme-a 细线终端（Linear 式·默认）/
    theme-b 硬件面板（Teenage Engineering 式·液晶屏/LED排灯/键阵/推子）/
    theme-c 印刷年报（Feltron 式·暖白纸底/朱红贯穿/巨号数字/行式数据条）
  - 架构：单 DOM + 单 LIVE_JS（id 零冲突·数据注入一份）+ 三套 CSS 变量主题；
    切换器在右上角（终端/面板/年报三钮）·localStorage('panel-theme') 记住选择·
    body 首行内联恢复脚本防主题闪烁；趋势图颜色改读 CSS 变量
    （--c-detected/--c-fixed/--c-immune/--chart-grid/--chart-axis），切主题自动重绘
  - 设计语言来源：huashu-design 风格库（web 11-Dark Editorial / app 01-Hardware Panel /
    info 01-Personal Annual Report·参照系 Linear/Teenage Engineering/Feltron）·
    三方向真实数据预览页见 可视化呈现/design-demos/·你裁定三套全要
  - 可读性底线落地（huashu-design 硬规则）：全站字号 ≥12px（v4 的 9.5-10px 微字全升档）
  - 配套：merge_collision_viz.py DASHBOARD_CSS 改引用面板 CSS 变量（--accent/--panel2 等）
    ——碰撞模块自身零主题逻辑，自动随面板主题换肤

v1.0.0（2026-10-25·皮叔令「升级成简约但高级」·v4 视觉重构·峰终保留）：
  - 形态：单页+分区+下钻——L0 心跳（闭环流唯一 hero + 四方向状态灯·10 秒读完）→
    L1 分区带（愿景进度 / 知识库 / 平台覆盖）→ L2 点击下钻（口径/公式/构念保真度/明细表
    全部 details 收纳）·零按钮零跳转（按钮工作台留给「面板上有动作」的那天）
  - 设计语言七规则落地：字号阶梯（hero 40px mono / 分区读数 20-24px / 标签 11px）；
    色彩三档制（中性灰阶承载 95% 面积 + 语义色只给状态 + 唯一强调色 --accent:#5b8cff）；
    闭环流四阶段装饰色退役（数字中性白·差异化交给位置与箭头）；渐变全退役（进度条纯色）；
    标题 emoji 全退役；「差值」pill 降级为 hero 脚注 chip（不可消信号不占主视图·宪法④）；
    tabular-nums 全站
  - 数据层零改动：take_snapshot/write_panel_data_js 一字未动（audit 对账 panel_data.js
    不受影响）；全部元素 id 保留（LIVE_JS 注入契约不破）；PANEL_DATA 失败红横幅保留；
    治理闸门红框保留（class alarm）；n·CI 仍随四方向卡数字同屏（显示契约不破）
  - 配套：merge_collision_viz.py 同批 v4 化（注入产物新设计语言 + mount 锚点
    id="collision-mount" + 幂等 remove）——两件须同批部署，单改一件=注入错位

v0.9.14（2026-10-25·Zwork·第 19 端 extra 腿补齐·皮叔令「像 WorkBuddy 一样如实反馈加号后面挂了多少个」）：
  - 病形：`extra_count()` 无 Zwork 分支 ⇒ 本端 extra 恒 None、面板「+N」空白——看着像
    "本端没挂任何东西"，实为本端承载形态不同（软约束端·无 hooks 配置面·童灵包 2026-10-12
    已真接入 v2.1.3）。同 Trae CN/MiniMax Code 补腿先例（v0.9.8/v0.9.12 族）。
  - 修法：Zwork extra = 安装回执机械计数——读
    `~/Library/Application Support/AutoClaw-official/doenglingz/installed_manifest.json`
    （install_receipt.py 产出·⛔禁手写副本＝机械源），verdict=ok 才计（防假绿）：
    installed capabilities + installed components + twin_core(core_built) ⇒ 2+5+1=+8。
    ⛔ 不入 12-Hook 分母口径（平台边界·0/12 如实）——本端 extra 语义=端承载件非守卫·
    渲染 tooltip 同步扩注「平台附加守卫/端承载件」。

v0.9.13（2026-10-25·退役件残留清理·共享分母名单归正）：
  - 病形：`extra_count()` 的共享分母名单（SHARED13·13 项）含 **已退役** 的 `reply_format_guard`
    （退役台账 `脚本中心/守卫/retired-hooks.json`：2026-08-13 你令退役·2026-08-26 完全删除·
    form=entity_deleted）⇒ 判据面含一个不存在的项 = 名单与退役台账脱钩（口径双本账）。
  - 实测：全端 6 个真实挂载面（workbuddy / qoder-cn / qoder / trae-cn / zcode / minimaxcode）
    对 `reply_format_guard` 命中数 **全为 0** ⇒ 清理**零数值影响**（各端 extra 读数不变）。
  - 修法：名单 13→12 项（= `load_live_rates` 的 HOOKS12 逐项对齐）·常量名 SHARED13→SHARED12
    （名称=实际条目数，消除「名单 13 / 分母 12」的数名不符）。
  - ⛔ 未改任何端的判定结论·未改 extra 公式·未改 SSOT 登记值。

v0.9.12（2026-10-25·MiniMax Code·第 21 端实盘腿补齐）：
  - 你质证「这里面显示你还没有登记，并且你缺了很多……你看一下像 Workbuddy 啊这些，
    它加号数字还有好多个 hook 或脚本呢，你的机制应该也是支持的」。
  - 病形①：`load_live_rates()` 的 PLATFORMS 无 MiniMax Code ⇒ 本端 num/den 一直吃 SSOT 人工登记值
    （配置改了面板不跟·同 Trae CN v0.9.11 族）。
  - 病形②：`extra_count()` 无 MiniMax Code 分支（PLATFORM_CFG 只认 settings.json，而本端唯一真实
    挂载面是 Plugin 包 hooks.json·本端无用户级 settings.json）⇒ extra 恒 None、「+N」空白。
  - 病形③：SSOT §二·七 校验覆盖段 🟢机械校验名单无 minimaxcode ⇒ 本端恒判「❔未登记」＝假红
    （同 Trae CN v1.8.15 族·根因＝登记做了但判据读不到）。
  - 修法：补 Plugin hooks.json 实盘腿（形态与 settings.json 同构·12 项清单与其他端同口径）
    + extra_count 实盘统计 + 校验覆盖段补 minimaxcode（与 platform_adaptation_check.check_minimaxcode 同源）。
  - ⛔ 母本 ~/.workbuddy/settings.json 不算本端挂载面（那是 WorkBuddy 运行时·本端 Plugin 不读它）。

v0.9.11（2026-10-25·Trae CN·本端接入自检腿补齐）：
  - 你质证「你的接入你自己都不检查呢？……为什么 WorkBuddy/Qoder 有那么多的加号，你没有？」
  - 病形①：`load_live_rates()` 的 PLATFORMS 无 Trae CN ⇒ 本端 num/den 一直吃 SSOT 人工登记值，
    配置改了面板不跟（他端是实盘直读，本端是"人记账"）。
  - 病形②：`extra_count()` 无 Trae CN 分支（PLATFORM_CFG 只认 settings.json，而本端官方挂载面
    是 ~/.trae-cn/hooks.json）⇒ extra 恒 None、面板「+N」空白——看着像"本端不需要附加守卫"，
    实为脚本漏配。
  - 修法：补 hooks.json 实盘腿（本端清单 12 项·crossend N/A 排除·rule_fragment/title_namer 计入，
    与 platform_adaptation_check.check_traecn 同口径）；extra 计入 NON_GUARD_CMDS 剔除探针。
  - 附带发现（未代改·ZCode 端待办）：本文件 v0.9.10 顶注声称「ZCode 移出 PATROL_EXTRA_SCRIPT·
    入 PLATFORM_CFG + SHARED13 补 title_namer」，但正文实盘仍是旧写法（PATROL 表内 ZCode、SHARED13
    无 title_namer）＝写侧声称未回指（铁律-016 ④）。按端归属留给 ZCode 端自查补齐。

v0.9.10（2026-10-25·ZCode·extra 假读数根治）：
  - 病形：ZCode 走 PATROL_EXTRA_SCRIPT 写死「zcode_config_guard.py 存在即 +1」（patrol 型记法遗留），
    实盘 36 挂载条目（共享 12 + 本端承载 24）只显示 +1——登记面≠实盘（与 SSOT ZCode 格 09-12
    口径未回写同轮根治）。
  - 修法：ZCode 移出 PATROL_EXTRA_SCRIPT·入 PLATFORM_CFG（~/.zcode/cli/config.json），
    命令收集兼容 hooks.events 联合形态（对齐 platform_adaptation_check.classify_entries）；
    SHARED13 补 `title_namer`（12 项分母第 12 项·各端适配器名均含该串——否则 zcode_title_namer
    被误计成附加守卫）。连带动效：QD/QCN 的 title_namer 适配器由附加改计共享（+N 各降 1·口径归 12 项分母）。

你的定案（2026-08-21 愿景仪表盘 §10·任务交接）：
  看板从"静态分数清单"重构为"峰终体验 + 闭环流"的活系统呈现。
  - 峰值 = 闭环流（最大区块·检测→修正→免疫→抗体库·趋势图优先喂系统1）
  - 终点 = 一句话总结（峰终收尾·你记住的那句）
  - 中间 = 少而真（四方向原生数据·不合成·分数全去：北极星0.8/自动化率100%是虚荣指标）
  -   刷新即最新：panel_data.js?v={时间戳} cache_bust + fswatch/Stop 钩子重渲染

v0.9.9（2026-10-25·Trae CN·端名去序号后缀配套）：
  - 皮叔令「（第 20 端）这种很难看后缀，把我全部都撤掉，留着名字就行了」⇒ SSOT 表头端名
    已瘦身为 `Trae CN 💡`／`Zwork 🧠`／`MiniMax Code 🐰`（v1.8.16）。
  - 本件两步归一（先剥括号段再剥非字母数字）**保留**：服务 `WorkBuddy AI（国际版）`
    这类真实括号后缀；端名不带序号后 key 直接命中覆盖段，无需再靠剥离代偿。

v0.9.8（2026-10-25·Trae CN·面板「未登记」假红根治）：
  - 病形：SSOT 平台列名带徽标/序号后缀（如「Trae CN 💡（第 20 端）」「Zwork 🧠（第 19 端）」），
    _parse_coverage_from_ssot 的 key 归一只去空格与连字符 → key 变成 "traecn💡（第20端）"，
    永远匹配不上校验覆盖段里的 "traecn" → 已登记机械校验的端在面板显示「❔ 未登记」= 假红。
  - 修法：key 归一改为两步——先剥括号段（re.sub(r"[（(][^）)]*[）)]", "")），
    再剥一切非字母数字（re.sub(r"[^a-z0-9]+", "", base.lower())）。
    只剥非字母数字不够：括号里的序号数字会残留 ⇒ "traecn20" 仍匹配不上 "traecn"；
    中文端（豆包办公等）走原「自核」兜底分支不受影响。
  - ⛔ 不改校验覆盖段判定规则、不改任何端的登记结论（只让已有登记被正确读到）。

v0.9.7（2026-09-07·皮叔批准归属约定·补全 v0.9.6 根治的最后一段）：
  - 归属约定入报警文案：自动补登报警文本新增"收到本报警的端须在变更日志补一条归属说明"
    + 可直接复制的 changelog_append.py 补登模板（--tool <你的端名>·--desc 注明变更原因与归属）——
    自动补登只证明"检测到变动"，归属说明才记录"谁改的、为什么"；约定放在报警文案=各端收到
    报警时的唯一必读处，不依赖翻文档。
  - 与 v0.9.6 关系：v0.9.6 解决"变动必须留痕"（检测即留痕·机械兜底）；v0.9.7 解决"留痕必须可归属"。

v0.9.6（2026-09-07·皮叔令"帮我根治"·CatPaw 第17端接入漏登实证）：
  - 治理闸门根治：check_registry_governance 检测到注册表指纹变动且变更日志无「平台注册表」治理记录时，
    自动调 changelog_append.py 补登一条"检测留痕"（--target 透传账本路径·隔离压测同路径）——
    检测即留痕，不依赖端自觉（09-06 CatPaw 批次改 SSOT §二·七 加列却漏登·面板 09-07 才喊）。
    本次仍返回报警（提示相关端可补充变更说明）；下次运行命中记录即更新登记消警。
    根因（第一性原理）：修改注册表的动作与留痕动作无强制绑定→事后检测只喊不记=闭环断血。

v0.9.5（2026-09-02·童灵上岗·皮叔问"免疫为何0/自动化为何降"根因裁定）：
  - ① 全自动化卡去「审计闭环率(returncode==0)」陈旧误标：显示值=auto_rate.actual=hook_auto 触发占比（自动触发调用/总调用），
    而 returncode==0 可靠性=100%(legacy) 被旧标签冒用 → 改诚实标签「hook_auto 触发占比·愿景①=机制自动运转不依赖人记得」+显 returncode 成功=100%
  - ① 降值根因说明：74.7% 较上周 87.8% 下滑=手动调用累积拉低占比（离线守卫默认 manual + 本次调试重跑脚本计入），非自动化退化；机制可靠性仍 100%
  - 免疫环节去"复发拦截"误导框：闭环流 stage 改「免疫 · 复发监测（本周）」+ src 注「0=无复发=抗体生效」；②卡注「免疫命中=历史复发被捕获次数(证明闭环在跑·非未实现)·有效抗体=已建防复发规则」

v0.9.4（2026-09-02·童灵上岗·皮叔令"彻彻底底的解决"）：
  - 闭环流 ≤0 分支去「无未核销差」伪断言：该分支此前暗示"已逐项核销=0"，实情是 detected/fixed 两源独立计数（DRIFT 行 vs 变更日志 WorkBuddy 行），
    从无共同追踪 ID、从未做逐项核销 → 文案改为中性算术描述「检出 ≤ 留痕 · 粗口径」（两源独立计数·非核销）
  - A3（真 per-item 核销）根因裁定：detected 来自 platform_adaptation_check.log [DRIFT] 行、fixed 来自变更日志 WorkBuddy 行，二者无事件级关联键；
    要真核销须重构 checker 日志（每条 DRIFT 发唯一 ID）+ 修正规程（修复须引用该 ID）——属新建可验证基建，非本轮可得，且半吊子重建会造新伪信号
    → 童灵裁决：A3 当前架构不可行，A+B 即终态。差值只作「检出−留痕·粗口径·非核销」真实算术差，绝不作「积压/未闭合」解释

v0.9.3（2026-09-02·童灵上岗·皮叔令"只要符合愿景的最优解"）：
  - 免疫环节去粉饰：闭环流 immune 恒 0 经核为真实（免疫复发记录 26 条命中全落在 08-20~08-25，本周窗口内确无一命中），
    但原 summary「免疫拦截复发 0 次——调节回路在跑」= 拿 0 证成"在跑"·编造结论
    → 改条件化：imm>0 说"拦截复发 N 次"；imm==0 说"免疫本周无触发（末次 YYYY-MM-DD）"，把真实静默时长显出来（可观测）
  - 口径歧义根治：闭环流 immune 标注「（本周）」、四方向②免疫命中标注「（累计）」
    ——26(累计) vs 0(本周) 不再像矛盾读数；引擎侧增 immune_total/immune_last_date（累计口径·不受窗口限制）

v0.9.2（2026-09-02·皮叔令"面板只能有真实有效的数据"）：
  - 闭环流 pill 去「有积压信号」伪断言：差值=detected−fixed 是两不同源计数器的粗口径差（非逐项核销），
    「积压」是假解释 → 保留真实差值数字，改中性灰字「粗口径·非核销」（红 warn→neutral），不编造积压结论（立场卡#S602 看板数字须绑实录）
  - 内联 PANEL_DATA 进 HTML 单文件：去掉外部 panel_data.js + cache_bust，render 时直内联 window.PANEL_DATA
    → 根治「HTML 的 ?v 与 data 不同步→浏览器用旧缓存→你看到过期数」（原你见 10 实际 20）· 打开即最新

v0.8.0（2026-08-23·DSH 三明智 L1 评审整改·皮叔令"做到100分"）：
  - 一句话总结去因果包装："修复N个"→"留痕变更N条"（fixed 源=变更日志全量行，非检出项逐项核销）
    积压 pill 改"差值"语义+悬停标注粗口径——根治 max(0,det-fix)=0 的假阴性闭环宣告
  - ①面孔统一(A v2)：四方向卡「审计闭环 X% · 覆盖 N/M」与 OKR 区同源同读数·覆盖不并入目标线
    （原"自动检测20·免疫拦截14"与冻结口径 returncode==0 占比脱节=三面孔不可复算）
  - ④窗口标注+证据封顶：卡面同显本月/本季累计双窗口；state=过渡时 evidence 机械封顶🟡
    （代理计数不配🟢——记录量≠预测力，防虚荣温床）
  - 零外链化：移除 chart.js/fonts CDN，内联 SVG 趋势图（原生 <title> 悬停读数）——断网可渲染，
    全自动化不依赖外部服务；今日进行中数据不入图（防零值断崖）
  - 平台表列分离：「核验方式」独立文本列（机械/自核/自治），色通道只留给覆盖度——三色混义根治
  - 维护行单轴化：环节Top 与总量显式标注不同轴（原 58+33=91 与 32+25+23+15=95 同行无法对账）
  - PANEL_DATA 加载失败显式横幅（原静默回退快照值=违反"宁可少不要假"）
  - 新增价值层占位卡（北极星产出轴·待量化明示——S451 投资回收轴入口，不装假指标）
  - 配套：SSOT 方案文档 §十二 治理记录回写 + okr_quarter.json 注记去易变数值（注记派生化规则）

v0.7.5（2026-08-22·Hermes 平台专属守卫漏标 +1 修正）：
  - PATROL_EXTRA_SCRIPT 增 Hermes 项（hermes_read_evidence_guard.py·文件存在即 +1）
    ——根因：Hermes 走插件型（无 hook 命令列表可解析），extra_count 落 None → 看板 Hermes 专属守卫漏标 null
    ——但 Hermes 有真实专属守卫（hermes_read_evidence_guard.py·route-audit-hook _READ_EVIDENCE_SCRIPT 实挂）
    →改按"专属守卫脚本文件存在判真"计入，与 AutoClaw/LobsterAI/ZCode patrol 型记法一致
  - mark 三级（🟢机械/🟡自核/🔴需自治核对·解析自 SSOT §二·七 校验覆盖段）保持不变——该语义=校验登记状态，
    接入完备度已由 num/den 独立呈现，色块与数字不混
  - 验证：Hermes extra null→1·Trae Work/其他端不变·exit 0

v0.7（2026-08-22·你点名"季度目标板块漏看"·补上真实空缺·任务交接§五-B）：
  - 新增「🎯 季度 OKR 目标对照层」板块：本季目标线 vs 实际进度·每方向进度条
    （目标≥/当前/完成度+证据档位色·达标🟢/接近🟡≥70%/落后🔴）
  - 目标值←okr_quarter.json（SSOT·自定义层/待完成工作/okr_quarter.json）；当前值←evolution_deviation 机械映射
    （auto=auto_rate.actual / evo=autonomous_evolution.actual / knows=本季 by_month 累计 / better=待量化不上假指标）
  - 剩余天数=end−today 机械算；JS 动态注入（改 okr_quarter.json→重跑→刷新即变·cache_bust 保留）

v0.7.1（2026-08-22·结构性少定义定版落地·网页端同步）：
  - OKR evidence 改为机械判定（current vs target·达标🟢/接近🟡≥70%/落后🔴）·不照抄 okr_quarter.json 静态字段（防过渡冒充定案）
  - 四方向卡③改为「本季进化事件 N · 净采纳率 X%」新口径（旧"本周进化事件69"口径错·与OKR区背离）
  - 四方向卡 badge 与 OKR 区强一致（JS 读 four_dir.state + okr.evidence 更新徽标）+ 状态行「定案/过渡」可视
  - okr_quarter.json 删除死字段 evidence（机械判定接管·单一真相源）

v0.7.4（2026-08-22·诚实降档根治"自动化105%"与"平台缺N"同页打脸）：
  - OKR「全自动化」当前值 = min(审计闭环率 auto_rate.actual, 平台接入完备度)
    （完备度=已接满额且机械核验被审平台占比·⛔任一平台未满额/未机械核验→auto 卡自然降档）
    ——根治 auto_rate(returncode==0 占比 100%)与 Qoder Desktop/Hermes/Trae Work 缺额自相矛盾
  - auto 降档时保留诚实 note（不被 evolution json 的"审计闭环率"note 覆盖）
  - 平台接入标题改「已登记 N 端（🟢机械核验 M）」·⚠️不再用"已核验 N/N"冒充全机械
  - Trae Work 自签 🟢→🟡「自核签名·非机械核验（待补追）」（诚实区分 8 机械 + 1 自签）
  - LobsterAI 升机械校验第 8 端（--src lobsterai·读 openclaw.json/patrol/state-hooks 三源）
    ——推翻"运行时不可见"旧判定·运行时配置在 ~/Library/Application Support/LobsterAI/ 完全可读

数据源（只上线有数据源的指标·宁可少一个不要假指标）：
  closed_loop  ← evolution_deviation v0.3（检测DRIFT/修正WorkBuddy行/免疫命中/抗体🛡+7日趋势）
  四方向       ← evolution_deviation directions（原生数+证据档位🟢🟡🔴）
  维护成本     ← 环节维护台账.py（git log 按环节统计提交数/周·免人工免自评）
  平台接入率   ← 各端 settings.json 实盘直读 + SSOT 兜底
  季度 OKR     ← okr_quarter.json（目标 SSOT·本季框定）+ evolution_deviation（当前值机械映射）
"""
# Win console UTF-8 guard (auto by build chain · V9)
try:
    import sys as _v9sys; _v9sys.stdout.reconfigure(encoding="utf-8"); _v9sys.stderr.reconfigure(encoding="utf-8"); _v9sys.stdin.reconfigure(encoding="utf-8")
except Exception: pass
import sys as _sys, os as _os; _SCROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))); _SCROOT in _sys.path or _sys.path.insert(1, _SCROOT)  # sc-rootfix-20261014 域搬补路
import os, json, glob, re, sys
from datetime import datetime

MC = os.path.expanduser("[记忆共享中心]")
AILIB_DIR = os.path.expanduser("~/[日记仓库]/2-知识库/09-AI学习库")  # 2026-10-13 C''波次2迁移后路径同步
SYSLOG = os.path.join(MC, "开发工具/logs/runtime")
TS_PATH = os.path.join(SYSLOG, "panel_timeseries.jsonl")
LIVE_HTML = os.path.join(MC, "可视化呈现/panel_live.html")
OKR_PATH = os.path.join(MC, "自定义层/待完成工作/okr_quarter.json")   # 季度目标 SSOT（详见愿景看板v3任务交接§五-B）

def latest_json(prefix):
    try:
        fs = sorted(glob.glob(os.path.join(SYSLOG, prefix + "_*.json")))
        return fs[-1] if fs else None
    except Exception:
        return None

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def check_registry_governance(platform_names, changelog_path=None, state_path=None):
    """A v2 治理闸门(机械化·S257 检测不得靠人纪律)：平台注册表变动 ↔ 变更日志治理记录 机械对账。
    返回 None=通过；返回 str=报警文案（主流程打印+注入OKR区红框）。
    对账规则：指纹变动时，变更日志.md 中须存在含「平台注册表」且日期≥上次登记日的行。
    v0.9.6 根治：无治理记录时自动补登"检测留痕"（走 changelog_append.py 唯一合法写入口·
    --target 透传账本路径=隔离压测同路径）——检测即留痕，不依赖端自觉；本次仍返回报警
    提示相关端可补充变更说明，下次运行命中记录即更新登记消警。"""
    import hashlib
    try:
        if changelog_path is None:
            changelog_path = os.path.join(MC, "变更日志.md")
        if state_path is None:
            state_path = os.path.join(MC, "可视化呈现", ".registry_state.json")
        fp = hashlib.sha1("|".join(sorted(platform_names or [])).encode("utf-8")).hexdigest()[:12]
        today = datetime.now().strftime("%Y-%m-%d")
        state = load_json(state_path) or {}
        if not state.get("fp"):
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump({"fp": fp, "since": today}, f, ensure_ascii=False)
            return None
        if state["fp"] == fp:
            return None
        old_fp = state.get("fp", "?")
        hit = False
        try:
            with open(changelog_path, encoding="utf-8") as f:
                for line in f:
                    if "平台注册表" in line and line.strip().startswith("|"):
                        d = line.strip().split("|")[1].strip()
                        if d >= state.get("since", ""):
                            hit = True
                            break
        except Exception:
            hit = False
        if hit:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump({"fp": fp, "since": today}, f, ensure_ascii=False)
            return None
        # v0.9.6 根治：无治理记录 → 自动补登"检测留痕"（不依赖端自觉）
        auto = False
        try:
            import subprocess
            append_py = os.path.join(MC, "脚本中心", "守卫", "changelog_append.py")
            desc = ("平台注册表变动检测留痕（fp {}→{}·{}平台）——panel_snapshot 治理闸门自动补登·"
                    "相关端可另补变更说明或回滚".format(old_fp, fp, len(platform_names or [])))
            r = subprocess.run(
                [sys.executable, append_py, "--tool", "panel_snapshot治理闸门",
                 "--file", "平台注册表", "--version", "—", "--desc", desc,
                 "--target", changelog_path],
                capture_output=True, timeout=60)
            auto = (r.returncode == 0)
        except Exception:
            auto = False
        if auto:
            return ("平台注册表已变动(原登记 {}·fp {}→{})——治理闸门已自动补登检测留痕。\n"
                    "归属约定(2026-09-07 你批准·所有端适用)：收到本报警的端须在变更日志补一条"
                    "归属说明，模板：\npython3 [记忆共享中心]/脚本中心/changelog_append.py "
                    "--tool \"<你的端名>\" --file \"平台注册表（SSOT §二·七）\" "
                    "--version \"<SSOT版本>\" --desc \"归属说明：<变更原因>\"\n"
                    "或回滚注册表改动".format(state.get("since", "?"), old_fp, fp))
        return ("平台注册表已变动(原登记 {}) 但变更日志无对应治理记录——"
                "请用 changelog_append.py 追加一行(--file 含「平台注册表」)，或回滚注册表改动".format(state.get("since", "?")))
    except Exception as e:
        return "治理闸门自身异常(不阻塞面板)：{}".format(e)

def load_kanban_rates():
    """从 SSOT（01-脚本架构设计通用规范.md §二·七 接入率行）机械解析各端接入率。
    根治手敲漂移：SSOT 改一处，面板自动对齐（铁律016·查实盘不查看板）。"""
    path = os.path.join(MC, "记忆蓝图/04_系统文件设计/布洛陀脚本架构设计哲学/04-跨端接入指南.md")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print("[panel_snapshot][WARN] 读取 SSOT 失败: {}".format(e), file=sys.stderr)
        return None
    def _plain(s):
        # 匹配前剥 markdown 装饰：文档给人加粗，不该把机器锚点震断
        # （2026-09-26 实证：SSOT 那行被写成「接入率（**分母=11」→ 字面锚点失配
        #   → 回退手敲兜底值 → 兜底是裸 int → 下游按 (num,den) 解包直接崩）
        return re.sub(r"[*_`]+", "", s)
    header = rate_line = None
    # 只认表格行，且必须在其上方 40 行内找到列头——否则 frontmatter 摘要里
    # 恰好同时含"接入率/分母"的散文行会被误当锚点（2026-09-26 改宽松匹配时实测踩中）
    # 2026-10-13 二次根治（Qoder CN）：仅"行内含字样"判据不够——2026-10-04 复核新增的
    # 签名行（行内含"接入率重估…分母12项"字样）抢中锚点且格子数 17≠表头 16，整行列错位
    # → 10 端接入率全变"未解析"、ZCode 显示从 Hermes 签名错抢的假 11/12。
    # 收紧判据：首格必须以"接入率"开头（真行首格=「接入率（分母=…」），签名/散文行进不来。
    for i, line in enumerate(lines):
        if not _plain(line).lstrip().startswith("|"):
            continue
        _first_cell = _plain(line).strip().strip("|").split("|")[0].strip()
        if not _first_cell.startswith("接入率"):
            continue
        cand = None
        for j in range(i - 1, max(-1, i - 40), -1):
            if _plain(lines[j]).lstrip().startswith("|") and "Hook 脚本" in _plain(lines[j]):
                cand = lines[j]
                break
        if cand is None:
            continue  # 这行不是那张表的接入率行，继续往下找
        rate_line, header = line, cand
        break
    if not rate_line or not header:
        print("[panel_snapshot][WARN] SSOT 未找到接入率行，回退手敲值", file=sys.stderr)
        return None
    def cells(s):
        return [c.replace("**", "").strip() for c in s.strip().strip("|").split("|")]
    platforms = cells(header)[1:]
    raw_vals = cells(rate_line)[1:]
    out = {}
    for name, raw in zip(platforms, raw_vals):
        m = re.search(r"(\d+)/(\d+)", raw)
        if m:
            out[name] = (int(m.group(1)), int(m.group(2)))
        else:
            out[name] = None
    return out

def parse_kanban_rates():
    """各端接入率——直接派生自 SSOT（见 load_kanban_rates）。不再手敲。"""
    rates = load_kanban_rates()
    if rates:
        return rates
    # 兜底值⛔不得携带具体数字：手敲数字=漂移源（原注释自陈"已过时"），
    # 且其裸 int 形态违反 {平台:(num,den)} 契约。降级=如实标不可判(None)。
    print("[panel_snapshot][WARN] SSOT 接入率锚点未命中→各端接入率标为「不可判」"
          "（不回填手敲值）", file=sys.stderr)
    return {}

def _parse_coverage_from_ssot():
    """从 SSOT §二·七 校验覆盖段自动解析 🟢/🔴 标记（不硬编码）。
    返回 {平台名: (标记, 说明)}。
    """
    out = {}
    ssot_path = os.path.join(MC, "记忆蓝图/04_系统文件设计/布洛陀脚本架构设计哲学/04-跨端接入指南.md")
    try:
        with open(ssot_path, encoding="utf-8") as f:
            txt = f.read()
    except Exception:
        return out
    # 找校验覆盖段：🟢机械校验=xxx·🔴需自治核对=xxx
    m = re.search(r"🟢机械校验=([^·]+)", txt)
    green_raw = m.group(1) if m else ""
    m = re.search(r"🔴需自治核对=([^·]+)", txt)
    red_raw = m.group(1) if m else ""
    # 清洗：去 bold 标记、按 / 分割、每段取开头英文平台名（去掉后续中文/括号内容）
    def clean(s):
        s = re.sub(r"\*\*", "", s)
        out = []
        for part in s.split("/"):
            part = part.strip()
            if not part:
                continue
            # 取开头连续的英文字母/数字（平台名），遇到中文/括号/空格停止
            m = re.match(r"^[a-zA-Z0-9\-]+", part)
            if m:
                out.append(m.group(0).lower().replace(" ", "").replace("-", ""))
        return out
    green_names = clean(green_raw)
    red_names = clean(red_raw)
    # 别名映射：SSOT 校验覆盖段中的特殊标识 → 平台名 key（lower+去空格）
    # 例：dsh → deepseekharness（DeepSeek Harness）
    alias_map = {"dsh": "deepseekharness", "workbuddyai": "workbuddyai（国际版）"}
    green_set = set(green_names)
    red_set = set(red_names)
    for alias, mapped in alias_map.items():
        if alias in green_set:
            green_set.add(mapped)
        if alias in red_set:
            red_set.add(mapped)
    # 从 SSOT 表头获取平台名
    rates = load_kanban_rates() or {}
    for name in rates:
        # v0.9.8 端名归一：先剥括号段（（第 20 端）/（国际版）），再剥一切非字母数字
        # （emoji/中文）。少了第一步，「Trae CN 💡（第 20 端）」会因序号里的数字残留
        # 变成 "traecn20" ⇒ 恒匹配不上覆盖段的 "traecn" = 假「未登记」
        base = re.sub(r"[（(][^）)]*[）)]", "", name)
        key = re.sub(r"[^a-z0-9]+", "", base.lower())
        if key in green_set:
            out[name] = ("🟢", "机械校验 · 登记自 SSOT §二·七")
        elif key in red_set:
            out[name] = ("🔴", "需自治核对 · 登记自 SSOT §二·七")
        # fallback: SSOT 表格中 "平台名 自核" 也视为已登记（但非机械核验→🟡 诚实区分）
        elif re.search(re.escape(name) + r"\s*自核", txt):
            out[name] = ("🟡", "自核签名 · 非机械核验（待补追）· 登记自 SSOT §二·七")
    return out

def load_live_rates():
    """实盘接入率：直接读各端 settings.json 算 12-Hook N/M。
    跳过"人更新 SSOT 文档"环节——配置一改，面板刷新即最新（愿景: 全自动化·减少人工）。
    2026-10-23 口径根治（面板与 platform_adaptation_check.py 打架）：
      · 分母统一 12（2026-10-09 title_namer 族转正 +1）——旧 11 项清单造成
        WorkBuddy 假缺 3（8/11 vs 核验器 12/12）、Qoder CN 假满额（11/11 vs 11/12）、
        同表 11/12 分母混用→"缺 N"不可横向比；
      · title_namer 族按各端适配器名识别（session_title_namer / wbai_title_namer / title_namer）；
      · WorkBuddy 端 UPS 已收敛为 ups_aggregator 单出口，四件作为聚合器内部 provider
        （settings.json 顶层无独立挂载）→ 认聚合器承载，对齐核验器 1411 行同口径；
      · Hermes 退出实盘直读：插件级颗粒度无法逐钩核验（旧逻辑 7/11 与 SSOT 11/11 恒冲突
        = 假红）→ 返回 None 由 SSOT 登记值兜底（同文件顶部设计声明"其余平台回退 SSOT"）。
    2026-10-25 补齐 Trae CN 实盘腿（你质证"你的接入你自己都不检查"）：
      · 读 ~/.trae-cn/hooks.json（官方全局挂载面·核验器 platform_adaptation_check.check_traecn 同源）；
      · 清单按本端适用口径：crossend_guard N/A（合并单端·无他端共居）排除，
        rule_fragment_inject + traecode_title_namer 计入 ⇒ 分母 12，不再吃 SSOT 人工登记值。
    """
    HOOKS12 = [
        ("crossend_guard", ("crossend_guard",)),
        ("route_inject_prompt", ("route_inject_prompt",)),
        ("route_miss_feeder", ("route_miss_feeder",)),
        ("kb_inject_prompt", ("kb_inject_prompt",)),
        ("route_unknown_unknown", ("route_unknown_unknown",)),
        ("audit_search_kb", ("audit_search_kb",)),
        ("route_audit", ("route_audit",)),
        ("route_guard_audit", ("route_guard_audit",)),
        ("feedback_detect", ("feedback_detect",)),
        ("rule_three_layer_guard", ("rule_three_layer_guard",)),
        ("card_id_guard", ("card_id_guard",)),
        ("title_namer", ("session_title_namer", "wbai_title_namer", "title_namer")),
    ]
    PLATFORMS = [
        ("Qoder Desktop", os.path.expanduser("~/.qoder/settings.json")),
        ("Qoder CN", os.path.expanduser("~/.qoder-cn/settings.json")),
        ("WorkBuddy", os.path.expanduser("~/.workbuddy/settings.json")),
        ("WorkBuddy AI（国际版）", os.path.expanduser("~/.workbuddy-ai/settings.json")),
        # 2026-10-25 v0.9.12：MiniMax Code（第 21 端）——本端无用户级 settings.json，
        # 唯一真实挂载面 = Plugin 包 hooks.json（形态与 settings.json 同构：hooks.<Event>.<group>.hooks[]）
        # ⇒ 直接进 PLATFORMS 实盘腿，12 项清单与其他端同口径（title_namer 适配器名含该串）。
        ("MiniMax Code 🐰", os.path.expanduser("~/.minimax/plugins/bulutuo-guards/hooks/hooks.json")),
    ]
    # Trae CN 本端清单（2026-10-25）：crossend N/A + rule_fragment/title_namer 计入
    TRAECN_HOOKS12 = [
        ("route_inject_prompt", ("route_inject_prompt",)),
        ("route_miss_feeder", ("route_miss_feeder",)),
        ("kb_inject_prompt", ("kb_inject_prompt",)),
        ("route_unknown_unknown", ("route_unknown_unknown",)),
        ("audit_search_kb", ("audit_search_kb",)),
        ("route_audit", ("route_audit",)),
        ("route_guard_audit", ("route_guard_audit",)),
        ("feedback_detect", ("feedback_detect",)),
        ("rule_three_layer_guard", ("rule_three_layer_guard",)),
        ("card_id_guard", ("card_id_guard",)),
        ("rule_fragment_inject", ("rule_fragment_inject",)),
        ("title_namer", ("traecode_title_namer", "session_title_namer", "title_namer")),
    ]
    out = {}
    for name, cfg in PLATFORMS:
        try:
            with open(cfg, encoding="utf-8") as f:
                d = json.load(f)
            # 2026-10-23 口径根治②：区分挂载形态，对齐 platform_adaptation_check.classify_entries——
            # 扁平形态（事件数组条目直接带 command·无 hooks 包裹）= 实测不执行（Qoder CN 9 条死形态
            # 前后回执对比），旧逻辑一律计入分子 → Qoder Desktop 假 11/12（实 7/12·4 条死形态）。
            cmds = []
            hooks_root = d.get("hooks", {})
            for evt in ("SessionStart", "UserPromptSubmit", "Stop"):
                evt_entries = list(hooks_root.get(evt, [])) + \
                    list(hooks_root.get("events", {}).get(evt, []))
                for it in evt_entries:
                    if "hooks" in it:
                        for hh in it["hooks"]:
                            cmds.append(hh.get("command", ""))
                    # 扁平 dead 形态不计入（无 else 分支即丢弃）
            mounted = set(k for k, pats in HOOKS12
                          if any(p in c for p in pats for c in cmds))
            # WorkBuddy 聚合器承载（对齐 platform_adaptation_check.py 同口径）
            if name == "WorkBuddy" and any("ups_aggregator.py" in c for c in cmds):
                mounted |= {"route_inject_prompt", "route_miss_feeder",
                            "kb_inject_prompt", "title_namer"}
            out[name] = (len(mounted), len(HOOKS12))
        except Exception:
            out[name] = None
    out["Hermes"] = None   # 插件级不可逐钩核验 → SSOT 登记值兜底
    # Trae CN 实盘腿（2026-10-25）：读官方全局 hooks.json，本端清单 12 项
    try:
        with open(os.path.expanduser("~/.trae-cn/hooks.json"), encoding="utf-8") as f:
            d = json.load(f)
        cmds = []
        hooks_root = d.get("hooks", {})
        for evt in ("SessionStart", "UserPromptSubmit", "Stop"):
            for it in hooks_root.get(evt, []):
                if "hooks" in it:
                    for hh in it["hooks"]:
                        cmds.append(hh.get("command", ""))
                elif "command" in it:
                    cmds.append(it["command"])
        mounted = set(k for k, pats in TRAECN_HOOKS12
                      if any(p in c for p in pats for c in cmds))
        out["Trae CN 💡"] = (len(mounted), len(TRAECN_HOOKS12))
    except Exception:
        out["Trae CN 💡"] = None
    return out

def load_okr():
    try:
        with open(OKR_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def compute_okr(platform_rates=None):
    """季度 OKR 目标对照层：读 okr_quarter.json（目标/本季框定）+ evolution_deviation（当前值机械映射）。
    铁律：目标值来自 JSON·当前值来自脚本输出·剩余天数=end−today 机械算——三处均不硬编码、不手填。
    platform_rates：{平台名:(num,den)} 或 SSOT 🟢/🔴 标注——auto 当前值据此做诚实降级
    （⛔禁止"审计闭环率 105%"与"平台接入缺 5"同页打脸·2026-08-22 你点名根治）。"""
    okr = load_okr()
    if not okr:
        return None
    # v0.9.8 季度机械轮转（2026-10-07 野根根治轮·Q3 已越界 7 天面板仍挂"剩余 -8 天"）：
    # SSOT 自带 derive 规则「当前季度由 today 的月份机械推导·不手填」——顶层 quarter/start/end
    # 在此按 today 现场推导覆盖手填残值；目标值(target)不动·不触价值层。
    try:
        import calendar as _cal
        _now = datetime.now()
        _qn = (_now.month - 1) // 3 + 1
        _m1 = _qn * 3
        okr["quarter"] = "%d-Q%d" % (_now.year, _qn)
        okr["start"] = "%d-%02d-01" % (_now.year, _qn * 3 - 2)
        okr["end"] = "%d-%02d-%02d" % (_now.year, _m1, _cal.monthrange(_now.year, _m1)[1])
    except Exception:
        pass
    dirs = (load_json(latest_json("evolution_deviation")) or {}).get("directions", {})
    today = datetime.now()
    try:
        end = datetime.strptime(okr["end"], "%Y-%m-%d")
        remaining = (end - today).days
    except Exception:
        remaining = None
    qstart, qend = okr.get("start")[:7], okr.get("end")[:7]  # "2026-07-01"→"2026-07"
    by_month = (dirs.get("knows_user_better", {}) or {}).get("by_month", {}) or {}
    def quarter_sum(bm):
        if not qstart or not qend:
            return None
        lo, hi = (qstart, qend) if qstart <= qend else (qend, qstart)
        return sum(v for k, v in (bm or {}).items() if lo <= k <= hi)

    rows = []
    for obj in okr.get("objectives", []):
        d = obj.get("dir")
        unit = obj.get("unit", "count")
        target = obj.get("target")
        current = None
        note = ""
        extra = {}  # v0.8.0：方向附加读数（仅 auto 使用·每轮重置防残留）
        if d == "auto":
            current = dirs.get("auto_rate", {}).get("actual")
            # 治理史注记：8/22 曾以 min(闭环率,完备度) 防打脸；2026-08-23 L3双Agent裁定 min() 焊死正交两轴
            # 且目标线压复合值可被分母游戏劫持 → A v2 双轴分离（覆盖为独立读数·治理闸门机械化对账）。
            pr = platform_rates or {}
            green_full = 0
            denom_pt = 0
            for _p, _v in pr.items():
                if not (isinstance(_v, (tuple, list)) and len(_v) == 2):
                    continue  # 形态不符=不可判：不进分母、不崩、不拿它冒充读数
                _n, _d = _v
                denom_pt += 1
                if _d and _n == _d:
                    green_full += 1
            platform_done = (green_full / denom_pt) if denom_pt else None
            if unit == "rate":
                auto_trigger_rate = current  # hook_auto触发占比原值（0~1）·2026-09-03童灵口径修正（旧名closure=审计闭环率已废弃）
                # A v2 双轴分离(2026-08-23 L3双Agent裁定·你"go")：目标线=hook_auto触发占比；
                # 平台覆盖 N/M 为独立环境读数，不再 min() 焊入名值——杀分母游戏激励，回归 §11.1 冻结口径。
                note = "A v2 双轴分离 · 目标线=hook_auto 触发占比({:.0%})·愿景①真义=机制自动运转不依赖人记得 · 手动调用累积拉低占比(非退化) · 平台覆盖 {}/{} 为独立读数·不并入目标进度".format(
                    auto_trigger_rate if auto_trigger_rate is not None else 0, green_full, denom_pt)
                if current is not None:
                    current = round(current * 100)
                # A v2 同源暴露：hook_auto触发占比(目标线)/覆盖独立读数随行输出（min下界概念废除）
                extra = {
                    "auto_closure": current,  # 兼容旧消费方·2026-09-03童灵修正：实际是hook_auto触发占比非审计闭环率
                    "auto_trigger_rate": current,  # 2026-09-03童灵新增：正确命名
                    "auto_closure_rate": dirs.get("auto_rate", {}).get("auto_closure_rate"),  # 第二指标：自动闭环率（2026-09-03童灵新增·数据积累中可能为None）
                    "auto_coverage": dirs.get("auto_rate", {}).get("coverage"),  # 覆盖面（2026-09-03童灵实事求是根治：机械计算有埋点的守卫数）
                    "auto_done": round(platform_done * 100) if platform_done is not None else None,
                    "auto_cov": "{}/{}".format(green_full, denom_pt),
                    "auto_breakdown": dirs.get("auto_rate", {}).get("breakdown"),  # 2026-09-03童灵透明度提升：分母构成
                }
            else:
                if platform_done is not None and current is not None:
                    current = round(current * platform_done, 2)
        elif d == "evo":
            # 挑战线=净采纳率(愿景③质量·adoption_rate)：进度条测它；底盘事件数放 note 补充
            ar = dirs.get("autonomous_evolution", {}).get("adoption_rate")
            if ar is not None:
                current = round(ar * 100)
            unit = "rate"
            target = obj.get("challenge_target", target)  # 挑战线覆盖底盘 target
            ev = dirs.get("autonomous_evolution", {}).get("actual")
            note = "本季进化事件 {} · 净采纳率 · 抗刷量/存量无牵引".format(ev if ev is not None else "—")
        elif d == "knows":
            current = quarter_sum(by_month)
            cur_month = dirs.get("knows_user_better", {}).get("count")
            note = "本季 by_month 累计 · 当月 {} 条 · 自然月归当月".format(cur_month if cur_month is not None else "—")
        elif d == "better":
            # 2026-09-27 童灵根治：transition_baseline=免疫命中÷有效抗体（倍数语义·本次抗体 0→39 修复后
            # 首次有值即暴露"基线 2349%"+OKR 假绿 100%——旧代码按百分比乘 100 塞进"高好"进度条，
            # 而该读数是低好方向（目标≤0.8倍=抗体覆盖住复发），方向语义进渲染层前须经你定案。
            # ⛔宁可 N/A 待量化，不上假绿（面板红条幅原话：宁可少，不要假）。
            # 定案口径=漏触发修复率（两池 join·现值 0.078 待治理），届时由脚本接管 current。
            tb = dirs.get("gets_better", {}).get("transition_baseline")
            im = dirs.get("gets_better", {}).get("immune_hits")
            fb = dirs.get("gets_better", {}).get("fanbu_antibodies")
            # 10-07 终审轮：定案口径=漏触发修复率(活跃)——state=定案 且 活跃join有值时脚本接管 current
            if (dirs.get("gets_better", {}).get("state") == "定案"
                    and dirs.get("gets_better", {}).get("join_rate_active") is not None):
                current = min(round(dirs["gets_better"]["join_rate_active"] * 100), 100)
            if im is not None and fb is not None and tb is not None:
                note = "过渡读数=免疫 {}/抗体 {} = {:.1f} 倍（每抗体摊命中·低好方向·待定案不进进度条）· 定案=漏触发修复率(两池join现值{:.3f})".format(
                    im, fb, tb, dirs.get("gets_better", {}).get("join_rate") or 0)
        target_pct = round(target * 100) if (unit == "rate" and target is not None) else target
        if not note:
            note = obj.get("note", "")
        # v0.7.2：note 统一优先读 evolution json（口径单一真相源，含定案/过渡/证据）
        # 根治实测漂移：better 已定案（baseline93%/join92%），面板 note 却还硬编码"过渡基线·待池统一"。
        # 改口径只改 evolution json（脚本生成），面板永不再回落旧档。
        _d2j = {"auto": "auto_rate", "better": "gets_better",
                "evo": "autonomous_evolution", "knows": "knows_user_better"}
        # auto 降档时保留诚实 note（平台完备度口径），⛔不让 evolution json 的"hook_auto触发占比"note 覆盖——
        # 否则 67% 的卡配"hook_auto触发占比105%"的note又重演割裂（2026-08-22 你点名根治·2026-09-03童灵口径修正）。
        if d in _d2j and (d != "auto" or not note.startswith("min(")):
            _jn = dirs.get(_d2j[d], {}).get("note")
            if _jn:
                note = _jn
        # 机械 evidence（v0.7.1·你结构定案·不照抄静态字段防过渡冒充定案）：
        #   count 型：达成🟢 否则🔴（过渡目标同理·不硬标达标）
        #   rate  型：≥100% 达成🟢 · ≥70% 接近🟡 · 否则落后🔴
        mec_ev = "🔴"
        if current is not None and target not in (None, 0):
            if unit == "count":
                mec_ev = "🟢" if current >= target else "🔴"
            else:
                ratio = current / (target * 100)  # current 已是百分比数
                mec_ev = "🟢" if ratio >= 1.0 else ("🟡" if ratio >= 0.7 else "🔴")
        # v0.8.0 证据封顶：state=过渡的方向，代理计数再高也只配🟡（记录量≠预测力·防虚荣温床）
        _st = dirs.get(_d2j.get(d, ""), {}).get("state") if d in _d2j else None
        if _st == "过渡" and mec_ev == "🟢":
            mec_ev = "🟡"
        evidence = mec_ev if current is not None else obj.get("evidence", "🔴")
        row = {
            "dir": d, "name": obj.get("name"), "unit": unit,
            "target": target, "target_pct": target_pct, "current": current,
            "evidence": evidence, "remaining": remaining, "note": note,
            "formula": obj.get("formula", ""),  # v0.8.1 公式随行输出(口径SSOT=okr_quarter.json·静态语义)
            "fidelity": obj.get("fidelity", ""),  # v0.9.1 构念保真度档位(防盲目自信·2026-08-23你质证)
            "measures": obj.get("measures", ""),  # v0.9.1 测什么/不测什么明示
        }
        row.update(extra)
        rows.append(row)
    return {
        "quarter": okr.get("quarter"), "start": okr.get("start"), "end": okr.get("end"),
        "remaining": remaining, "objectives": rows,
    }

def load_knowledge_ladder():
    """L1-L4 知识内化阶梯（2026-08-26 童灵执行·管道打通后入板）
    数据源：INDEX.md（L1-L4 分布·机械解析）+ 引用台账（L4 试金石）
    """
    stats = {"L1": 0, "L2": 0, "L3": 0, "L4": 0}
    idx = os.path.join(AILIB_DIR, "INDEX.md")
    try:
        with open(idx, encoding="utf-8") as f:
            for line in f:
                m = re.search(r"\| (?:立场卡#S\d+|技能卡#K\d+).*?\|\s*(L[1-4])", line)
                if m:
                    stats[m.group(1)] += 1
    except Exception as e:
        print("[panel_snapshot][WARN] INDEX 读取失败: {}".format(e), file=sys.stderr)
    # L4 试金石：引用台账中引用≥3 的卡（含你决策引用数）
    ledger = os.path.join(AILIB_DIR, "引用台账.md")
    counts = {}
    try:
        with open(ledger, encoding="utf-8") as f:
            for line in f:
                if line.startswith("|") and "#S" in line:
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if len(cells) >= 4 and cells[0].startswith("#S"):
                        cid = cells[0]
                        c = counts.setdefault(cid, {"total": 0, "ge": 0})
                        c["total"] += 1
                        if "你决策" in cells[3]:
                            c["ge"] += 1
    except Exception as e:
        print("[panel_snapshot][WARN] 引用台账读取失败: {}".format(e), file=sys.stderr)
    probe = None
    for cid, c in sorted(counts.items(), key=lambda x: -x[1]["total"]):
        if c["total"] >= 3:
            probe = {"card": cid, "total": c["total"], "ge": c["ge"]}
            break
    # 技能卡候选数量（V0.2·2026-08-26新增·统计候选台账中待确认+提醒中）
    skill_candidates = 0
    cand_ledger = os.path.join(AILIB_DIR, "技能卡候选台账.md")
    try:
        with open(cand_ledger, encoding="utf-8") as f:
            for line in f:
                # 只匹配候选记录表中的行：以|开头+包含日期(YYYY-MM-DD)+状态为待确认或提醒中
                if line.startswith("|") and re.search(r"\d{4}-\d{2}-\d{2}", line) and ("待确认" in line or "提醒中" in line):
                    skill_candidates += 1
    except Exception:
        pass
    return {"stats": stats, "l4_probe": probe, "skill_candidates": skill_candidates, "updated": datetime.now().strftime("%Y-%m-%d")}


def take_snapshot():
    today = datetime.now().strftime("%Y-%m-%d")
    snap = {"date": today, "source": "panel_snapshot.py v0.9.1"}
    evo = load_json(latest_json("evolution_deviation")) or {}
    dirs = evo.get("directions", {})

    # ★ 闭环流（v0.6 峰值数据源）
    cl = evo.get("closed_loop", {}) or {}
    snap["closed_loop"] = {
        "detected": cl.get("detected"),
        "fixed": cl.get("fixed"),
        "immune": cl.get("immune"),
        "immune_total": cl.get("immune_total"),
        "immune_last_date": cl.get("immune_last_date"),
        "antibodies": cl.get("antibodies"),
        "pending": cl.get("pending"),
        "trend": cl.get("trend_7d", []),
        "sources": cl.get("sources", {}),
    }
    snap["cl_detected"] = cl.get("detected")
    snap["cl_fixed"] = cl.get("fixed")
    snap["cl_immune"] = cl.get("immune")
    snap["cl_immune_last"] = cl.get("immune_last_date")

    # 四方向原生数据（v0.6：状态+原生数+证据档位·分数全去）
    snap["auto_rate"] = dirs.get("auto_rate", {}).get("actual")
    snap["regulator_activity"] = dirs.get("regulator_activity", {}).get("actual")
    snap["regulator_last"] = dirs.get("regulator_activity", {}).get("last_week")
    snap["evo_events"] = dirs.get("autonomous_evolution", {}).get("actual")
    # 2026-10-23 口径根治（你令）：采纳三态 + 样本量 + 区间——比率⛔不裸报
    _evo = dirs.get("autonomous_evolution", {})
    snap["evo_adopted"] = _evo.get("adopted")
    snap["evo_waived"] = _evo.get("waived")
    snap["evo_pending"] = _evo.get("pending")
    snap["evo_rate_n"] = _evo.get("adoption_rate_n")
    snap["evo_rate_ci"] = _evo.get("adoption_rate_ci")
    snap["evo_evidence"] = dirs.get("autonomous_evolution", {}).get("evidence")
    snap["evo_adoption_rate"] = dirs.get("autonomous_evolution", {}).get("adoption_rate")
    snap["evo_state"] = dirs.get("autonomous_evolution", {}).get("state")
    snap["auto_state"] = dirs.get("auto_rate", {}).get("state")
    snap["auto_closure_rate"] = dirs.get("auto_rate", {}).get("auto_closure_rate")  # 第二指标：自动闭环率（2026-09-03童灵新增·数据积累中可能为None）
    snap["auto_coverage"] = dirs.get("auto_rate", {}).get("coverage")  # 覆盖面（2026-09-03童灵实事求是根治：机械计算有埋点的守卫数）
    snap["auto_breakdown"] = dirs.get("auto_rate", {}).get("breakdown")  # 2026-09-03童灵透明度提升：分母构成（total/hook_auto/manual/other）
    snap["better_state"] = dirs.get("gets_better", {}).get("state")
    snap["better_immune_hits"] = dirs.get("gets_better", {}).get("immune_hits")
    snap["better_antibodies"] = dirs.get("gets_better", {}).get("fanbu_antibodies")
    snap["better_join_active"] = dirs.get("gets_better", {}).get("join_rate_active")
    snap["better_join_all"] = dirs.get("gets_better", {}).get("join_rate")
    snap["better_pool"] = dirs.get("gets_better", {}).get("antibody_pool_dual")
    snap["better_evidence"] = dirs.get("gets_better", {}).get("evidence")
    snap["better_baseline"] = dirs.get("gets_better", {}).get("transition_baseline")
    snap["better_join_rate"] = dirs.get("gets_better", {}).get("join_rate")
    snap["better_note"] = dirs.get("gets_better", {}).get("note")
    snap["knows_state"] = dirs.get("knows_user_better", {}).get("state")
    snap["new_30d"] = dirs.get("knows_user_better", {}).get("actual_new_30d")  # 兼容旧字段=当月数
    snap["knows_current_month"] = dirs.get("knows_user_better", {}).get("current_month")
    snap["knows_count"] = dirs.get("knows_user_better", {}).get("count")
    snap["knows_days_left"] = dirs.get("knows_user_better", {}).get("days_left_in_month")
    snap["knows_evidence"] = dirs.get("knows_user_better", {}).get("evidence")
    sug = load_json(latest_json("route_evolution_suggest")) or {}
    st = sug.get("stats", {})
    snap["uncovered_skills"] = st.get("uncovered_skills")

    # 维护成本（环节台账·git log 派生）
    tai = load_json(latest_json("环节维护台账")) or {}
    snap["maintenance"] = {
        "total_commits": tai.get("total_commits"),
        "segments": [
            {"segment": s.get("segment"), "commits": s.get("commits_7d")}
            for s in (tai.get("segments") or [])[:6]
        ],
    }

    # 实盘优先：workbuddy/qoder-cn/qoder-desktop 直接读配置；其余平台回退 SSOT
    live = load_live_rates() or {}
    ssot = parse_kanban_rates() or {}
    merged = {}
    for name in ssot:
        if not name.strip():
            continue  # 2026-10-23 根治：SSOT 表头含空列（Trae CN 与 MiniMax 之间的占位列）→ 旧逻辑渲染出空名"未登记"行
        lv = live.get(name)
        # 实盘直读若返回 None（如 Hermes 插件级不可逐钩核验）也回退 SSOT——否则 None 覆盖 SSOT 值 → 假"未解析"
        merged[name] = lv if lv is not None else ssot.get(name)
    for name in live:
        if name.strip():
            merged.setdefault(name, live[name])
    snap["platform_rates"] = merged
    snap["knowledge_ladder"] = load_knowledge_ladder()   # 知识内化流（L1-L4）
    snap["okr"] = compute_okr(platform_rates=merged)
    # 季度时间进度（2026-10-23）：与"本季累计 X/30"并列，防读者把产量%误读为完成度
    try:
        import calendar as _cal2
        _n2 = datetime.now()
        _q2 = (_n2.month - 1) // 3 + 1
        _s2 = datetime(_n2.year, _q2 * 3 - 2, 1)
        _e2 = datetime(_n2.year, _q2 * 3, _cal2.monthrange(_n2.year, _q2 * 3)[1], 23, 59)
        snap["quarter_time_pct"] = round((_n2 - _s2).total_seconds() / (_e2 - _s2).total_seconds() * 100)
    except Exception:
        snap["quarter_time_pct"] = None

    # 知识库可视化3模块数据（2026-09-08 童灵根治·合并入panel_snapshot.py）
    kb_metadata_path = os.path.join(MC, "可视化呈现/data/kb_metadata.json")
    try:
        with open(kb_metadata_path, encoding="utf-8") as f:
            snap["knowledge_base"] = json.load(f)
    except Exception as e:
        print("[panel_snapshot][WARN] kb_metadata.json 读取失败: {}".format(e), file=sys.stderr)
        snap["knowledge_base"] = None
   # 季度 OKR 目标对照层（auto 卡含平台完备度诚实边界）
    return snap

def already_has_date(date):
    try:
        with open(TS_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip() and json.loads(line).get("date") == date:
                    return True
    except Exception:
        pass
    return False

def append_snapshot(snap):
    os.makedirs(os.path.dirname(TS_PATH), exist_ok=True)
    with open(TS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")

def read_timeseries():
    rows = []
    try:
        with open(TS_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    except Exception:
        pass
    return sorted(rows, key=lambda x: x.get("date", ""))

def build_summary(cl):
    """一句话总结（峰终·终点）——自动生成·数据说话·缺源明说。
    v0.8.0 因果安全措辞：fixed 源=变更日志全量行，≠"对检出项的修复"——⛔不用因果动词暗示管线闭合
    （你最高原则"宁可少一个指标，不要一个假指标"+数学之美卡4 信息熵测试）。"""
    det, fix, imm = cl.get("detected"), cl.get("fixed"), cl.get("immune")
    if det is None or fix is None or imm is None:
        missing = [k for k, v in (("检出", det), ("留痕", fix), ("免疫", imm)) if v is None]
        return "闭环数据采集中——{} 数据源待接入（宁可少一个，不要假指标）".format("、".join(missing))
    imm_last = cl.get("immune_last_date")
    if imm:
        imm_txt = "免疫拦截复发 {} 次".format(imm)
    else:
        imm_txt = "免疫本周无触发" + ("（末次 {}）".format(imm_last) if imm_last else "（无历史命中记录）")
    text = "本周自动检出偏差 {} 次 · 留痕变更 {} 条 · {}".format(det, fix, imm_txt)
    if det > fix:
        text += " · 检出−留痕差值 {}（粗口径·非逐项核销）".format(det - fix)
    return text

def _fmt_okr_val(v, unit):
    if v is None:
        return "—"
    return (str(v) + "%") if unit == "rate" else str(v)

def build_okr_html(snap):
    """季度 OKR 目标对照层（本季目标线 vs 实际进度）。目标值来自 okr_quarter.json·当前值来自脚本·机械算。
    v4.1：表面=名称/目标/进度条/读数（n·CI 由同区四方向卡同屏承载·显示契约不破）+达标线刻度（okr-tick@100%）；
    口径 note/公式 formula/构念保真度 fidelity/measures 长文全部收进 <details> 下钻层。"""
    okr = snap.get("okr")
    if not okr:
        return '<div class="card"><div class="drill-body">季度 OKR 数据源缺失（okr_quarter.json 未读到）——季度目标线待接入，只上线有数据源的指标</div></div>'
    rows = ""
    for i, o in enumerate(okr.get("objectives", [])):
        unit = o.get("unit")
        tgt = o.get("target_pct")
        cur = o.get("current")
        tgt_txt = "目标 ≥" + (_fmt_okr_val(tgt, unit)) if tgt is not None else "目标 —"
        if cur is None:
            cur_lbl, st_lbl, fill_cls, width = "N/A", "待量化", "f-gray", 0
        else:
            denom = tgt or 1
            pct = cur / denom * 100
            disp = min(round(pct), 100)  # A v2: 目标进度封顶100·防"105%✓"观感打脸(当前值标签仍真实)
            if pct >= 100:
                fill_cls, cur_lbl = "f-green", "{}% ✓".format(disp)
            elif pct >= 70:
                fill_cls, cur_lbl = "f-amber", "{}%".format(disp)
            else:
                fill_cls, cur_lbl = "f-red", "{}%".format(disp)
            width = min(pct, 100)
            st_lbl = "当前 " + _fmt_okr_val(cur, unit)
        d = o.get("dir", "x")
        rows += (
            '<div class="okr-item{first}">'
            '<div class="okr-idx">{name} <span class="e">{ev}</span><span class="tg">{tgt}</span></div>'
            '<div><div class="okr-track">'
            '<div class="okr-fill {cls}" id="o-fill-{d}" style="width:{w}%"></div>'
            '<div class="okr-tick" style="left:100%" title="到此线=达标"></div>'
            '</div>'
            '<details class="drill"><summary>口径 · 公式 · 构念保真度 ▾</summary>'
            '<div class="drill-body"><b>口径</b>：{note}'
            '<span class="fx">ƒ {formula}</span>'
            '<span class="fx">🧪 {fidelity} — {measures}</span>'
            '</div></details></div>'
            '<div class="okr-pct" id="o-pct-{d}">{cur}<span class="st" id="o-st-{d}">{st}</span></div>'
            '</div>'
        ).format(first=(" okr-first" if i == 0 else ""),
                 name=o.get("name", "—"), ev=o.get("evidence", ""), tgt=tgt_txt,
                 cls=fill_cls, d=d, w=width,
                 note=o.get("note", ""),
                 formula=o.get("formula", ""),
                 fidelity=o.get("fidelity", ""),
                 measures=o.get("measures", ""),
                 cur=cur_lbl, st=st_lbl)
    head = (
        '<div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:4px">'
        '<span style="font-size:13px;font-weight:600">季度 OKR · {q} <span style="font-size:12px;color:var(--ink3);font-weight:400;font-family:var(--f-mono)">{s} → {e}</span></span>'
        '<span class="tag" id="okr-remaining" style="font-size:12px;font-family:var(--f-mono);color:var(--ink2)">剩余 {r} 天 · 目标/当前由 okr_quarter.json + 脚本机械映射 · 自然季度框定</span>'
        '</div>'
    ).format(q=okr.get("quarter", "—"), s=okr.get("start", "—"), e=okr.get("end", "—"),
             r=(okr.get("remaining") if okr.get("remaining") is not None else "—"))
    alarm = snap.get("registry_alarm")
    alarm_html = ('<div class="alarm">🚨 {}</div>'.format(alarm)) if alarm else ""
    return '<div class="card">{}</div>'.format(alarm_html + head + rows)


# ─────────────────────────────────────────────────────────────
# 渲染 v1.1.0：v4.1 三主题（a 细线终端 / b 硬件面板 / c 印刷年报·右上角切换）·单页分区下钻保留
# ─────────────────────────────────────────────────────────────

CSS = """
/* ═══ v4.1 主题系统：共享骨架（布局/间距/字号·与主题无关）+ 三主题皮肤（theme-a/b/c） ═══ */
/* 字号纪律（花叔可读性底线）：全站最小 12px */
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--text);padding:28px 24px 40px;min-height:100vh;font-family:var(--f-sans)}
.n,.num,.count,.pct,.rd{font-variant-numeric:tabular-nums}
.wrap{max-width:var(--wrap-w,1180px);margin:0 auto}
/* ── 顶栏 ── */
.topbar{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;border-bottom:2px solid var(--line2);padding-bottom:14px}
.topbar .lft{display:flex;flex-direction:column;gap:4px}
.brand{font-size:var(--brand-size);font-weight:var(--brand-weight);letter-spacing:.01em;color:var(--text)}
.brand .ver{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-left:10px;font-weight:400}
.brand .sub{font-family:var(--f-mono);font-size:12px;color:var(--ink3);letter-spacing:.18em;margin-top:4px}
.topbar .rgt{display:flex;align-items:center;gap:18px}
.live{font-size:12px;color:var(--ink2);font-family:var(--f-mono)}
.live .dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--ok);margin-right:7px;vertical-align:1px}
/* ── 切换器 ── */
.tswitch{display:flex;border:1px solid var(--line2);border-radius:var(--radius);overflow:hidden}
.tswitch button{appearance:none;border:none;background:transparent;color:var(--ink3);font-family:var(--f-mono);font-size:12px;letter-spacing:.08em;padding:7px 14px;cursor:pointer;border-right:1px solid var(--line)}
.tswitch button:last-child{border-right:none}
.tswitch button:hover{color:var(--text)}
.tswitch button.on{background:var(--accent);color:var(--btn-on-ink);font-weight:600}
/* ── 分区 ── */
.sec{margin-top:40px}
.sec-head{display:flex;align-items:baseline;gap:14px;padding-bottom:9px;margin-bottom:16px}
.sec-head .no{font-family:var(--f-mono);font-size:12px;color:var(--accent)}
.sec-head .t{font-size:13px;font-weight:600;letter-spacing:.06em;color:var(--text)}
.sec-head .m{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-left:auto}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px}
/* ── L0 心跳 ── */
.hero{border-radius:var(--radius);padding:22px 24px;position:relative}
.hero-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:18px}
.hero-head .t{font-size:12px;font-weight:600;color:var(--ink2);letter-spacing:.16em}
.hero-head .no{font-family:var(--f-mono);font-size:12px;color:var(--accent);margin-right:8px}
.hero-head .m{font-size:12px;color:var(--ink3);font-family:var(--f-mono)}
.flow{display:flex;align-items:stretch;flex-wrap:wrap}
.stage{flex:1;min-width:150px;padding:4px 20px;text-align:center;border-left:1px solid var(--line)}
.stage:first-child{border-left:none;padding-left:0}
.stage .tag{font-family:var(--f-mono);font-size:12px;color:var(--ink3);letter-spacing:.2em}
.stage .num{font-size:var(--hero-num-size);font-weight:var(--hero-num-weight);line-height:1.15;font-family:var(--hero-num-font);letter-spacing:var(--hero-num-ls);margin:12px 0 8px;color:var(--text)}
.stage .lbl{font-size:13px;font-weight:600;color:var(--ink2)}
.stage .src{font-size:12px;color:var(--ink3);margin-top:5px;font-family:var(--f-mono)}
.stage.hot .num{color:var(--accent)}
.arrow{color:var(--ink3);font-size:16px;align-self:center;padding:0 6px}
.hero-mid{display:grid;grid-template-columns:1fr 300px;gap:24px;margin-top:18px}
.chart-box{position:relative;height:170px}
.chart-legend{position:absolute;top:-2px;right:0;display:flex;gap:14px;font-size:12px;color:var(--ink2);align-items:center}
.chart-legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px}
svg#clTrend{width:100%;height:100%;display:block}
.chart-note{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-top:12px;line-height:1.8}
.hero-side{border-left:1px solid var(--line);padding-left:22px;display:flex;flex-direction:column;justify-content:center;gap:12px}
.hside-title{font-size:12px;color:var(--ink3);font-weight:600;letter-spacing:.14em}
.hs-item{display:flex;align-items:center;gap:9px;font-size:13px;padding:6px 0;border-bottom:1px solid var(--line)}
.hs-item:last-child{border-bottom:none}
.hs-item .dot{width:7px;height:7px;border-radius:50%;flex:none}
.hs-item .nm{color:var(--ink2);font-weight:600}
.hs-item .vl{font-family:var(--f-mono);font-weight:600;font-size:16px;margin-left:auto}
.dot.ev-g{background:var(--ok)}.dot.ev-a{background:var(--warn)}.dot.ev-r{background:var(--bad)}.dot.ev-n{background:var(--line2)}
.chip{display:inline-block;font-size:12px;font-weight:600;padding:3px 10px;border-radius:99px;font-family:var(--f-mono)}
.chip-neutral{background:rgba(127,127,127,.1);color:var(--ink2);border:1px solid var(--line2)}
.chip-ok{background:transparent;color:var(--ok);border:1px solid var(--ok)}
/* ── 下钻 ── */
details.drill{margin-top:8px}
details.drill>summary{cursor:pointer;list-style:none;font-size:12px;color:var(--ink3);font-family:var(--f-mono);user-select:none}
details.drill>summary::-webkit-details-marker{display:none}
details.drill>summary:hover{color:var(--ink2)}
details.drill[open]>summary{margin-bottom:8px}
.drill-body{font-size:13px;color:var(--ink2);line-height:1.75;padding:11px 14px;background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius)}
.drill-body b{color:var(--text);font-weight:600}
.drill-body .fx{font-family:var(--f-mono);font-size:12px;color:var(--ink3);display:block;margin-top:7px;line-height:1.7}
/* ── 愿景进度 ── */
.fourdir{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.fd{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px}
.fd .name{font-size:12px;color:var(--ink2);font-weight:600;display:flex;justify-content:space-between;align-items:center;gap:6px}
.fd .badge{font-size:12px;flex:none}
.fd .val{font-size:13.5px;font-weight:600;margin-top:8px;line-height:1.55;color:var(--text)}
.fd .note{font-size:12px;color:var(--ink3);margin-top:6px}
.okr-item{display:grid;grid-template-columns:220px 1fr 90px;gap:16px;align-items:center;padding:13px 0;border-top:1px solid var(--line)}
.okr-first{border-top:none}
.okr-idx{font-size:13.5px;font-weight:700}
.okr-idx .e{font-size:12px;margin-left:6px}
.okr-idx .tg{display:block;font-size:12px;color:var(--ink3);font-weight:400;margin-top:3px;font-family:var(--f-mono)}
.okr-track{position:relative;height:var(--track-h);background:var(--track-bg);border-radius:99px;overflow:hidden;box-shadow:var(--track-shadow)}
.okr-fill{position:absolute;top:0;left:0;height:100%;border-radius:99px;background:var(--accent);transition:width .5s ease}
.okr-fill.f-green{background:var(--ok)}
.okr-fill.f-amber{background:var(--warn)}
.okr-fill.f-red{background:var(--bad)}
.okr-fill.f-gray{background:var(--line2)}
.okr-tick{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--text);opacity:.75}
.okr-pct{font-size:18px;font-weight:700;text-align:right}
.okr-pct .st{font-size:12px;color:var(--ink3);font-weight:500;display:block;margin-top:2px;font-family:var(--f-mono)}
.alarm{background:transparent;border:1px solid var(--bad);color:var(--bad);padding:9px 13px;border-radius:var(--radius);font-size:12.5px;line-height:1.7;margin-bottom:14px;white-space:pre-wrap}
.ops{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}
.ops .card{padding:14px 17px}
.ops h4{font-size:12px;color:var(--ink3);font-weight:600;letter-spacing:.12em;margin-bottom:8px}
.ops .line{font-size:12.5px;color:var(--ink2);line-height:1.8}
.ops .line b{color:var(--text);font-weight:600}
/* ── 知识库 ── */
.kb-flow{display:flex;align-items:center;flex-wrap:wrap;margin-bottom:16px}
.kb-flow .stage{min-width:118px}
.kb-flow .stage .num{font-size:26px}
.kb-grid{display:grid;grid-template-columns:repeat(8,1fr);gap:10px}
.kb-cell{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:11px 10px;text-align:center}
.kb-cell .label{font-size:12px;color:var(--ink2);font-weight:600;margin-bottom:5px}
.kb-cell .val{font-size:20px;font-weight:700;line-height:1.2;font-family:var(--f-mono)}
.kb-cell .src{font-size:12px;color:var(--ink3);margin-top:4px;font-family:var(--f-mono)}
.kb-bars{margin:14px 0 12px}
.kb-bar-row{display:grid;grid-template-columns:78px 1fr 52px;gap:10px;align-items:center;margin-bottom:8px}
.kb-bar-row .name{font-size:12px;color:var(--ink2);font-weight:600}
.kb-bar-row .bar-track{height:10px;background:var(--track-bg);border-radius:99px;overflow:hidden}
.kb-bar-row .bar-fill{height:100%;border-radius:99px;background:var(--accent);opacity:.85}
.kb-bar-row .count{font-size:13px;font-weight:700;text-align:right}
.kb-progress-track{position:relative;height:16px;background:var(--track-bg);border-radius:99px;overflow:hidden}
.kb-progress-fill{position:absolute;top:0;left:0;height:100%;background:var(--accent);border-radius:99px;transition:width .6s ease}
.kb-progress-text{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;color:var(--text)}
.kb-progress-meta{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-top:7px;font-size:12px;color:var(--ink3);font-family:var(--f-mono)}
/* ── 平台覆盖 ── */
.cov-strip{display:grid;grid-template-columns:repeat(8,1fr);gap:var(--cov-gap)}
.cov-cell{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:12px 12px 11px}
.cov-cell .nm{font-size:12px;color:var(--ink2);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cov-cell .rd{font-family:var(--f-mono);font-size:18px;font-weight:700;margin-top:6px;color:var(--text)}
.cov-cell .ex{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-top:3px}
.cov-cell .bar{display:none;position:relative;height:12px;background:var(--track-bg);margin-top:7px;border-radius:2px}
.cov-cell .bar i{position:absolute;top:0;left:0;bottom:0;background:var(--text);border-radius:2px}
.cov-cell.c-ok{border-color:var(--cov-ok-border)}
.cov-cell.c-mid .rd{color:var(--warn)}
.cov-cell.c-bad .rd{color:var(--bad)}
details.rates{margin-top:14px}
details.rates>summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:12px}
details.rates>summary::-webkit-details-marker{display:none}
details.rates>summary .hint{font-size:12px;color:var(--ink3);font-family:var(--f-mono)}
details.rates[open]>summary{margin-bottom:10px}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th{text-align:left;color:var(--ink3);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;padding:0 8px 8px}
td{padding:7px 8px;border-top:1px solid var(--line)}
td:first-child{color:var(--ink2);font-weight:600}
td:nth-child(2){font-weight:600}
.vmethod{color:var(--ink2);font-weight:600;font-size:12px}
/* ── 季度时间进度旋钮（P2·三主题皮肤：--knob-base/--knob-shadow） ── */
.knob-row{display:flex;align-items:center;gap:14px;margin-top:14px;padding-top:13px;border-top:1px solid var(--line)}
.knob{position:relative;width:46px;height:46px;flex:none}
.knob .base{position:absolute;inset:0;border-radius:50%;background:var(--knob-base);box-shadow:var(--knob-shadow)}
.knob .needle{position:absolute;left:50%;top:50%;width:2px;height:21px;background:var(--accent);transform-origin:50% 0;border-radius:2px}
.knob .cap{position:absolute;left:50%;top:50%;width:11px;height:11px;border-radius:50%;background:var(--knob-cap,#E9E9E4);transform:translate(-50%,-50%);box-shadow:0 1px 2px rgba(0,0,0,.4)}
.knob-row .kv{font-family:var(--f-mono);font-size:26px;font-weight:700}
.knob-row .kl{font-size:12px;color:var(--ink2);font-weight:600;margin-top:2px}
.knob-row .ks{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-top:2px}
/* ── 终点 ── */
.summary{margin-top:40px;border-radius:var(--radius);padding:24px 26px;display:flex;gap:18px;align-items:flex-start}
.summary .bolt{font-family:var(--f-mono);font-size:14px;color:var(--accent);line-height:1.5}
.summary .text{font-size:19px;font-weight:600;line-height:1.65;color:var(--text)}
.summary .meta{font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-top:9px}
.footer{max-width:1180px;margin:18px auto 0;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink3);font-family:var(--f-mono)}
@media(max-width:1100px){
.hero-mid{grid-template-columns:1fr}
.hero-side{border-left:none;padding-left:0;border-top:1px solid var(--line);padding-top:16px}
.kb-grid,.cov-strip{grid-template-columns:repeat(4,1fr)}
.fourdir{grid-template-columns:repeat(2,1fr)}
.okr-item{grid-template-columns:1fr;gap:8px}
.okr-pct{text-align:left}
.ops{grid-template-columns:1fr}
}
/* ═══════════ 主题 A · 细线终端（Linear / Vercel） ═══════════ */
body.theme-a{
color-scheme:dark;
--bg:#0C0D10;--panel:transparent;--panel2:#131519;--line:#232529;--line2:#33363D;
--text:#E8E9ED;--ink2:#9BA0AC;--ink3:#6B7180;
--accent:#7C7CFF;--ok:#5BD88E;--warn:#E8B04B;--bad:#F0655F;
--wrap-w:1240px;--radius:0;--btn-on-ink:#0C0D10;--knob-base:#131519;--knob-shadow:inset 0 0 0 1px #33363D;
--f-sans:-apple-system,"Inter Tight","PingFang SC","Segoe UI",system-ui,sans-serif;
--f-mono:"SF Mono",ui-monospace,Menlo,"JetBrains Mono",monospace;
--brand-size:14px;--brand-weight:600;
--hero-num-size:56px;--hero-num-weight:500;--hero-num-font:var(--f-mono);--hero-num-ls:0;
--track-h:3px;--track-bg:var(--line);--track-shadow:none;--cov-gap:0;
--cov-ok-border:transparent;
--c-detected:#F0655F;--c-fixed:#7C7CFF;--c-immune:#5BD88E;--chart-grid:#232529;--chart-axis:#6B7180;
}
body.theme-a .topbar{border-bottom:1px solid var(--line)}
body.theme-a .hero{background:transparent;border:none;padding:22px 0 0}
body.theme-a .hero .flow{border:1px solid var(--line);border-left:1px solid var(--line)}
body.theme-a .stage{border-right:1px solid var(--line);border-left:none;border-bottom:1px solid var(--line)}
body.theme-a .stage:first-child{padding-left:20px}
body.theme-a .stage:last-child{border-right:1px solid var(--line)}
body.theme-a .hero-mid{border-left:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:18px 20px;margin-top:0;grid-column-gap:20px}
body.theme-a .card{border:1px solid var(--line)}
body.theme-a .cov-cell{border-right:1px solid var(--line);border-bottom:1px solid var(--line);border-radius:0}
body.theme-a .cov-cell.c-ok{border-color:rgba(91,216,142,.4)}
body.theme-a .hs-item{border-bottom-color:transparent;padding:5px 0}
body.theme-a .sec-head{border-bottom:1px solid var(--line)}
body.theme-a .okr-item{border-top:1px solid var(--line)}
body.theme-a .summary{background:transparent;border-top:1px solid var(--line);border-radius:0;padding:26px 0 0}
body.theme-a .chip-neutral{background:transparent;border-color:var(--line2)}
/* ═══════════ 主题 B · 硬件面板（Teenage Engineering） ═══════════ */
body.theme-b{
color-scheme:light;
--bg:#D9D7D0;--panel:#CFCCC3;--panel2:#D6D3CB;--line:#B3AFA4;--line2:#8F8B7E;
--text:#17150F;--ink2:#5B574C;--ink3:#6E6A5E;
--accent:#FF5A1F;--ok:#3FA34D;--warn:#A87A28;--bad:#B3402A;--wrap-w:1340px;
--radius:7px;--btn-on-ink:#FFFFFF;--knob-base:#2A2A26;--knob-shadow:inset 0 2px 5px rgba(0,0,0,.8);
--f-sans:-apple-system,"PingFang SC","Helvetica Neue",system-ui,sans-serif;
--f-mono:"SF Mono",ui-monospace,Menlo,monospace;
--brand-size:21px;--brand-weight:800;
--hero-num-size:44px;--hero-num-weight:700;--hero-num-font:var(--f-mono);--hero-num-ls:.06em;
--track-h:14px;--track-bg:#B8B4A9;--track-shadow:inset 0 2px 4px rgba(23,21,15,.35);--cov-gap:12px;
--cov-ok-border:transparent;
--c-detected:#FF5A1F;--c-fixed:#EDEDE4;--c-immune:#3FA34D;--chart-grid:#2A2A26;--chart-axis:#8B8D82;
/* B 专属：液晶屏 */
--screen:#0B0B0B;--screen2:#141412;--lcd:#EDEDE4;--lcd2:#8B8D82;
}
body.theme-b{
background-image:
 repeating-linear-gradient(0deg,rgba(23,21,15,.06) 0 1px,transparent 1px 28px),
 repeating-linear-gradient(90deg,rgba(23,21,15,.06) 0 1px,transparent 1px 28px);
}
body.theme-b .topbar{border-bottom:2px solid var(--text)}
body.theme-b .brand{letter-spacing:.02em}
body.theme-b .stage .tag,body.theme-b .hero-head .m{letter-spacing:.2em}
body.theme-b .tswitch,body.theme-b .card,body.theme-b .fd{box-shadow:0 1px 0 #EAE8E0,0 2px 5px rgba(23,21,15,.12)}
body.theme-b .tswitch button.on{background:var(--accent);box-shadow:inset 0 -2px 0 rgba(0,0,0,.25)}
body.theme-b .cov-cell{box-shadow:0 3px 0 #B1ADA2,0 4px 6px rgba(23,21,15,.16);cursor:default}
body.theme-b .cov-cell:active{transform:translateY(2px);box-shadow:0 1px 0 #B1ADA2}
/* B 核心：hero=液晶屏（暗屏+扫描线+LCD发光数字） */
body.theme-b .hero{background:var(--screen);box-shadow:inset 0 3px 12px rgba(0,0,0,.85),0 1px 0 #EAE8E0;border:1px solid #23231F;overflow:hidden}
body.theme-b .hero::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 2px,transparent 2px 4px);pointer-events:none;border-radius:inherit}
body.theme-b .hero .hero-head .t,body.theme-b .hero .chart-note{color:var(--lcd2)}
body.theme-b .hero .stage{border-left-color:#23231F}
body.theme-b .hero .stage .tag{color:var(--lcd2)}
body.theme-b .hero .stage .num{color:var(--lcd);text-shadow:0 0 10px rgba(237,237,228,.3)}
body.theme-b .hero .stage.hot .num{color:var(--accent);text-shadow:0 0 12px rgba(255,90,31,.55)}
body.theme-b .hero .stage .lbl{color:var(--lcd2)}
body.theme-b .hero .stage .src{color:#5B5D52}
body.theme-b .hero .arrow{color:var(--lcd2)}
body.theme-b .hero .hero-side{border-left-color:#23231F}
body.theme-b .hero .hside-title{color:var(--lcd2)}
body.theme-b .hero .hs-item{border-bottom-color:#23231F}
body.theme-b .hero .hs-item .nm{color:var(--lcd2)}
body.theme-b .hero .hs-item .vl{color:var(--lcd)}
body.theme-b .hero .chart-legend{color:var(--lcd2)}
body.theme-b .hero .chip-neutral{color:var(--lcd2);border-color:#3A3A34;background:rgba(255,255,255,.04)}
/* B：LED 排灯（方形+辉光） */
body.theme-b .hs-item .dot{border-radius:2px}
body.theme-b .hs-item .dot.ev-g{box-shadow:0 0 7px rgba(63,163,77,.65)}
body.theme-b .hs-item .dot.ev-r{box-shadow:0 0 8px rgba(255,90,31,.75)}
body.theme-b .hs-item .dot.ev-a{box-shadow:0 0 7px rgba(200,127,31,.65)}
/* B：推子感进度槽（okr-fill 顶距+刻度指针已由 okr-tick 承担） */
body.theme-b .okr-fill{top:3px;bottom:3px;left:3px;height:auto}
body.theme-b .okr-fill.f-green{background:var(--ok)}
body.theme-b .okr-fill.f-red{background:var(--accent)}
body.theme-b .summary{background:var(--screen);box-shadow:inset 0 3px 12px rgba(0,0,0,.85),0 1px 0 #EAE8E0;border:1px solid #23231F}
body.theme-b .summary .text{color:var(--lcd)}
body.theme-b .summary .bolt{color:var(--accent)}
body.theme-b .summary .meta{color:var(--lcd2)}
body.theme-b .sec-head .t{letter-spacing:.24em;font-weight:700}
body.theme-b .sec-head{border-bottom:2px solid var(--text)}
body.theme-b .fd .name,body.theme-b .ops h4{letter-spacing:.1em}
/* ── B v4.2 设备感全套（P0+P1·适配 1440×900：板宽 1340 居中·四周露底板） ── */
body.theme-b{padding:34px 26px 60px}
body.theme-b .wrap{background:var(--panel);border:1px solid #B9B5AA;border-radius:16px;box-shadow:0 1px 0 #EDEBE4 inset,0 16px 44px rgba(23,21,15,.18);padding:32px 36px 38px;position:relative}
/* 对角螺丝（五金件·径向高光圆） */
body.theme-b .wrap::before,body.theme-b .wrap::after{content:"";position:absolute;width:13px;height:13px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#E8E6DE,#B7B3A8 70%);box-shadow:inset 0 1px 2px rgba(23,21,15,.5),0 1px 0 #EDEBE4}
body.theme-b .wrap::before{top:11px;left:11px}
body.theme-b .wrap::after{bottom:11px;right:11px}
/* 电源灯：live 圆点升级为带辉光 LED */
body.theme-b .live .dot{width:10px;height:10px;box-shadow:0 0 9px rgba(63,163,77,.85),0 0 2px rgba(63,163,77,1)}
/* 屏内像素格：横向扫描线+竖向点阵（竖向淡一档防摩尔纹） */
body.theme-b .hero::before{background:repeating-linear-gradient(0deg,rgba(255,255,255,.022) 0 2px,transparent 2px 4px),repeating-linear-gradient(90deg,rgba(255,255,255,.015) 0 2px,transparent 2px 4px)}
/* 推子头：fill 前端米白竖帽（随 width 动画走） */
body.theme-b .okr-fill::after{content:"";position:absolute;right:0;top:-4px;bottom:-4px;width:4px;background:#E9E9E4;border-radius:1px;box-shadow:0 1px 2px rgba(0,0,0,.5)}
/* 4×4 键阵 */
body.theme-b .cov-strip{grid-template-columns:repeat(4,1fr)}
/* 一橙纪律：进度 fill 收灰（读数交给语义色与刻线）·纯橙只留焦点与交互 */
body.theme-b .okr-fill{background:#4A463C}
body.theme-b .kb-bar-row .bar-fill{background:#6E6A5E}
body.theme-b .kb-progress-fill{background:#6E6A5E}
body.theme-b .kb-progress-text{color:#F2F0E9}
/* 键阵厚度加深（凸起感） */
body.theme-b .cov-cell{box-shadow:0 3px 0 #A8A499,0 4px 7px rgba(23,21,15,.2)}
body.theme-b .footer{letter-spacing:.1em}
/* ── B v4.3 下半页功能色码（TE 按键分组色·油墨版）+第二块屏 + OKR语义色修复 ── */
/* OKR 语义色修复：v4.2 收灰规则特异性压掉了 f-green/f-red/f-amber——红色告警被抹（红必须能消），此处恢复 */
body.theme-b .okr-fill.f-green{background:var(--ok)}
body.theme-b .okr-fill.f-red{background:var(--bad)}
body.theme-b .okr-fill.f-amber{background:var(--warn)}
/* 知识库=第二块屏：内化流 L1-L4 是读数，屏语义成立（OP-1 主屏+编码器小屏的布局） */
body.theme-b .kb-flow{background:var(--screen);border:1px solid #23231F;border-radius:8px;padding:14px 18px;position:relative;overflow:hidden}
body.theme-b .kb-flow::before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 2px,transparent 2px 4px);pointer-events:none}
body.theme-b .kb-flow .stage{border-left-color:#23231F}
body.theme-b .kb-flow .stage .num{color:var(--lcd);text-shadow:0 0 9px rgba(237,237,228,.28)}
body.theme-b .kb-flow .stage.hot .num{color:var(--accent);text-shadow:0 0 12px rgba(255,90,31,.55)}
body.theme-b .kb-flow .stage .lbl{color:var(--lcd2)}
body.theme-b .kb-flow .stage .src{color:#5B5D52}
body.theme-b .kb-flow .stage .tag{color:var(--lcd2)}
body.theme-b .kb-flow .arrow{color:var(--lcd2)}
body.theme-b .kb-flow + .chart-note{color:var(--ink3)}
body.theme-b .kb-cell{box-shadow:0 2px 0 #B1ADA2}
body.theme-b .kb-cell.hot .val{color:var(--ok)}
/* 满额端去绿框改绿数字（2026-10-26 你令：外框难看·数字绿即可） */
body.theme-b .cov-cell.c-ok .rd{color:var(--ok)}
/* 卡类型功能色码：色=卡类型语义（TE 按键分组色的油墨低饱和版·oklch chroma≈0.06-0.1） */
/* 卡类型色码收敛（2026-10-26 你令收色）：只留知识卡分布+索引进度两条彩，其余归灰 */
body.theme-b .bar-fill.c-knowledge{background:#4A6FA5}
body.theme-b .bar-fill.c-stance,body.theme-b .bar-fill.c-concept,
body.theme-b .bar-fill.c-index,body.theme-b .bar-fill.c-skill{background:#6E6A5E}
body.theme-b .kb-progress-fill{background:#4A6FA5}
/* 碰撞分级恢复：强共识=高置信激活（信号橙）·互补=中灰·潜在=浅灰——三级不是装饰是置信度 */
/* 碰撞产出=完成态绿 */
body.theme-b .coll-prog-fill{background:var(--ok)}
/* 旋钮读数入屏色体系：kv=LCD亮字+辉光·kl=lcd2·ks=屏内灰（v4.3.1·修"黑字压黑屏看不清"） */
body.theme-b .hero .knob-row{border-top-color:#23231F}
body.theme-b .hero .knob-row .kv{color:var(--lcd);text-shadow:0 0 9px rgba(237,237,228,.28);font-size:30px}
body.theme-b .hero .knob-row .kl{color:var(--lcd2)}
body.theme-b .hero .knob-row .ks{color:#5B5D52}
/* ── B v4.3.2 浅色控件面质感：磨砂细网格（7px·密度高于底板28px=机件加工面）+顶部内高光（受光塑料缘）── */
body.theme-b .cov-cell,body.theme-b .kb-cell,body.theme-b .fd,
body.theme-b .ops .card,body.theme-b .drill-body,body.theme-b .tswitch{
 background-image:
  repeating-linear-gradient(0deg,rgba(23,21,15,.02) 0 1px,transparent 1px 7px),
  repeating-linear-gradient(90deg,rgba(23,21,15,.02) 0 1px,transparent 1px 7px);
}
body.theme-b .cov-cell{box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 3px 0 #A8A499,0 4px 7px rgba(23,21,15,.2)}
body.theme-b .kb-cell{box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 2px 0 #B1ADA2}
body.theme-b .fd{box-shadow:inset 0 1px 0 rgba(255,255,255,.4),0 1px 0 #EAE8E0,0 2px 5px rgba(23,21,15,.12)}
body.theme-b .ops .card{box-shadow:inset 0 1px 0 rgba(255,255,255,.4),0 1px 0 #EAE8E0}
body.theme-b .drill-body{box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}
/* 推子帽随行语义：达标（f-green）=米白帽·未达标/待量化（f-red/f-amber/f-gray）=墨黑帽（浅底上白帽像高亮·2026-10-26 你令） */
body.theme-b .okr-fill.f-red::after,body.theme-b .okr-fill.f-amber::after,body.theme-b .okr-fill.f-gray::after{background:#6E6A5E}
/* ═══════════ 主题 C · 印刷年报（Feltron） ═══════════ */
body.theme-c{
color-scheme:light;
--bg:#F7F4EC;--panel:transparent;--panel2:#EFEADF;--line:#D8D2C4;--line2:#1C1A17;
--text:#1C1A17;--ink2:#57534A;--ink3:#8B857A;
--accent:#C8371E;--ok:#4A7C59;--warn:#B07A2A;--bad:#C8371E;
--wrap-w:1180px;--radius:0;--btn-on-ink:#F7F4EC;--knob-base:#EFEADF;--knob-shadow:inset 0 0 0 1px #C4BCA9;--knob-cap:#1C1A17;
--f-sans:-apple-system,"Helvetica Neue","PingFang SC",system-ui,sans-serif;
--f-mono:"SF Mono",ui-monospace,Menlo,monospace;
--brand-size:30px;--brand-weight:800;
--hero-num-size:60px;--hero-num-weight:800;--hero-num-font:var(--f-sans);--hero-num-ls:-.03em;
--track-h:5px;--track-bg:var(--line);--track-shadow:none;--cov-gap:0;
--cov-ok-border:transparent;
--c-detected:#C8371E;--c-fixed:#4A6FA5;--c-immune:#4A7C59;--chart-grid:#D8D2C4;--chart-axis:#8B857A;
}
body.theme-c .topbar{border-bottom:3px solid var(--text)}
body.theme-c .brand .sub{letter-spacing:.22em}
body.theme-c .hero{padding:22px 0 0}
body.theme-c .flow{border-bottom:1px solid var(--line)}
body.theme-c .stage{border-left:1px solid var(--line);text-align:left;padding:4px 22px 20px}
body.theme-c .stage:first-child{border-left:none;padding-left:0}
body.theme-c .stage .tag{color:var(--ink3)}
body.theme-c .stage .lbl{font-weight:700}
body.theme-c .stage.hot .num{color:var(--accent)}
body.theme-c .hero-mid{border-bottom:1px solid var(--line);padding-bottom:20px}
body.theme-c .hero-side{border-left:1px solid var(--line)}
body.theme-c .card{border:1px solid var(--line);background:transparent}
body.theme-c .sec-head{border-bottom:1px solid var(--text);border-top:3px solid var(--text);padding:8px 0 8px;margin-top:34px}
body.theme-c .sec{margin-top:22px}
body.theme-c .fd{border:none;border-bottom:1px solid var(--line);background:transparent;border-radius:0;padding:13px 8px}
body.theme-c .fd .name{font-weight:700}
body.theme-c .fd .val{font-weight:700}
body.theme-c .okr-item{border-top:1px solid var(--line)}
body.theme-c .okr-idx{font-weight:800}
body.theme-c .okr-fill.f-green{background:var(--text)}
body.theme-c .okr-fill.f-red,body.theme-c .okr-fill.f-amber{background:var(--accent)}
body.theme-c .okr-tick{background:var(--accent);opacity:1}
/* C：平台覆盖改行式数据条 */
body.theme-c .cov-strip{grid-template-columns:1fr 1fr;gap:0 44px}
body.theme-c .cov-cell{display:grid;grid-template-columns:130px 1fr 58px;gap:10px;align-items:center;background:transparent;border:none;border-radius:0;border-bottom:1px solid var(--line);padding:8px 0}
body.theme-c .cov-cell .rd{margin-top:0;font-size:13px;text-align:right}
body.theme-c .cov-cell .ex{display:none}
body.theme-c .cov-cell .bar{display:block;margin-top:0}
body.theme-c .cov-cell .bar i{background:var(--text)}
body.theme-c .cov-cell.c-bad .bar i,body.theme-c .cov-cell.c-mid .bar i{background:var(--accent)}
body.theme-c .cov-cell.c-ok{border-color:transparent}
body.theme-c .summary{border-top:3px solid var(--text);border-radius:0;padding:26px 0 0;background:transparent}
body.theme-c .summary .text{font-size:23px;font-weight:800;letter-spacing:-.01em;max-width:860px}
body.theme-c .summary .text .em{color:var(--accent)}
body.theme-c .chip-neutral{border:none;color:var(--ink3)}
body.theme-c .tswitch button.on{background:var(--text);color:var(--bg)}
"""

HEAD_JS = """
// v1.0.1 零外链：内联 SVG 趋势图（原生 <title> 悬停读数·断网可渲染·无 Chart.js/字体 CDN）
// v4.1 主题化：折线/网格颜色从 body 的 CSS 变量读取（--c-detected/--c-fixed/--c-immune/--chart-grid/--chart-axis）
// ——三主题（a 终端/b 硬件/c 年报）各自定义变量值，切换主题后重调 renderTrend 即换色
(function(){
  function cssVar(name, fallback){
    try{
      var v = getComputedStyle(document.body).getPropertyValue(name).trim();
      return v || fallback;
    }catch(e){ return fallback; }
  }
  window.renderTrend=function(trend){
    var svg=document.getElementById("clTrend");
    if(!svg||!trend||!trend.length)return;
    window._lastTrend=trend;   // v4.1：留存末次数据，主题切换后由切换器重绘
    var SERIES=[
      ["detected", cssVar("--c-detected","#f0564f"), "检出"],
      ["fixed",    cssVar("--c-fixed",   "#5b8cff"), "留痕"],
      ["immune",   cssVar("--c-immune",  "#3ecf8e"), "免疫"]
    ];
    var MUTED=cssVar("--chart-axis","#8b90a0"),GRID=cssVar("--chart-grid","#252a35");
    var W=720,H=170,L=38,R=16,T=14,B=24,n=trend.length;
    var vals=[];trend.forEach(function(r){SERIES.forEach(function(s){if(typeof r[s[0]]==="number")vals.push(r[s[0]]);});});
    if(!vals.length)return;
    var rawMax=Math.max.apply(null,vals);
    var step=rawMax<=8?2:rawMax<=30?5:rawMax<=60?10:20;
    var ymax=Math.max(step,Math.ceil(rawMax/step)*step);
    function xp(i){return L+(W-L-R)*(n===1?0:i/(n-1));}
    function yp(v){return T+(H-T-B)*(1-v/ymax);}
    var out="";
    for(var g=0;g<=ymax;g+=step){
      var y=yp(g);
      out+='<line x1="'+L+'" y1="'+y.toFixed(1)+'" x2="'+(W-R)+'" y2="'+y.toFixed(1)+'" stroke="'+GRID+'" stroke-opacity=".7" stroke-width="1"/>';
      out+='<text x="'+(L-7)+'" y="'+(y+3).toFixed(1)+'" text-anchor="end" font-size="12" fill="'+MUTED+'">'+g+'</text>';
    }
    trend.forEach(function(r,i){
      out+='<text x="'+xp(i).toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle" font-size="12" fill="'+MUTED+'">'+r.date+'</text>';
    });
    SERIES.forEach(function(s){
      var key=s[0],col=s[1],name=s[2],pts=[];
      trend.forEach(function(r,i){pts.push([xp(i),yp(r[key]||0)]);});
      var d="";
      pts.forEach(function(p,i){d+=(i?" L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1);});
      out+='<path d="'+d+' L'+pts[n-1][0].toFixed(1)+' '+yp(0).toFixed(1)+' L'+pts[0][0].toFixed(1)+' '+yp(0).toFixed(1)+' Z" fill="'+col+'" opacity="0.07"/>';
      out+='<path d="'+d+'" fill="none" stroke="'+col+'" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>';
      pts.forEach(function(p,i){
        out+='<circle cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="2.4" fill="'+col+'"><title>'+trend[i].date+' · '+name+' '+(trend[i][key]||0)+'</title></circle>';
      });
      var lp=pts[n-1],lv=(trend[n-1][key]||0);
      out+='<text x="'+(lp[0]-7).toFixed(1)+'" y="'+(lp[1]-7).toFixed(1)+'" text-anchor="end" font-size="12" font-weight="600" fill="'+col+'">'+lv+'</text>';
    });
    svg.setAttribute("viewBox","0 0 "+W+" "+H);
    svg.setAttribute("preserveAspectRatio","xMidYMid meet");
    svg.innerHTML=out;
    var lg=document.getElementById("clLegend");
    if(lg)lg.innerHTML=SERIES.map(function(s){return '<span><i style="background:'+s[1]+'"></i>'+s[2]+'</span>';}).join("");
  };
})();
"""

LIVE_JS = """
(function(){
  var d = window.PANEL_DATA;
  if (!d) {
    var b = document.createElement('div');
    b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99;background:#f0564f;color:#fff;font:600 12px/1.6 system-ui;padding:8px 14px';
    b.textContent = '⚠️ panel_data.js 加载失败——下方数字为上次生成的快照，非实时（宁可少，不要假）';
    document.body.appendChild(b);
    return;
  }
  function set(id, v){ var el = document.getElementById(id); if(el && v !== undefined && v !== null) el.textContent = v; }
  set("panel-updated", d.updated);

  // v4.1 主题切换器：三主题共存（a 终端 / b 硬件 / c 年报）·localStorage 记住选择·切换后趋势图按新主题色重绘
  (function(){
    var sw = document.getElementById('theme-switch');
    if (!sw) return;
    var btns = sw.querySelectorAll('button');
    function curTheme(){
      var m = /theme-([abc])/.exec(document.body.className || '');
      return m ? m[1] : 'a';
    }
    function syncBtns(){
      var t = curTheme();
      btns.forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-t') === t); });
    }
    function apply(t){
      document.body.className = 'theme-' + t;
      try { localStorage.setItem('panel-theme', t); } catch(e){}
      syncBtns();
      if (window.renderTrend && window._lastTrend) window.renderTrend(window._lastTrend);
    }
    syncBtns();
    btns.forEach(function(b){
      b.addEventListener('click', function(){ apply(b.getAttribute('data-t')); });
    });
  })();

  var cl = d.closed_loop || {};
  set("cl-detected", cl.detected); set("cl-fixed", cl.fixed);
  set("cl-immune", cl.immune); set("cl-antibodies", cl.antibodies);
  // 差值为 hero 脚注 chip（不可消信号不占主视图·文案与口径声明保真）
  var pill = document.getElementById("cl-pending");
  if (pill) {
    if (cl.pending > 0) { pill.className = "chip chip-neutral"; pill.title = "粗口径=检出−留痕·非逐项核销·不代表积压"; pill.textContent = "检出−留痕差值 " + cl.pending + " · 粗口径·非核销"; }
    else if (cl.detected !== null && cl.detected !== undefined) { pill.className = "chip chip-ok"; pill.title = "粗口径=检出−留痕·两源独立计数·非核销"; pill.textContent = "检出 ≤ 留痕 · 粗口径"; }
  }
  var st = document.getElementById("summary-text");
  if (st && d.summary) { st.innerHTML = d.summary; }
  // 知识内化流动态注入（2026-08-26 根治硬编码快照·数据来自knowledge_ladder）
  var kl = d.knowledge_ladder;
  if (kl && kl.stats) {
    set("kf-l1", kl.stats.L1); set("kf-l2", kl.stats.L2);
    set("kf-l3", kl.stats.L3); set("kf-l4", kl.stats.L4);
    var kc = document.getElementById("kf-cand");
    if (kc && kl.skill_candidates !== undefined) {
      kc.textContent = "技能卡候选 " + kl.skill_candidates;
      kc.style.color = kl.skill_candidates > 0 ? "var(--warn)" : "var(--ink3)";
    }
    var kp = document.getElementById("kf-pill");
    if (kp && kl.l4_probe) {
      kp.textContent = (kl.stats.L4 > 0 ? "L4 已破冰 · 已内化 " + kl.stats.L4 + " 张" : "管道已通 · L4 待首例") + " · 试金石 " + kl.l4_probe.card + " 引用" + kl.l4_probe.total + "含你决策" + kl.l4_probe.ge;
    }
  }
  var fd = d.four_dir || {};
  if (fd.auto) set("fd-auto", fd.auto);
  if (fd.better) set("fd-better", fd.better);
  if (fd.evo) set("fd-evo", fd.evo);
  if (fd.knows) set("fd-knows", fd.knows);
  if (fd.knows_note) set("fd-knows-note", fd.knows_note);
  // 四方向卡 badge 与 OKR 区强一致：从 four_dir 的 state/evidence 更新徽标（过渡不冒充定案·定案显示机械 evidence）
  var stateMap = {auto: fd.auto_state, better: fd.better_state, evo: fd.evo_state, knows: fd.knows_state};
  var okrObjs = (d.okr && d.okr.objectives) || [];
  ['auto','better','evo','knows'].forEach(function(k){
    var oi = okrObjs.filter(function(o){return o.dir===k;})[0];
    var fdCard = document.querySelector('#fd-'+k);
    var cardEl = fdCard ? fdCard.closest('.fd') : null;
    if (cardEl) {
      var bd = cardEl.querySelector('.badge');
      var evRaw = (oi && oi.evidence) || '—';
      var stRaw = stateMap[k] || '';
      if (bd) bd.textContent = evRaw;
      var nm = cardEl.querySelector('.name');
      if (nm && stRaw) {
        var existing = nm.querySelector('.st-badge'); if (existing) existing.remove();
        var sb = document.createElement('span'); sb.className = 'st-badge'; sb.textContent = '· ' + stRaw; sb.style.cssText = 'font-weight:400;font-size:12px;opacity:.6;margin-left:4px;'; nm.appendChild(sb);
      }
    }
  });
  if (d.maintenance_line) set("maint-line", d.maintenance_line);
  if (cl.trend && cl.trend.length && window.renderTrend) { window.renderTrend(cl.trend); }
  // 接入率表
  if (!d.platform_rates) return;
  var html = '';
  d.platform_rates.forEach(function(r){
    var gapHtml = (r.gap !== undefined && r.gap !== null)
      ? '<span style="color:' + (r.gap>0?'var(--bad)':'var(--ok)') + '">缺 ' + r.gap + '</span>'
      : '—';
    var numHtml = (r.num !== undefined && r.num !== null)
      ? '<span style="color:' + r.color + ';font-weight:700">' + r.num + '/' + r.den + '</span>'
      : '—';
    var extraHtml = (r.extra > 0)
      ? ' <span title="平台附加守卫/端承载件(非共享清单)" style="color:var(--accent);font-weight:600">+' + r.extra + '</span>'
      : '';
    html += '<tr><td>' + r.name + '</td>' +
            '<td><span class="vmethod" title="' + r.note + '">' + (r.method || r.mark || '—') + '</span></td>' +
            '<td>' + numHtml + extraHtml + '</td><td>' + gapHtml + '</td></tr>';
  });
  var table = document.getElementById("rates-table");
  if (table) {
    table.innerHTML = '<tr><th>平台</th><th>核验</th><th>已接</th><th>缺口</th></tr>' + html;
    var upd = document.createElement("div");
    upd.style.cssText = 'font-size:12px;color:var(--ink3);font-family:var(--f-mono);margin-top:8px;text-align:right';
    upd.textContent = '数据更新: ' + (d.updated || '—');
    table.parentElement.appendChild(upd);
  }
  // 季度 OKR 目标对照层（目标线 vs 实际进度·动态注入，改 okr_quarter.json→重跑脚本→刷新即变）
  var okr = d.okr;
  if (okr) {
    var rem = document.getElementById("okr-remaining");
    if (rem && okr.remaining !== undefined && okr.remaining !== null) rem.textContent = "剩余 " + okr.remaining + " 天 · 目标/当前由 okr_quarter.json + 脚本机械映射 · 自然季度框定";
    (okr.objectives || []).forEach(function(o){
      var pctEl = document.getElementById("o-pct-" + o.dir);
      var fillEl = document.getElementById("o-fill-" + o.dir);
      var stEl = document.getElementById("o-st-" + o.dir);
      if (!pctEl || !fillEl) return;
      if (o.current === null || o.current === undefined) {
        pctEl.textContent = "N/A";
        if (stEl) stEl.textContent = "待量化";
        fillEl.className = "okr-fill f-gray"; fillEl.style.width = "0%";
        return;
      }
      var tgt = o.target_pct || 1, p = o.current / tgt * 100, disp = Math.min(Math.round(p), 100); // A v2 封顶100
      var cls = p >= 100 ? "f-green" : p >= 70 ? "f-amber" : "f-red";
      pctEl.textContent = cls === "f-green" ? disp + "% ✓" : disp + "%";
      if (stEl) stEl.textContent = "当前 " + o.current + (o.unit === "rate" ? "%" : "");
      fillEl.className = "okr-fill " + cls;
      fillEl.style.width = Math.min(p, 100) + "%";
    });
  }

  // 知识库可视化数据加载（2026-09-08 童灵根治·合并入panel_snapshot.py）
  var kb = d.knowledge_base;
  if (kb) {
    if (kb.ai_lib) set("kb-ai-lib", kb.ai_lib.total);
    if (kb.obsidian_kb) set("kb-obsidian", kb.obsidian_kb.total_md);
    if (kb.blueprint) set("kb-blueprint", kb.blueprint.total_md);
    if (kb.federation) set("kb-total", kb.federation.total);
    var fc = kb.federated_cards || {};
    set("kb-stance", fc.stance); set("kb-concept", fc.concept);
    set("kb-knowledge", fc.knowledge); set("kb-skill", fc.skill);
    var maxCard = Math.max(fc.knowledge||0, fc.stance||0, fc.concept||0, fc.index||0, fc.skill||0, 1);
    var cardBars = [
      {id:"kb-bar-knowledge", count:"kb-count-knowledge", val:fc.knowledge},
      {id:"kb-bar-stance", count:"kb-count-stance", val:fc.stance},
      {id:"kb-bar-concept", count:"kb-count-concept", val:fc.concept},
      {id:"kb-bar-index", count:"kb-count-index", val:kb.index_cards?kb.index_cards.generated:0},
      {id:"kb-bar-skill", count:"kb-count-skill", val:fc.skill}
    ];
    cardBars.forEach(function(c){
      var bar = document.getElementById(c.id);
      var cnt = document.getElementById(c.count);
      if (bar && c.val !== undefined) { bar.style.width = Math.max(c.val/maxCard*100, 0.5) + "%"; }
      if (cnt && c.val !== undefined) { cnt.textContent = c.val; }
    });
    var ic = kb.index_cards;
    if (ic) {
      var fill = document.getElementById("kb-progress-fill");
      var text = document.getElementById("kb-progress-text");
      if (fill) fill.style.width = ic.progress_pct + "%";
      if (text) text.textContent = ic.generated + " / " + ic.total_needed + " · " + ic.progress_pct + "%";
    }
  }
})();
"""

def _stage(num, tag, lbl, src, num_id, hot=False):
    return ('<div class="stage{hot}"><div class="tag">{tag}</div><div class="num" id="{i}">{n}</div>'
            '<div class="lbl">{l}</div><div class="src">{s}</div></div>').format(
        hot=(" hot" if hot else ""), tag=tag, i=num_id,
        n=("—" if num is None else num), l=lbl, s=src)

def render_html(snap):
    cl = snap.get("closed_loop", {}) or {}
    det, fix, imm = cl.get("detected"), cl.get("fixed"), cl.get("immune")
    anti, pending = cl.get("antibodies"), cl.get("pending") or 0
    trend = cl.get("trend") or []
    today_md = (snap.get("date") or "")[5:]   # "MM-DD"
    trend_plot = [r for r in trend if r.get("date") != today_md]  # 今日进行中不入图·防零值断崖

    # ── L0 心跳：闭环流（全页唯一主角·v4.1 三主题皮肤·检测格 hot 高亮） ──
    flow_html = (
        _stage(det, "DETECT", "检测 · DRIFT 检出", "platform_adaptation_check.log", "cl-detected", hot=True) +
        '<div class="arrow">→</div>' +
        _stage(fix, "FIX", "修正 · 变更留痕", "变更日志 WorkBuddy 行", "cl-fixed") +
        '<div class="arrow">→</div>' +
        _stage(imm, "IMMUNE", "免疫 · 复发监测", "免疫复发记录「命中」（本周·0=无复发=抗体生效）", "cl-immune") +
        '<div class="arrow">→</div>' +
        _stage(anti, "ANTIBODY", "抗体库 · 累计", "规范反哺日志「🛡」", "cl-antibodies")
    )
    if det is not None and fix is not None and det > fix:
        pill = '<span class="chip chip-neutral" id="cl-pending" title="粗口径=检出−留痕·非逐项核销·不代表积压">检出−留痕差值 {} · 粗口径·非核销</span>'.format(det - fix)
    elif det is not None:
        pill = '<span class="chip chip-ok" id="cl-pending" title="粗口径=检出−留痕·两源独立计数·非核销">检出 ≤ 留痕 · 粗口径</span>'
    else:
        pill = '<span class="chip chip-neutral" id="cl-pending">数据采集中</span>'

    # 四方向状态灯（SSR·与 OKR 同源·L0 十秒心跳的一部分）
    _okr_map = {}
    for _o in ((snap.get("okr") or {}).get("objectives") or []):
        _okr_map[_o.get("dir")] = _o
    _EV_DOT = {"🟢": "ev-g", "🟡": "ev-a", "🔴": "ev-r"}
    def _hs(dirkey):
        o = _okr_map.get(dirkey) or {}
        cur, tgt = o.get("current"), o.get("target_pct")
        # 口径统一（2026-10-26 你令）：灯条读数=季度达成度%（与 OKR 进度条同口径·封顶100）；
        # 当前值/目标收进悬停明细——计数型（knows 条/目标）也在此转达成度，防 4/30 与百分比混排致晕
        if cur is None or not tgt:
            disp = "—"
        else:
            disp = "{}%".format(min(round(cur / tgt * 100), 100))
        dot = _EV_DOT.get(o.get("evidence"), "ev-n")
        cur_txt = "{}{}".format(cur, ("%" if o.get("unit") == "rate" else " 条"))
        title = "当前 {} · 目标 ≥{} · 达成度 {}".format(cur_txt, tgt, disp)
        if dirkey == "knows":
            title += " · 时间进度 {}%".format(snap.get("quarter_time_pct"))
        return ('<div class="hs-item" title="{tt}"><span class="dot {d}"></span>'
                '<span class="nm">{n}</span><span class="vl">{v}</span></div>').format(
            tt=title, d=dot, n=o.get("name") or dirkey, v=disp)
    # 季度时间进度旋钮（P2·指针角度=进度·SSR·三主题皮肤）
    _qtp = snap.get("quarter_time_pct")
    _okr_q = snap.get("okr") or {}
    if isinstance(_qtp, (int, float)):
        _knob_deg = round(-135 + (_qtp / 100.0) * 270, 1)   # 旋钮行程 270°：-135°(0%) → +135°(100%)
    else:
        _knob_deg = -135
    knob_html = (
        '<div class="knob-row">'
        '<div class="knob"><div class="base"></div>'
        '<div class="needle" style="transform:translateX(-50%) rotate({deg}deg)"></div>'
        '<div class="cap"></div></div>'
        '<div><div class="kv">{pct}%</div><div class="kl">季度时间进度</div>'
        '<div class="ks">{qs} → {qe} · 剩 {rem} 天</div></div>'
        '</div>'
    ).format(deg=_knob_deg,
             pct=(_qtp if _qtp is not None else "—"),
             qs=(_okr_q.get("start") or "—"), qe=(_okr_q.get("end") or "—"),
             rem=(_okr_q.get("remaining") if _okr_q.get("remaining") is not None else "—"))
    hero_side = (
        '<div class="hero-side"><div class="hside-title">四方向 · 季度达成度</div>'
        + _hs("auto") + _hs("better") + _hs("evo") + _hs("knows") +
        knob_html +
        '</div>'
    )
    hero = (
        '<section class="hero">'
        '<div class="hero-head">'
        '<span class="no">01</span><span class="t">系统心跳 · 闭环流</span>'
        '<span class="m">本周流量 · 检测 → 修正 → 免疫 → 抗体库 ↺ 自主进化回路</span></div>'
        '<div class="flow">{f}</div>'
        '<div class="hero-mid">'
        '<div><div class="chart-box"><div class="chart-legend" id="clLegend"></div><svg id="clTrend" role="img" aria-label="近7日闭环流趋势"></svg></div>'
        '<div class="chart-note">近7日逐日流量 · 今日进行中不入图（防零值断崖） · 结构性基线从 2026-08-21 起自动积累（缺数日=0·不编造）&nbsp;&nbsp;{p}</div></div>'
        '{s}</div>'
        '</section>'
    ).format(f=flow_html, p=pill, s=hero_side)

    # ── 知识内化流（L1-L4·知识库分区内的一行流·v4.1 加 mono 阶梯标签） ──
    kl = snap.get("knowledge_ladder") or {}
    kl_stats = kl.get("stats") or {}
    kl_probe = kl.get("l4_probe")
    def _klv(k):
        v = kl_stats.get(k)
        return v if v is not None else "—"
    probe_txt = ""
    if kl_probe:
        probe_txt = " · 试金石 {} 引用{}含你决策{}".format(kl_probe["card"], kl_probe["total"], kl_probe["ge"])
    if _klv("L4") == 0 and _klv("L4") != "—":
        kl_chip = '<span class="chip chip-ok" id="kf-pill" title="引用登记已自动化·L4 首例待你决策引用触发">管道已通 · L4 待首例{}</span>'.format(probe_txt)
    else:
        kl_chip = '<span class="chip chip-ok" id="kf-pill">L4 已破冰</span>'
    ladder_html = (
        '<div class="kb-flow">'
        '<div class="stage"><div class="tag">L1</div><div class="num" id="kf-l1">{l1}</div><div class="lbl">提炼 · 待质证</div><div class="src">AI学习库</div></div>'
        '<div class="arrow">→</div>'
        '<div class="stage"><div class="tag">L2</div><div class="num" id="kf-l2">{l2}</div><div class="lbl">质证 · 初审</div><div class="src">分身初审 / 你锤事件</div></div>'
        '<div class="arrow">→</div>'
        '<div class="stage"><div class="tag">L3</div><div class="num" id="kf-l3">{l3}</div><div class="lbl">应用 · 自动登记</div><div class="src">引用台账</div></div>'
        '<div class="arrow">→</div>'
        '<div class="stage hot"><div class="tag">L4</div><div class="num" id="kf-l4">{l4}</div><div class="lbl">内化 · 引用≥3 含你决策</div><div class="src">引用台账</div></div>'
        '<div style="margin-left:auto;display:flex;flex-direction:column;gap:6px;align-items:flex-end">'
        '<span id="kf-cand" style="font-size:12px;color:var(--ink3);font-family:var(--f-mono)">技能卡候选 {sc}</span>'
        '{chip}</div>'
        '</div>'
        '<div class="chart-note">知识内化回路（2026-08-26 童灵打通）· 更新于 {upd} · 每批碰撞/你确认自动登记引用</div>'
    ).format(l1=_klv("L1"), l2=_klv("L2"), l3=_klv("L3"), l4=_klv("L4"),
             sc=kl.get("skill_candidates", 0), chip=kl_chip, upd=kl.get("updated", "—"))

    # ── 知识库联邦（规模读数·方法论收进下钻） ──
    kb = snap.get("knowledge_base") or {}
    fc = kb.get("federated_cards", {}) or {}
    ic = kb.get("index_cards", {}) or {}
    ai_lib = kb.get("ai_lib", {}) or {}
    obs_kb = kb.get("obsidian_kb", {}) or {}
    bp = kb.get("blueprint", {}) or {}
    fed = kb.get("federation", {}) or {}
    def _kbv(d, k, default="—"):
        v = d.get(k)
        return v if v is not None else default
    max_card = max(_kbv(fc, "knowledge", 0), _kbv(fc, "stance", 0), _kbv(fc, "concept", 0), _kbv(ic, "generated", 0), _kbv(fc, "skill", 0), 1)
    def _bar_w(val):
        return max(val / max_card * 100, 0.5) if max_card > 0 else 0.5
    kb_html = (
        '<div class="card">'
        + ladder_html +
        '<div style="height:16px"></div>'
        '<div class="kb-grid">'
        '<div class="kb-cell"><div class="label">AI学习库</div><div class="val" id="kb-ai-lib">{v1}</div><div class="src">立场卡+技能卡+其他</div></div>'
        '<div class="kb-cell"><div class="label">Obsidian知识库</div><div class="val" id="kb-obsidian">{v2}</div><div class="src">10子目录 · 知识池/概念层/读书笔记</div></div>'
        '<div class="kb-cell"><div class="label">记忆蓝图</div><div class="val" id="kb-blueprint">{v3}</div><div class="src">6顶层目录 · 设计哲学/开发规范</div></div>'
        '<div class="kb-cell hot"><div class="label">联邦总规模</div><div class="val" id="kb-total">{v4}</div><div class="src">AI学习库+Obsidian+蓝图</div></div>'
        '<div class="kb-cell"><div class="label">立场卡</div><div class="val" id="kb-stance">{v5}</div><div class="src">AI学习库 · 决策判据</div></div>'
        '<div class="kb-cell"><div class="label">概念卡</div><div class="val" id="kb-concept">{v6}</div><div class="src">Obsidian 08-概念层</div></div>'
        '<div class="kb-cell"><div class="label">知识卡</div><div class="val" id="kb-knowledge">{v7}</div><div class="src">Obsidian 05-知识池</div></div>'
        '<div class="kb-cell"><div class="label">技能卡</div><div class="val" id="kb-skill">{v8}</div><div class="src">AI学习库 · Skill用法卡</div></div>'
        '</div>'
        '<div class="kb-bars">'
        '<div class="kb-bar-row"><div class="name">知识卡</div><div class="bar-track"><div class="bar-fill c-knowledge" id="kb-bar-knowledge" style="width:{bw1}%"></div></div><div class="count" id="kb-count-knowledge">{c1}</div></div>'
        '<div class="kb-bar-row"><div class="name">立场卡</div><div class="bar-track"><div class="bar-fill c-stance" id="kb-bar-stance" style="width:{bw2}%"></div></div><div class="count" id="kb-count-stance">{c2}</div></div>'
        '<div class="kb-bar-row"><div class="name">概念卡</div><div class="bar-track"><div class="bar-fill c-concept" id="kb-bar-concept" style="width:{bw3}%"></div></div><div class="count" id="kb-count-concept">{c3}</div></div>'
        '<div class="kb-bar-row"><div class="name">蓝图索引卡</div><div class="bar-track"><div class="bar-fill c-index" id="kb-bar-index" style="width:{bw4}%"></div></div><div class="count" id="kb-count-index">{c4}</div></div>'
        '<div class="kb-bar-row"><div class="name">技能卡</div><div class="bar-track"><div class="bar-fill c-skill" id="kb-bar-skill" style="width:{bw5}%"></div></div><div class="count" id="kb-count-skill">{c5}</div></div>'
        '</div>'
        '<div class="kb-progress-track"><div class="kb-progress-fill" id="kb-progress-fill" style="width:{pp}%"></div><div class="kb-progress-text" id="kb-progress-text">{pg} / {pt} · {pp}%</div></div>'
        '<div class="kb-progress-meta"><span>蓝图索引卡已生成 {pg} 张</span><span>待生成 {pd} 张</span>{watch}</div>'
        '<details class="drill"><summary>统计方法 · 数据链 · 运作机制 ▾</summary><div class="drill-body">'
        '<b>三维度联合识别方法</b>：文件名前缀 + YAML type字段 + 目录位置，不强制改名，联邦多路径统计。立场卡=AI学习库立场卡#前缀，概念卡=Obsidian 08-概念层目录，知识卡=Obsidian 05-知识池目录，技能卡=AI学习库技能卡#前缀。<br><br>'
        '<b>数据链</b>：kb_metadata_extract.py 机械采集（无人工填报）· 每日 07:30 · 蓝图索引卡=记忆蓝图文件的索引卡（核心原则+摘要+路径指针），进知识库可被语义检索；条形图按数量比例渲染。<br><br>'
        '<b>童灵全系统导航协议（K2 W1第12条）</b>：蓝图结构（6顶层目录）+ 映射表（蓝图文件→索引卡路径）+ 渐进式加载4步（L0恒驻核→L1条目索引→L2域切片→L3单条目）+ 7大域导航路径。检索引擎=search_kb.py（5源联邦检索·三路融合）；卡片碰撞=概念卡+知识卡+立场卡三向碰撞产生新洞察；增量更新=launchd 每日 07:30 自动校验。'
        '</div></details>'
        '</div>'
    ).format(
        v1=_kbv(ai_lib, "total"), v2=_kbv(obs_kb, "total_md"), v3=_kbv(bp, "total_md"), v4=_kbv(fed, "total"),
        v5=_kbv(fc, "stance"), v6=_kbv(fc, "concept"), v7=_kbv(fc, "knowledge"), v8=_kbv(fc, "skill"),
        bw1=_bar_w(_kbv(fc, "knowledge", 0)), c1=_kbv(fc, "knowledge"),
        bw2=_bar_w(_kbv(fc, "stance", 0)), c2=_kbv(fc, "stance"),
        bw3=_bar_w(_kbv(fc, "concept", 0)), c3=_kbv(fc, "concept"),
        bw4=_bar_w(_kbv(ic, "generated", 0)), c4=_kbv(ic, "generated"),
        bw5=_bar_w(_kbv(fc, "skill", 0)), c5=_kbv(fc, "skill"),
        pp=_kbv(ic, "progress_pct", 0), pg=_kbv(ic, "generated"), pt=_kbv(ic, "total_needed"),
        pd=_kbv(ic, "pending", 0),
        # 2026-09-27 童灵根治：守卫状态改读数据字段（watch_active），⛔不再硬编码✅——假绿=反模式
        watch=('<span>防漂移校验 ✅</span><span>launchd增量监控 ✅</span>'
               if _kbv(ic, "watch_active", False)
               else '<span style="color:var(--warn)">⚠️ 防漂移守卫未挂载（kb-card-version-watch / blueprint-index-watcher 均缺位）</span>')
    )

    # ── 四方向详情卡（愿景进度分区·L1 层·长注收 title 悬停·n·CI 随 val 同屏） ──
    def _pf(v):  # percent-or-dash
        return ("{}%".format(v) if isinstance(v, (int, float)) else "—")
    _oa = _okr_map.get("auto") or {}
    auto_txt = "自动触发占比 {} · 覆盖 {}".format(
        _pf(_oa.get("auto_closure")), _oa.get("auto_cov") or "—")
    auto_badge = _oa.get("evidence") or "🔴"
    imm_h = snap.get("better_immune_hits")
    anti_e = snap.get("better_antibodies")
    better_base = snap.get("better_baseline")
    if snap.get("better_state") == "定案" and snap.get("better_join_active") is not None:
        better_txt = "漏触发修复率(近14天活跃) {:.0%} · 全史对照 {:.0%} · 双载体池 {} 条".format(
            snap["better_join_active"], (snap.get("better_join_all") or 0),
            snap.get("better_pool") or "—")
    else:
        better_txt = "免疫命中 {}（累计） · 有效抗体 {}".format(imm_h if imm_h is not None else "—", anti_e if anti_e is not None else "—")
    better_ev = snap.get("better_evidence") or "🟢"
    evo_v = snap.get("evo_events")
    _ci = snap.get("evo_rate_ci") or []
    evo_txt = "本季提案 {} · 采纳 {} · 豁免 {} · 未决 {} · 净采纳率 {}（n={} · 95%CI {}）".format(
        evo_v if evo_v is not None else "—",
        snap.get("evo_adopted") if snap.get("evo_adopted") is not None else "—",
        snap.get("evo_waived") if snap.get("evo_waived") is not None else "—",
        snap.get("evo_pending") if snap.get("evo_pending") is not None else "—",
        ("{:.0f}%".format(snap.get("evo_adoption_rate") * 100) if snap.get("evo_adoption_rate") is not None else "待量"),
        snap.get("evo_rate_n") if snap.get("evo_rate_n") is not None else "—",
        ("{:.0f}–{:.0f}%".format(_ci[0] * 100, _ci[1] * 100) if len(_ci) == 2 else "—"))
    evo_badge = snap.get("evo_evidence") or "🔴"
    knows_v = snap.get("knows_count")
    knows_dl = snap.get("knows_days_left")
    _ok = _okr_map.get("knows") or {}
    knows_txt = "本月 {} 条 · 本季累计 {}/{} · 时间进度 {}% · 剩 {} 天".format(
        knows_v if knows_v is not None else "—",
        _ok.get("current") if _ok.get("current") is not None else "—",
        _ok.get("target_pct") if _ok.get("target_pct") is not None else "—",
        snap.get("quarter_time_pct") if snap.get("quarter_time_pct") is not None else "—",
        knows_dl if knows_dl is not None else "—")
    knows_badge = _ok.get("evidence") or snap.get("knows_evidence") or "🟡"
    fourdir = (
        '<div class="fourdir">'
        '<div class="fd" title="值为 hook_auto 触发占比(愿景①=机制自动运转不依赖人记得·自动触发调用/总调用) · 手动调用累积会拉低占比(非自动化退化) · returncode 成功=100%(可靠性) · 覆盖N/M独立读数">'
        '<div class="name">① 全自动化 <span class="badge" title="愿景①真义=机制自动运转不依赖人记得·值为hook_auto触发占比(自动触发调用/总调用)·手动调用累积会拉低占比(非自动化退化)">{ab}</span></div>'
        '<div class="val" id="fd-auto">{av}</div><div class="note">hook_auto 触发占比 · 手动调用累积拉低占比≠自动化退化 · 🧪过程代理</div></div>'
        '<div class="fd">'
        '<div class="name">② 越用越好用 <span class="badge" title="定案(v0.5)=漏触发修复率·两池join≥90%门槛实过">{be}</span></div>'
        '<div class="val" id="fd-better">{bv}</div><div class="note">定案口径=漏触发修复率（两池join）· 免疫命中/抗体为过渡基线</div></div>'
        '<div class="fd">'
        '<div class="name">③ 自主进化 <span class="badge" title="净采纳率=采纳÷(采纳+未决)·豁免排除分母·小样本带95%CI">{ee}</span></div>'
        '<div class="val" id="fd-evo">{ev}</div><div class="note">三态口径 · 分母=采纳+未决 · 比率必带 n 与区间</div></div>'
        '<div class="fd">'
        '<div class="name">④ 越懂你 <span class="badge" title="过渡方向·代理计数证据封顶🟡">{kb}</span></div>'
        '<div class="val" id="fd-knows">{kv}</div><div class="note" id="fd-knows-note">过渡=认知发现数·自然月归当月 · 定案=预测准确率（需先建「预测vs实际」成对标签）</div></div>'
        '</div>'
    ).format(ab=auto_badge, av=auto_txt, be=better_ev, bv=better_txt,
             ee=evo_badge, ev=evo_txt, kb=knows_badge, kv=knows_txt)

    okr_html = build_okr_html(snap)   # 季度 OKR 目标对照层（v4.1·口径收下钻·达标线 tick）

    # ── 运营行：维护成本 + 价值层（待量化明示·不装假指标） ──
    mt = snap.get("maintenance", {}) or {}
    if mt.get("total_commits") is not None:
        segs = " · ".join("{} {}".format(s["segment"], s["commits"]) for s in mt.get("segments", []) if s.get("commits") is not None)
        maint_line = "近7天共 {} 次提交 · 环节Top：{}（环节口径≠总量口径·示集中度）".format(mt["total_commits"], segs)
    else:
        maint_line = "数据采集中（环节维护台账.py 待产出）"
    ops = (
        '<div class="ops">'
        '<div class="card"><h4>维护成本 · GIT 环节统计</h4><div class="line" id="maint-line">{ml}</div></div>'
        '<div class="card"><h4>价值层 · 北极星产出轴（S451 投资回收轴 · 建/停决策依据）</h4><div class="line">待量化（定义中：本周「系统帮你产出」事件数——视频发布 / 文案产出 / 账号数据） · 无数据源不上假指标</div></div>'
        '</div>'
    ).format(ml=maint_line)

    # ── 平台覆盖（16 端色带一眼扫缺口·明细表收下钻·v4.1 加数据条供 C 主题行式呈现） ──
    ssot_cov = _parse_coverage_from_ssot()
    rates = snap.get("platform_rates", {})
    def rate_key(item):
        v = item[1]
        return (v[0] / v[1]) if v and v[1] else -1
    METHOD_TXT = {"🟢": "机械", "🟡": "自核", "🔴": "自治"}
    cov_cells = ""
    rate_rows = ""
    verified = 0
    known = 0
    for name, v in sorted(rates.items(), key=rate_key, reverse=True):
        if v is None:
            cov_cells += '<div class="cov-cell c-bad" title="{n}"><div class="nm">{n}</div><div class="rd">—</div><div class="ex">未登记</div><div class="bar"><i style="width:0%"></i></div></div>\n'.format(n=name)
            rate_rows += '<tr><td>{}</td><td><span class="vmethod">未登记</span></td><td>—</td><td>—</td></tr>\n'.format(name)
            continue
        num, den = v
        known += 1
        mark, note = ssot_cov.get(name, ("❔", "未登记"))
        if mark == "🟢":
            verified += 1
        gap = den - num
        ratio = (num / den) if den else 0
        cell_cls = "c-ok" if gap == 0 else ("c-mid" if ratio >= 0.5 else "c-bad")
        bar_w = round(ratio * 100, 1)
        cov_cells += ('<div class="cov-cell {c}" title="{n}"><div class="nm">{n}</div>'
                      '<div class="rd">{a}/{b}</div><div class="ex">{m}</div>'
                      '<div class="bar"><i style="width:{w}%"></i></div></div>\n').format(
            c=cell_cls, n=name, a=num, b=den, m=METHOD_TXT.get(mark, "未登记"), w=bar_w)
        pct = round(num / den * 100) if den else 0
        color = "var(--ok)" if pct >= 80 else ("var(--warn)" if pct >= 50 else "var(--bad)")
        rate_rows += ('<tr><td>{}</td>'
                      '<td><span class="vmethod" title="{}">{}</span></td>'
                      '<td style="color:{};font-weight:700">{}/{}</td>'
                      '<td style="color:{}">缺 {}</td></tr>\n').format(
            name, note, METHOD_TXT.get(mark, "未登记"), color, num, den,
            ("var(--bad)" if gap > 0 else "var(--ok)"), gap)
    platform_sec = (
        '<section class="sec">'
        '<div class="sec-head"><span class="no">04</span><span class="t">平台覆盖</span>'
        '<span class="m">已登记 {k} 端 · 🟢机械核验 {v} · N/M=12项共享清单实盘读数</span></div>'
        '<div class="cov-strip">{cells}</div>'
        '<details class="rates"><summary><span class="hint">{k} 端明细表 · 核验方式与缺口 ▾</span></summary>'
        '<table id="rates-table"><tr><th>平台</th><th>核验</th><th>已接</th><th>缺口</th></tr>{rows}</table>'
        '</details>'
        '</section>'
    ).format(k=known, v=verified, cells=cov_cells, rows=rate_rows)

    # ── 05 数字分身（2026-10-26 你纠偏升独立 section：分身=治理主体"谁在值班"，
    #    非知识库子域——初版蹭 suspend-mount 注入链属路径依赖，现归位） ──
    twin_sec = (
        '<section class="sec">'
        '<div class="sec-head"><span class="no">05</span><span class="t">数字分身 · 状态与治理</span>'
        '<span class="m">校准飞轮 · 岗位名册 · 纪律漂移 · 数据源=job台账/calibration/告警机</span></div>'
        '<div id="twin-mount"></div>'
        '</section>'
    )

    # ── 终点：一句话总结（峰终·终点） ──
    summary = build_summary(cl)
    summary_card = (
        '<div class="summary">'
        '<div class="bolt">⚡</div>'
        '<div><div class="text" id="summary-text">{}</div>'
        '<div class="meta">一句话总结 · 自动生成于 {} · 源: platform_adaptation_check / 变更日志 / 免疫复发记录 / 规范反哺日志</div></div>'
        '</div>'
    ).format(summary, snap.get("date", "—"))

    today_str = snap.get("date", "—")
    html = (
        '<!doctype html>\n<html lang="zh">\n<head>\n<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>\n'
        '<title>布洛陀 · 系统面板 v4.1</title>\n'
        '<!-- v1.1.0 三主题系统：a 终端 / b 硬件 / c 年报 · 右上角切换 · localStorage 记住选择 · 零外链保留 -->\n'
        '<style>' + CSS + '</style>\n'
        '<script>' + HEAD_JS + '</script>\n'
        '</head>\n<body class="theme-a">\n'
        '<script>try{var _t=localStorage.getItem("panel-theme");if(_t==="a"||_t==="b"||_t==="c"){document.body.className="theme-"+_t;}}catch(e){}</script>\n'
        '<div class="wrap">\n'
        '<header class="topbar">'
        '<div class="lft">'
        '<div class="brand">布洛陀 · 系统面板<span class="ver">v4.1 · 三主题</span></div>'
        '<div class="sub">BULUOTUO SYSTEM PANEL · 自主进化系统监测</div>'
        '</div>'
        '<div class="rgt">'
        '<div class="tswitch" id="theme-switch">'
        '<button type="button" data-t="a">终端</button>'
        '<button type="button" data-t="b">面板</button>'
        '<button type="button" data-t="c">年报</button>'
        '</div>'
        '<div class="live"><span class="dot"></span>活 · <span id="panel-updated">' + today_str + '</span></div>'
        '</div>'
        '</header>\n'
        + hero + "\n"
        + '<section class="sec">'
        + '<div class="sec-head"><span class="no">02</span><span class="t">愿景进度 · 季度 OKR</span><span class="m">四方向原生读数 · 不合成总分（量纲不同不可加）</span></div>'
        + fourdir + okr_html + ops +
        '</section>\n'
        + '<section class="sec">'
        + '<div class="sec-head"><span class="no">03</span><span class="t">知识库</span><span class="m">内化阶梯 · 联邦统计 · 碰撞机制 · kb_metadata_extract 机械采集</span></div>'
        + kb_html + "\n" + '<div id="collision-mount"></div>' + '<div id="suspend-mount"></div>'
        '</section>\n'
        + platform_sec + "\n" + twin_sec + "\n" + summary_card + '\n'
        '</div>\n'
        '<div class="footer">'
        '<span>最后更新: ' + today_str + ' · v4.1 三主题：终端 / 面板 / 年报（右上角切换·记住选择） · 峰终保留（峰值=闭环流 · 终点=一句话）</span>'
        '<span>数据源: evolution_deviation / 环节维护台账 / 各端 settings.json · 刷新即最新 · 零外链</span>'
        '</div>\n'
        '<script>window.PANEL_DATA = ' + json.dumps(write_panel_data_js(snap), ensure_ascii=False) + ';</script>\n'
        '<script>window.renderTrend(' + json.dumps(trend_plot, ensure_ascii=False) + ');</script>\n'
        '<script>' + LIVE_JS + '</script>\n'
        '</body>\n</html>\n'
    )
    return html

def write_live_html(html):
    os.makedirs(os.path.dirname(LIVE_HTML), exist_ok=True)
    with open(LIVE_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("[panel_snapshot] 已渲染 {}".format(LIVE_HTML))

def write_panel_data_js(snap):
    """生成 panel_data.js（刷新即最新核心）。

    HTML 用 <script src="panel_data.js"> 加载（script 不受 file:// CORS 限制），
    页面每次加载/刷新都会重新读取本文件 → 数据与 HTML 渲染解耦：
    fswatch/Stop 钩子更新本文件 → 你刷新网页 = 读到最新数据（v0.6：闭环流/四方向/维护成本/总结全量覆盖）。
    """
    cl = snap.get("closed_loop", {}) or {}
    rates = snap.get("platform_rates", {})
    # 自动解析 SSOT（与 render_html 用同一个函数·数据同源）
    coverage = _parse_coverage_from_ssot()
    # 保底：auto-parse 缺失的平台按 SSOT 自核签名补
    for name in rates:
        if name not in coverage:
            ssot_path = os.path.join(MC, "记忆蓝图/04_系统文件设计/布洛陀脚本架构设计哲学/04-跨端接入指南.md")
            try:
                with open(ssot_path, encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                txt = ""
            if re.search(re.escape(name) + r"\s*自核", txt):
                coverage[name] = ("🟢", "自核签名 · 登记自 SSOT §二·七")
    # 共享 12 项分母名单（SHARED12）——名称 = 实际条目数，与 load_live_rates 的 HOOKS12 逐项对齐。
    # 2026-10-25 v0.9.13：原名单 13 项含 **已退役** 的 reply_format_guard
    #   （退役台账 脚本中心/守卫/retired-hooks.json：2026-08-13 你令退役·08-26 完全删除·form=entity_deleted）
    #   ⇒ 名单与退役台账脱钩（判据面读到不存在的项）。全端 6 个挂载面实测 hit=0
    #   （workbuddy / qoder-cn / qoder / trae-cn / zcode / minimaxcode）⇒ 清理**零数值影响**，
    #   纯口径归正（名单数 13→12 = 真实分母 12）。
    SHARED12 = ["crossend_guard","route_inject_prompt","route_miss_feeder","kb_inject_prompt",
        "route_unknown_unknown","audit_search_kb","route_audit","route_guard_audit",
        "feedback_detect","rule_three_layer_guard","card_id_guard","title_namer"]
    PLATFORM_CFG = {
        "WorkBuddy": os.path.expanduser("~/.workbuddy/settings.json"),
        "Qoder CN": os.path.expanduser("~/.qoder-cn/settings.json"),
        "Qoder Desktop": os.path.expanduser("~/.qoder/settings.json"),
        # 2026-10-25：Trae CN 官方全局挂载面=hooks.json（非 settings.json）——补此分支，
        # 否则 extra 恒 None＝面板「+N」空白（你质证：看起来像"本端不需要额外守卫"，实为脚本漏配）
        "Trae CN 💡": os.path.expanduser("~/.trae-cn/hooks.json"),
        # 2026-10-25 v0.9.10：ZCode 入直读清单（hooks.events 形态·对齐 classify_entries 联合取法）——
        # extra 从「zcode_config_guard 文件存在 +1」写死改为实盘条目统计（对齐 WB 实挂盘点记法）
        "ZCode": os.path.expanduser("~/.zcode/cli/config.json"),
        # 2026-10-25 v0.9.12：MiniMax Code 入直读清单——本端唯一真实挂载面是 Plugin 包 hooks.json
        # （本端无用户级 settings.json·⛔母本 ~/.workbuddy/settings.json 是 WorkBuddy 运行时·不算本端）
        "MiniMax Code 🐰": os.path.expanduser("~/.minimax/plugins/bulutuo-guards/hooks/hooks.json"),
    }
    DSH_PLUGIN = os.path.expanduser(
        "[记忆共享中心]/脚本中心/five-layer-memory/src/index.js")
    # 平台专属守卫实盘映射（SSOT §二·七 + 守卫家族实例登记·脚本文件存在即计入 +N·对齐 DSH/LobsterAI 记法）
    # 这 4 平台走 patrol 拉模式（无 CC 式 hooks），extra 只能从专属守卫脚本文件判真——不存在则 0，极端不存盘不计数
    # Hermes 走插件型（无 hook 命令列表可解析·专属守卫 hermes_read_evidence_guard.py 由 route-audit-hook
    # _READ_EVIDENCE_SCRIPT 实挂）——同样按"专属守卫脚本文件存在判真"计入，与 AutoClaw/LobsterAI/ZCode 记法一致
    PATROL_EXTRA_SCRIPT = {
        "AutoClaw": os.path.expanduser("[记忆共享中心]/脚本中心/autoclaw_gateway_guard.py"),
        "LobsterAI": os.path.expanduser("[记忆共享中心]/脚本中心/内容创作/lobsterai_session_anomaly_guard.py"),
        "Trae Work": os.path.expanduser("[记忆共享中心]/脚本中心/内容创作/session_memory_quality_guard.py"),
        # 2026-10-25 v0.9.10：ZCode 移出（转 PLATFORM_CFG 实盘统计）——写死+1 是 patrol 型遗留，
        # 实盘 36 条只显 +1 = 登记面≠实盘（WB 2026-10-06 实挂盘点同族根治）
        "Hermes": os.path.expanduser("[记忆共享中心]/脚本中心/hermes_read_evidence_guard.py"),
    }
    # 非守卫命令（挂在 hooks 里但不是"专属守卫"：渲染器/机械校验器/探针）——统计专属守卫时剔除，防 +N 虚高
    NON_GUARD_CMDS = ("panel_snapshot.py", "platform_adaptation_check.py", "hooks-probe/probe.sh")
    def extra_count(name):
        if name in PATROL_EXTRA_SCRIPT:
            return 1 if os.path.exists(PATROL_EXTRA_SCRIPT[name]) else 0
        if name == "Zwork 🧠":
            # 2026-10-25 v0.9.14：Zwork（第 19 端·软约束端·无 hooks 配置面）——
            # extra=童灵包安装回执机械计数（installed capabilities + installed components
            # + twin_core core_built）·回执由 install_receipt.py 产出（⛔禁手写副本=机械源）·
            # verdict!=ok 不计（防假绿）·⛔不入 12-Hook 分母（平台边界 0/12 如实）
            try:
                with open(os.path.expanduser(
                    "~/Library/Application Support/AutoClaw-official/doenglingz/installed_manifest.json"),
                    encoding="utf-8") as f:
                    man = json.load(f)
                if man.get("verdict") != "ok":
                    return 0
                n = sum(1 for c in man.get("capabilities", []) if c.get("status") == "installed")
                n += sum(1 for c in man.get("components", {}).values()
                         if isinstance(c, dict) and c.get("status") == "installed")
                if (man.get("twin_core") or {}).get("state") == "core_built":
                    n += 1
                return n
            except Exception:
                return None
        cfg = PLATFORM_CFG.get(name)
        if name == "DeepSeek Harness":
            try:
                with open(DSH_PLUGIN, encoding="utf-8") as f:
                    src = f.read()
                # 行级解析到独立 "]" 行为止——args 内联 "]" 会提前截断（实测 bug）
                seg_lines = []
                for line in src.split("STOP_GUARDS", 1)[1].splitlines():
                    if line.strip().startswith("]") and "script:" not in line:
                        break
                    seg_lines.append(line)
                seg = "\n".join(seg_lines)
                total = seg.count("script:")
                in_shared = sum(1 for s in SHARED12 if s in seg)
                return max(total - in_shared, 0)
            except Exception:
                return None
        if not cfg:
            return None
        try:
            with open(cfg, encoding="utf-8") as f:
                d = json.load(f)
            cmds = []
            for evt in ("SessionStart", "UserPromptSubmit", "Stop"):
                # 2026-10-25 v0.9.10：兼容 ZCode hooks.events.<Event> 联合形态（对齐 classify_entries）
                evt_entries = list(d.get("hooks", {}).get(evt, [])) + \
                    list(d.get("hooks", {}).get("events", {}).get(evt, []))
                for it in evt_entries:
                    if "hooks" in it:
                        for hh in it["hooks"]:
                            cmds.append(hh.get("command", ""))
                    elif "command" in it:
                        cmds.append(it["command"])
            in_shared = sum(1 for c in cmds if any(s in c for s in SHARED12))
            non_guard = sum(1 for c in cmds if any(s in c for s in NON_GUARD_CMDS))
            return max(len(cmds) - in_shared - non_guard, 0)
        except Exception:
            return None
    rows = []
    def rk(item):
        v = item[1]
        return (v[0] / v[1]) if v and v[1] else -1
    METHOD_TXT = {"🟢": "机械", "🟡": "自核", "🔴": "自治"}
    for name, v in sorted(rates.items(), key=rk, reverse=True):
        if v is None:
            rows.append({"name": name, "num": None, "den": None, "mark": "❔", "method": "未登记", "note": "未解析", "extra": None})
            continue
        num, den = v
        gap = den - num
        pct = round(num / den * 100) if den else 0
        color = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"
        mark, note = coverage.get(name, ("❔", "未登记"))
        rows.append({"name": name, "num": num, "den": den, "gap": gap,
                     "mark": mark, "method": METHOD_TXT.get(mark, "未登记"),
                     "note": note, "color": color,
                     "extra": extra_count(name)})

    # 四方向文本（与 render_html 同口径·单一来源由同一函数生成）
    det, fix, imm = cl.get("detected"), cl.get("fixed"), cl.get("immune")
    anti = cl.get("antibodies")
    mt = snap.get("maintenance", {}) or {}
    # 免疫命中 / 有效抗体（过渡基线·与 closed_loop.antibodies 同口径——免疫拦截效果·单一事实源）
    imm_h = snap.get("better_immune_hits")
    anti_e = snap.get("better_antibodies")
    if mt.get("total_commits") is not None:
        segs = " · ".join("{} {}".format(s["segment"], s["commits"]) for s in mt.get("segments", []) if s.get("commits") is not None)
        maint_line = "近7天共 {} 次提交 · 环节Top：{}（环节口径≠总量口径·示集中度）".format(mt["total_commits"], segs)
    else:
        maint_line = None

    # v0.8.0 三面孔同源：①/④ 卡复用 OKR 机械映射行（与 OKR 区同一读数·根治口径脱节）
    _okr_rows_js = (snap.get("okr") or {}).get("objectives") or []
    _oa = next((o for o in _okr_rows_js if o.get("dir") == "auto"), {})
    _ok = next((o for o in _okr_rows_js if o.get("dir") == "knows"), {})
    def _pf(v):
        return ("{}%".format(v) if isinstance(v, (int, float)) else "—")

    data = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "closed_loop": {
            "detected": det, "fixed": fix, "immune": imm,
            "immune_total": cl.get("immune_total"), "immune_last_date": cl.get("immune_last_date"),
            "antibodies": anti, "pending": cl.get("pending"),
            "trend": cl.get("trend", []),
        },
        "summary": build_summary(cl),
        "four_dir": {
            "auto": "自动触发占比 {} · 覆盖 {}".format(
                _pf(_oa.get("auto_closure")), _oa.get("auto_cov") or "—"),
            # 2026-09-27 童灵根治：基线是倍数语义（免疫命中÷抗体），⛔按百分比渲染出过"2349%"
            # 10-07 终审轮：state=定案 时四方向②卡同步切定案读数（活跃口径+全史对照，⛔不再挂过渡文案）
            "better": ("漏触发修复率(近14天活跃) {:.0%} · 全史对照 {:.0%} · 双载体池 {} 条".format(
                snap["better_join_active"], (snap.get("better_join_all") or 0),
                snap.get("better_pool") or "—")
                if (snap.get("better_state") == "定案" and snap.get("better_join_active") is not None)
                else "免疫命中 {}（累计） · 有效抗体 {} · {}".format(
                    imm_h if imm_h is not None else "—",
                    anti_e if anti_e is not None else "—",
                    ("命中/抗体 {:.1f} 倍".format(snap.get("better_baseline"))
                     if isinstance(snap.get("better_baseline"), (int, float)) else "基线 —"))),
            "evo": "本季提案 {} · 采纳 {} · 豁免 {} · 未决 {} · 净采纳率 {}（n={} · 95%CI {}）".format(
                snap.get("evo_events") if snap.get("evo_events") is not None else "—",
                snap.get("evo_adopted") if snap.get("evo_adopted") is not None else "—",
                snap.get("evo_waived") if snap.get("evo_waived") is not None else "—",
                snap.get("evo_pending") if snap.get("evo_pending") is not None else "—",
                ("{:.0f}%".format(snap.get("evo_adoption_rate")*100) if snap.get("evo_adoption_rate") is not None else "待量"),
                snap.get("evo_rate_n") if snap.get("evo_rate_n") is not None else "—",
                ("{:.0f}–{:.0f}%".format((snap.get("evo_rate_ci") or [0, 0])[0]*100,
                                          (snap.get("evo_rate_ci") or [0, 0])[1]*100)
                 if snap.get("evo_rate_ci") else "—")),
            "knows": "本月 {} 条 · 本季累计 {}/{} · 时间进度 {}% · 剩 {} 天".format(
                snap.get("knows_count") if snap.get("knows_count") is not None else "—",
                _ok.get("current") if _ok.get("current") is not None else "—",
                _ok.get("target_pct") if _ok.get("target_pct") is not None else "—",
                snap.get("quarter_time_pct") if snap.get("quarter_time_pct") is not None else "—",
                snap.get("knows_days_left") if snap.get("knows_days_left") is not None else "—"),
            "auto_state": snap.get("auto_state") or "定案",
            "better_state": snap.get("better_state") or "过渡",
            "evo_state": snap.get("evo_state") or "定案",
            "knows_state": snap.get("knows_state") or "过渡",
            "knows_note": "过渡=认知发现数·自然月归当月 · 定案=预测准确率（需先建「预测vs实际」成对标签）",
        },
        "maintenance_line": maint_line,
        "platform_rates": rows,
        "knowledge_ladder": snap.get("knowledge_ladder"),
        "knowledge_base": snap.get("knowledge_base"),  # 2026-09-08 童灵根治：知识库可视化3模块数据
        "hermes_kpi": snap.get("hermes_kpi"),
        "okr": snap.get("okr"),
        # 2026-09-03 童灵新增：全自动化指标扩展字段（snap层面，与okr层面同源）
        "auto_coverage": snap.get("auto_coverage"),  # 覆盖面：有埋点的守卫数（机械计算）
        "auto_closure_rate": snap.get("auto_closure_rate"),  # 第二指标：自动闭环率（数据积累中可能为None）
        "auto_breakdown": snap.get("auto_breakdown"),  # 分母构成：total/hook_auto/manual/other
        "auto_state": snap.get("auto_state"),  # 状态：过程代理/定案
    }
    js_path = os.path.join(os.path.dirname(LIVE_HTML), "panel_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// 面板实时数据（panel_snapshot v0.9.2 生成·勿手改）\n")
        f.write("window.PANEL_DATA = {};\n".format(json.dumps(data, ensure_ascii=False)))
    print("[panel_snapshot] 已更新 {}".format(js_path))
    return data

if __name__ == "__main__":
    snap = take_snapshot()
    # 总是用最新数据覆盖当日快照（避免陈旧数据残留）
    if already_has_date(snap["date"]):
        rows = read_timeseries()
        rows = [r for r in rows if r.get("date") != snap["date"]]
        rows.append(snap)
        os.makedirs(os.path.dirname(TS_PATH), exist_ok=True)
        with open(TS_PATH, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("[panel_snapshot] 已更新 {} 快照".format(snap["date"]))
    else:
        append_snapshot(snap)
        print("[panel_snapshot] 已追加 {} 快照".format(snap["date"]))
    # A v2 治理闸门（机械化对账）：注册表变动未留治理记录 → 大声报错+OKR区红框
    try:
        _alarm = check_registry_governance(list((snap.get("platform_rates") or {}).keys()))
    except Exception:
        _alarm = None
    if _alarm:
        print("[REGISTRY-GOVERNANCE] " + _alarm)
        snap["registry_alarm"] = _alarm
    html = render_html(snap)
    write_live_html(html)

# ── 布洛陀发布包·路径覆盖层 ──────────────────────────────────
# 装包时安装器生成本机实况的 path_override.py，把上面这些
# **作者态落点**（"[记忆共享中心]/…"）改成本机值或哨兵路径。
# ⛔ 本块必须留在**所有模块级常量之后**——插早了会被后面的定义覆盖回去。
# 作者侧运行（开发工具/ 下）时 path_overlay 不可达 ⇒ ImportError ⇒ 原样运行。
try:
    from path_overlay import apply_override
    apply_override(globals())
except ImportError:
    pass