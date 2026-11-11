# TI TPS3840

类别：器件参数。
器件：低功耗电压监控复位器，含开漏与推挽、正负复位极性版本。
手册：SNVSB03E，2026 年 5 月修订。

## 来源

- S1：Datasheet/08_电源管理/电压监控_复位(Supervisor)/TI - TPS3840.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 输入电压 |  | VDD | −0.3 | 12 | V | S1 p5 |
| 复位输出电压 |  | PL、PH | −0.3 | VDD + 0.3 | V | S1 p5 |
| 复位输出电压 |  | DL | −0.3 | 12 | V | S1 p5 |
| 手动复位电压 |  | MR；脚注仍要求不高于 VDD | −0.3 | 12 | V | S1 p5 |
| 定时电压 |  | CT | −0.3 | 5.5 | V | S1 p5 |
| 复位输出电流 |  |  |  | ±70 | mA | S1 p5 |
| 结温 | TJ |  | −40 | 150 | °C | S1 p5 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p5 |

## 推荐工作条件

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 输入电压 | VDD |  | 1.5 |  | 10 | V | S1 p5 |
| 复位脚电压 | VRESET |  | 0 |  | 10 | V | S1 p5 |
| 复位脚电流 | IRESET |  | 0 |  | ±5 | mA | S1 p5 |
| 结温 | TJ | 低耗散假设结温等于环境温度 | −40 |  | 125 | °C | S1 p5 |
| 手动复位电压 | VMR |  | 0 |  | VDD | V | S1 p5 |

## 电气特性

VDD = 1.5 到 10 V，CT/MR 悬空，RESET 经 100 kΩ 上拉至 VDD，CLOAD = 10 pF，全温 −40 到 125 °C；典型在 25 °C。定时条件 VDD 斜率 < 100 mV/µs（S1 p6、p7）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 输入电压 | VDD |  | 1.5 |  | 10 | V | S1 p6 |
| 下降门限精度 | VIT− | −40 到 125 °C | −1.5 | 1 | 1.5 | % | S1 p6 |
| 门限迟滞 | VHYS | VIT− = 3.1 到 4.9 V | 175 | 200 | 225 | mV | S1 p6 |
| 门限迟滞 | VHYS | VIT− = 1.6 到 3.0 V | 75 | 100 | 125 | mV | S1 p6 |
| 供电电流 | IDD | VDD > VIT+，1.5 V < VDD < 10 V，−40 到 125 °C |  | 300 | 700 | nA | S1 p6 |
| 手动复位低电平 | VMR_L |  |  |  | 600 | mV | S1 p6 |
| 手动复位高电平 | VMR_H |  | 0.7 × VDD |  |  | V | S1 p6 |
| 手动复位内部上拉 | RMR |  |  | 100 |  | kΩ | S1 p6 |
| 定时内部电阻 | RCT |  | 350 | 500 | 650 | kΩ | S1 p6 |
| 上电复位电压 | VPOR | PL，VOL(max) = 200 mV，吸电流 200 nA |  |  | 300 | mV | S1 p6 |
| 输出低电平 | VOL | PL，1.5 V < VDD < 5 V，VDD < VIT−，吸电流 2 mA |  |  | 200 | mV | S1 p6 |
| 输出高电平 | VOH | PL，1.5 V < VDD < 5 V，VDD > VIT+，源电流 2 mA | 0.8 × VDD |  |  | V | S1 p6 |
| 输出高电平 | VOH | PL，5 V < VDD < 10 V，VDD > VIT+，源电流 5 mA | 0.8 × VDD |  |  | V | S1 p6 |
| 上电复位电压 | VPOR | PH，源电流 500 nA |  |  | 950 | mV | S1 p6 |
| 输出低电平 | VOL | PH，1.5 V < VDD < 5 V，VDD > VIT+，吸电流 2 mA |  |  | 200 | mV | S1 p6 |
| 输出低电平 | VOL | PH，1.5 V < VDD < 5 V，VDD > VIT+，吸电流 5 mA；照原件条件 |  |  | 200 | mV | S1 p6 |
| 输出高电平 | VOH | PH，1.5 V < VDD < 5 V，VDD < VIT−，源电流 2 mA | 0.8 × VDD |  |  | V | S1 p6 |
| 上电复位电压 | VPOR | DL，VOL(max) = 0.2 V，吸电流 5.6 µA |  |  | 950 | mV | S1 p6 |
| 输出低电平 | VOL | DL，1.5 V < VDD < 5 V，VDD < VIT−，吸电流 2 mA |  |  | 200 | mV | S1 p6 |
| 开漏输出漏电 | Ilkg(OD) | 高阻态，VDD = VRESET = 5.5 V，VIT+ < VDD |  |  | 90 | nA | S1 p7 |
| 启动延迟 | tSTRT | CT 悬空 | 100 | 220 | 350 | µs | S1 p7 |
| 下降检测传播延迟 | tP_HL | VDD 从 VIT+ 到 VIT− 以下 10% |  | 15 | 30 | µs | S1 p7 |
| 复位延迟 | tD | CT 悬空 |  |  | 50 | µs | S1 p7 |
| 复位延迟 | tD | CT = 10 nF |  | 6.2 |  | ms | S1 p7 |
| 复位延迟 | tD | CT = 1 µF |  | 619 |  | ms | S1 p7 |
| 毛刺抗扰时间 | tGI_VIT− | 5% VIT− 过驱动 |  | 10 |  | µs | S1 p7 |
| 手动复位脉宽 | tMR_PW |  |  | 300 |  | ns | S1 p7 |
| 手动复位传播延迟 | tMR_RES | VDD = 4.5 V，MR < VMR_L |  | 700 |  | ns | S1 p7 |

