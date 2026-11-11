# TI ISO6440

类别：器件参数。
器件：四通道数字隔离器系列；ISO6440 为全部正向通道
手册：SLLSG01C，2026 年 5 月修订。

## 来源

- S1：Datasheet/15_接口与隔离/数字隔离器/TI - ISO6440.pdf

页码均为 PDF 文件页序；原件共 57 页。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| 侧一电源 | VCC1 | 对 GND1 | −0.5 | 6 | V | S1 p6 |
| 侧二电源 | VCC2 | 对 GND2 | −0.5 | 6 | V | S1 p6 |
| 数字输入 | INx | 对本侧地 | −0.5 | 6 | V | S1 p6 |
| 使能输入 | ENx | 对本侧地 | −0.5 | 6 | V | S1 p6 |
| 数字输出 | OUTx | 对本侧地；且最大不得超过 6 V | −0.5 | VCCx + 0.5 | V | S1 p6 |
| 数字输出电流 | IO |  | −15 | 15 | mA | S1 p6 |
| 结温 | TJ |  |  | 150 | °C | S1 p6 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p6 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 侧一供电 | VCC_RO | VCC1，可与另一侧独立 | 2.25 |  | 5.5 | V | S1 p7 |
| 侧二供电 | VCC_RO | VCC2，可与另一侧独立 | 2.25 |  | 5.5 | V | S1 p7 |
| 欠压上升门限 | VCC_UVLO+ |  |  |  | 2.24 | V | S1 p7 |
| 欠压下降门限 | VCC_UVLO− |  | 1.6 |  |  | V | S1 p7 |
| 欠压迟滞 | VCC_UVLO_HYS |  | 0.1 |  |  | V | S1 p7 |
| 输入高电平 | VIH(INx) | VCCI 为本侧电源 | 0.7 × VCCI |  | VCCI | V | S1 p7 |
| 输入低电平 | VIL(INx) |  | 0 |  | 0.3 × VCCI | V | S1 p7 |
| 使能高电平 | VIH(ENx) |  | 0.7 × VCCI |  | VCCI | V | S1 p7 |
| 使能低电平 | VIL(ENx) |  | 0 |  | 0.3 × VCCI | V | S1 p7 |
| 数据率 | DR | 3.0 V≤VCCx≤5.5 V，CL≤15 pF | 0 |  | 150 | Mbps | S1 p7 |
| 数据率 | DR | 2.25 V≤VCCx<3 V，CL≤10 pF | 0 |  | 150 | Mbps | S1 p7 |
| 数据率 | DR | 2.25 V≤VCCx<3 V，10 pF<CL≤15 pF | 0 |  | 100 | Mbps | S1 p7 |
| 环境温度 | TA |  | −40 | 25 | 125 | °C | S1 p7 |
| 高电平输出电流 | IOH | VCCO=5 V | −4 |  |  | mA | S1 p7 |
| 低电平输出电流 | IOL | VCCO=5 V |  |  | 4 | mA | S1 p7 |
| 高电平输出电流 | IOH | VCCO=3.3 V | −2 |  |  | mA | S1 p7 |
| 低电平输出电流 | IOL | VCCO=3.3 V |  |  | 2 | mA | S1 p7 |
| 高电平输出电流 | IOH | VCCO=2.5 V | −1 |  |  | mA | S1 p7 |
| 低电平输出电流 | IOL | VCCO=2.5 V |  |  | 1 | mA | S1 p7 |

## 电气特性

