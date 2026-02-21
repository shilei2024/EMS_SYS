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

	"component-agent/finance-service/internal/config"
	"component-agent/finance-service/internal/database"
	"component-agent/finance-service/internal/handlers"
	"component-agent/finance-service/internal/middleware"
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
	if err := database.RunMigrations(db.DB); err != nil {
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
	router.Use(middleware.CORS(middleware.CORSConfig{AllowOrigins: cfg.CORS.AllowOrigins, AllowMethods: cfg.CORS.AllowMethods, AllowHeaders: cfg.CORS.AllowHeaders, AllowCredentials: true}))

	// 初始化处理器
	expenseHandler := handlers.NewExpenseHandler(db.DB, cfg, logger)
	salaryHandler := handlers.NewSalaryHandler(db.DB, cfg, logger)
	reconciliationHandler := handlers.NewReconciliationHandler(db.DB, cfg, logger)

	// 公开路由
	public := router.Group("/api/v1")
	{
		public.GET("/health", healthCheck)
	}

	// 受保护路由
	protected := router.Group("/api/v1")
	protected.Use(middleware.JWTAuth(cfg.JWT.Secret))
	{
		// 报销管理
		protected.GET("/expenses", expenseHandler.ListExpenses)
		protected.GET("/expenses/:id", expenseHandler.GetExpense)
		protected.POST("/expenses", expenseHandler.CreateExpense)
		protected.PUT("/expenses/:id", expenseHandler.UpdateExpense)
		protected.DELETE("/expenses/:id", expenseHandler.DeleteExpense)
		protected.POST("/expenses/:id/approve", expenseHandler.ApproveExpense)
		protected.POST("/expenses/:id/reject", expenseHandler.RejectExpense)

		// 工资奖金
		protected.GET("/salaries", salaryHandler.ListSalaries)
		protected.GET("/salaries/:id", salaryHandler.GetSalary)
		protected.POST("/salaries", salaryHandler.CreateSalary)
		protected.PUT("/salaries/:id", salaryHandler.UpdateSalary)
		protected.DELETE("/salaries/:id", salaryHandler.DeleteSalary)

		// 销售对账
		protected.GET("/reconciliations", reconciliationHandler.ListReconciliations)
		protected.GET("/reconciliations/:id", reconciliationHandler.GetReconciliation)
		protected.POST("/reconciliations", reconciliationHandler.CreateReconciliation)
		protected.POST("/reconciliations/:id/confirm", reconciliationHandler.ConfirmReconciliation)
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

	logger.Info("Finance service started successfully",
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
		"service":   "finance-service",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}
