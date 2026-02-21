package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/auth-service/internal/config"
	"component-agent/auth-service/internal/database"
	"component-agent/auth-service/internal/handlers"
	"component-agent/auth-service/internal/middleware"
)

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	// 加载配置
	cfg, err := config.Load()
	if err != nil {
		logger.Fatal("Failed to load configuration", zap.Error(err))
	}

	// 初始化数据库连接
	db, err := database.NewConnection(cfg.Database)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer db.Close()

	// 运行数据库迁移
	if err := database.RunMigrations(db.DB); err != nil {
		logger.Fatal("Failed to run database migrations", zap.Error(err))
	}

	// 设置 Gin 模式
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	// 创建 Gin 引擎
	router := gin.New()

	// 添加中间件
	router.Use(gin.Recovery())
	router.Use(middleware.Logger(logger))
	router.Use(middleware.CORS(cfg.CORS.AllowOrigins, cfg.CORS.AllowMethods, cfg.CORS.AllowHeaders))

	// 初始化处理器
	authHandler := handlers.NewAuthHandler(db.DB, cfg, logger)

	// 公开路由（无需认证）
	public := router.Group("/api/v1")
	{
		public.POST("/login", authHandler.Login)
		public.POST("/register", authHandler.Register)
		public.POST("/refresh-token", authHandler.RefreshToken)
		public.POST("/forgot-password", authHandler.ForgotPassword)
		public.POST("/reset-password", authHandler.ResetPassword)
		public.GET("/health", healthCheck)
	}

	// 受保护路由（需要认证）
	protected := router.Group("/api/v1")
	protected.Use(middleware.JWTAuth(cfg.JWT.Secret))
	{
		// 会话管理
		protected.GET("/sessions", authHandler.ListSessions)
		protected.DELETE("/sessions/:id", authHandler.RevokeSession)
		protected.POST("/logout", authHandler.Logout)
	}

	// 启动服务器
	srv := &http.Server{
		Addr:         ":" + cfg.Server.Port,
		Handler:      router,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
		IdleTimeout:  cfg.Server.IdleTimeout,
	}

	// 优雅关机
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	logger.Info("Auth service started successfully",
		zap.String("address", srv.Addr),
		zap.String("environment", cfg.Environment),
	)

	// 等待中断信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}
}

// healthCheck 健康检查端点
func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "auth-service",
		"version":   "1.0.0",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}
