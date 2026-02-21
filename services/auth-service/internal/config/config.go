package config

import (
	"fmt"
	"log"
	"os"
	"strings"
	"time"
)

type Config struct {
	Environment string
	Server      ServerConfig
	Database    DatabaseConfig
	Redis       RedisConfig
	JWT         JWTConfig
	CORS        CORSConfig
	Security    SecurityConfig
}

type ServerConfig struct {
	Port         string
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
}

type DatabaseConfig struct {
	URL                string
	MaxOpenConnections int
	MaxIdleConnections int
	ConnectionLifetime time.Duration
}

type RedisConfig struct {
	URL      string
	Password string
	DB       int
}

type JWTConfig struct {
	Secret               string
	AccessTokenDuration  time.Duration
	RefreshTokenDuration time.Duration
	Issuer               string
}

type CORSConfig struct {
	AllowOrigins []string
	AllowMethods []string
	AllowHeaders []string
}

type SecurityConfig struct {
	BCryptCost           int
	MaxLoginAttempts     int
	LockoutDuration      time.Duration
	PasswordMinLength    int
	PasswordRequireUpper bool
	PasswordRequireLower bool
	PasswordRequireDigit bool
	PasswordRequireSpecial bool
}

// Load 直接从环境变量加载配置
func Load() (*Config, error) {
	config := &Config{
		Environment: getEnv("ENVIRONMENT", "development"),
		Server: ServerConfig{
			Port:         getEnv("SERVER_PORT", "8001"),
			ReadTimeout:  30 * time.Second,
			WriteTimeout: 30 * time.Second,
			IdleTimeout:  120 * time.Second,
		},
		Database: DatabaseConfig{
			URL:                getEnv("DATABASE_URL", ""),
			MaxOpenConnections: 10,
			MaxIdleConnections: 5,
			ConnectionLifetime: 5 * time.Minute,
		},
		Redis: RedisConfig{
			URL: getEnv("REDIS_URL", ""),
		},
		JWT: JWTConfig{
			Secret:               os.Getenv("JWT_SECRET"),
			AccessTokenDuration:  60 * time.Minute,
			RefreshTokenDuration: 24 * time.Hour,
			Issuer:               "component-agent-auth",
		},
		CORS: CORSConfig{
			AllowOrigins: []string{"http://localhost:3000", "http://localhost:8080"},
			AllowMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
			AllowHeaders: []string{"Origin", "Content-Type", "Accept", "Authorization"},
		},
		Security: SecurityConfig{
			BCryptCost:           12,
			MaxLoginAttempts:     5,
			LockoutDuration:      15 * time.Minute,
			PasswordMinLength:    8,
			PasswordRequireUpper: true,
			PasswordRequireLower: true,
			PasswordRequireDigit: true,
			PasswordRequireSpecial: true,
		},
	}

	// 从环境变量覆盖 CORS 配置
	if corsOrigins := os.Getenv("CORS_ALLOW_ORIGINS"); corsOrigins != "" {
		config.CORS.AllowOrigins = strings.Split(corsOrigins, ",")
	}

	// 验证关键配置
	if err := validateConfig(config); err != nil {
		return nil, err
	}

	return config, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// validateConfig 验证关键配置
func validateConfig(config *Config) error {
	// 验证 JWT 密钥
	if config.JWT.Secret == "" {
		return fmt.Errorf("JWT_SECRET environment variable is required")
	}

	// 验证密码是否足够强
	if len(config.JWT.Secret) < 32 {
		log.Printf("WARNING: JWT_SECRET is too short (%d chars), recommend at least 32 characters", len(config.JWT.Secret))
	}

	// 验证数据库 URL
	if config.Database.URL == "" {
		return fmt.Errorf("DATABASE_URL environment variable is required")
	}

	// 验证 Redis URL
	if config.Redis.URL == "" {
		return fmt.Errorf("REDIS_URL environment variable is required")
	}

	return nil
}
