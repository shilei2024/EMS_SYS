package database

import (
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq"
	"go.uber.org/zap"
)

// NewConnection 创建数据库连接
func NewConnection(url string) (*sql.DB, error) {
	db, err := sql.Open("postgres", url)
	if err != nil {
		return nil, fmt.Errorf("failed to open database connection: %w", err)
	}

	// 设置连接池参数
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	// 测试连接
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return db, nil
}

// RunMigrations 运行数据库迁移
func RunMigrations(db *sql.DB) error {
	logger, _ := zap.NewDevelopment()

	migrations := []string{
		// 库存表
		`CREATE TABLE IF NOT EXISTS inventory (
			id VARCHAR(50) PRIMARY KEY,
			mpn VARCHAR(200) NOT NULL,
			manufacturer VARCHAR(200) NOT NULL,
			description TEXT,
			category VARCHAR(100),
			warehouse_location VARCHAR(100),
			quantity INTEGER DEFAULT 0,
			safety_stock INTEGER DEFAULT 0,
			reorder_point INTEGER DEFAULT 0,
			unit_cost DECIMAL(12,4) DEFAULT 0,
			currency VARCHAR(10) DEFAULT 'CNY',
			last_count_date TIMESTAMP,
			last_purchase_date TIMESTAMP,
			supplier_id VARCHAR(50),
			supplier_mpn VARCHAR(200),
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(mpn, manufacturer)
		)`,

		// 库存调整记录表
		`CREATE TABLE IF NOT EXISTS inventory_adjustments (
			id VARCHAR(50) PRIMARY KEY,
			inventory_id VARCHAR(50) REFERENCES inventory(id),
			adjustment_type VARCHAR(50) NOT NULL,
			quantity_change INTEGER NOT NULL,
			quantity_before INTEGER NOT NULL,
			quantity_after INTEGER NOT NULL,
			reason TEXT,
			reference_type VARCHAR(50),
			reference_id VARCHAR(50),
			created_by VARCHAR(50),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 库存预警表
		`CREATE TABLE IF NOT EXISTS inventory_alerts (
			id VARCHAR(50) PRIMARY KEY,
			inventory_id VARCHAR(50) REFERENCES inventory(id),
			alert_type VARCHAR(50) NOT NULL,
			severity VARCHAR(20) NOT NULL,
			message TEXT NOT NULL,
			current_quantity INTEGER,
			threshold_quantity INTEGER,
			status VARCHAR(20) DEFAULT 'active',
			acknowledged_by VARCHAR(50),
			acknowledged_at TIMESTAMP,
			resolved_at TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 需求预测表
		`CREATE TABLE IF NOT EXISTS demand_forecasts (
			id VARCHAR(50) PRIMARY KEY,
			inventory_id VARCHAR(50) REFERENCES inventory(id),
			forecast_date DATE NOT NULL,
			predicted_demand INTEGER NOT NULL,
			confidence_level DECIMAL(5,4),
			actual_demand INTEGER,
			accuracy DECIMAL(5,4),
			model_version VARCHAR(50),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(inventory_id, forecast_date)
		)`,

		// 创建索引
		`CREATE INDEX IF NOT EXISTS idx_inventory_mpn ON inventory(mpn)`,
		`CREATE INDEX IF NOT EXISTS idx_inventory_manufacturer ON inventory(manufacturer)`,
		`CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category)`,
		`CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity)`,
		`CREATE INDEX IF NOT EXISTS idx_alerts_status ON inventory_alerts(status)`,
		`CREATE INDEX IF NOT EXISTS idx_alerts_inventory ON inventory_alerts(inventory_id)`,
		`CREATE INDEX IF NOT EXISTS idx_forecasts_inventory ON demand_forecasts(inventory_id)`,
		`CREATE INDEX IF NOT EXISTS idx_forecasts_date ON demand_forecasts(forecast_date)`,
		`CREATE INDEX IF NOT EXISTS idx_adjustments_inventory ON inventory_adjustments(inventory_id)`,
	}

	for i, migration := range migrations {
		if _, err := db.Exec(migration); err != nil {
			logger.Error("Migration failed", zap.Int("index", i), zap.Error(err))
			return fmt.Errorf("migration %d failed: %w", i, err)
		}
	}

	logger.Info("Database migrations completed successfully")
	return nil
}

// Close 关闭数据库连接
func Close(db *sql.DB) error {
	return db.Close()
}