用这些数时要注意：

- RMR、外接电容定时、毛刺免疫、MR 脉宽及 MR 传播延迟只有典型值；外接电容延迟上下限须按 RCT 和手册公式处理，本条目不推算（S1 p6、p7）。
- VPOR 控制输出的条件是 VDD 斜率 ≤100 mV/µs；低于 VPOR 输出未定义（S1 p7、p8）。
- MR 虽列 12 V 绝对最大，脚注仍限制不高于 VDD；低于 VDD 驱动会增加流入 VDD、流出 MR 的电流。PH 两条 VOL 测试均写 1.5 到 5 V，照抄不擅改为高压条件（S1 p5、p6）。

## 热特性

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 结到环境热阻 | RθJA | 封装列顺序见下文 | 187.5 | °C/W | S1 p5 |
| 结到壳顶热阻 | RθJC(top) | 封装列顺序见下文 | 109.2 | °C/W | S1 p5 |
| 结到板热阻 | RθJB | 封装列顺序见下文 | 92.8 | °C/W | S1 p5 |
| 结到顶热特性参数 | ψJT | 封装列顺序见下文 | 35.4 | °C/W | S1 p5 |
| 结到板热特性参数 | ψJB | 封装列顺序见下文 | 92.5 | °C/W | S1 p5 |

## 静电额定

| 参数 | 符号 | 条件 | 数值 | 单位 | 来源 |
|---|---|---|---|---|---|
| 人体模型 | V(ESD) | JS-001 | ±2000 | V | S1 p5 |
| 带电器件模型 | V(ESD) | JESD22-C101 | ±750 | V | S1 p5 |

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 1 RESET | O，PL/DL 低有效、PH 高有效；PL/PH 推挽、DL 开漏 | 见绝对最大表 | DL 使用上拉 | S1 p4、p5、p30 |
| 2 VDD | I，被监控电源 | 1.5 到 10 V（工作） |  | S1 p4、p5 |
| 3 GND | —，地 |  | 接地 | S1 p4 |
| 4 MR/NC | I，手动复位或无连接 | 0 到 VDD（工作） | 不用可悬空 | S1 p4、p5 |
| 5 CT | —，定时电容脚 | −0.3 到 5.5 V（绝对最大） | 不用悬空，得到最短固定延迟 | S1 p4、p5 |
| 散热焊盘 | 未给独立散热焊盘 |  |  | S1 p4 |

## 必需外围

- 建议 VDD 对地放至少 0.1 µF 陶瓷电容并就近；同页另一条写 >0.1 µF，原文如此。DL 输出需上拉；CT 悬空时寄生电容应 <5 pF，定时电容应靠近 CT。手册未给统一 CCT 取值上下限（S1 p28）。

## 订货型号与封装

