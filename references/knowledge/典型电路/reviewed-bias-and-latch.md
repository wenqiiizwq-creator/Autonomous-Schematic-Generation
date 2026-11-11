# 宽范围偏置与故障锁定（已拆分，指路）

功能：本条目原把四件互不相关的电路（可调输出反激的宽范围辅助供电、一次侧 VCC 取电的交流指示、高有效故障脚的比较器驱动、二次侧反向保护 LDO）和三个审查案例放在一起，并含某块板的数值、订货码与位号。2026-11-10 深读复核把有来源、有通用价值的内容分别并入下列条目，这里只留指路。

电路类型：无（指路条目）

## 来源清单

- S1：Datasheet/08_电源管理/AC-DC 转换器/onsemi - NCP1343.pdf

原条目的来源（LM5168、NCP1343、TPS3700、LT3010、AND90156、Vishay AC）随内容转到下列条目。

## 内容去向

| 原内容 | 现在在哪里 |
|---|---|
| 方案 1：辅助绕组整流加高压降压变换器与纹波注入；高压降压与高压 LDO 的比较 | [aux-bias-supply](aux-bias-supply.md) 的“辅助绕组整流 + 高压降压变换器”方案与比较表；纹波注入的直流偏移见 [cot-buck](cot-buck.md) 与 [恒定导通时间降压的纹波注入](../计算方法/恒定导通时间降压的纹波注入.md) |
| 方案 2：一次侧 VCC 取电的低电流交流指示 | [ac-indicator](ac-indicator.md) 的“从一次侧控制器 VCC 取电”方案 |
| 方案 3：比较器经高侧晶体管驱动高有效故障脚；故障脚上下门限的两种用途 | [aux-overvoltage-latch](aux-overvoltage-latch.md) 的“比较器经高侧晶体管驱动高有效故障脚”方案；锁存记忆的通用做法见 [fault-memory-comparator](fault-memory-comparator.md) |
| 方案 4：二次侧辅助经反向保护 LDO 和串联二极管供同步整流 | [ldo](ldo.md) 的“带输入反接与输出反灌保护的高压 LDO”方案；同步整流一侧见 [synchronous-rectification](synchronous-rectification.md) |
| 判断案例 F-001：功率因数校正控制器的线电压档判别 | [pfc-boost](pfc-boost.md) 必算项“高/低压档判别点”，去掉了那块板的分压值与电压 |
| 判断案例 F-005：订货码的公差字段 | [ac-input-protection](ac-input-protection.md) 方案 3 已知坑，去掉了那块板的订货码与阻值 |
| 判断案例 F-006：压敏电阻按位号前缀套用了普通电阻的模板 | 删去：说的是某个工具的模板规则，不是电路知识；压敏电阻的选用见 [ac-input-protection](ac-input-protection.md) |

控制器故障脚的门限（拉高超过 2.79～3.21 V 为过压锁定，拉低到 380～420 mV 以下为过温，S1 p8）现写在 aux-overvoltage-latch。
