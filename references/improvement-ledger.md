# 此前问题点的改造闭环

## Existing-project electrical changes and delivery, 2026-09-15

- Added a native-XML change-contract verifier: explicit component additions,
  removals and before/after identity/partition changes; retained physical NC
  pins; optional frozen-baseline hash and named/same-net/distinct-net contracts.
- Added a root hierarchy audit: instance-aware page/component counts, portable
  sheet paths, missing/cyclic children, annotation coverage, cached-library and
  multi-unit pin signatures, actual PDF count and descriptive baseline delta.
- Added neutral failure fixtures and native KiCad before/after resistor pin/value
  changes. Tests cover unexpected opens/shorts, DNP drift, pin loss, stale hashes,
  cache conflicts, reused sheets and historical PDF count mismatch.
- Carried forward System_block as the architecture cover, and documented module
  expansion, electrical redesign, canonical cross-page symbols and CopperPilot
  candidate provenance. No private board or vendor reference package is included.
- The tools are read-only verifiers, not an automatic multi-page writer. The
  project-specific geometry extensions are documented as bounded work requiring
  native validation; the stock engine's unsupported objects remain insufficient.
- All earlier generation, redraw and population mechanisms are retained. The
  release evidence is in `release-validation.md`; electrical/production approval
  and external service availability are not implied by these checks.

对应 2026-09-08 调研清单，更新于 2026-09-14。本表说明程序真正执行的规则，
不把流程文字或单一 ERC 结果当成已解决图面问题。

| 编号/原问题 | 落地变化 | 证据与边界 |
| --- | --- | --- |
| G1 临时写坐标和 S 表达式，缺稳定接口 | Circuit IR v2 → pin 编译 → 自动 layout → route → writer → native verification | `build_circuit.py`、输入/编译/每次尝试快照；旧 v1 明确定位接口继续可用 |
| G2 把 Buck 布局套到所有稳压器 | 分开 rc/divider/capacitor_bank/ldo/buck_async/integrated_power/functional | 角色合同拒绝缺失/不支持的角色；电源模板是布局模板，特定 IC 仍须电气与原生回归 |
| G3 控制区只考虑本体间距 | 按 body、pin 出线、Reference/Value 总占用计算行列；扩距重排 | 12 只长 Value 电容；改变字长后占用扩大；纸张不足明确失败 |
| G4 wire_geometry 只有统计，无穿芯检测 | 回读真实缓存符号，线段检查本体/字段/引脚 | 既有穿芯/线穿文字反例 + 生成前避障 + 生成后独立 QA |
| G5 按坐标猜功能组 | 原始电路模块/实例/角色；默认布局按实际连接遍历 | 两组 RC 实例隔离、单页拼排；不是完整电路功能识别或任意拓扑优化器 |
| G6 geometry check 缺统一覆盖与结果 | PASS/FAIL/INSUFFICIENT/REVIEW；对象、坐标、缺口、版本与 hash | 未覆盖的隐藏脚、叠加脚、复杂原生页对象不会伪装成零碰撞 |
| G7 固化可疑的连线规则 | 保留 KiCad 10.0.4 原生直连/未分段 T/旋转镜像实验 | 每次回归重做 native XML；不推广为所有历史版本必然相同 |
| G8 为了排版改变引脚或接口定义 | 编译器锁真实物理引脚；named pin 必须实库解析；符号 hash | 错脚、重名脚、遗漏脚、重复位号、库 hash 漂移全部拒绝 |
| G9 机械套公共地母线/PWR_FLAG | 标签必须在 presentation 显式选择；端口只绑定已声明网络 | 无自动标签降级、无自动补 PWR_FLAG 或改 pin type；复杂电源符号未覆盖则失败 |
| G10 没有固定生成回归包 | 旧 29 项加 IR/自动布局/多单元/属性/锁定/导入回归 | fixtures、原生 XML/ERC/PDF、源码对象探针、最终产物 hash；示例均标为测试夹具 |

四类主要痛点的自动验收：

- **器件堆叠**：分开分配真实总占用；生成后本体/字段相交仍是硬失败。
- **走线穿芯**：引脚朝向约束 + 完整线段避障；路由失败触发有限重排。
- **Value 堆积**：可见字段水平并预留宽度，采购/额定值另存隐藏属性；不截断原值。
- **布局不清楚/标题栏侵入**：按功能模块、方向、标题、留白拼页，预留页框和标题栏。
  自动布局只在硬约束通过后交付候选；可读性仍以最终原生全页与局部目检确认。