TA 为推荐工作范围；电气、供电电流及开关特性分别在 5 V、3.3 V、2.5 V ±10% 下列出，不在不同供电档之间推算；VCCI/VCCO 为相应输入/输出侧电源（S1 p12–p20）。“最小”“最大”为手册限值，“典型”不是保证值。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 输出高电平 | VOH(OUTx) | VCC1=VCC2=5 V ±10%，IOH=−4 mA | VCCO − 0.4 |  |  | V | S1 p12 |
| 输出低电平 | VOL(OUTx) | VCC1=VCC2=5 V ±10%，IOL=4 mA |  |  | 0.4 | V | S1 p12 |
| 上升切换门限 | VIT+(INx) | VCC1=VCC2=5 V ±10%， |  |  | 0.7 × VCCI | V | S1 p12 |
| 下降切换门限 | VIT−(INx) | VCC1=VCC2=5 V ±10%， | 0.3 × VCCI |  |  | V | S1 p12 |
| 门限迟滞 | VI_HYS(INx) | VCC1=VCC2=5 V ±10%， | 0.1 × VCCI |  |  | V | S1 p12 |
| 上升切换门限 | VIH(ENx) | VCC1=VCC2=5 V ±10%， |  |  | 0.7 × VCCI | V | S1 p12 |
| 下降切换门限 | VIL(ENx) | VCC1=VCC2=5 V ±10%， | 0.3 × VCCI |  |  | V | S1 p12 |
| 门限迟滞 | VI_HYS(ENx) | VCC1=VCC2=5 V ±10%， | 0.1 × VCCI |  |  | V | S1 p12 |
| 输入电流 | II(INx) | VCC1=VCC2=5 V ±10%，无 F，INx=VCCI |  |  | 1 | µA | S1 p12 |
| 输入电流 | II(INx) | VCC1=VCC2=5 V ±10%，无 F，INx=0 V | −10 |  |  | µA | S1 p12 |
| 输入电流 | II(INx) | VCC1=VCC2=5 V ±10%，F，INx=VCCI |  |  | 10 | µA | S1 p12 |
| 输入电流 | II(INx) | VCC1=VCC2=5 V ±10%，F，INx=0 V | −1 |  |  | µA | S1 p12 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=5 V ±10%，ENx=VCCI |  |  | 1 | µA | S1 p12 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=5 V ±10%，ENx=0 V | −10 |  |  | µA | S1 p12 |
| 增强型共模瞬变抗扰 | CMTI_R | VCC1=VCC2=5 V ±10%，DW/DFP，VI=VCC 或 0，VCM=1200 V，VENx=VCC | 200 | 250 |  | kV/µs | S1 p12 |
| 基本型共模瞬变抗扰 | CMTI_B | VCC1=VCC2=5 V ±10%，DBQ，VI=VCC 或 0，VCM=500 V，VENx=VCC | 150 | 180 |  | kV/µs | S1 p12 |
| 输入电容 | Ci | VCC1=VCC2=5 V ±10%，VI=VCC/2+0.4×sin(2πft)，f=2 MHz |  | 1.5 |  | pF | S1 p12 |
| 输出高电平 | VOH(OUTx) | VCC1=VCC2=3.3 V ±10%，IOH=−2 mA | VCCO − 0.2 |  |  | V | S1 p14 |
| 输出低电平 | VOL(OUTx) | VCC1=VCC2=3.3 V ±10%，IOL=2 mA |  |  | 0.2 | V | S1 p14 |
| 上升切换门限 | VIT+(INx) | VCC1=VCC2=3.3 V ±10%， |  |  | 0.7 × VCCI | V | S1 p14 |
| 下降切换门限 | VIT−(INx) | VCC1=VCC2=3.3 V ±10%， | 0.3 × VCCI |  |  | V | S1 p14 |
| 门限迟滞 | VI_HYS(INx) | VCC1=VCC2=3.3 V ±10%， | 0.1 × VCCI |  |  | V | S1 p14 |
| 上升切换门限 | VIH(ENx) | VCC1=VCC2=3.3 V ±10%， |  |  | 0.7 × VCCI | V | S1 p14 |
| 下降切换门限 | VIL(ENx) | VCC1=VCC2=3.3 V ±10%， | 0.3 × VCCI |  |  | V | S1 p14 |
| 门限迟滞 | VI_HYS(ENx) | VCC1=VCC2=3.3 V ±10%， | 0.1 × VCCI |  |  | V | S1 p14 |
| 输入电流 | II(INx) | VCC1=VCC2=3.3 V ±10%，无 F，INx=VCCI |  |  | 1 | µA | S1 p14 |
| 输入电流 | II(INx) | VCC1=VCC2=3.3 V ±10%，无 F，INx=0 V | −10 |  |  | µA | S1 p14 |
| 输入电流 | II(INx) | VCC1=VCC2=3.3 V ±10%，F，INx=VCCI |  |  | 10 | µA | S1 p14 |
| 输入电流 | II(INx) | VCC1=VCC2=3.3 V ±10%，F，INx=0 V | −1 |  |  | µA | S1 p14 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=3.3 V ±10%，ENx=VCCI |  |  | 1 | µA | S1 p14 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=3.3 V ±10%，ENx=0 V | −10 |  |  | µA | S1 p14 |
| 增强型共模瞬变抗扰 | CMTI_R | VCC1=VCC2=3.3 V ±10%，DW/DFP，VI=VCC 或 0，VCM=1200 V，VENx=VCC | 200 | 250 |  | kV/µs | S1 p14 |
| 基本型共模瞬变抗扰 | CMTI_B | VCC1=VCC2=3.3 V ±10%，DBQ，VI=VCC 或 0，VCM=500 V，VENx=VCC | 150 | 180 |  | kV/µs | S1 p14 |
| 输入电容 | Ci | VCC1=VCC2=3.3 V ±10%，VI=VCC/2+0.4×sin(2πft)，f=2 MHz |  | 1.5 |  | pF | S1 p14 |
| 输出高电平 | VOH(OUTx) | VCC1=VCC2=2.5 V ±10%，IOH=−1 mA | VCCO − 0.1 |  |  | V | S1 p16 |
| 输出低电平 | VOL(OUTx) | VCC1=VCC2=2.5 V ±10%，IOL=1 mA |  |  | 0.1 | V | S1 p16 |
| 上升切换门限 | VIT+(INx) | VCC1=VCC2=2.5 V ±10%， |  |  | 0.7 × VCCI | V | S1 p16 |
| 下降切换门限 | VIT−(INx) | VCC1=VCC2=2.5 V ±10%， | 0.3 × VCCI |  |  | V | S1 p16 |
| 门限迟滞 | VI_HYS(INx) | VCC1=VCC2=2.5 V ±10%， | 0.1 × VCCI |  |  | V | S1 p16 |
| 上升切换门限 | VIH(ENx) | VCC1=VCC2=2.5 V ±10%， |  |  | 0.7 × VCCI | V | S1 p16 |
| 下降切换门限 | VIL(ENx) | VCC1=VCC2=2.5 V ±10%， | 0.3 × VCCI |  |  | V | S1 p16 |
| 门限迟滞 | VI_HYS(ENx) | VCC1=VCC2=2.5 V ±10%， | 0.1 × VCCI |  |  | V | S1 p16 |
| 输入电流 | II(INx) | VCC1=VCC2=2.5 V ±10%，无 F，INx=VCCI |  |  | 1 | µA | S1 p16 |
| 输入电流 | II(INx) | VCC1=VCC2=2.5 V ±10%，无 F，INx=0 V | −10 |  |  | µA | S1 p16 |
| 输入电流 | II(INx) | VCC1=VCC2=2.5 V ±10%，F，INx=VCCI |  |  | 10 | µA | S1 p16 |
| 输入电流 | II(INx) | VCC1=VCC2=2.5 V ±10%，F，INx=0 V | −1 |  |  | µA | S1 p16 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=2.5 V ±10%，ENx=VCCI |  |  | 1 | µA | S1 p16 |
| 使能输入电流 | II(ENx) | VCC1=VCC2=2.5 V ±10%，ENx=0 V | −10 |  |  | µA | S1 p16 |
| 增强型共模瞬变抗扰 | CMTI_R | VCC1=VCC2=2.5 V ±10%，DW/DFP，VI=VCC 或 0，VCM=1200 V，VENx=VCC | 200 | 250 |  | kV/µs | S1 p16 |
| 基本型共模瞬变抗扰 | CMTI_B | VCC1=VCC2=2.5 V ±10%，DBQ，VI=VCC 或 0，VCM=500 V，VENx=VCC | 150 | 180 |  | kV/µs | S1 p16 |
| 输入电容 | Ci | VCC1=VCC2=2.5 V ±10%，VI=VCC/2+0.4×sin(2πft)，f=2 MHz |  | 1.5 |  | pF | S1 p16 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.4 | 4.7 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 1.3 | 1.5 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 11.3 | 13.1 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 1.1 | 1.3 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 7.25 | 8.9 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 1.4 | 1.6 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 7.35 | 8.9 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 3.2 | 3.9 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 7.8 | 10.0 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 22 | 26 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.2 | 4.6 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 2.2 | 3 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 8.5 | 10.5 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 3.9 | 4.8 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 5.9 | 7.5 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 3.2 | 4 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 6.5 | 8.1 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 4.7 | 5.6 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 11.5 | 13.9 | mA | S1 p13 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 18.4 | 21.7 | mA | S1 p13 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 2.2 | 3.15 | mA | S1 p13 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 5.6 | 7.4 | mA | S1 p13 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 4.1 | 5.3 | mA | S1 p13 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 5.5 | 6.5 | mA | S1 p13 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 15.2 | 18.0 | mA | S1 p13 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.3 | 4.7 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 1.2 | 1.5 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 10.3 | 13.1 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 1.1 | 1.3 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 7.5 | 8.8 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 1.3 | 1.5 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 7.5 | 8.9 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 2.5 | 2.9 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 8.0 | 9.5 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 14.9 | 17.0 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.2 | 4.5 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 2.2 | 2.9 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 8.5 | 10.4 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 3.8 | 4.8 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 5.9 | 7.4 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 3.1 | 3.9 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 6.2 | 7.8 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 4.1 | 5 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 9.5 | 11.6 | mA | S1 p15 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 13.2 | 15.5 | mA | S1 p15 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC 第一行，VI=VCC1（无F）/0（F） |  | 2.4 | 3.1 | mA | S1 p15 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，DC 第二行，原表重复相同输入条件 |  | 5.6 | 7.3 | mA | S1 p15 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，AC 1 Mbps，原表写固定 VI=0（无F）/VCC1（F） |  | 4.4 | 5.2 | mA | S1 p15 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，AC 10 Mbps，同前 |  | 5.1 | 6.0 | mA | S1 p15 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=3.3 V ±10%，ENx=VCCx，AC 100 Mbps，同前 |  | 11.5 | 13.1 | mA | S1 p15 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.3 | 4.6 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 1.2 | 1.4 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 11.2 | 13.0 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 1.0 | 1.21 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 7.3 | 8.8 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 1.2 | 1.5 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 7.4 | 8.8 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 2.2 | 2.5 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 7.6 | 9.3 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6440/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 11.5 | 13.3 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 3.1 | 4.5 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 2.1 | 2.9 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 8.5 | 10.4 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 3.8 | 4.7 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 5.8 | 7.4 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 3.1 | 3.9 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 6.1 | 7.7 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 3.8 | 4.7 | mA | S1 p17 |
| 电源电流 | ICC1 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 8.6 | 10.6 | mA | S1 p17 |
| 电源电流 | ICC2 | ISO6441/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 10.7 | 12.7 | mA | S1 p17 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=VCC1（无F）/0（F） |  | 2.1 | 3.1 | mA | S1 p17 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，DC：VI=0（无F）/VCC1（F） |  | 5.6 | 7.2 | mA | S1 p17 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 1 Mbps，CL=15 pF |  | 3.9 | 5.2 | mA | S1 p17 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 10 Mbps，CL=15 pF |  | 4.6 | 5.8 | mA | S1 p17 |
| 电源电流 | ICC1,ICC2 | ISO6442/F，VCC1=VCC2=2.5 V ±10%，ENx=VCCx，全部通道方波 100 Mbps，CL=15 pF |  | 9.3 | 11.5 | mA | S1 p17 |
| 传播延迟 | tPLH,tPHL | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，100 kbps | 3.85 | 6.2 | 10 | ns | S1 p18 |
| 脉宽畸变 | PWD | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  | 0.07 | 1.8 | ns | S1 p18 |
| 同片通道偏差 | tsk(o) | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，同方向通道，输入相连，相同负载 |  |  | 1.5 | ns | S1 p18 |
| 片间偏差 | tsk(pp) | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，同电源/温度/输入/负载，同方向 |  |  | 3 | ns | S1 p18 |
| 输出边沿时间 | tr | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 3 | ns | S1 p18 |
| 输出边沿时间 | tf | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 3 | ns | S1 p18 |
| 使能或禁止传播延迟 | tPHZ | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 9 | ns | S1 p18 |
| 使能或禁止传播延迟 | tPLZ | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 8 | ns | S1 p18 |
| 使能或禁止传播延迟 | tPZH | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 7 | ns | S1 p18 |
| 使能或禁止传播延迟 | tPZL | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 8 | ns | S1 p18 |
| 上电有效数据时间 | tPU | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，VCC 上升时间<1 µs，从 UVLO 起 |  |  | 90 | µs | S1 p18 |
| 失电默认输出延迟 | tDO | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，输入侧 VCC 低于 VCC_UVLO−(MIN) 起，电源斜率按图 7-2 |  | 0.045 | 0.1 | µs | S1 p18 |
| 时间间隔误差 | tie | VCC1=VCC2=5 V ±10%，CL=15 pF±20%，第 7 节测试波形，2¹⁶−1 PRBS，100 Mbps |  | 0.23 |  | ns | S1 p18 |
| 传播延迟 | tPLH,tPHL | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，100 kbps | 4 | 7 | 12 | ns | S1 p19 |
| 脉宽畸变 | PWD | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  | 0.35 | 2.2 | ns | S1 p19 |
| 同片通道偏差 | tsk(o) | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，同方向通道，输入相连，相同负载 |  |  | 1.5 | ns | S1 p19 |
| 片间偏差 | tsk(pp) | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，同电源/温度/输入/负载，同方向 |  |  | 3 | ns | S1 p19 |
| 输出边沿时间 | tr | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 4 | ns | S1 p19 |
| 输出边沿时间 | tf | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 4 | ns | S1 p19 |
| 使能或禁止传播延迟 | tPHZ | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 14 | ns | S1 p19 |
| 使能或禁止传播延迟 | tPLZ | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 12 | ns | S1 p19 |
| 使能或禁止传播延迟 | tPZH | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 11 | ns | S1 p19 |
| 使能或禁止传播延迟 | tPZL | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 10 | ns | S1 p19 |
| 上电有效数据时间 | tPU | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，VCC 上升时间<1 µs，从 UVLO 起 |  |  | 70 | µs | S1 p19 |
| 失电默认输出延迟 | tDO | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，输入侧 VCC 低于 VCC_UVLO−(MIN) 起，电源斜率按图 7-2 |  | 0.045 | 0.1 | µs | S1 p19 |
| 时间间隔误差 | tie | VCC1=VCC2=3.3 V ±10%，CL=15 pF±20%，第 7 节测试波形，2¹⁶−1 PRBS，100 Mbps |  | 0.2 |  | ns | S1 p19 |
| 传播延迟 | tPLH,tPHL | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，100 kbps | 4.75 | 8.4 | 14.5 | ns | S1 p20 |
| 脉宽畸变 | PWD | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  | 0.55 | 2.6 | ns | S1 p20 |
| 同片通道偏差 | tsk(o) | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，同方向通道，输入相连，相同负载 |  |  | 1.5 | ns | S1 p20 |
| 片间偏差 | tsk(pp) | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，同电源/温度/输入/负载，同方向 |  |  | 3 | ns | S1 p20 |
| 输出边沿时间 | tr | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 5 | ns | S1 p20 |
| 输出边沿时间 | tf | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 5 | ns | S1 p20 |
| 使能或禁止传播延迟 | tPHZ | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 19 | ns | S1 p20 |
| 使能或禁止传播延迟 | tPLZ | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 17 | ns | S1 p20 |
| 使能或禁止传播延迟 | tPZH | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 17 | ns | S1 p20 |
| 使能或禁止传播延迟 | tPZL | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形， |  |  | 12 | ns | S1 p20 |
| 上电有效数据时间 | tPU | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，VCC 上升时间<1 µs，从 UVLO 起 |  |  | 80 | µs | S1 p20 |
| 失电默认输出延迟 | tDO | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，输入侧 VCC 低于 VCC_UVLO−(MIN) 起，电源斜率按图 7-2 |  | 0.047 | 0.1 | µs | S1 p20 |
| 时间间隔误差 | tie | VCC1=VCC2=2.5 V ±10%，CL=15 pF±20%，第 7 节测试波形，2¹⁶−1 PRBS，100 Mbps |  | 0.22 |  | ns | S1 p20 |
| 最大功耗 | PD | ISO6440/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 268.2 | mW | S1 p8 |
| 最大功耗 | PD1 | ISO6440/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 58.1 | mW | S1 p8 |
| 最大功耗 | PD2 | ISO6440/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 210.1 | mW | S1 p8 |
| 最大功耗 | PD | ISO6441/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 262.2 | mW | S1 p8 |
| 最大功耗 | PD1 | ISO6441/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 94.1 | mW | S1 p8 |
| 最大功耗 | PD2 | ISO6441/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 168.1 | mW | S1 p8 |
| 最大功耗 | PD | ISO6442/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 268 | mW | S1 p8 |
| 最大功耗 | PD1 | ISO6442/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 134 | mW | S1 p8 |
| 最大功耗 | PD2 | ISO6442/F，VCC1=VCC2=5.5 V，TJ=150 °C，CL=15 pF，75 MHz、50% 方波 |  |  | 134 | mW | S1 p8 |
| 电气间隙 | CLR | DW，侧间空气距离 | >8.15 |  |  | mm | S1 p9 |
| 爬电距离 | CPG | DW，侧间表面距离 | >8.15 |  |  | mm | S1 p9 |
| 内部绝缘间距 | DTI | DW，内部最小间距 | >17 |  |  | µm | S1 p9 |
| 耐电痕化指数 | CTI | DW，IEC60112 | >600 |  |  | V | S1 p9 |
| 重复峰值隔离电压 | VIORM | DW，双极性交流 |  |  | 1500 | VPK | S1 p9 |
| 隔离工作电压 | VIOWM | DW，正弦交流，TDDB |  |  | 1061 | VRMS | S1 p9 |
| 隔离工作电压 | VIOWM | DW，直流 |  |  | 1500 | VDC | S1 p9 |
| 瞬态隔离电压 | VIOTM | DW，VTEST=VIOTM，60 s 资格；1.2×VIOTM，1 s 生产测试 |  |  | 7071 | VPK | S1 p9 |
| 冲击电压 | VIMP | DW，空气中，1.2/50 µs |  |  | 8000 | VPK | S1 p9 |
| 浪涌隔离电压 | VIOSM | DW，油中资格，1.2/50 µs，≥1.3×VIMP |  |  | 10400 | VPK | S1 p9 |
| 耐受隔离电压 | VISO | DW，VTEST=VISO，60 s 资格；1.2×VISO，1 s 生产测试 |  |  | 5000 | VRMS | S1 p9 |
| 隔离电容 | CIO | DW，VIO=0.4×sin(2πft)，f=1 MHz，两侧分别短接所有脚 |  | ≈1.6 |  | pF | S1 p9 |
| 绝缘电阻 | RIO | DW，VIO=500 V，25 °C，两侧分别短接所有脚 | >10¹² |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DW，VIO=500 V，100 至 125 °C，两侧分别短接所有脚 | >10¹¹ |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DW，VIO=500 V，TS=150 °C，两侧分别短接所有脚 | >10⁹ |  |  | Ω | S1 p9 |
| 局部放电视在电荷 | qpd | DW，方法 a，安全测试分组 2/3 后，Vini=VIOTM、60 s，Vpd=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DW，方法 a，环境分组 1 后，Vini=VIOTM、60 s，增强型 Vpd=1.6×VIORM，基本型=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DW，方法 b 逐件测试，Vini=1.2×VIOTM、1 s，增强型 Vpd=1.875×VIORM，基本型=1.5×VIORM、1 s（b1），或 Vpd=Vini、tm=tini（b2） |  |  | ≤5 | pC | S1 p9 |
| 电气间隙 | CLR | DFP，侧间空气距离 | >8.0 |  |  | mm | S1 p9 |
| 爬电距离 | CPG | DFP，侧间表面距离 | >8.0 |  |  | mm | S1 p9 |
| 内部绝缘间距 | DTI | DFP，内部最小间距 | >17 |  |  | µm | S1 p9 |
| 耐电痕化指数 | CTI | DFP，IEC60112 | >600 |  |  | V | S1 p9 |
| 重复峰值隔离电压 | VIORM | DFP，双极性交流 |  |  | 1500 | VPK | S1 p9 |
| 隔离工作电压 | VIOWM | DFP，正弦交流，TDDB |  |  | 1061 | VRMS | S1 p9 |
| 隔离工作电压 | VIOWM | DFP，直流 |  |  | 1500 | VDC | S1 p9 |
| 瞬态隔离电压 | VIOTM | DFP，VTEST=VIOTM，60 s 资格；1.2×VIOTM，1 s 生产测试 |  |  | 7071 | VPK | S1 p9 |
| 冲击电压 | VIMP | DFP，空气中，1.2/50 µs |  |  | 8000 | VPK | S1 p9 |
| 浪涌隔离电压 | VIOSM | DFP，油中资格，1.2/50 µs，≥1.3×VIMP |  |  | 10400 | VPK | S1 p9 |
| 耐受隔离电压 | VISO | DFP，VTEST=VISO，60 s 资格；1.2×VISO，1 s 生产测试 |  |  | 5000 | VRMS | S1 p9 |
| 隔离电容 | CIO | DFP，VIO=0.4×sin(2πft)，f=1 MHz，两侧分别短接所有脚 |  | ≈1.3 |  | pF | S1 p9 |
| 绝缘电阻 | RIO | DFP，VIO=500 V，25 °C，两侧分别短接所有脚 | >10¹² |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DFP，VIO=500 V，100 至 125 °C，两侧分别短接所有脚 | >10¹¹ |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DFP，VIO=500 V，TS=150 °C，两侧分别短接所有脚 | >10⁹ |  |  | Ω | S1 p9 |
| 局部放电视在电荷 | qpd | DFP，方法 a，安全测试分组 2/3 后，Vini=VIOTM、60 s，Vpd=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DFP，方法 a，环境分组 1 后，Vini=VIOTM、60 s，增强型 Vpd=1.6×VIORM，基本型=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DFP，方法 b 逐件测试，Vini=1.2×VIOTM、1 s，增强型 Vpd=1.875×VIORM，基本型=1.5×VIORM、1 s（b1），或 Vpd=Vini、tm=tini（b2） |  |  | ≤5 | pC | S1 p9 |
| 电气间隙 | CLR | DBQ，侧间空气距离 | >3.7 |  |  | mm | S1 p9 |
| 爬电距离 | CPG | DBQ，侧间表面距离 | >3.7 |  |  | mm | S1 p9 |
| 内部绝缘间距 | DTI | DBQ，内部最小间距 | >9 |  |  | µm | S1 p9 |
| 耐电痕化指数 | CTI | DBQ，IEC60112 | >600 |  |  | V | S1 p9 |
| 重复峰值隔离电压 | VIORM | DBQ，双极性交流 |  |  | 707 | VPK | S1 p9 |
| 隔离工作电压 | VIOWM | DBQ，正弦交流，TDDB |  |  | 500 | VRMS | S1 p9 |
| 隔离工作电压 | VIOWM | DBQ，直流 |  |  | 707 | VDC | S1 p9 |
| 瞬态隔离电压 | VIOTM | DBQ，VTEST=VIOTM，60 s 资格；1.2×VIOTM，1 s 生产测试 |  |  | 4243 | VPK | S1 p9 |
| 冲击电压 | VIMP | DBQ，空气中，1.2/50 µs |  |  | 4000 | VPK | S1 p9 |
| 浪涌隔离电压 | VIOSM | DBQ，油中资格，1.2/50 µs，≥1.3×VIMP |  |  | 5200 | VPK | S1 p9 |
| 耐受隔离电压 | VISO | DBQ，VTEST=VISO，60 s 资格；1.2×VISO，1 s 生产测试 |  |  | 3000 | VRMS | S1 p9 |
| 隔离电容 | CIO | DBQ，VIO=0.4×sin(2πft)，f=1 MHz，两侧分别短接所有脚 |  | ≈1.9 |  | pF | S1 p9 |
| 绝缘电阻 | RIO | DBQ，VIO=500 V，25 °C，两侧分别短接所有脚 | >10¹² |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DBQ，VIO=500 V，100 至 125 °C，两侧分别短接所有脚 | >10¹¹ |  |  | Ω | S1 p9 |
| 绝缘电阻 | RIO | DBQ，VIO=500 V，TS=150 °C，两侧分别短接所有脚 | >10⁹ |  |  | Ω | S1 p9 |
| 局部放电视在电荷 | qpd | DBQ，方法 a，安全测试分组 2/3 后，Vini=VIOTM、60 s，Vpd=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DBQ，方法 a，环境分组 1 后，Vini=VIOTM、60 s，增强型 Vpd=1.6×VIORM，基本型=1.2×VIORM、10 s |  |  | ≤5 | pC | S1 p9 |
| 局部放电视在电荷 | qpd | DBQ，方法 b 逐件测试，Vini=1.2×VIOTM、1 s，增强型 Vpd=1.875×VIORM，基本型=1.5×VIORM、1 s（b1），或 Vpd=Vini、tm=tini（b2） |  |  | ≤5 | pC | S1 p9 |
| 安全电流 | IS | DW，RθJA=83 °C/W，VI=5.5 V，TJ=150 °C，TA=25 °C |  |  | 273.8 | mA | S1 p11 |
| 安全电流 | IS | DW，RθJA=83 °C/W，VI=3.6 V，TJ=150 °C，TA=25 °C |  |  | 418.3 | mA | S1 p11 |
| 安全电流 | IS | DW，RθJA=83 °C/W，VI=2.75 V，TJ=150 °C，TA=25 °C |  |  | 547.6 | mA | S1 p11 |
| 安全功耗 | PS | DW，RθJA=83 °C/W，TJ=150 °C，TA=25 °C |  |  | 1506 | mW | S1 p11 |
| 安全温度 | TS | DW |  |  | 150 | °C | S1 p11 |
| 安全电流 | IS | DFP，RθJA=113.3 °C/W，VI=5.5 V，TJ=150 °C，TA=25 °C |  |  | 200.6 | mA | S1 p11 |
| 安全电流 | IS | DFP，RθJA=113.3 °C/W，VI=3.6 V，TJ=150 °C，TA=25 °C |  |  | 306.5 | mA | S1 p11 |
| 安全电流 | IS | DFP，RθJA=113.3 °C/W，VI=2.75 V，TJ=150 °C，TA=25 °C |  |  | 401.2 | mA | S1 p11 |
| 安全功耗 | PS | DFP，RθJA=113.3 °C/W，TJ=150 °C，TA=25 °C |  |  | 1103.3 | mW | S1 p11 |
| 安全温度 | TS | DFP |  |  | 150 | °C | S1 p11 |
| 安全电流 | IS | DBQ，RθJA=117.8 °C/W，VI=5.5 V，TJ=150 °C，TA=25 °C |  |  | 192.9 | mA | S1 p11 |
| 安全电流 | IS | DBQ，RθJA=117.8 °C/W，VI=3.6 V，TJ=150 °C，TA=25 °C |  |  | 294.8 | mA | S1 p11 |
| 安全电流 | IS | DBQ，RθJA=117.8 °C/W，VI=2.75 V，TJ=150 °C，TA=25 °C |  |  | 385.9 | mA | S1 p11 |
| 安全功耗 | PS | DBQ，RθJA=117.8 °C/W，TJ=150 °C，TA=25 °C |  |  | 1061.1 | mW | S1 p11 |
| 安全温度 | TS | DBQ |  |  | 150 | °C | S1 p11 |

