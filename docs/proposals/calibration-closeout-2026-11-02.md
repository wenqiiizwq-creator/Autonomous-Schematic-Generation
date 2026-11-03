# 工业 I/O 校准板收口：SR 审查、记录按新规则补齐、典型电路（2026-11-02）

> 读者：ASG 维护者、用户。用户 2026-11-02：再帮我执行"已识别但没做的改进"。
> 校准板目录 `~/Documents/ASG-calibration/industrial-io-rs485-can/`（不在仓库）；SR 只读使用。

## 1. SR 审查结果摘要

按 SR `SKILL.md` 流程对 `原理图/` 跑了冷扫 → 意图 → 资料审计 → 电路候选与决定（18 块电路）→ 带候选重扫 → 合并计划（856 项检查、42 个功能框架）→ 结果 → 门禁 → 报告。
产出在校准板 `record/sr-review/`：`审查报告.md/.html`、`findings.json`（归因）、`record/`（计划、结果、门禁、意图、lint、候选、资料审计与生成脚本）。

审查深度按 SR `evals/boards/README.md` 的板子回路：连接、脚表、身份、文档方面逐项判；计算与电气窗口方面（C/E）本轮没有由 SR 独立重算，每个功能留一条“需人判”开放项。
因此门禁 `valid=false`（3113 条，绝大多数是“需人判”开放项不是 SR 的两种开放项种类、需求条款未逐条拆分），报告顶部带“记录有错”提示，不能打包。这与板子回路其余 100 块的做法一致（全部 gate FAIL）。

发现与归因（22 条 + 漏报 3 条）：

| SR 规则 | true_defect | false_alarm | knowledge_gap | needs_human |
|---|---|---|---|---|
| DEV-D01（身份） | 1 | | | |
| DEV-D02（物理脚/脚名） | 2 | 1 | 1 | |
| DEV-Q01（资料审计/器件类别） | | 3 | | |
| PRO-E02 / PRO-C01（钳位窗口与协调） | | 1 | 1 | 5 |
| DOC-A01 | | | | 1 |
| NET-A07、RST-A02、RST-A03 | | 3 | | |
| 电路候选、电路框架 | | 3 | | |
| 合计 | 3 | 11 | 2 | 6 |

漏报（`misses`）：DC_24V 入口没出候选且无默认状态（M01）、`/07_DI/DI1` 斜杠网名没出 INDUSTRIAL_DI 候选（M02）、MCU 晶体没出 CLOCK 候选（M03）。准则问题（criterion_issue）0 条。

### 真缺陷与处置

| 编号 | 缺陷 | 处置 |
|---|---|---|
| F01 | D501 料号 ESD2CAN36WQDCKRQ1 不在 TI 订货表（只有 ESD2CAN36WDXARQ1，DXA/USON-3），符号说明写 SOT-323 | 已改：`board_iio.py` 料号、`symbols_iio.py` 说明，重生成 |
| F02 | U301 自建符号把 9 个未用 GPIO 写成 NC，VBAT/VDDA/VSSA 写成 VDD/VSS | 已改：`symbols_iio.py` 允许堆叠脚与隐藏脚各带手册名，按 DS5319 表 5 命名 |
| F03 | U201.13、U601.29 散热焊盘写成 PGND/FGND（手册 EP），U701 STATUSn 写成 STATn | 已改：同上 |

需人判的 6 条中 4 件需要设计方取舍，写成设计待办 `W-SR-DECIDE`（open）：D102 击穿下限 34 V 落在 OV 动作窗 33.5–36.1 V 内（F06）；FIELD+ 是否按直流电源口核线-线浪涌（F10）；DI 输入 TVS 钳位约 48 V 对 IPx 绝限 36 V（F11）；U401 料号在手册里只以预量产 XISOW3080PDWER 出现（F07）。

SR 侧修改材料（不在本分支改 SR）：`findings.json` 每条 false_alarm 与漏报带 `proposed_fix`（器件类别线索词按整词匹配、括号内封装注释当别名、PRO-E02 穿过一颗串联电阻找被保护脚、DC_24V/INDUSTRIAL_DI/CLOCK 候选、保持电路与 BOOT 下拉的框架）。

## 2. W-DOC 批量引用改为逐条证据

- `closure_iio.py` 的 W-DOC 不再批量列 49 条准则：`guideline_evidence` 逐条写 `<证据编号>#<节/表/行>`，每处最多 3 条。
  证据扩到 E-REQ、E-CALC、E-IF、E-FMEA、E-WC，新增 E-PERI（外围电路核对表）、E-CR（器件性能要求）、E-DLV（交付流程）。
