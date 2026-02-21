package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq"

	"component-agent/finance-service/internal/config"
)

type DB struct {
	*sql.DB
}

func NewConnection(cfg config.DatabaseConfig) (*DB, error) {
	db, err := sql.Open("postgres", cfg.URL)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	db.SetMaxOpenConns(cfg.MaxOpenConnections)
	db.SetMaxIdleConns(cfg.MaxIdleConnections)
	db.SetConnMaxLifetime(cfg.ConnectionLifetime)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &DB{db}, nil
}

func (db *DB) Close() error {
	return db.DB.Close()
}

func RunMigrations(db *sql.DB) error {
	queries := []string{
		// 报销表
		`CREATE TABLE IF NOT EXISTS expenses (
			id UUID PRIMARY KEY,
			user_id UUID NOT NULL,
			type VARCHAR(50) NOT NULL,
			amount DECIMAL(15,2) NOT NULL,
			currency VARCHAR(3) DEFAULT 'CNY',
			description TEXT,
			status VARCHAR(20) DEFAULT 'pending',
			receipt_url TEXT,
			approved_by UUID,
			approved_at TIMESTAMP,
			payment_at TIMESTAMP,
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 工资奖金表
		`CREATE TABLE IF NOT EXISTS salaries (
			id UUID PRIMARY KEY,
			user_id UUID NOT NULL,
			year INTEGER NOT NULL,
			month INTEGER NOT NULL,
			base_salary DECIMAL(15,2) NOT NULL,
			bonus DECIMAL(15,2) DEFAULT 0,
			overtime_pay DECIMAL(15,2) DEFAULT 0,
			deductions DECIMAL(15,2) DEFAULT 0,
			tax DECIMAL(15,2) DEFAULT 0,
			net_salary DECIMAL(15,2) NOT NULL,
			currency VARCHAR(3) DEFAULT 'CNY',
			status VARCHAR(20) DEFAULT 'pending',
			paid_at TIMESTAMP,
			notes TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(user_id, year, month)
		)`,

		// 销售对账表
		`CREATE TABLE IF NOT EXISTS reconciliations (
			id UUID PRIMARY KEY,
			sales_order_id VARCHAR(50) NOT NULL,
			customer_name VARCHAR(200),
			order_amount DECIMAL(15,2) NOT NULL,
			received_amount DECIMAL(15,2) DEFAULT 0,
			difference DECIMAL(15,2) DEFAULT 0,
			status VARCHAR(20) DEFAULT 'pending',
			invoice_number VARCHAR(50),
			payment_date TIMESTAMP,
			notes TEXT,
			confirmed_by UUID,
			confirmed_at TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 索引
		`CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status)`,
		`CREATE INDEX IF NOT EXISTS idx_expenses_created_at ON expenses(created_at)`,
		`CREATE INDEX IF NOT EXISTS idx_salaries_user_id ON salaries(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_salaries_year_month ON salaries(year, month)`,
		`CREATE INDEX IF NOT EXISTS idx_reconciliations_status ON reconciliations(status)`,
		`CREATE INDEX IF NOT EXISTS idx_reconciliations_sales_order ON reconciliations(sales_order_id)`,
	}

	for i, query := range queries {
		if _, err := db.Exec(query); err != nil {
			return fmt.Errorf("failed to execute migration %d: %w", i, err)
		}
	}

	return nil
}

// 避免未使用导入错误
var _ = context.Background()