用这些数时要注意：

- Ci、CIO、时间间隔误差只有典型或近似数值。隔离耐压、冲击、浪涌与持续工作电压是不同的试验条件，不能互换（S1 p9、p12–p20）。
- 过压容忍章节举例允许输入高于本侧电源，但推荐表的 INx/ENx 高电平最大列写 VCCI，两处表达冲突，不能据此补造推荐输入上限（S1 p7、p29）。
- 两侧电源在 VCC_UVLO− 至推荐最小电压之间，输出不确定；默认状态不能代替该区间的确定性保证（S1 p7）。
- ISO6442 的 3.3 V 电流表两行 DC 重复输入条件，AC 行又写静态电平，与其他电源档的方波条件不一致。已按原表标注，未自行修正（S1 p15、p17）。
- 描述段称已认证，但特性和认证表均写计划认证；不能凭此手册认定认证已经完成（S1 p1、p11）。
- 安全限流/功耗仅用于故障下保护隔离栅，随环境温度变化，不是可用输出电流；测试时两侧分别把所有脚短接的 RIO/CIO 也不是普通工作接线（S1 p9–p11）。
- 开关负载包含仪器/夹具电容；输入信号发生器的终端电阻只在测试中需要，实际应用不要求（S1 p25）。

## 热特性