架构阶段的当前边界：

| 原建议阶段 | 当前状态 |
| --- | --- |
| 一：坏图必须被拦住 | 已有统一几何门禁与坏图反例；明确报告模型未覆盖对象 |
| 二：单功能块稳定生成 | 已有电路表示、模板、真实空间预算、自动放置/布线/复验；RC、电容阵列、多单元夹具实测；实际 Buck/LDO 等仍按具体器件复验 |
| 三：多块多页 | 模块复用、逻辑层次/端口/标量总线、多块单页已实现；原生多页 sheet/跨页导出、图形总线仍未实现 |
| 四：增量编辑 | 已有带差异与锁定检查的新目录再生成；不宣称支持任意手工工程原位编辑或任意已有分页工程的局部重排 |

对已有的复杂硬件工程，应先回读原生网表和组件身份，再建立经确认的 IR。
资料不足保持 INSUFFICIENT；本次没有把历史 LM5013/RK3576/SSA100 原图当作
已修复或已电气验收的成果，也没有改动它们。

复验入口：`python3 -m unittest discover -s tests -v`，以及
`tests/probe_structured_upstream.py`（可选上游隔离环境）。具体运行结果保存在
本地 `output/ir-integration/`，不把临时路径或测试数据当成正式产品输入。

## Engineer-reference comparison, TPS53355 Rev B (2026-09-10)

- Added explicit local routing groups with exact terminal partition validation,
  original-net labels and per-group fixed rails. Replaced the TPS53355 test's
  temporary-name monkeypatch with a supported low-level API.
- Added measured explicit visible fields, including 90-degree capacitor-bank
  fields, reserved before automatic fields and routing. Pin corridors are now
  also protected when placing labels on wired nets; interior wire label anchors
  are normalized as real split points.
- Added four regressions including native group connectivity/identity, rotated
  fields, invalid groups, immutable IR and collision rejection. Adapted the
  unsplit-T native probe to merge all contiguous segments, including extra
  label split points, before testing the same physical topology.
- Added an engineer-comparison guide and a reproducible compact TPS53355 draft.
  This is an explicit project recipe; automatic packing still does not choose
  this topology, capacitor MPNs/DC-bias guarantees or production constraints.

## Control-pin and peripheral completeness, TPS53355 Rev C (2026-09-11)

- Added explicit pin-provenance and peripheral-function ledgers to the workflow;
  distinguish datasheet-required connections, calculated values, default
  population and engineering options. Reference-image NC/DNP resistors retain
  actual wired pads instead of disappearing into an IC no-connect marker.
- Extended the TPS53355 example from 37 to 47 components (40 fitted, 7 DNP),
  with RF/MODE options, PG/VDD/VREG isolation links and VIN/load bypasses.
  Default RF remains electrically open at nominal 500 kHz; documented RF
  alternatives are held for frequency-dependent redesign and validation.
- Added a recipe-specific population gate: remove DNP, collapse fitted 0-ohm
  links, enforce mutually exclusive controls and compare retained baseline pin
  groups. Eight regressions cover errors that native all-pads ERC cannot detect.
  This is not a universal analog or arbitrary-assembly validator.

## Reference circuits and existing-project redraw (2026-09-14)

- Added datasheet peripheral contracts, explicit local branch ownership and
  negative mutations for a bounded KSZ8081RNA example. Added shared-terminal
  coverage and power-marker geometry regressions; connectivity includes each
  physical pad even where one drawn stem is shared.
- Documented the project-specific multi-page redraw workflow in
  `existing-project-redraw.md`: preserve hierarchy/identity, plan local circuits,
  compare complete native pin partitions and named interfaces, retain raw ERC
  and inspect its semantic delta. Existing electrical findings remain visible.
- Recorded native-grid and actual drawing-frame checks, per-page visual review,
  explicit handling of changed local net names, protected application to the
  original project and verification from the delivered path. Compare decoded
  pixels rather than PNG file hashes for visual equivalence.
- These are reusable checks and drawing procedures derived from project work.
  The project-specific multi-page writer and proprietary engineering sources
  are not distributed. The general generator remains a bounded single-sheet
  backend; this update does not claim arbitrary automatic board layout or
  electrical/production qualification of the examples.
