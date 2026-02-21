package main

import (
	"context"
	"log"
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
	// 初始化配置
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// 初始化日志
	logger, err := initLogger(cfg)
	if err != nil {
		log.Fatalf("Failed to initialize logger: %v", err)
	}
	defer logger.Sync()

	// 初始化数据库连接
	db, err := database.NewConnection(cfg.Database)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer db.Close()

	// 运行数据库迁移
	if err := database.RunMigrations(db); err != nil {
		logger.Fatal("Failed to run database migrations", zap.Error(err))
	}

	// 设置Gin模式
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	// 创建Gin引擎
	router := gin.New()

	// 添加中间件
	router.Use(gin.Recovery())
	router.Use(middleware.Logger(logger))
	router.Use(middleware.CORS(cfg.CORS))

	// 初始化处理器
	authHandler := handlers.NewAuthHandler(db, cfg, logger)
	userHandler := handlers.NewUserHandler(db, cfg, logger)
	roleHandler := handlers.NewRoleHandler(db, cfg, logger)

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
		// 用户管理
		protected.GET("/users", userHandler.ListUsers)
		protected.GET("/users/:id", userHandler.GetUser)
		protected.PUT("/users/:id", userHandler.UpdateUser)
		protected.DELETE("/users/:id", userHandler.DeleteUser)
		protected.PUT("/users/:id/password", userHandler.ChangePassword)
		protected.PUT("/users/:id/status", userHandler.UpdateStatus)

		// 角色管理
		protected.GET("/roles", roleHandler.ListRoles)
		protected.GET("/roles/:id", roleHandler.GetRole)
		protected.POST("/roles", roleHandler.CreateRole)
		protected.PUT("/roles/:id", roleHandler.UpdateRole)
		protected.DELETE("/roles/:id", roleHandler.DeleteRole)

		// 会话管理
		protected.GET("/sessions", authHandler.ListSessions)
		protected.DELETE("/sessions/:id", authHandler.RevokeSession)
		protected.POST("/logout", authHandler.Logout)

		// 个人资料
		protected.GET("/profile", userHandler.GetProfile)
		protected.PUT("/profile", userHandler.UpdateProfile)
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

	logger.Info("Server started successfully",
		zap.String("address", srv.Addr),
		zap.String("environment", cfg.Environment),
	)

	// 等待中断信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// 给服务器5秒时间完成现有请求
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server exited properly")
}

func initLogger(cfg *config.Config) (*zap.Logger, error) {
	if cfg.Environment == "production" {
		return zap.NewProduction()
	}
	return zap.NewDevelopment()
}

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "auth-service",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}