DL 为开漏低有效、PL 为推挽低有效、PH 为推挽高有效；后两位表示检测电压，DBV 为 SOT23-5，R 为大卷。下表先列附录订货项，再列正文给出的门限/迟滞档；表内标称值不替代精度保证（S1 p30、p31）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| TPS3840DL16DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL16DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL16DBVRG4 | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL16DBVRG4.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL17DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL17DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL18DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL18DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL19DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL19DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL20DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL20DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL22DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL22DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL24DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL24DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL25DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL25DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL27DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL27DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL28DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL28DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL29DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL29DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL30DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL30DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL30DBVRG4 | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL30DBVRG4.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p33 |
| TPS3840DL31DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p33 |
| TPS3840DL31DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL35DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL35DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL40DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL40DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL42DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL42DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL44DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL44DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL45DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL45DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL46DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL46DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840DL49DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840DL49DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH18DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH18DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH19DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH19DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH27DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH27DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH30DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH30DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH40DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH40DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH45DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH45DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PH49DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PH49DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PL16DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p34 |
| TPS3840PL16DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p34 |
| TPS3840PL18DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL18DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL20DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL20DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL25DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL25DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL26DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL26DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL27DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL27DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL27DBVRG4 | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL27DBVRG4.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL28DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL28DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL29DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL29DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL30DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL30DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL31DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL31DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL33DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL33DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL34DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL34DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL40DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL40DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL41DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL41DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL42DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL42DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p35 |
| TPS3840PL43DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p35 |
| TPS3840PL43DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p36 |
| TPS3840PL44DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | SN | S1 p36 |
| TPS3840PL44DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | SN | S1 p36 |
| TPS3840PL45DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p36 |
| TPS3840PL45DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p36 |
| TPS3840PL45DBVRG4 | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p36 |
| TPS3840PL45DBVRG4.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p36 |
| TPS3840PL48DBVR | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU 或 SN | S1 p36 |
| TPS3840PL48DBVR.A | SOT-23 (DBV) | 5 |  | -40 to 125 | NIPDAU | S1 p36 |
| TPS3840DL16、TPS3840PL16、TPS3840PH16 | SOT23 DBV | 5 | 门限 1.6 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL17、TPS3840PL17、TPS3840PH17 | SOT23 DBV | 5 | 门限 1.7 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL18、TPS3840PL18、TPS3840PH18 | SOT23 DBV | 5 | 门限 1.8 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL19、TPS3840PL19、TPS3840PH19 | SOT23 DBV | 5 | 门限 1.9 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL20、TPS3840PL20、TPS3840PH20 | SOT23 DBV | 5 | 门限 2.0 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL21、TPS3840PL21、TPS3840PH21 | SOT23 DBV | 5 | 门限 2.1 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL22、TPS3840PL22、TPS3840PH22 | SOT23 DBV | 5 | 门限 2.2 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL23、TPS3840PL23、TPS3840PH23 | SOT23 DBV | 5 | 门限 2.3 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL24、TPS3840PL24、TPS3840PH24 | SOT23 DBV | 5 | 门限 2.4 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL25、TPS3840PL25、TPS3840PH25 | SOT23 DBV | 5 | 门限 2.5 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL26、TPS3840PL26、TPS3840PH26 | SOT23 DBV | 5 | 门限 2.6 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL27、TPS3840PL27、TPS3840PH27 | SOT23 DBV | 5 | 门限 2.7 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL28、TPS3840PL28、TPS3840PH28 | SOT23 DBV | 5 | 门限 2.8 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL29、TPS3840PL29、TPS3840PH29 | SOT23 DBV | 5 | 门限 2.9 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL30、TPS3840PL30、TPS3840PH30 | SOT23 DBV | 5 | 门限 3.0 V，迟滞 0.100 V（标称） |  |  | S1 p30 |
| TPS3840DL31、TPS3840PL31、TPS3840PH31 | SOT23 DBV | 5 | 门限 3.1 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL32、TPS3840PL32、TPS3840PH32 | SOT23 DBV | 5 | 门限 3.2 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL33、TPS3840PL33、TPS3840PH33 | SOT23 DBV | 5 | 门限 3.3 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL34、TPS3840PL34、TPS3840PH34 | SOT23 DBV | 5 | 门限 3.4 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL35、TPS3840PL35、TPS3840PH35 | SOT23 DBV | 5 | 门限 3.5 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL36、TPS3840PL36、TPS3840PH36 | SOT23 DBV | 5 | 门限 3.6 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL37、TPS3840PL37、TPS3840PH37 | SOT23 DBV | 5 | 门限 3.7 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL38、TPS3840PL38、TPS3840PH38 | SOT23 DBV | 5 | 门限 3.8 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL39、TPS3840PL39、TPS3840PH39 | SOT23 DBV | 5 | 门限 3.9 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL40、TPS3840PL40、TPS3840PH40 | SOT23 DBV | 5 | 门限 4.0 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL41、TPS3840PL41、TPS3840PH41 | SOT23 DBV | 5 | 门限 4.1 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL42、TPS3840PL42、TPS3840PH42 | SOT23 DBV | 5 | 门限 4.2 V，迟滞 0.200 V（标称） |  |  | S1 p30 |
| TPS3840DL43、TPS3840PL43、TPS3840PH43 | SOT23 DBV | 5 | 门限 4.3 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL44、TPS3840PL44、TPS3840PH44 | SOT23 DBV | 5 | 门限 4.4 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL45、TPS3840PL45、TPS3840PH45 | SOT23 DBV | 5 | 门限 4.5 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL46、TPS3840PL46、TPS3840PH46 | SOT23 DBV | 5 | 门限 4.6 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL47、TPS3840PL47、TPS3840PH47 | SOT23 DBV | 5 | 门限 4.7 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL48、TPS3840PL48、TPS3840PH48 | SOT23 DBV | 5 | 门限 4.8 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |
| TPS3840DL49、TPS3840PL49、TPS3840PH49 | SOT23 DBV | 5 | 门限 4.9 V，迟滞 0.200 V（标称） |  |  | S1 p30、p31 |

器件生命周期状态不在本条目收录，设计时查厂家网站并记录日期。

## 核对记录

- 2026-11-10：逐页对照原件抽取，工具核对通过（PASS）；核对了 584 个数，问题 0 条，没核对 0 处。
