# DMZ 区安全部署指南

本指南介绍如何在 DMZ（隔离区）安全地部署元器件商城系统。

---

## 目录

1. [DMZ 架构概述](#dmz-架构概述)
2. [网络拓扑](#网络拓扑)
3. [安全策略](#安全策略)
4. [部署步骤](#部署步骤)
5. [安全加固](#安全加固)
6. [合规要求](#合规要求)

---

## DMZ 架构概述

### 什么是 DMZ

DMZ（Demilitarized Zone，隔离区）是位于内网和外网之间的缓冲区域，用于部署对外服务，保护内网安全。

### 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                         互联网                               │
│                      (Internet)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │  防火墙 1  │  (外部防火墙)
                    │ (Edge FW) │
                    └─────┬─────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                          DMZ 区                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Nginx    │  │  Web 服务器 │  │  API 网关    │         │
│  │  (反向代理) │  │  (Nuxt.js)  │  │  (FastAPI)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │  防火墙 2  │  (内部防火墙)
                    │ (Internal)│
                    └─────┬─────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                         内网区                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │    Redis    │  │  内部管理   │         │
│  │  (数据库)   │  │   (缓存)    │  │   (Vue.js)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 网络拓扑

### IP 规划

| 区域 | 设备 | IP 地址 | 说明 |
|------|------|--------|------|
| DMZ | Nginx LB | 10.0.1.10 | 负载均衡 |
| DMZ | Web Server 1 | 10.0.1.11 | 外部门户 |
| DMZ | Web Server 2 | 10.0.1.12 | 外部门户 |
| DMZ | API Gateway | 10.0.1.20 | API 服务 |
| 内网 | DB Master | 10.0.2.10 | 主数据库 |
| 内网 | DB Slave | 10.0.2.11 | 从数据库 |
| 内网 | Redis | 10.0.2.20 | 缓存服务 |
| 内网 | Admin | 10.0.2.30 | 内部管理 |

### 防火墙规则

#### 外部防火墙（互联网 -> DMZ）

| 源 | 目标 | 端口 | 协议 | 说明 |
|----|------|------|------|------|
| Any | 10.0.1.10 | 80 | TCP | HTTP |
| Any | 10.0.1.10 | 443 | TCP | HTTPS |
| Any | Any | Any | Any | 拒绝其他所有 |

#### 内部防火墙（DMZ -> 内网）

| 源 | 目标 | 端口 | 协议 | 说明 |
|----|------|------|------|------|
| 10.0.1.20 | 10.0.2.10 | 5432 | TCP | PostgreSQL |
| 10.0.1.20 | 10.0.2.20 | 6379 | TCP | Redis |
| 10.0.1.11 | 10.0.2.10 | 5432 | TCP | Web->DB |
| 10.0.2.30 | 10.0.2.10 | 5432 | TCP | Admin->DB |
| Any | Any | Any | Any | 拒绝其他所有 |

---

## 安全策略

### 1. 网络隔离

```bash
# iptables 配置示例

# 外部防火墙
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

# 内部防火墙（DMZ 服务器）
iptables -A FORWARD -s 10.0.1.20 -d 10.0.2.10 -p tcp --dport 5432 -j ACCEPT
iptables -A FORWARD -s 10.0.1.20 -d 10.0.2.20 -p tcp --dport 6379 -j ACCEPT
iptables -A FORWARD -j DROP
```

### 2. 访问控制

#### 数据库访问限制

```yaml
# PostgreSQL pg_hba.conf
# 只允许特定 IP 访问
host    ecs_db    api_user    10.0.1.20/32    md5
host    ecs_db    api_user    10.0.2.30/32    md5
host    all       all         0.0.0.0/0       reject
```

#### Redis 访问控制

```bash
# Redis 配置
bind 10.0.2.20
requirepass YourStrongPassword123!
protected-mode yes
```

### 3. 应用安全

#### API 速率限制

```yaml
# Nginx 限流配置
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api-gateway:8001;
        }
    }
}
```

#### WAF 配置

```nginx
# 启用 ModSecurity
server {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/modsecurity-rules.conf;
}
```

---

## 部署步骤

### 步骤 1: 准备基础设施

```bash
# 1. 创建虚拟机/容器
# DMZ 区域
vm-create --name nginx-lb --network dmz-net --ip 10.0.1.10
vm-create --name web-1 --network dmz-net --ip 10.0.1.11
vm-create --name web-2 --network dmz-net --ip 10.0.1.12
vm-create --name api-gw --network dmz-net --ip 10.0.1.20

# 内网区域
vm-create --name db-master --network internal-net --ip 10.0.2.10
vm-create --name db-slave --network internal-net --ip 10.0.2.11
vm-create --name redis --network internal-net --ip 10.0.2.20
vm-create --name admin --network internal-net --ip 10.0.2.30
```

### 步骤 2: 配置防火墙

```bash
# 外部防火墙
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent
firewall-cmd --reload

# 内部防火墙
firewall-cmd --zone=internal --add-port=5432/tcp --permanent
firewall-cmd --zone=internal --add-port=6379/tcp --permanent
firewall-cmd --reload
```

### 步骤 3: 部署应用

```bash
# DMZ 区域部署
cd /opt/deploy/dmz
docker-compose -f docker-compose.dmz.yml up -d

# 内网区域部署
cd /opt/deploy/internal
docker-compose -f docker-compose.internal.yml up -d
```

### 步骤 4: 验证部署

```bash
# 从互联网测试
curl -I https://your-domain.com

# 从 DMZ 测试数据库连接
docker-compose exec api-gateway nc -zv 10.0.2.10 5432

# 验证防火墙规则
nmap -p 80,443,5432,6379 your-domain.com
```

---

## 安全加固

### 1. 系统加固

```bash
# 禁用 root 登录
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# 启用 fail2ban
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# 配置自动更新
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

### 2. 容器安全

```yaml
# Docker 安全配置
version: '3.8'
services:
  web:
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    user: 1000:1000
```

### 3. 密钥管理

```bash
# 使用 Vault 管理密钥
vault kv put secret/db/postgres host=10.0.2.10 username=api_user password=xxx

# 应用读取密钥
vault kv get secret/db/postgres
```

### 4. 审计日志

```bash
# 启用系统审计
apt install auditd
systemctl enable auditd
systemctl start auditd

# 配置审计规则
auditctl -w /etc/passwd -p wa -x /usr/bin/docker -k docker
```

---

## 合规要求

### 等级保护 2.0

- [ ] 网络架构安全（三级）
- [ ] 访问控制
- [ ] 安全审计
- [ ] 入侵防范
- [ ] 数据完整性
- [ ] 数据保密性

### GDPR 合规

- [ ] 数据加密存储
- [ ] 数据脱敏展示
- [ ] 用户同意管理
- [ ] 数据导出功能
- [ ] 被遗忘权支持

### PCI DSS（如处理信用卡）

- [ ] 网络安全
- [ ] 数据加密
- [ ] 访问控制
- [ ] 监控和日志
- [ ] 安全策略

---

## 应急预案

### DMZ 被攻破

1. **立即隔离**: 断开 DMZ 与内网的连接
2. **切换流量**: 将流量切换到备用环境
3. **取证分析**: 保留日志和镜像进行分析
4. **重建环境**: 从干净镜像重建 DMZ
5. **恢复服务**: 验证安全后恢复服务

### 数据库泄露

1. **立即停止**: 停止数据库服务
2. **修改密码**: 修改所有数据库密码
3. **审计访问**: 检查访问日志
4. **通知用户**: 如有数据泄露，通知受影响用户
5. **加固措施**: 加强访问控制和加密

---

## 联系方式

- 安全团队：security@example.com
- 紧急联系：+86-xxx-xxxx-xxxx

---

**最后更新**: 2026-02-21
**版本**: 1.0.0