以下为手册热特性表的单列数值，原表没有区分最小、典型、最大，不另行赋予保证边界。

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | DW | 83 | °C/W | S1 p7 |
| 结到顶壳热阻 | RθJC(top) | DW | 48.5 | °C/W | S1 p7 |
| 结到板热阻 | RθJB | DW | 49 | °C/W | S1 p7 |
| 结到顶热参数 | ψJT | DW | 28 | °C/W | S1 p7 |
| 结到板热参数 | ψJB | DW | 48.4 | °C/W | S1 p7 |
| 结到环境热阻 | RθJA | DFP | 113.3 | °C/W | S1 p7 |
| 结到顶壳热阻 | RθJC(top) | DFP | 63.6 | °C/W | S1 p7 |
| 结到板热阻 | RθJB | DFP | 75.6 | °C/W | S1 p7 |
| 结到顶热参数 | ψJT | DFP | 32.5 | °C/W | S1 p7 |
| 结到板热参数 | ψJB | DFP | 74.4 | °C/W | S1 p7 |
| 结到环境热阻 | RθJA | DBQ | 117.8 | °C/W | S1 p7 |
| 结到顶壳热阻 | RθJC(top) | DBQ | 60 | °C/W | S1 p7 |
| 结到板热阻 | RθJB | DBQ | 69.8 | °C/W | S1 p7 |
| 结到顶热参数 | ψJT | DBQ | 29.9 | °C/W | S1 p7 |
| 结到板热参数 | ψJB | DBQ | 69 | °C/W | S1 p7 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | HBM，ANSI/ESDA/JEDEC JS-001；所有引脚 | ±2000 | V | S1 p6 |
| 带电器件模型 | V(ESD) | CDM，JEDEC JESD22C101；所有引脚 | ±1500 | V | S1 p6 |

