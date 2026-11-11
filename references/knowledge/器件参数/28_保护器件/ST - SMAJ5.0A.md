# ST SMAJ5.0A

类别：器件参数。
器件：SMAJxxA/CA 系列 TVS，SMA 封装
手册：DS1251，Rev 15，2023 年 7 月。

## 来源

- S1：Datasheet/28_保护器件/TVS_ESD保护器件/ST - SMAJ5.0A.pdf

页码是 PDF 文件的页序。

## 绝对最大值

| 参数 | 符号 | 条件 | 最小 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|
| 接触放电峰值电压 | VPP | IEC 61000-4-2，C = 150 pF，R = 330 Ω，Tamb = 25 °C |  | 30 | kV | S1 p2 |
| 空气放电峰值电压 | VPP | IEC 61000-4-2，C = 150 pF，R = 330 Ω，Tamb = 25 °C |  | 30 | kV | S1 p2 |
| 峰值脉冲功率 | PPP | 10/1000 µs，Tj 初始 = Tamb = 25 °C |  | 400 | W | S1 p2 |
| 储存温度 | Tstg |  | −65 | 150 | °C | S1 p2 |
| 工作结温 | Tj |  | −55 | 150 | °C | S1 p2 |
| 焊接引线温度 | TL | 持续 10 s |  | 260 | °C | S1 p2 |


## 推荐工作条件

手册未单列推荐工作条件；不能把绝对最大值当作正常工作条件。

## 电气特性

测试条件：Tamb = 25 °C，除非另有注明。最小、最大为限值；典型不是保证值。IPP 按表列浪涌能力记录于最大栏，须与对应脉冲和 VCL 配对使用（S1 p3）。

