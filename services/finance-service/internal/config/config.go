package config

import (
	"fmt"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Environment string         `mapstructure:"ENVIRONMENT"`
	Server      ServerConfig   `mapstructure:"SERVER"`
	Database    DatabaseConfig `mapstructure:"DATABASE"`
	Redis       RedisConfig    `mapstructure:"REDIS"`
	JWT         JWTConfig      `mapstructure:"JWT"`
	CORS        CORSConfig     `mapstructure:"CORS"`
	Encryption  EncryptionConfig `mapstructure:"ENCRYPTION"`
}

type ServerConfig struct {
	Port         string        `mapstructure:"PORT"`
	ReadTimeout  time.Duration `mapstructure:"READ_TIMEOUT"`
	WriteTimeout time.Duration `mapstructure:"WRITE_TIMEOUT"`
	IdleTimeout  time.Duration `mapstructure:"IDLE_TIMEOUT"`
}

type DatabaseConfig struct {
	URL                string        `mapstructure:"DATABASE_URL"`
	MaxOpenConnections int           `mapstructure:"DB_MAX_OPEN_CONNECTIONS"`
	MaxIdleConnections int           `mapstructure:"DB_MAX_IDLE_CONNECTIONS"`
	ConnectionLifetime time.Duration `mapstructure:"DB_CONNECTION_LIFETIME"`
}

type RedisConfig struct {
	URL      string `mapstructure:"REDIS_URL"`
	Password string `mapstructure:"REDIS_PASSWORD"`
	DB       int    `mapstructure:"REDIS_DB"`
}

type JWTConfig struct {
	Secret              string        `mapstructure:"JWT_SECRET"`
	AccessTokenDuration time.Duration `mapstructure:"JWT_ACCESS_TOKEN_DURATION"`
}

type CORSConfig struct {
	AllowOrigins []string `mapstructure:"CORS_ALLOW_ORIGINS"`
	AllowMethods []string `mapstructure:"CORS_ALLOW_METHODS"`
	AllowHeaders []string `mapstructure:"CORS_ALLOW_HEADERS"`
}

type EncryptionConfig struct {
	AESKey string `mapstructure:"AES_KEY"`
}

func Load() (*Config, error) {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")
	viper.AutomaticEnv()

	setDefaults()

	var config Config
	if err := viper.Unmarshal(&config); err != nil {
		return nil, err
	}

	// 验证关键配置
	if err := validateConfig(&config); err != nil {
		return nil, err
	}

	return &config, nil
}

// validateConfig 验证关键配置
func validateConfig(config *Config) error {
	if config.Database.URL == "" {
		return fmt.Errorf("DATABASE_URL environment variable is required")
	}
	if config.JWT.Secret == "" {
		return fmt.Errorf("JWT_SECRET environment variable is required")
	}
	if config.Encryption.AESKey == "" || len(config.Encryption.AESKey) != 32 {
		return fmt.Errorf("AES_KEY environment variable is required and must be exactly 32 characters")
	}
	return nil
}

func setDefaults() {
	viper.SetDefault("ENVIRONMENT", "development")
	viper.SetDefault("SERVER.PORT", "8002")
	viper.SetDefault("SERVER.READ_TIMEOUT", 30*time.Second)
	viper.SetDefault("SERVER.WRITE_TIMEOUT", 30*time.Second)
	viper.SetDefault("SERVER.IDLE_TIMEOUT", 120*time.Second)

	viper.SetDefault("DATABASE_URL", "") // 必须设置环境变量
	viper.SetDefault("DB_MAX_OPEN_CONNECTIONS", 25)
	viper.SetDefault("DB_MAX_IDLE_CONNECTIONS", 5)
	viper.SetDefault("DB_CONNECTION_LIFETIME", 5*time.Minute)

	viper.SetDefault("JWT_SECRET", "") // 必须设置环境变量
	viper.SetDefault("JWT_ACCESS_TOKEN_DURATION", 15*time.Minute)

	viper.SetDefault("CORS_ALLOW_ORIGINS", []string{
		"http://localhost:3000",
		"http://localhost:8080",
	})
	viper.SetDefault("CORS_ALLOW_METHODS", []string{"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"})
	viper.SetDefault("CORS_ALLOW_HEADERS", []string{
		"Origin", "Content-Type", "Accept", "Authorization", "X-Requested-With",
	})

	viper.SetDefault("ENCRYPTION.AES_KEY", "") // 必须设置环境变量
}
