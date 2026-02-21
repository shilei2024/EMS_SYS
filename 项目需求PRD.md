---

# 电子元器件代理商增值系统 - 产品需求文档 (PRD)

| 文档版本 | V1.0 |
| :--- | :--- |
| **文档状态** | 可执行生产版 |
| **密级** | 内部保密 |
| **最后更新** | 2023-10-27 |

## 1. 项目概述 (Project Overview)

### 1.1 项目背景
电子元器件代理商面临订单来源分散、型号匹配复杂、库存管理困难及财务流程繁琐等痛点。本项目旨在构建一套集 **AI 自动化录单、FAE 智能匹配、知识图谱、ERP 财务库存、外网公共服务** 于一体的增值系统，通过大模型与知识图谱技术提升运营效率，保障数据准确性，并拓展外部服务能力。

### 1.2 项目目标
1.  **自动化降本**：实现 90% 以上的订单文档自动结构化录入，减少人工敲单。
2.  **智能化增效**：利用知识图谱和大模型实现毫秒级型号替代推荐。
3.  **合规与安全**：财务流程可审计，敏感数据加密，支持生产环境高可用部署。
4.  **生态扩展**：提供外网公共服务接口，吸引流量并反哺内部知识库。

### 1.3 适用范围
*   **内部系统**：销售、FAE 技术、财务、采购、HR、管理员。
*   **外部系统**：公共用户（查询替代型号、下载规格书）。

---

## 2. 用户角色与权限 (User Roles & RBAC)

| 角色 | 权限描述 | 关键功能 |
| :--- | :--- | :--- |
| **超级管理员** | 系统配置、用户管理、日志审计 | 模型配置、权限分配、数据备份 |
| **销售人员** | 订单录入、客户管理、报销申请 | 上传订单、查看库存、发起报销 |
| **FAE 工程师** | 型号匹配、图谱维护、规格书管理 | 替代推荐、参数校对、图谱修正 |
| **财务人员** | 审核报销、工资发放、对账 | 发票审核、付款执行、财务报表 |
| **采购/库存** | 库存管理、FCST 预测、原厂下单 | 库存预警、采购单生成、超期提醒 |
| **外部用户** | 公开查询、资料提交 | 型号替代查询、规格书下载、缺书反馈 |

---

## 3. 功能需求详情 (Functional Requirements)

### 3.1 智能订单中心 (Order Automation Center)
*   **多源接入**：
    *   支持 API 接收飞书/钉钉 webhook 消息。
    *   支持 IMAP 协议监听指定邮箱附件。
    *   支持前端上传 PDF/Image/Excel/Word。
    *   支持 RPA 机器人登录客户供应链系统下载（需配置账号密码 vault）。
*   **OCR 与结构化**：
    *   集成 PaddleOCR 提取文本。
    *   **LLM 解析**：调用大模型将非结构化文本转为标准 JSON（字段：`MPN`, `Manufacturer`, `Quantity`, `DC`, `TargetPrice`）。
    *   **置信度校验**：置信度低于 80% 的数据标红，强制人工介入。
*   **订单审核流**：
    *   录入后状态为 `Pending`。
    *   主管审核通过后状态变为 `Confirmed`，同步至库存系统。
    *   **审计日志**：记录所有修改痕迹（谁、何时、改了什么字段、原值/新值）。

### 3.2 FAE 与知识图谱中心 (FAE & Knowledge Graph)
*   **型号匹配引擎**：
    *   输入电气参数（电压、电流、封装等），向量检索 + 图谱查询推荐替代型号。
    *   支持 `Pin-to-Pin` 替代和 `Functionality` 替代标记。
*   **规格书管理**：
    *   存储原厂链接及本地缓存文件（MinIO/S3）。
    *   **定时同步**：每日爬虫检查原厂链接有效性，若失效或更新，触发通知给 FAE。
*   **外网公共服务 (Public Portal)**：
    *   独立部署于 DMZ 区，仅开放查询接口。
    *   用户搜索型号 -> 返回替代方案 & 规格书下载。
    *   **众包反馈**：若未找到规格书，用户可提交线索 -> 后台生成 `MissingDatasheet` 任务 -> FAE 补充录入 -> 审核后入库。
