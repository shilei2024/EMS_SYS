package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/lib/pq"
	"go.uber.org/zap"

	"component-agent/auth-service/internal/config"
)

// DB 是数据库连接池
type DB struct {
	*sql.DB
	logger *zap.Logger
}

// NewConnection 创建新的数据库连接
func NewConnection(cfg config.DatabaseConfig) (*DB, error) {
	db, err := sql.Open("postgres", cfg.URL)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// 配置连接池
	db.SetMaxOpenConns(cfg.MaxOpenConnections)
	db.SetMaxIdleConns(cfg.MaxIdleConnections)
	db.SetConnMaxLifetime(cfg.ConnectionLifetime)

	// 测试连接
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	logger, _ := zap.NewProduction()

	return &DB{
		DB:     db,
		logger: logger,
	}, nil
}

// Close 关闭数据库连接
func (db *DB) Close() error {
	db.logger.Info("Closing database connection")
	return db.DB.Close()
}

// RunMigrations 运行数据库迁移
func RunMigrations(db *sql.DB) error {
	// 这里可以集成 goose 或其它迁移工具
	// 现在先运行基础的初始化SQL

	queries := []string{
		// 启用UUID扩展
		`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`,

		// 创建更新触发器函数
		`CREATE OR REPLACE FUNCTION update_updated_at_column()
		RETURNS TRIGGER AS $$
		BEGIN
			NEW.updated_at = CURRENT_TIMESTAMP;
			RETURN NEW;
		END;
		$$ language 'plpgsql'`,

		// 检查并创建用户表
		`CREATE TABLE IF NOT EXISTS users (
			id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
			username VARCHAR(50) NOT NULL UNIQUE,
			email VARCHAR(100) NOT NULL UNIQUE,
			password_hash VARCHAR(255) NOT NULL,
			full_name VARCHAR(100),
			phone VARCHAR(20),
			department VARCHAR(50),
			role_id INTEGER,
			is_active BOOLEAN DEFAULT TRUE,
			last_login_at TIMESTAMP,
			failed_login_attempts INTEGER DEFAULT 0,
			locked_until TIMESTAMP,
			mfa_enabled BOOLEAN DEFAULT FALSE,
			mfa_secret VARCHAR(100),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 为用户表创建触发器
		`DROP TRIGGER IF EXISTS update_users_updated_at ON users;
		CREATE TRIGGER update_users_updated_at
			BEFORE UPDATE ON users
			FOR EACH ROW
			EXECUTE FUNCTION update_updated_at_column()`,

		// 创建角色表
		`CREATE TABLE IF NOT EXISTS roles (
			id SERIAL PRIMARY KEY,
			name VARCHAR(50) NOT NULL UNIQUE,
			description TEXT,
			permissions JSONB DEFAULT '{}'::jsonb,
			is_system_role BOOLEAN DEFAULT FALSE,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// 为角色表创建触发器
		`DROP TRIGGER IF EXISTS update_roles_updated_at ON roles;
		CREATE TRIGGER update_roles_updated_at
			BEFORE UPDATE ON roles
			FOR EACH ROW
			EXECUTE FUNCTION update_updated_at_column()`,

		// 创建用户会话表
		`CREATE TABLE IF NOT EXISTS user_sessions (
			id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
			user_id UUID NOT NULL,
			token_hash VARCHAR(255) NOT NULL,
			device_info JSONB,
			ip_address INET,
			expires_at TIMESTAMP NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
		)`,

		// 创建索引
		`CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)`,
		`CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users(LOWER(email))`,
		`CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role_id, is_active)`,
	}

	for i, query := range queries {
		if _, err := db.Exec(query); err != nil {
			// 如果是重复对象错误，忽略
			if pgErr, ok := err.(*pq.Error); ok && pgErr.Code == "42710" {
				continue
			}
			return fmt.Errorf("failed to execute migration query %d: %w", i, err)
		}
	}

	// 插入默认角色
	defaultRoles := []struct {
		name        string
		description string
		permissions string
		isSystem    bool
	}{
		{
			name:        "超级管理员",
			description: "系统最高权限管理员",
			permissions: `{"*": "*"}`,
			isSystem:    true,
		},
		{
			name:        "订单管理员",
			description: "负责订单审核和管理",
			permissions: `{"orders": ["read", "update", "review"], "users": ["read"]}`,
			isSystem:    false,
		},
		{
			name:        "FAE工程师",
			description: "技术支持工程师",
			permissions: `{"components": ["read", "create", "update"], "datasheets": ["read", "upload"]}`,
			isSystem:    false,
		},
		{
			name:        "财务专员",
			description: "负责财务相关操作",
			permissions: `{"finance": ["read", "create", "update"], "orders": ["read"]}`,
			isSystem:    false,
		},
		{
			name:        "库存管理员",
			description: "负责库存管理",
			permissions: `{"inventory": ["read", "create", "update", "delete"], "orders": ["read"]}`,
			isSystem:    false,
		},
		{
			name:        "普通用户",
			description: "基础权限用户",
			permissions: `{"orders": ["read", "create"], "profile": ["read", "update"]}`,
			isSystem:    false,
		},
	}

	for _, role := range defaultRoles {
		query := `
			INSERT INTO roles (name, description, permissions, is_system_role)
			VALUES ($1, $2, $3::jsonb, $4)
			ON CONFLICT (name) DO NOTHING
		`
		if _, err := db.Exec(query, role.name, role.description, role.permissions, role.isSystem); err != nil {
			return fmt.Errorf("failed to insert default role %s: %w", role.name, err)
		}
	}

	return nil
}

// HealthCheck 数据库健康检查
func HealthCheck(db *sql.DB) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return db.PingContext(ctx)
}