| 参数 | 符号 | 条件 | 最小 | 典型 | 最大 | 单位 | 来源 |
|---|---|---|---|---|---|---|---|
| 反向工作电压 | VRM | SMAJ5.0A/CA |  |  | 5.0 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ5.0A/CA，VRM = 5.0 V，Tamb = 25 °C |  |  | 20 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ5.0A/CA，VRM = 5.0 V，Tamb = 85 °C |  |  | 50 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ5.0A/CA，IBR = 10 mA | 6.40 | 6.74 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ5.0A/CA，10/1000 µs，IPP = 43.5 A |  |  | 9.2 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ5.0A/CA，10/1000 µs，配对 VCL = 9.2 V；表列能力值 |  |  | 43.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ5.0A/CA，10/1000 µs |  |  | 0.049 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ5.0A/CA，8/20 µs，IPP = 174 A |  |  | 13.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ5.0A/CA，8/20 µs，配对 VCL = 13.4 V；表列能力值 |  |  | 174 | A | S1 p3 |
| 动态电阻 | RD | SMAJ5.0A/CA，8/20 µs |  |  | 0.036 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ5.0A/CA |  |  | 5.7 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ6.0A/CA |  |  | 6.0 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ6.0A/CA，VRM = 6.0 V，Tamb = 25 °C |  |  | 20 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ6.0A/CA，VRM = 6.0 V，Tamb = 85 °C |  |  | 50 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ6.0A/CA，IBR = 10 mA | 6.70 | 7.05 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ6.0A/CA，10/1000 µs，IPP = 38.8 A |  |  | 10.3 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ6.0A/CA，10/1000 µs，配对 VCL = 10.3 V；表列能力值 |  |  | 38.8 | A | S1 p3 |
| 动态电阻 | RD | SMAJ6.0A/CA，10/1000 µs |  |  | 0.075 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ6.0A/CA，8/20 µs，IPP = 170 A |  |  | 13.7 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ6.0A/CA，8/20 µs，配对 VCL = 13.7 V；表列能力值 |  |  | 170 | A | S1 p3 |
| 动态电阻 | RD | SMAJ6.0A/CA，8/20 µs |  |  | 0.037 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ6.0A/CA |  |  | 5.9 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ6.5A/CA |  |  | 6.5 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ6.5A/CA，VRM = 6.5 V，Tamb = 25 °C |  |  | 20 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ6.5A/CA，VRM = 6.5 V，Tamb = 85 °C |  |  | 50 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ6.5A/CA，IBR = 10 mA | 7.20 | 7.58 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ6.5A/CA，10/1000 µs，IPP = 35.7 A |  |  | 11.2 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ6.5A/CA，10/1000 µs，配对 VCL = 11.2 V；表列能力值 |  |  | 35.7 | A | S1 p3 |
| 动态电阻 | RD | SMAJ6.5A/CA，10/1000 µs |  |  | 0.091 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ6.5A/CA，8/20 µs，IPP = 160 A |  |  | 14.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ6.5A/CA，8/20 µs，配对 VCL = 14.5 V；表列能力值 |  |  | 160 | A | S1 p3 |
| 动态电阻 | RD | SMAJ6.5A/CA，8/20 µs |  |  | 0.041 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ6.5A/CA |  |  | 6.1 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ8.5A/CA |  |  | 8.5 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ8.5A/CA，VRM = 8.5 V，Tamb = 25 °C |  |  | 20 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ8.5A/CA，VRM = 8.5 V，Tamb = 85 °C |  |  | 50 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ8.5A/CA，IBR = 1 mA | 9.4 | 9.9 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ8.5A/CA，10/1000 µs，IPP = 27.7 A |  |  | 14.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ8.5A/CA，10/1000 µs，配对 VCL = 14.4 V；表列能力值 |  |  | 27.7 | A | S1 p3 |
| 动态电阻 | RD | SMAJ8.5A/CA，10/1000 µs |  |  | 0.145 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ8.5A/CA，8/20 µs，IPP = 124 A |  |  | 19.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ8.5A/CA，8/20 µs，配对 VCL = 19.5 V；表列能力值 |  |  | 124 | A | S1 p3 |
| 动态电阻 | RD | SMAJ8.5A/CA，8/20 µs |  |  | 0.073 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ8.5A/CA |  |  | 7.3 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ10A/CA |  |  | 10 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ10A/CA，VRM = 10 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ10A/CA，VRM = 10 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ10A/CA，IBR = 1 mA | 11.1 | 11.7 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ10A/CA，10/1000 µs，IPP = 23.5 A |  |  | 17 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ10A/CA，10/1000 µs，配对 VCL = 17 V；表列能力值 |  |  | 23.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ10A/CA，10/1000 µs |  |  | 0.201 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ10A/CA，8/20 µs，IPP = 106 A |  |  | 21.7 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ10A/CA，8/20 µs，配对 VCL = 21.7 V；表列能力值 |  |  | 106 | A | S1 p3 |
| 动态电阻 | RD | SMAJ10A/CA，8/20 µs |  |  | 0.089 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ10A/CA |  |  | 7.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ12A/CA |  |  | 12 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ12A/CA，VRM = 12 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ12A/CA，VRM = 12 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ12A/CA，IBR = 1 mA | 13.3 | 14.0 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ12A/CA，10/1000 µs，IPP = 20.1 A |  |  | 19.9 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ12A/CA，10/1000 µs，配对 VCL = 19.9 V；表列能力值 |  |  | 20.1 | A | S1 p3 |
| 动态电阻 | RD | SMAJ12A/CA，10/1000 µs |  |  | 0.259 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ12A/CA，8/20 µs，IPP = 91 A |  |  | 25.3 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ12A/CA，8/20 µs，配对 VCL = 25.3 V；表列能力值 |  |  | 91 | A | S1 p3 |
| 动态电阻 | RD | SMAJ12A/CA，8/20 µs |  |  | 0.116 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ12A/CA |  |  | 8.3 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ13A/CA |  |  | 13 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ13A/CA，VRM = 13 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ13A/CA，VRM = 13 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ13A/CA，IBR = 1 mA | 14.4 | 15.2 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ13A/CA，10/1000 µs，IPP = 18.6 A |  |  | 21.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ13A/CA，10/1000 µs，配对 VCL = 21.5 V；表列能力值 |  |  | 18.6 | A | S1 p3 |
| 动态电阻 | RD | SMAJ13A/CA，10/1000 µs |  |  | 0.298 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ13A/CA，8/20 µs，IPP = 85 A |  |  | 27.2 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ13A/CA，8/20 µs，配对 VCL = 27.2 V；表列能力值 |  |  | 85 | A | S1 p3 |
| 动态电阻 | RD | SMAJ13A/CA，8/20 µs |  |  | 0.132 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ13A/CA |  |  | 8.4 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ15A/CA |  |  | 15 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ15A/CA，VRM = 15 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ15A/CA，VRM = 15 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ15A/CA，IBR = 1 mA | 16.7 | 17.6 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ15A/CA，10/1000 µs，IPP = 16.4 A |  |  | 24.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ15A/CA，10/1000 µs，配对 VCL = 24.4 V；表列能力值 |  |  | 16.4 | A | S1 p3 |
| 动态电阻 | RD | SMAJ15A/CA，10/1000 µs |  |  | 0.361 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ15A/CA，8/20 µs，IPP = 71 A |  |  | 32.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ15A/CA，8/20 µs，配对 VCL = 32.5 V；表列能力值 |  |  | 71 | A | S1 p3 |
| 动态电阻 | RD | SMAJ15A/CA，8/20 µs |  |  | 0.197 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ15A/CA |  |  | 8.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ18A/CA |  |  | 18 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ18A/CA，VRM = 18 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ18A/CA，VRM = 18 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ18A/CA，IBR = 1 mA | 20.0 | 21.1 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ18A/CA，10/1000 µs，IPP = 13.7 A |  |  | 29.2 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ18A/CA，10/1000 µs，配对 VCL = 29.2 V；表列能力值 |  |  | 13.7 | A | S1 p3 |
| 动态电阻 | RD | SMAJ18A/CA，10/1000 µs |  |  | 0.514 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ18A/CA，8/20 µs，IPP = 59 A |  |  | 39.3 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ18A/CA，8/20 µs，配对 VCL = 39.3 V；表列能力值 |  |  | 59 | A | S1 p3 |
| 动态电阻 | RD | SMAJ18A/CA，8/20 µs |  |  | 0.291 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ18A/CA |  |  | 9.2 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ20A/CA |  |  | 20 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ20A/CA，VRM = 20 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ20A/CA，VRM = 20 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ20A/CA，IBR = 1 mA | 22.2 | 23.4 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ20A/CA，10/1000 µs，IPP = 12.3 A |  |  | 32.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ20A/CA，10/1000 µs，配对 VCL = 32.4 V；表列能力值 |  |  | 12.3 | A | S1 p3 |
| 动态电阻 | RD | SMAJ20A/CA，10/1000 µs |  |  | 0.637 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ20A/CA，8/20 µs，IPP = 54 A |  |  | 42.8 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ20A/CA，8/20 µs，配对 VCL = 42.8 V；表列能力值 |  |  | 54 | A | S1 p3 |
| 动态电阻 | RD | SMAJ20A/CA，8/20 µs |  |  | 0.338 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ20A/CA |  |  | 9.4 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ24A/CA |  |  | 24 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ24A/CA，VRM = 24 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ24A/CA，VRM = 24 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ24A/CA，IBR = 1 mA | 26.7 | 28.1 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ24A/CA，10/1000 µs，IPP = 10.3 A |  |  | 38.9 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ24A/CA，10/1000 µs，配对 VCL = 38.9 V；表列能力值 |  |  | 10.3 | A | S1 p3 |
| 动态电阻 | RD | SMAJ24A/CA，10/1000 µs |  |  | 0.912 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ24A/CA，8/20 µs，IPP = 46 A |  |  | 50 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ24A/CA，8/20 µs，配对 VCL = 50 V；表列能力值 |  |  | 46 | A | S1 p3 |
| 动态电阻 | RD | SMAJ24A/CA，8/20 µs |  |  | 0.446 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ24A/CA |  |  | 9.6 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ26A/CA |  |  | 26 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ26A/CA，VRM = 26 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ26A/CA，VRM = 26 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ26A/CA，IBR = 1 mA | 28.9 | 30.4 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ26A/CA，10/1000 µs，IPP = 9.5 A |  |  | 42.1 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ26A/CA，10/1000 µs，配对 VCL = 42.1 V；表列能力值 |  |  | 9.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ26A/CA，10/1000 µs |  |  | 1.07 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ26A/CA，8/20 µs，IPP = 43 A |  |  | 53.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ26A/CA，8/20 µs，配对 VCL = 53.5 V；表列能力值 |  |  | 43 | A | S1 p3 |
| 动态电阻 | RD | SMAJ26A/CA，8/20 µs |  |  | 0.502 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ26A/CA |  |  | 9.7 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ28A/CA |  |  | 28 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ28A/CA，VRM = 28 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ28A/CA，VRM = 28 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ28A/CA，IBR = 1 mA | 31.1 | 32.7 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ28A/CA，10/1000 µs，IPP = 8.8 A |  |  | 45.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ28A/CA，10/1000 µs，配对 VCL = 45.4 V；表列能力值 |  |  | 8.8 | A | S1 p3 |
| 动态电阻 | RD | SMAJ28A/CA，10/1000 µs |  |  | 1.26 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ28A/CA，8/20 µs，IPP = 39 A |  |  | 59 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ28A/CA，8/20 µs，配对 VCL = 59 V；表列能力值 |  |  | 39 | A | S1 p3 |
| 动态电阻 | RD | SMAJ28A/CA，8/20 µs |  |  | 0.632 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ28A/CA |  |  | 9.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ30A/CA |  |  | 30 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ30A/CA，VRM = 30 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ30A/CA，VRM = 30 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ30A/CA，IBR = 1 mA | 33.3 | 35.1 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ30A/CA，10/1000 µs，IPP = 8.3 A |  |  | 48.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ30A/CA，10/1000 µs，配对 VCL = 48.4 V；表列能力值 |  |  | 8.3 | A | S1 p3 |
| 动态电阻 | RD | SMAJ30A/CA，10/1000 µs |  |  | 1.39 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ30A/CA，8/20 µs，IPP = 36 A |  |  | 64.3 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ30A/CA，8/20 µs，配对 VCL = 64.3 V；表列能力值 |  |  | 36 | A | S1 p3 |
| 动态电阻 | RD | SMAJ30A/CA，8/20 µs |  |  | 0.762 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ30A/CA |  |  | 9.9 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ33A/CA |  |  | 33 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ33A/CA，VRM = 33 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ33A/CA，VRM = 33 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ33A/CA，IBR = 1 mA | 36.7 | 38.6 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ33A/CA，10/1000 µs，IPP = 7.5 A |  |  | 53.3 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ33A/CA，10/1000 µs，配对 VCL = 53.3 V；表列能力值 |  |  | 7.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ33A/CA，10/1000 µs |  |  | 1.70 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ33A/CA，8/20 µs，IPP = 33 A |  |  | 69.7 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ33A/CA，8/20 µs，配对 VCL = 69.7 V；表列能力值 |  |  | 33 | A | S1 p3 |
| 动态电阻 | RD | SMAJ33A/CA，8/20 µs |  |  | 0.884 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ33A/CA |  |  | 10.0 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ40A/CA |  |  | 40 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ40A/CA，VRM = 40 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ40A/CA，VRM = 40 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ40A/CA，IBR = 1 mA | 44.4 | 46.7 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ40A/CA，10/1000 µs，IPP = 6.2 A |  |  | 64.5 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ40A/CA，10/1000 µs，配对 VCL = 64.5 V；表列能力值 |  |  | 6.2 | A | S1 p3 |
| 动态电阻 | RD | SMAJ40A/CA，10/1000 µs |  |  | 2.49 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ40A/CA，8/20 µs，IPP = 27 A |  |  | 84 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ40A/CA，8/20 µs，配对 VCL = 84 V；表列能力值 |  |  | 27 | A | S1 p3 |
| 动态电阻 | RD | SMAJ40A/CA，8/20 µs |  |  | 1.30 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ40A/CA |  |  | 10.1 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ43A/CA |  |  | 43 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ43A/CA，VRM = 43 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ43A/CA，VRM = 43 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ43A/CA，IBR = 1 mA | 47.8 | 50.3 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ43A/CA，10/1000 µs，IPP = 5.7 A |  |  | 69.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ43A/CA，10/1000 µs，配对 VCL = 69.4 V；表列能力值 |  |  | 5.7 | A | S1 p3 |
| 动态电阻 | RD | SMAJ43A/CA，10/1000 µs |  |  | 2.91 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ43A/CA，8/20 µs，IPP = 25 A |  |  | 91 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ43A/CA，8/20 µs，配对 VCL = 91 V；表列能力值 |  |  | 25 | A | S1 p3 |
| 动态电阻 | RD | SMAJ43A/CA，8/20 µs |  |  | 1.53 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ43A/CA |  |  | 10.2 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ48A/CA |  |  | 48 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ48A/CA，VRM = 48 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ48A/CA，VRM = 48 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ48A/CA，IBR = 1 mA | 53.3 | 56.1 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ48A/CA，10/1000 µs，IPP = 5.2 A |  |  | 77.4 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ48A/CA，10/1000 µs，配对 VCL = 77.4 V；表列能力值 |  |  | 5.2 | A | S1 p3 |
| 动态电阻 | RD | SMAJ48A/CA，10/1000 µs |  |  | 3.56 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ48A/CA，8/20 µs，IPP = 23 A |  |  | 100 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ48A/CA，8/20 µs，配对 VCL = 100 V；表列能力值 |  |  | 23 | A | S1 p3 |
| 动态电阻 | RD | SMAJ48A/CA，8/20 µs |  |  | 1.79 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ48A/CA |  |  | 10.3 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ58A/CA |  |  | 58 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ58A/CA，VRM = 58 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ58A/CA，VRM = 58 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ58A/CA，IBR = 1 mA | 64.4 | 67.8 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ58A/CA，10/1000 µs，IPP = 4.3 A |  |  | 93.6 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ58A/CA，10/1000 µs，配对 VCL = 93.6 V；表列能力值 |  |  | 4.3 | A | S1 p3 |
| 动态电阻 | RD | SMAJ58A/CA，10/1000 µs |  |  | 5.21 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ58A/CA，8/20 µs，IPP = 19 A |  |  | 121 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ58A/CA，8/20 µs，配对 VCL = 121 V；表列能力值 |  |  | 19 | A | S1 p3 |
| 动态电阻 | RD | SMAJ58A/CA，8/20 µs |  |  | 2.62 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ58A/CA |  |  | 10.4 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ70A/CA |  |  | 70 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ70A/CA，VRM = 70 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ70A/CA，VRM = 70 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ70A/CA，IBR = 1 mA | 77.8 | 81.9 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ70A/CA，10/1000 µs，IPP = 3.5 A |  |  | 113 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ70A/CA，10/1000 µs，配对 VCL = 113 V；表列能力值 |  |  | 3.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ70A/CA，10/1000 µs |  |  | 7.72 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ70A/CA，8/20 µs，IPP = 16 A |  |  | 146 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ70A/CA，8/20 µs，配对 VCL = 146 V；表列能力值 |  |  | 16 | A | S1 p3 |
| 动态电阻 | RD | SMAJ70A/CA，8/20 µs |  |  | 3.75 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ70A/CA |  |  | 10.5 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ85A/CA |  |  | 85 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ85A/CA，VRM = 85 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ85A/CA，VRM = 85 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ85A/CA，IBR = 1 mA | 94 | 99 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ85A/CA，10/1000 µs，IPP = 2.9 A |  |  | 137 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ85A/CA，10/1000 µs，配对 VCL = 137 V；表列能力值 |  |  | 2.9 | A | S1 p3 |
| 动态电阻 | RD | SMAJ85A/CA，10/1000 µs |  |  | 11.4 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ85A/CA，8/20 µs，IPP = 13 A |  |  | 178 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ85A/CA，8/20 µs，配对 VCL = 178 V；表列能力值 |  |  | 13 | A | S1 p3 |
| 动态电阻 | RD | SMAJ85A/CA，8/20 µs |  |  | 5.70 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ85A/CA |  |  | 10.6 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ100A/CA |  |  | 100 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ100A/CA，VRM = 100 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ100A/CA，VRM = 100 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ100A/CA，IBR = 1 mA | 111 | 117 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ100A/CA，10/1000 µs，IPP = 2.5 A |  |  | 162 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ100A/CA，10/1000 µs，配对 VCL = 162 V；表列能力值 |  |  | 2.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ100A/CA，10/1000 µs |  |  | 15.7 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ100A/CA，8/20 µs，IPP = 11 A |  |  | 212 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ100A/CA，8/20 µs，配对 VCL = 212 V；表列能力值 |  |  | 11 | A | S1 p3 |
| 动态电阻 | RD | SMAJ100A/CA，8/20 µs |  |  | 8.10 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ100A/CA |  |  | 10.7 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ130A/CA |  |  | 130 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ130A/CA，VRM = 130 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ130A/CA，VRM = 130 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ130A/CA，IBR = 1 mA | 144 | 152 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ130A/CA，10/1000 µs，IPP = 1.9 A |  |  | 209 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ130A/CA，10/1000 µs，配对 VCL = 209 V；表列能力值 |  |  | 1.9 | A | S1 p3 |
| 动态电阻 | RD | SMAJ130A/CA，10/1000 µs |  |  | 26.0 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ130A/CA，8/20 µs，IPP = 9 A |  |  | 265 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ130A/CA，8/20 µs，配对 VCL = 265 V；表列能力值 |  |  | 9 | A | S1 p3 |
| 动态电阻 | RD | SMAJ130A/CA，8/20 µs |  |  | 11.7 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ130A/CA |  |  | 10.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ154A/CA |  |  | 154 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ154A/CA，VRM = 154 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ154A/CA，VRM = 154 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ154A/CA，IBR = 1 mA | 171 | 180 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ154A/CA，10/1000 µs，IPP = 1.6 A |  |  | 246 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ154A/CA，10/1000 µs，配对 VCL = 246 V；表列能力值 |  |  | 1.6 | A | S1 p3 |
| 动态电阻 | RD | SMAJ154A/CA，10/1000 µs |  |  | 35.6 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ154A/CA，8/20 µs，IPP = 7 A |  |  | 317 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ154A/CA，8/20 µs，配对 VCL = 317 V；表列能力值 |  |  | 7 | A | S1 p3 |
| 动态电阻 | RD | SMAJ154A/CA，8/20 µs |  |  | 18.3 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ154A/CA |  |  | 10.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ170A/CA |  |  | 170 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ170A/CA，VRM = 170 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ170A/CA，VRM = 170 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ170A/CA，IBR = 1 mA | 189 | 199 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ170A/CA，10/1000 µs，IPP = 1.4 A |  |  | 275 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ170A/CA，10/1000 µs，配对 VCL = 275 V；表列能力值 |  |  | 1.4 | A | S1 p3 |
| 动态电阻 | RD | SMAJ170A/CA，10/1000 µs |  |  | 47.2 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ170A/CA，8/20 µs，IPP = 6.5 A |  |  | 353 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ170A/CA，8/20 µs，配对 VCL = 353 V；表列能力值 |  |  | 6.5 | A | S1 p3 |
| 动态电阻 | RD | SMAJ170A/CA，8/20 µs |  |  | 22.2 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ170A/CA |  |  | 10.8 | 10⁻⁴/°C | S1 p3 |
| 反向工作电压 | VRM | SMAJ188A/CA |  |  | 188 | V | S1 p3 |
| 反向漏电流 | IRM | SMAJ188A/CA，VRM = 188 V，Tamb = 25 °C |  |  | 0.2 | µA | S1 p3 |
| 反向漏电流 | IRM | SMAJ188A/CA，VRM = 188 V，Tamb = 85 °C |  |  | 1 | µA | S1 p3 |
| 击穿电压 | VBR | SMAJ188A/CA，IBR = 1 mA | 209 | 220 |  | V | S1 p3 |
| 钳位电压 | VCL | SMAJ188A/CA，10/1000 µs，IPP = 1.4 A |  |  | 328 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ188A/CA，10/1000 µs，配对 VCL = 328 V；表列能力值 |  |  | 1.4 | A | S1 p3 |
| 动态电阻 | RD | SMAJ188A/CA，10/1000 µs |  |  | 69.3 | Ω | S1 p3 |
| 钳位电压 | VCL | SMAJ188A/CA，8/20 µs，IPP = 6 A |  |  | 388 | V | S1 p3 |
| 脉冲电流能力 | IPP | SMAJ188A/CA，8/20 µs，配对 VCL = 388 V；表列能力值 |  |  | 6 | A | S1 p3 |
| 动态电阻 | RD | SMAJ188A/CA，8/20 µs |  |  | 26.2 | Ω | S1 p3 |
| 击穿电压温度系数 | αT | SMAJ188A/CA |  |  | 10.8 | 10⁻⁴/°C | S1 p3 |


