# TPS53355 compact comparison draft

A4 synchronous Buck drawing: regulated 4.75–5.25 V to nominal 0.85 V, 15 A
comparison target, 500 kHz nominal in CCM, auto-skip, Rev C with 47 physical
components: 40 fitted and 7 DNP by default.

This is a presentation/regression example, not a production reference design.
Read the TPS53355 notes at the end of this file and the assumptions in
`calculations.json`. Input capacitor MPNs and effective capacitance/ESR,
production footprints/connectors, temperature and load-transient behavior need
engineering closure. Preserve the original 10 A baseline when comparing.

```sh
cd examples/tps53355_compact
python3 prepare_design.py
python3 calculate.py
python3 calculate_options.py
python3 verify_population.py electrical_intent.json --output population.json
python3 build_compact.py --out /path/to/new/TPS53355-Test-RevC
```

Run the commands from the repository root with the `cd` shown above.
The prepared `compiled.json` records library hashes and portable paths:
`example_directory` means this example folder, and `kicad_symbol_directory`
means the installed KiCad symbol folder. The writer records the actual resolved
library locations again in each output directory.

The writer rejects an existing output folder. `AUTOMATED_PASS` is only the
native/geometry gate; inspect the exported full page and crowded regions.
Default enable is automatic: R7 fitted, R9 DNP. External sequencing requires
R7 DNP, R9 fitted, and an externally driven/pulled EN signal meeting the TI
thresholds. Do not leave EN floating or connect a 5 V pull-up to an incompatible
upstream driver. Snubber C15/R11 and bleeder R12 are DNP tuning provisions.

RF pin 22 is now wired to option pads, not a no-connect marker. R13 (866k to
VREG) and R14 (187k to GND) are BOTH DNP for default 500 kHz (TI Rev G Table
7-1). Fit at most one; 650/300 kHz are documented setting codes, not released
alternate designs. The engineer image's two 100k/NC resistors are treated as
unpopulated placeholders, not supported default frequency-setting values.
`option-calculations.json` demonstrates the coupling: unchanged 300 kHz parts
give a conditional minimum ripple-network inequality margin below 1. Rework
the network and divider before using that option. Neither calculation proves
stability, transient response or component behavior over temperature.

MODE defaults to R5 fitted and R15 DNP. FCCM after PG requires swapping those
states and reviewing light-load/negative-current behavior. R10 (PG isolation),
R16 (VDD feed) and R17 (VREG external-bias link) are fitted 0-ohm links in all
supported profiles. This is external regulated 5 V bias, not a 10-ohm VDD RC
filter or a qualified internal-LDO alternate. C20/C21 add local VIN bypass;
C22/C23 add load bypass without crediting them toward minimum Ceff.

`verify_population.py` rejects conflicting RF/MODE/EN population, incomplete
snubbers, wrong option values/endpoints and unsupported bias-link changes. The
writer runs this default-population gate before drawing. `--baseline <intent>`
also compares the active baseline pins after removing DNP and collapsing fitted
zero-ohm resistors. This checks assembly connectivity, not analog equivalence
or arbitrary circuit validity; the usual pin/identity/ERC/geometry gates remain
required. Refer to TI pin Table 5-1, ceramic application Figure 8-2 and Section
8.2.1.2.3 for topology and calculations; values and control choices are adapted
for this operating point, not copied unchanged from one application figure.

## TPS53355 对照笔记（原 references/engineer-template-comparison.md 的个案部分）

### 紧凑的同步 Buck 图面

经过测试的 TPS53355 例子用的是显式的画法，不是通用的 Buck 自动识别：`examples/tps53355_compact/`。
它的电气值是计算出的对照草稿；不要当作合格的默认值复用。

1. VIN 和 LL 的物理引脚阵列相对放置。按功能重排它们的图形位置，保持引脚号、类型和全部端子不变。
2. 主电源轨走直线：输入到 VIN、LL 到 L、L 到输出。电容组共用一条电源轨和一条地网络轨。为引脚总线留位置。
3. VDD/VREG 去耦放在各自引脚旁，配置放在上方/左侧，BOOT 放在 LL 到 L 那段的上方，注入/分压放在下方。
   补偿连接保持可见；只对明确的远程控制用限定范围的标签。
4. 规整的密集电容组可以用 90° 的 Reference/Value 字段。朝向一致，间距要容得下实测的文字、本体和引脚出线。
   完整的额定值/MPN 留作元数据；不为缩短可见值而删掉容差。普通字段默认保持水平。
5. 需要走直的地方指定局部组的电源轨。A* 走线可能电气有效但视觉很差。走线后检查 KiCad 渲染，
   包括引脚名/引脚号区域和图框，不只做简单的 AABB 检查。
6. 有用的调试设施只按设计网表添加：测试点、EN/PG 接口、可选的缓冲/泄放电路。DNP 是装配状态，不是 NC 引脚。
   记录互斥的装配规则和外部信号要求。

### 从 TPS53355 对照中学到的电气检查

查当前器件数据手册并保留确切版本。按 Rev G：

- RF 开路的 500 kHz 是连续导通下的名义设定。自动跳脉冲在轻载时不是固定频率工作。
- MODE 接 GND 和 MODE 接 PGOOD 是不同的模式；不要用通用的下拉经验规则把手册写明的配置判为问题。
- 输出用陶瓷电容时按纹波注入的步骤，包括 `L*Cout/(Rinj*Cinj) > N*Ton/2`，`L<=250nH` 时 `N=4`。
- 估算平均 VFB 和选分压时计入注入/输出纹波。简单的 `0.6*(1+Rtop/Rbottom)` 估算会漏掉设定点偏移。
- OCP 检测谷值电流；区分平均负载的动作点和瞬时峰值。典型 RDS(on)、名义的 TRIP 公式和 25°C 的 Isat 曲线
  不能证明全温度、全工艺下有保证的电流保护。
- 外部 5 V 稳压偏置和内部 VREG 供电在厂家允许时是两种合法的架构。照抄串联 VDD 滤波前，在最低输入电压下核对电压余量。
- 有效电容和 ESR 在有厂家曲线或实测支持之前保持有条件。算术裕量不是环路/瞬态证据。

最后用 KiCad ERC、按原设计网表的引脚分区/身份检查、序列化几何、整页/局部的 KiCad 渲染、电气改动清单、
确切哈希和剩余的电气证据缺口清单收尾。

### 可选支路与装配

TPS53355 的 Rev G 表 7-1 规定 RF 开路为 500 kHz。两只可选的 RF 电阻可以画出但不装。Rev C 例子画了接 VREG 的 866k
（650 kHz）和接 GND 的 187k（300 kHz），默认都是 DNP。图片里的 100k/NC 占位不能证明装 100k 上拉是推荐设定。
保留这些选项并标注默认状态；不要只为让原理图像参考图而加装上拉。

显式的 TPS53355 画法增加了 RF/MODE 选项、PG 隔离、独立的 VDD 和 VREG 偏置跳接，以及 VIN/负载高频去耦
（37 到 47 个物理器件）。0 欧 VDD 跳接是测试/隔离设施，不是有效的 RC 滤波；在 5 V 最低偏置下照抄 10 欧滤波需要重新核对余量。
器件数更多本身从来不是验收标准。

