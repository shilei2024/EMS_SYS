// 知识图谱初始化Cypher脚本
// Phase 3: 知识图谱与财务模块

// 创建约束
CREATE CONSTRAINT component_mpn_manufacturer IF NOT EXISTS
ON (c:Component)
ASSERT (c.mpn, c.manufacturer) IS UNIQUE;

CREATE CONSTRAINT parameter_name_value IF NOT EXISTS
ON (p:Parameter)
ASSERT (p.name, p.value) IS UNIQUE;

// 创建常用参数类别
CREATE (p1:ParameterCategory {name: "电气参数", description: "电压、电流、功率等电气特性"})
CREATE (p2:ParameterCategory {name: "封装参数", description: "封装尺寸、引脚数等"})
CREATE (p3:ParameterCategory {name: "环境参数", description: "工作温度、湿度等"})
CREATE (p4:ParameterCategory {name: "时序参数", description: "时钟频率、延迟等"})
CREATE (p5:ParameterCategory {name: "质量参数", description: "可靠性、寿命等"});

// 创建元器件分类
CREATE (c1:Category {name: "MCU", description: "微控制器", code: "IC_MCU"})
CREATE (c2:Category {name: "MPU", description: "微处理器", code: "IC_MPU"})
CREATE (c3:Category {name: "Memory", description: "存储器", code: "IC_MEM"})
CREATE (c4:Category {name: "Power", description: "电源管理", code: "IC_PWR"})
CREATE (c5:Category {name: "Analog", description: "模拟芯片", code: "IC_ANALOG"})
CREATE (c6:Category {name: "Sensor", description: "传感器", code: "IC_SENSOR"})
CREATE (c7:Category {name: "Wireless", description: "无线芯片", code: "IC_WIRELESS"})
CREATE (c8:Category {name: "Passive", description: "被动器件", code: "PASSIVE"})

// 创建制造商
CREATE (m1:Manufacturer {Microelectronics", shortname: "ST_name: "ST", country: "Switzerland"})
CREATE (m2:Manufacturer {name: "Texas Instruments", short_name: "TI", country: "USA"})
CREATE (m3:Manufacturer {name: "Infineon Technologies", short_name: "Infineon", country: "Germany"})
CREATE (m4:Manufacturer {name: "NXP Semiconductors", short_name: "NXP", country: "Netherlands"})
CREATE (m5:Manufacturer {name: "Microchip Technology", short_name: "Microchip", country: "USA"})
CREATE (m6:Manufacturer {name: "Renesas Electronics", short_name: "Renesas", country: "Japan"})
CREATE (m7:Manufacturer {name: "Espressif Systems", short_name: "Espressif", country: "China"})
CREATE (m8:Manufacturer {name: "Nordic Semiconductor", short_name: "Nordic", country: "Norway"})
CREATE (m9:Manufacturer {name: "Qualcomm", short_name: "Qualcomm", country: "USA"})
CREATE (m10:Manufacturer {name: "Samsung Electronics", short_name: "Samsung", country: "South Korea"})

// 创建示例元器件
// ST MCU系列
CREATE (c1:Component {
  mpn: "STM32F407VGT6",
  manufacturer: "STMicroelectronics",
  description: "32-bit ARM Cortex-M4 MCU, 168MHz, 1MB Flash, 192KB SRAM",
  category: "MCU",
  package: "LQFP100",
  lifecycle_status: "Active",
  datalink: "https://www.st.com/stm32f4"
})
CREATE (c1)-[:MANUFACTURED_BY]->(m1)
CREATE (c1)-[:BELONGS_TO]->(cat1:Category {name: "MCU"});

CREATE (c2:Component {
  mpn: "STM32F103C8T6",
  manufacturer: "STMicroelectronics",
  description: "32-bit ARM Cortex-M3 MCU, 72MHz, 64KB Flash, 20KB SRAM",
  category: "MCU",
  package: "LQFP48",
  lifecycle_status: "Active",
  datalink: "https://www.st.com/stm32f1"
})
CREATE (c2)-[:MANUFACTURED_BY]->(m1)
CREATE (c2)-[:BELONGS_TO]->(cat1);