*   **修正记录**：FAE 对匹配结果的人工修正需记录版本，用于优化模型提示词（Prompt）。

### 3.3 财务与人力资源模块 (Finance & HR)
*   **报销管理**：
    *   员工上传发票图片（OCR 识别金额/税号）。
    *   **工作流**：员工提交 -> 部门领导审批 -> 财务复核 -> 出纳付款。
    *   支持绑定银行卡信息（加密存储）。
*   **工资奖金**：
    *   保密模块，仅 HR 和财务总监可见。
    *   支持导入 Excel 算薪，生成银行发放批次文件。
*   **销售对账**：
    *   每月自动生成客户对账单（PDF），支持邮件发送。
    *   记录回款状态，逾期自动提醒销售。

### 3.4 库存与供应链模块 (Inventory & Supply Chain)
*   **库存预警**：
    *   **超期管理**：库龄超过设定阈值（如 1 年）自动标记 `Slow Moving`，提醒促销。
    *   **缺货预警**：库存低于安全水位，触发采购建议。
*   **FCST 与采购**：
    *   基于历史销售数据，利用时序模型预测未来需求。
    *   生成采购订单（PO）草稿，记录下单给原厂的时间点。

### 3.5 系统管理与配置 (System Administration)
*   **大模型网关配置**：
    *   **可视化配置页**：管理员可在此添加/修改模型 API Key、Endpoint。
    *   **主备策略**：设置 `Primary Model` 和 `Fallback Models` 列表。
    *   **健康检查**：系统每分钟 ping 模型接口，故障自动切换。
*   **API 开放平台**：
    *   提供 Swagger/OpenAPI 文档。
    *   生成 API Token 供第三方系统调用（如调用查询库存接口）。
*   **人员培训**：
    *   上传培训视频/文档。
    *   记录员工学习进度和考试成绩。

---

## 4. 技术架构与非功能需求 (Technical & Non-Functional)

### 4.1 技术栈选型 (Production Standard)
*   **前端**：Vue 3 + TypeScript + Element Plus (内部), Nuxt.js (外部 SEO 友好)。
*   **后端**：Python FastAPI (AI/业务逻辑) + Go (高并发查询/财务核心)。
*   **数据库**：
    *   **PostgreSQL 15**：核心业务数据、财务数据、用户信息。
    *   **Neo4j**：知识图谱（型号 - 参数 - 替代关系）。
    *   **Redis**：缓存、会话管理、队列缓冲。
    *   **Milvus/Pgvector**：规格书语义向量存储。
*   **AI/OCR**：PaddleOCR (本地), LiteLLM (模型代理), LangChain (逻辑编排)。
*   **基础设施**：Docker, Kubernetes (K8s), Nginx, MinIO。

### 4.2 大模型兼容性方案 (LLM Compatibility)
*   **统一接口层**：后端不直接调用 OpenAI/阿里/百度 API，而是调用内部 `Model Gateway` 服务。
*   **配置简化**：
    *   数据库表 `llm_providers` 存储配置。
    *   支持热加载，修改配置无需重启服务。
*   **无缝切换逻辑**：
    ```python
    # 伪代码示例
    def chat_with_fallback(prompt):
        for provider in get_configured_providers(): # 按优先级排序
            try:
                return provider.complete(prompt)
            except Exception as e:
                log_error(provider.name, e)
                continue
        raise ServiceUnavailable("All models failed")
    ```

### 4.3 安全性要求 (Security)
*   **数据传输**：全站 HTTPS (TLS 1.3)。
*   **数据加密**：
    *   数据库敏感字段（银行卡、密码、薪资）使用 AES-256 加密存储。
    *   备份文件加密。
*   **访问控制**：
    *   内部系统：JWT 认证 + IP 白名单（可选）。
    *   外部系统：Rate Limiting (限流)，防止爬虫滥用。
*   **审计**：所有写操作（增删改）必须写入 `audit_logs` 表，不可删除。

### 4.4 性能与可靠性 (Performance & Reliability)
*   **响应时间**：普通页面 < 500ms，AI 推理任务异步处理（前端轮询或 WebSocket 通知）。
*   **可用性**：目标 99.9%，核心服务多副本部署。
*   **备份策略**：
    *   数据库：每日全量备份，WAL 日志实时归档。
    *   文件存储：多副本冗余。