手册静电警告（译文）：本集成电路可能被静电损坏，操作时应采取适当防护；不遵守正确的操作和安装程序可能造成损坏。损害可能从轻微性能退化到完全失效；精密集成电路很小的参数变化就可能使其不再满足公布的规格（S1 p36）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
| --- | --- | --- | --- | --- |
| VCC1（1）/VCC2（16） | 两侧独立电源 | 推荐 2.25 至 5.5 V；绝对最大 −0.5 至 6 V | 各接本侧电源与去耦 | S1 p5、p6、p7 |
| GND1（2、8）/GND2（9、15） | 各侧参考地 |  | 各接本侧地，不跨隔离栅短接 | S1 p5 |
| INA/INB/INC/IND | 通道输入；ISO6440 为 3/4/5/6，其他配置见订货差异 | 绝对最大 −0.5 至 6 V | 默认高器件有上拉，F 有下拉；可按所需逻辑固定至本侧电源或地 | S1 p5、p6、p12 |
| OUTA/OUTB/OUTC/OUTD | 通道输出；ISO6440 为 14/13/12/11 | 绝对最大 −0.5 至 VCCx+0.5 V，且不得超过 6 V | 未用输出处置未单列 | S1 p5、p6 |
| EN2（10）、EN1（7，仅 ISO6441/2） | 高或悬空使能，低时高阻 | 绝对最大 −0.5 至 6 V | 常开可悬空 | S1 p5、p6 |
| NC（7，仅 ISO6440） | 不连接 |  | 手册未规定其他用途 | S1 p5 |