// TI MCU系列
CREATE (c3:Component {
  mpn: "MSP430F149IPM",
  manufacturer: "Texas Instruments",
  description: "16-bit Ultra-Low-Power MCU, 8KB FRAM, 2KB SRAM",
  category: "MCU",
  package: "LQFP64",
  lifecycle_status: "Active",
  datalink: "https://www.ti.com/msp430"
})
CREATE (c3)-[:MANUFACTURED_BY]->(m2)
CREATE (c3)-[:BELONGS_TO]->(cat1);

// Espressif WiFi芯片
CREATE (c4:Component {
  mpn: "ESP32-WROOM-32",
  manufacturer: "Espressif Systems",
  description: "WiFi + Bluetooth MCU, 240MHz, 4MB Flash",
  category: "Wireless",
  package: "Module",
  lifecycle_status: "Active",
  datalink: "https://www.espressif.com/esp32"
})
CREATE (c4)-[:MANUFACTURED_BY]->(m7)
CREATE (c4)-[:BELONGS_TO]->(cat7:Category {name: "Wireless"});

// Nordic BLE芯片
CREATE (c5:Component {
  mpn: "nRF52832-QFAA",
  manufacturer: "Nordic Semiconductor",
  description: "Bluetooth 5.0 SoC, 64MHz, 512KB Flash, 64KB SRAM",
  category: "Wireless",
  package: "QFN48",
  lifecycle_status: "Active",
  datalink: "https://www.nordicsemi.com/nRF52832"
})
CREATE (c5)-[:MANUFACTURED_BY]->(m8)
CREATE (c5)-[:BELONGS_TO]->(cat7);

// Microchip AVR
CREATE (c6:Component {
  mpn: "ATMEGA328P-PU",
  manufacturer: "Microchip Technology",
  description: "8-bit AVR MCU, 20MHz, 32KB Flash, 2KB SRAM",
  category: "MCU",
  package: "DIP28",
  lifecycle_status: "Active",
  datalink: "https://www.microchip.com/atmega328p"
})
CREATE (c6)-[:MANUFACTURED_BY]->(m5)
CREATE (c6)-[:BELONGS_TO]->(cat1);

// 创建替代关系
CREATE (c2)-[:CAN_SUBSTITUTE {confidence: 0.95, description: "Pin-to-pin兼容"}]->(c1)
CREATE (c6)-[:CAN_SUBSTITUTE {confidence: 0.7, description: "功能类似，需要修改代码"}]->(c1)
CREATE (c4)-[:CAN_SUBSTITUTE {confidence: 0.8, description: "可作为无线升级方案"}]->(c1);

// 创建参数
CREATE (p1:Parameter {name: "工作电压", value: "1.8V-3.6V", unit: "V", category: "电气参数"})
CREATE (p2:Parameter {name: "主频", value: "168", unit: "MHz", category: "时序参数"})
CREATE (p3:Parameter {name: "Flash容量", value: "1", unit: "MB", category: "存储参数"})
CREATE (p4:Parameter {name: "SRAM容量", value: "192", unit: "KB", category: "存储参数"})
CREATE (p5:Parameter {name: "工作温度", value: "-40~85", unit: "℃", category: "环境参数"})

CREATE (c1)-[:HAS_PARAMETER]->(p1)
CREATE (c1)-[:HAS_PARAMETER]->(p2)
CREATE (c1)-[:HAS_PARAMETER]->(p3)
CREATE (c1)-[:HAS_PARAMETER]->(p4)
CREATE (c1)-[:HAS_PARAMETER]->(p5);

// 创建质量参数
CREATE (q1:Parameter {name: "ESD防护", value: "2000", unit: "V", category: "质量参数"})
CREATE (q2:Parameter {name: "平均无故障时间", value: "100000", unit: "小时", category: "质量参数"})
CREATE (c1)-[:HAS_PARAMETER]->(q1)
CREATE (c1)-[:HAS_PARAMETER]->(q2);

RETURN "知识图谱初始化完成";
