package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// CORSConfig CORS 配置
type CORSConfig struct {
	AllowOrigins  []string
	AllowMethods  []string
	AllowHeaders  []string
	AllowCredentials bool
}

// CORS CORS 中间件
func CORS(cfg CORSConfig) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization, Accept")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}