- 准则库 1.7.0 新增的 7 条未覆盖规则：G02-036/037/038/039、G04-101、G04-102 进 W-DOC 并各指证据；G04-102 的证据是新写的 `pin_dispositions`（47 个不接脚逐脚写手册处置与页码）；
  G03-059（内补偿变换器前馈/注入网络在手册窗内）没有证据——LM5160 Type 3 纹波注入元件没按手册方程核，留成设计待办 `W-BUCK-RIPPLE`（open）。
- G05-012 原来同时在 W-DOC 和“不适用”里（理由写错），改为指到 FMEA 处置列。
- 审计：`audit_design_closure.py` 0 错误，状态 INCOMPLETE（open：W-EXT-STD、W-BUCK-RIPPLE、W-SR-DECIDE）。
- 顺带修正：纲要改动后器件性能要求要电容写 `working_voltage/rated_voltage`，本板 5 颗电容写法不符使 `board_iio.py` 报错（issues.md #27），已补。

## 3. 新典型电路（12 个）

`dc-24v-input-protection`、`ideal-diode-hotswap`、`hold-up`、`cot-buck`、`ldo`、`mcu-min-system`、`swd-debug`、`industrial-di-serializer`、`di-digital-isolation`、`high-side-quad`、`chassis-y-cap`、`status-led`。
每个实现方案写了落实规则（只用库里 active、与声明电路类型相容的编号；`swd-debug`、`status-led` 写“无”并括注），已知坑引用 `review:calibration/industrial-io-rs485-can/<编号>` 或手册页。
`references/typical-circuits.md` 加第三批表；校准板 `page-plan.json` 的 `circuits` 按块填上（母线取样一块无合适典型电路，未标）。
测试：`tests/test_typical_circuits.py` 数量 19→31，新增“第三批每条已知坑带来源”。

## 4. 报告状态

`deliver.py --for-review` 出 PDF → 按本版 PDF 写图面审阅 → 全程重跑：自动检查 10 项 PASS（ERC、引脚表核对、几何等），器件性能与待办审计 INCOMPLETE（正常设计状态），`设计报告.md` 生成成功，开头不再有“结论不可靠”。
为通过新规则另补：Y301 写频率容差、J301 写额定电压/电流（规格要求，part_classes #7/#21）；`records_iio.py` 要带新导出的网表跑一次才会按新符号重写引脚表合同。

`lessons.json` 第 15 条改正：原 `change` 指向 `references/calculation-preflight.md`（计算条件记录的格式说明，没改、也不该放电路知识），`why_not_rule` 说规则写不出支路组合——实际 G05-026 已要求下级支路短路时下级先动作。
改为：判断失误（规则在、初值漏用 G05-026），`change` 指向 `references/typical-circuits/ideal-diode-hotswap.md` 的必算项与已知坑。

## 5. 纲要建议（只供确认，未改 SKILL.md）

1. **binding_version 1 的落地成本**：任务 2.4 已要求以 `binding_version 1` 无错误为准，但本板试跑是 505 条错误（引脚表缺 `datasheet_name/datasheet_type` 478 条、手册引脚表名不符 14 条、电源轨电压 8 条、值与料号前段 5 条）。
   建议纲要写明：已交付的校准板/旧板改版时才补，或给引脚表一条从符号库+手册页自动填的路径，否则这条做完标志对既有板不可达。
2. **典型电路的已知坑来源**：本板 12 个典型电路要等 SR 审查才有可引用的坑。建议任务 5.x 加一句“新板交付后跑一次 SR，发现进典型电路的已知坑”。
3. **W-DOC 类已关闭文档待办**：逐条证据后单条待办引用 55 条准则，可读性差。建议纲要允许把文档类准则直接挂在接口表/工况矩阵/FMEA 的证据条目上（证据级 `guidelines`），而不是挂在一件待办上。

## 6. 没做完的与原因

- **打包失败**：`deliver.py` 打包步拒收 `record/sr-review/`（交付目录 record/ 下只允许 calculations、scripts、evidence）。任务要求 SR 产出放在这里，两者冲突；本次未挪动，报告与记录都已生成。建议打包白名单加 `sr-review`，或把 SR 审查放到交付目录外。
- **SR 门禁不 valid**：计算类方面没有按 SR 结果格式逐项写余量（板子回路深度），需人判的 6 条待设计方定。
- **binding_version 1** 未启用（试跑 505 条错误，见第 5 节建议 1）。
- **W-BUCK-RIPPLE、W-SR-DECIDE** 两件设计待办 open。
- **共用层对齐测试**：`test_schematic_review_holds_the_same_shared_layer` 失败，原因是 SR 与 ASG main 已到准则库 1.7.1（他处提交 162a38e），本分支从 b3df8f8 分出仍是 1.7.0；按约束不改共用层，合并 main 后应恢复。校准板 `record/runtime.json` 临时指向本工作树（main 已是 1.7.1，与记录里的 1.7.0 不符），合并后改回 main 并重跑。