---

## 5. 数据库设计概要 (Database Schema Overview)

为满足生产环境要求，核心表结构设计如下：

### 5.1 核心业务表 (PostgreSQL)
*   `users`: 用户信息，密码哈希，角色 ID。
*   `orders`: 订单主表，状态机（待审/已通过/已发货）。
*   `order_items`: 订单明细，关联型号 ID，OCR 置信度。
*   `finance_reimbursements`: 报销单，关联审批流实例 ID。
*   `inventory_batches`: 库存批次，入库时间，过期时间。
*   `audit_logs`: 操作日志，`user_id`, `action`, `table_name`, `old_value`, `new_value`, `timestamp`.

### 5.2 知识图谱 (Neo4j)
*   `(:Component {mpn, manufacturer})`
*   `(:Parameter {name, value, unit})`
*   `(:Datasheet {url, hash, last_checked})`
*   `(:Component)-[:SUBSTITUTE {confidence}]->(:Component)`
*   `(:Component)-[:HAS_PARAM]->(:Parameter)`

### 5.3 模型配置表 (PostgreSQL)
*   `llm_configs`: `id`, `provider_name`, `api_key_enc`, `endpoint`, `priority`, `is_active`.

---

## 6. 部署与运维计划 (Deployment & DevOps)

### 6.1 环境规划
*   **Dev**: 开发人员本地 Docker 环境。
*   **Staging**: 预生产环境，数据脱敏，用于 UAT 测试。
*   **Prod**: 生产环境，多可用区部署，数据库主从复制。
*   **DMZ**: 外网公共服务区，通过 API 网关与内网隔离。

### 6.2 CI/CD 流水线
*   **代码提交**：GitLab/GitHub Webhook 触发。
*   **自动化测试**：单元测试 (Pytest) + 接口测试。
*   **镜像构建**：构建 Docker 镜像并推送至私有 Registry。
*   **部署**：Kubernetes Helm Chart 更新，支持滚动更新 (Rolling Update) 和回滚。

### 6.3 监控与告警
*   **基础设施**：Prometheus + Grafana (CPU, Memory, Disk)。
*   **应用监控**：SkyWalking 或 Jaeger (链路追踪)。
*   **日志系统**：ELK Stack (Elasticsearch, Logstash, Kibana)。
*   **告警**：钉钉/飞书机器人通知（服务宕机、模型切换、库存预警）。

---

## 7. 项目实施路线图 (Roadmap)

| 阶段 | 周期 | 交付物 | 关键里程碑 |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Week 1-4 | 基础架构、用户中心、模型网关 | 完成数据库部署，模型主备切换测试通过 |
| **Phase 2** | Week 5-8 | 订单自动化、OCR 集成、内部 ERP 核心 | 实现 PDF 订单自动解析入库，准确率达 85% |
| **Phase 3** | Week 9-12 | 知识图谱、FAE 匹配、财务模块 | 图谱上线，替代推荐功能可用，财务流程跑通 |
| **Phase 4** | Week 13-14 | 外网公共服务、安全加固、压力测试 | 外网门户上线，通过安全渗透测试 |
| **Phase 5** | Week 15+ | 运维移交、培训、正式投产 | 完成文档移交，系统正式切换 |

---

## 8. 附录：风险与应对 (Risks & Mitigation)

1.  **风险**：大模型 API 不稳定或费用过高。
    *   **应对**：本地部署轻量模型（如 Llama-3-8B）作为兜底；建立 Token 消耗监控预算。
2.  **风险**：外网门户被恶意爬取数据。
    *   **应对**：实施严格的 IP 限流，关键数据（如库存实时数量）不对外展示，仅展示“有货/无货”。
3.  **风险**：财务数据泄露。
    *   **应对**：数据库字段级加密，运维人员无权直接查看明文，操作需双人复核。

---

**确认指令**：
如果您确认这份 PRD 符合您的预期，我将基于此文档为您生成**数据库 SQL 初始化脚本**、**核心模型网关代码**以及**Docker 部署配置文件**。请指示下一步工作重点。