package middleware

import (
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"go.uber.org/zap"
)

// Logger 日志中间件
func Logger(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		c.Next()

		logger.Info("HTTP Request",
			zap.String("path", path),
			zap.String("query", query),
			zap.String("ip", c.ClientIP()),
			zap.Int("status", c.Writer.Status()),
			zap.Duration("latency", time.Since(start)),
		)
	}
}

// CORS CORS 中间件
func CORS(allowOrigins []string, allowMethods, allowHeaders []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		origin := c.Request.Header.Get("Origin")
		allowed := false

		for _, o := range allowOrigins {
			if o == "*" || o == origin {
				allowed = true
				break
			}
		}

		if allowed {
			c.Header("Access-Control-Allow-Origin", origin)
			if origin == "" {
				c.Header("Access-Control-Allow-Origin", "*")
			}
		} else {
			c.Header("Access-Control-Allow-Origin", allowOrigins[0])
		}

		c.Header("Access-Control-Allow-Methods", strings.Join(allowMethods, ", "))
		c.Header("Access-Control-Allow-Headers", strings.Join(allowHeaders, ", "))
		c.Header("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

// JWTAuth JWT 认证中间件
func JWTAuth(secret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Missing authorization header",
			})
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authorization format",
			})
			return
		}

		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return []byte(secret), nil
		})

		if err != nil || !token.Valid {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid or expired token",
			})
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid token claims",
			})
			return
		}

		// 将用户信息存入上下文
		if userID, ok := claims["user_id"]; ok {
			c.Set("user_id", userID)
		}
		if role, ok := claims["role"]; ok {
			c.Set("role", role)
		}

		c.Next()
	}
}

// RateLimit 限流中间件（线程安全版本）
func RateLimit(requestsPerMinute int) gin.HandlerFunc {
	type rateLimitData struct {
		mu         sync.Mutex
		timestamps map[string][]time.Time
	}

	data := &rateLimitData{
		timestamps: make(map[string][]time.Time),
	}

	cleanupInterval := time.Minute

	// 定期清理过期的请求记录
	go func() {
		for {
			time.Sleep(cleanupInterval)
			now := time.Now()
			data.mu.Lock()
			for ip, timestamps := range data.timestamps {
				var valid []time.Time
				for _, ts := range timestamps {
					if now.Sub(ts) < time.Minute {
						valid = append(valid, ts)
					}
				}
				if len(valid) == 0 {
					delete(data.timestamps, ip)
				} else {
					data.timestamps[ip] = valid
				}
			}
			data.mu.Unlock()
		}
	}()

	return func(c *gin.Context) {
		ip := c.ClientIP()
		now := time.Now()

		data.mu.Lock()
		defer data.mu.Unlock()

		// 获取该 IP 的请求记录
		timestamps, exists := data.timestamps[ip]
		if !exists {
			timestamps = []time.Time{}
		}

		// 移除一分钟前的记录
		var recent []time.Time
		for _, ts := range timestamps {
			if now.Sub(ts) < time.Minute {
				recent = append(recent, ts)
			}
		}

		// 检查是否超过限制
		if len(recent) >= requestsPerMinute {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"error": "Too many requests",
			})
			return
		}

		// 添加当前请求
		recent = append(recent, now)
		data.timestamps[ip] = recent

		c.Next()
	}
}

// Recovery 恢复中间件
func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("panic recovered: %v", err)
				c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
					"error": "Internal server error",
				})
			}
		}()
		c.Next()
	}
}
