# SSL/HTTPS 配置指南

本指南介绍如何为元器件商城系统配置 HTTPS，确保数据传输安全。

---

## 目录

1. [证书获取](#证书获取)
2. [Nginx 配置](#nginx-配置)
3. [自动续期](#自动续期)
4. [安全加固](#安全加固)

---

## 证书获取

### 方式一：Let's Encrypt 免费证书（推荐）

使用 Certbot 自动申请和配置：

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 申请证书（自动配置 Nginx）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 或仅申请证书（手动配置）
sudo certbot certonly --standalone -d your-domain.com
```

证书文件位置：
- 证书：`/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- 私钥：`/etc/letsencrypt/live/your-domain.com/privkey.pem`

### 方式二：阿里云 SSL 证书

1. 登录阿里云控制台
2. 购买或申请免费 SSL 证书
3. 下载 Nginx 格式的证书文件
4. 上传到服务器指定目录

### 方式三：腾讯云 SSL 证书

1. 登录腾讯云控制台
2. 申请免费 SSL 证书
3. 下载证书文件
4. 上传到服务器

---

## Nginx 配置

### 外部门户 Nginx 配置

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 优化配置
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # 现代安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_prefer_server_ciphers on;

    # HSTS（仅 HTTPS）
    add_header Strict-Transport-Security "max-age=63072000" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 文件根目录
    root /var/www/external-portal;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # 浏览器缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 内部管理 Nginx 配置

```nginx
server {
    listen 443 ssl http2;
    server_name admin.your-domain.com;

    # SSL 证书配置（同上）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 安全配置（同上）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;

    # 访问控制（内部管理仅限内网）
    allow 192.168.0.0/16;
    allow 10.0.0.0/8;
    deny all;

    root /var/www/internal-admin;
    index index.html;

    # ... 其他配置同上
}
```

---

## 自动续期

### Certbot 自动续期

Let's Encrypt 证书有效期 90 天，需配置自动续期：

```bash
# 测试续期
sudo certbot renew --dry-run

# 配置定时任务（通常 Certbot 自动添加）
sudo crontab -e

# 添加以下行（每天凌晨 2 点检查续期）
0 2 * * * certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

### 续期回调

续期成功后自动重载 Nginx：

```bash
# 创建续期钩子脚本
sudo nano /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh

# 内容：
#!/bin/bash
systemctl reload nginx

# 赋予执行权限
sudo chmod +x /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh
```

---

## 安全加固

### 1. 禁用不安全的协议

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

### 2. 配置 HSTS

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

### 3. 配置 CSP

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### 4. 防火墙配置

```bash
# UFW 防火墙
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 或使用 firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 5. 定期检查

```bash
# 检查证书过期时间
sudo certbot certificates

# 检查 SSL 配置（在线工具）
# https://www.ssllabs.com/ssltest/
```

---

## Docker 环境配置

### docker-compose.yml SSL 配置

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/letsencrypt
      - ./html:/var/www
    restart: unless-stopped
```

---

## 故障排查

### 常见问题

1. **证书不信任**
   - 检查证书链是否完整
   - 使用 `openssl s_client -connect your-domain.com:443` 检查

2. **混合内容警告**
   - 确保所有资源使用 HTTPS 或相对路径
   - 检查 API 请求是否使用 HTTPS

3. **重定向循环**
   - 检查 Nginx 配置中的 `return 301` 规则
   - 确认后端应用的 HTTPS 检测配置

---

## 联系支持

- 技术支持：support@example.com
- 文档：https://docs.example.com
