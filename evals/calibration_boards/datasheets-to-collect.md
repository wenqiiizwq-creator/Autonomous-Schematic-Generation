# 校准板待采集手册清单

日期：2026-11-02。盘点依据和完整结论见
[开工前知识缺口报告](../../docs/proposals/calibration-boards-readiness-2026-11-02.md)。
这里只写系列名，不写参数；下载后读手册再判断是否合用。

**存放**：`~/Documents/知识库/HardwareWiki/raw/Datasheet/<分类>/<子类>/`，文件名 `Vendor - PartNumber.pdf`；
厂商简称查 `VENDORS.yaml`，分类查 `元器件体系/器件统一分类大表.md`。

**系列名来源**：**参考设计** = 库内参考设计实际使用；**联网** = 本次在厂家或分销页面看到；
**经验** = 凭工程经验列出，下载时确认系列还在产。

## 必须采集（阻塞 PoE 板）

### PoE 传感节点：RJ45 与数据磁件

以下三类任选一条路线即可开工：**A = 第 1 类 + 第 2 类（分立）**，或 **B = 第 3 类（集成）**。建议都下，好做方案比较。

| # | 器件类（存放子类） | 需求里的关键指标 | 建议搜集的系列 | 来源 |
|---|---|---|---|---|
| 1 | 带 PoE 额定的 10/100 分立数据磁件（21_电感器与磁件/变压器） | 802.3af Type 1 受电（POE-002）；媒体侧中心抽头引出；手册写明 PoE 直流偏置；MDI 隔离 1500 Vrms、50～60 Hz、60 s（POE-012）；贴片；温度待 C11，尽量宽温 | Pulse HX1198 系列 | 参考设计（TIDA-010046 用 HX1198FNL） |
| | | | Würth WE-LAN 7490130 系列 | 联网 |
| | | | LINK-PP LP2019 系列 | 联网 |
| 2 | 无磁 RJ45 插座（27_连接器/IO连接器） | 8 触点全部引出，支持 Alternative A/B（POE-004）；带屏蔽壳，屏蔽接法要满足 POE-011；通孔或贴片不限 | Würth WR-MJ 系列 | 经验 |
| | | | Amphenol RJHSE 系列 | 经验 |
| | | | Molex Modular Jack 系列 | 经验 |
| 3 | 带 PoE 的 10/100 集成磁件 RJ45（27_连接器/IO连接器） | 中心抽头**引出到管脚**，含备用线对；手册标 802.3af；隔离 1500 Vrms、60 s；不能是 HR911105A 那种内部接 75 Ω 的结构；LED 可选 | Würth WE-RJ45 LAN 系列 | 经验 |
| | | | Bel MagJack 系列 | 经验 |
| | | | Pulse JXD 系列 | 经验 |

## 建议采集（增强，不阻塞）

库内有替代，补了以后候选更多、参考设计能完整对上。

| # | 板 | 器件类（存放子类） | 需求里的关键指标 | 建议搜集的系列 | 来源 |
|---|---|---|---|---|---|
| 4 | PoE | PD 控制器，集成反激或配独立反激（08_电源管理/以太网供电 (PoE)） | 802.3at Type 1 或 af；≤12.95 W；隔离输出 | TI TPS23755 | 参考设计（TIDA-010046） |
| | | | | TI TPS23753A | 经验 |
| | | | | Microchip PD70100 系列 | 联网 |
| 5 | PoE | PoE 专用反激变压器（21_电感器与磁件/变压器） | ≤12.95 W；初次级满足 1500 Vrms、60 s（POE-011）；36～57 V 输入 | Würth WE-POE 系列 | 联网 |
| | | | | Würth WE-FLYLT 系列 | 联网 |
| | | | | Pulse PA 系列（PoE 件） | 联网 |
| 6 | 工业 | 一体隔离数字输入（15_接口与隔离/工业接口） | 8 路 24 V、IEC 61131-2 Type 待 C07；组隔离，耐压待 C10 | TI ISO1228、ISO1212 系列 | 经验 |
| | | | | ADI MAX22190、MAX22192 系列（需配隔离器） | 经验 |
| 7 | 工业 | 多通道光耦（24_光电器件/光耦） | 分立 DI 路线，4 通道封装；隔离待 C10 | Toshiba TLP291-4 系列 | 经验 |
| | | | | Liteon LTV-247 系列 | 经验 |
| 8 | PoE | 温湿度传感器（16_传感器/湿度传感器） | 温度和相对湿度同时输出（POE-019）；I²C；精度待 C07 | Sensirion SHT4x 系列 | 经验 |
| | | | | TI HDC302x 系列 | 经验 |