用这些数时要注意：

- VBR 的典型值不能当作击穿门限保证值；αT 为最大值。表下注 1、2 说明 VBR、VCL 随结温变化；注 3 给出按应用浪涌电流使用 RD 的关系，本条目不另行计算电压（S1 p3）。
- 注 4 声明单向 A 和双向 CA 器件的浪涌能力适用于两个方向，但不能把这句话理解为单向器件的两个方向具有相同击穿电压（S1 p3）。
- 原件 VBR 只列 Min.、Typ.，未给 Max.；已对照页面图像，第二列 6.74 V 等按典型值记录，最大栏留空。首页描述说用于低于 600 W 的浪涌，但首页特性和绝对最大值表为 400 W，不能按描述段的 600 W 选型（S1 p1、p2、p3）。

## 热特性

热阻及热阻抗仅以曲线形式提供，不从曲线读数（S1 p5）。

## 静电额定

手册没有给出静电额定（已查全文）。

未见人体模型、带电器件模型额定表；首页另有 IEC 61000-4-2 防护声明，不据此补人体模型或带电器件模型数值（S1 p1）。

## 引脚与处置

| 引脚 | 功能 | 能接受的电压 | 不用时怎么接 | 来源 |
|---|---|---|---|---|
| 阴极 | A 型为标记条端；CA 型为双向端子 | 反向工作电压按型号，见电气特性表 |  | S1 p3、p7、p10 |
| 阳极 | A 型另一端；CA 型为双向端子 |  |  | S1 p3、p7、p10 |


## 必需外围

手册未规定必需外部元件及其取值范围。

## 订货型号与封装

xx 对应反向工作电压，A、CA 分别为单向、双向，-TR 表示卷带（S1 p10）。

| 订货型号或后缀 | 封装 | 脚数 | 电压或功能档 | 温度范围 | 引脚镀层 | 来源 |
|---|---|---|---|---|---|---|
| SMAJ5.0A-TR | SMA |  | 单向 |  | 哑光锡 | S1 p1、p10 |
| SMAJ5.0CA-TR | SMA |  | 双向 |  | 哑光锡 | S1 p1、p10 |

其余见 S1 p10。

A 为单向，CA 为双向；电压档的 VRM、VBR、漏电流、两种波形的钳位、脉冲能力、动态电阻及温度系数均已逐型号列出。封装及包装信息见原件（S1 p3、p6、p10）。

## 核对记录

- 2026-11-09：逐页对照原件 p1 至 p3、p5、p6、p7、p10 的规格、引脚、脚注及适用应用说明；工具核对通过，核对 346 个数。
