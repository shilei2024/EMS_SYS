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

	"component-agent/inventory-service/internal/config"
	"component-agent/inventory-service/internal/database"
	"component-agent/inventory-service/internal/handlers"
	"component-agent/inventory-service/internal/middleware"
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
	inventoryHandler := handlers.NewInventoryHandler(db, cfg, logger)
	forecastHandler := handlers.NewForecastHandler(db, cfg, logger)
	alertHandler := handlers.NewAlertHandler(db, cfg, logger)

	// 公开路由
	public := router.Group("/api/v1")
	{
		public.GET("/health", healthCheck)
	}

	// 受保护路由
	protected := router.Group("/api/v1")
	protected.Use(middleware.JWTAuth(cfg.JWT.Secret))
	{
		// 库存管理
		protected.GET("/inventory", inventoryHandler.ListInventory)
		protected.GET("/inventory/:id", inventoryHandler.GetInventory)
		protected.POST("/inventory", inventoryHandler.CreateInventory)
		protected.PUT("/inventory/:id", inventoryHandler.UpdateInventory)
		protected.DELETE("/inventory/:id", inventoryHandler.DeleteInventory)
		protected.POST("/inventory/adjust", inventoryHandler.AdjustInventory)

		// 库存预警
		protected.GET("/inventory/alerts", alertHandler.ListAlerts)
		protected.POST("/inventory/alerts/:id/acknowledge", alertHandler.AcknowledgeAlert)

		// FCST预测
		protected.GET("/forecast", forecastHandler.GetForecast)
		protected.POST("/forecast/generate", forecastHandler.GenerateForecast)
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

	logger.Info("Inventory service started successfully",
		zap.String("address", srv.Addr),
		zap.String("environment", cfg.Environment),
	)

	// 等待中断信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

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
		"service":   "inventory-service",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}