## 条件性采集（EMC 等级确认后再决定）

| # | 板 | 器件类（存放子类） | 什么情况下需要 | 建议搜集的系列 | 来源 |
|---|---|---|---|---|---|
| 9 | 两板 | 气体放电管（28_保护器件，库内尚无子类，无分类放 `ZZ_其他` 并报告） | 通信口对地浪涌等级要求较高时（工业 C13、PoE C14）；须核其点火与隔离耐压的关系，不能短路 1500 Vrms 隔离 | Bourns 2038 系列 | 经验 |
| | | | | Littelfuse CG 系列 | 经验 |
| 10 | 工业 | CAN 共模扼流圈（21_电感器与磁件/共模扼流圈） | C12/C13 或 C06 需要时；库内 Würth 件手册写的电感量在 0.1～9 µH，未核是否适合 CAN；也可选免扼流收发器（库内 SLLY020） | TDK ACT45B 系列 | 经验 |
| | | | | Würth WE-SL2 系列 | 经验 |

## 不是手册，但也要取得

记作 `external` 待办，不阻塞选型。

| 资料 | 用途 | 状态 |
|---|---|---|
| IEC 61131-2:2017 正文 | C01/C07 的电源和 DI 限值 | 库内只有 Siemens 转引（EN 61131-2:2003） |
| IEEE 802.3 现行汇编 Clause 33、14、25、28 | PoE-C01、C05 | 库内没有 |
| IEC 61000-4-2:2025、IEC 61000-4-4:2012 | 试验方法 | 库内没有；等级已有 GB/T 17799.2—2023，4-5 已有原文 |
| ANSI/TIA-485-A、ISO 11898-2:2026 | 工业 C05、C06 | 库内没有，已有 TI 转引 |

## 采集状态（2026-11-02）

已下载并放入 `HardwareWiki/raw/Datasheet/`（厂家官网原件，版次已核）：

| 清单项 | 文件 | 版次 | 备注 |
|---|---|---|---|
| 1 | 21_电感器与磁件/变压器/LINK-PP - LP2019ANL.pdf | Rev B 2017-06-29 | 纯图片 PDF；PoE+、中心抽头引出（TXCT 15/RXCT 10）、1500 Vrms、−40～85 ℃；未写 60 s 时长 |
| 3 | 27_连接器/IO连接器/Bel - 0826-1X1T-57-F.pdf | Rev F 2016-08-09 | 官网只给机械图，缺电气规格页，不能据此判合格；完整规格书要向 Bel 索取 |
| 4 | 08_电源管理/以太网供电 (PoE)/TI - TPS23755.pdf | SLVSDW2B 2020-11 | |
| 4 | 08_电源管理/以太网供电 (PoE)/TI - TPS23753A.pdf | SLVS933D 2020-12 | |
| 4 | 08_电源管理/以太网供电 (PoE)/Microchip - PD70100.pdf | DS00003639C 2025 | 只是 PD 前端，不带 PWM；带 PWM 的是 PD70101 |

未取得（厂家站拦脚本下载或连不上，第三方镜像按规矩不取；需在浏览器里手动保存）：

| 清单项 | 器件 | 直接链接 |
|---|---|---|
| 1 | Pulse HX1198FNL（分销商标“不推荐新设计”，HX1198NL 是否带 PoE 额定待手册确认） | https://productfinder.pulseelectronics.com/api/open/part-attachments/datasheet/HX1198FNL |
| 1 | Würth WE-LAN 749013011A | https://www.we-online.com/components/products/datasheet/749013011A.pdf |
| 2 | Würth WR-MJ 615008137421 | https://www.we-online.com/components/products/datasheet/615008137421.pdf |
| 2 | Amphenol RJHSE | https://www.amphenol-cs.com/media/wysiwyg/files/documentation/datasheet/inputoutput/io_modjack_rjhse.pdf |
| 2 | Molex 屏蔽 8P8C Modular Jack | https://www.molex.com/ |
| 3 | Würth WE-RJ45 LAN 7499010121A | https://www.we-online.com/components/products/datasheet/7499010121A.pdf |
| 3 | Pulse JXD 系列 | https://productfinder.pulseelectronics.com/ |
| 5 | Würth WE-POE 749119xxx、WE-FLYLT | https://www.we-online.com/ |
| 5 | Pulse PA 系列 PoE 反激变压器 | https://productfinder.pulseelectronics.com/ |

A 路线（分立磁件 + 无磁 RJ45）缺第 2 类，B 路线（集成磁件 RJ45）缺可用的电气规格页，两条路线都还凑不齐。
