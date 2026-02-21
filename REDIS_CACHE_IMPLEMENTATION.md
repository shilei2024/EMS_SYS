# Redis 缓存实现文档

## 概述

已在 auth-service 中实现 Redis 缓存功能，用于提升认证和会话管理的性能。

## 已实现功能

### 1. 用户会话缓存

**方法**: `cacheUserSession`, `getUserSession`, `deleteUserSession`

**用途**:
- 缓存用户登录会话
- 快速验证会话有效性
- 登出时快速删除会话

**缓存键**: `session:{session_id}`

**TTL**: 7 天（与刷新令牌有效期一致）

### 2. JWT 令牌黑名单

**方法**: `addTokenToBlacklist`, `isTokenBlacklisted`

**用途**:
- 用户登出时将令牌加入黑名单
- 防止已登出的令牌继续使用
- 实现令牌吊销功能

**缓存键**: `token:blacklist:{token_id}`

**TTL**: 令牌剩余有效期

### 3. 登录失败计数缓存

**方法**: `cacheLoginFailed`, `getFailedLoginCount`, `resetFailedLoginCount`

**用途**:
- 缓存登录失败次数
- 防止暴力破解攻击
- 账户锁定检查

**缓存键**: `login:failed:{username}`

**TTL**: 15 分钟（锁定时长）

### 4. 账户锁定状态缓存

**方法**: `isAccountLocked`, `getLockRemainingTime`

**用途**:
- 快速检查账户是否被锁定
- 获取锁定剩余时间
- 减少数据库查询

**缓存键**: `account:locked:{username}`

**TTL**: 自动过期（与锁定时间一致）

### 5. 用户信息缓存

**方法**: `cacheUserInfo`, `getUserInfo`, `deleteUserCache`

**用途**:
- 缓存用户基本信息
- 减少频繁的用户信息查询
- 提升认证性能

**缓存键**: `user:info:{user_id}`

**TTL**: 30 分钟

---

## 集成点

### Login 函数集成

```go
// 登录成功后，缓存用户会话
h.cacheUserSession(userID, sessionID, 7*24*time.Hour)

// 登录失败时，使用 Redis 计数
h.cacheLoginFailed(username, maxAttempts, lockoutDuration)
```

### Logout 函数集成

```go
// 将令牌加入黑名单
h.addTokenToBlacklist(tokenID, expiresIn)

// 删除用户缓存
h.deleteUserCache(userID)
```

### JWT 中间件集成（待实现）

```go
// 在 JWT 认证中间件中检查黑名单
blacklisted, _ := h.isTokenBlacklisted(tokenID)
if blacklisted {
    c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Token revoked"})
    return
}
```

---

## Redis 配置

### 环境变量

```bash
# .env 文件
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

### Docker Compose 配置

```yaml
auth-service:
  environment:
    REDIS_URL: "redis://:redispassword@redis:6379/0"
  depends_on:
    redis:
      condition: service_healthy
```

---

## 缓存键命名规范

```
session:{session_id}           # 用户会话
token:blacklist:{token_id}     # 令牌黑名单
login:failed:{username}        # 登录失败计数
account:locked:{username}      # 账户锁定状态
user:info:{user_id}            # 用户信息缓存
```

---

## 性能提升预期

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 登录失败检查 | 数据库查询 (~5ms) | Redis 查询 (~0.1ms) | 50x |
| 账户锁定检查 | 数据库查询 (~5ms) | Redis 查询 (~0.1ms) | 50x |
| 会话验证 | 数据库查询 (~5ms) | Redis 查询 (~0.1ms) | 50x |
| 令牌吊销检查 | 不支持 | Redis 检查 (~0.1ms) | 新功能 |

---

## 监控和维护

### Redis 内存使用监控

```bash
# 查看 Redis 内存使用
redis-cli INFO memory

# 查看 key 数量
redis-cli DBSIZE

# 查看过期 key 统计
redis-cli INFO stats | grep expired
```

### 缓存清理策略

所有缓存键都设置了 TTL，会自动过期，无需手动清理。

### 故障降级

如果 Redis 不可用，系统会自动降级到数据库查询：

```go
if h.redis == nil {
    return nil // 跳过缓存，使用数据库
}
```

---

## 下一步扩展建议

1. **刷新令牌缓存**: 将刷新令牌存储在 Redis 中，提升验证速度
2. **热点数据缓存**: 缓存频繁访问的配置数据
3. **分布式锁**: 使用 Redis 实现分布式锁，防止并发问题
4. **限流功能**: 使用 Redis 实现更精确的 API 限流

---

**创建时间**: 2026-02-21
**最后更新**: 2026-02-21