## 必需外围

两侧分别接 0.1 µF 旁路：VCC1–GND1 与 VCC2–GND2。手册明确正常运行只需这两个外部旁路电容，图示要求距电源脚不超过 0.5 mm（S1 p31）。

## 订货型号与封装

DW、DBQ、DFP 分别对应下表封装，F 后缀的默认输出差异见本节原说明；带 X 的订货型号按附录原样保留（S1 p46）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| ISO6440DWR | SOIC (DW) | 16 | 默认输出高 | -40～125 °C | NIPDAU | S1 p46、p3 |
| ISO6440FDWR | SOIC (DW) | 16 | 默认输出低 | -40～125 °C | NIPDAU | S1 p46、p3 |
| XISO6440DBQR | SSOP (DBQ) | 16 | 默认输出高 | -40～125 °C | Call TI | S1 p46、p3 |
| XISO6440DFPR | SSOP (DFP) | 16 | 默认输出高 | -40～125 °C | Call TI | S1 p46、p3 |
| XISO6440FDBQR | SSOP (DBQ) | 16 | 默认输出低 | -40～125 °C | Call TI | S1 p46、p3 |
| XISO6440FDFPR | SSOP (DFP) | 16 | 默认输出低 | -40～125 °C | Call TI | S1 p46、p3 |

本条列同向四通道型号；同手册其他通道方向组合见 S1 p46。

F 后缀输入失电/失信号时默认低，无 F 默认高；ISO6440/1/2 分别有零/一/二路反向通道，引脚随方向改变。DW/DFP 为增强绝缘额定，DBQ 为基本绝缘额定，隔离耐压、爬电/间隙及 CMTI 不同，详见参数表（S1 p3–p5、p9、p12）。

用这些数时还要注意：附录中另一通道方向型号的封装字段为“null (null)”，脚数也未填，不能从相邻行补造；本条未收该行（S1 p46）。


## 核对记录

- 2026-11-09：逐页对照原件，工具核对通过，核对 423 个数。
