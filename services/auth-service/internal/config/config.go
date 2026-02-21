package config

import (
	"fmt"
	"log"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Environment string `mapstructure:"ENVIRONMENT"`
	Server      ServerConfig
	Database    DatabaseConfig
	Redis       RedisConfig
	JWT         JWTConfig
	CORS        CORSConfig
	Security    SecurityConfig
}

type ServerConfig struct {
	Port         string        `mapstructure:"PORT"`
	ReadTimeout  time.Duration `mapstructure:"READ_TIMEOUT"`
	WriteTimeout time.Duration `mapstructure:"WRITE_TIMEOUT"`
	IdleTimeout  time.Duration `mapstructure:"IDLE_TIMEOUT"`
}

type DatabaseConfig struct {
	URL                string `mapstructure:"DATABASE_URL"`
	MaxOpenConnections int    `mapstructure:"DB_MAX_OPEN_CONNECTIONS"`
	MaxIdleConnections int    `mapstructure:"DB_MAX_IDLE_CONNECTIONS"`
	ConnectionLifetime time.Duration `mapstructure:"DB_CONNECTION_LIFETIME"`
}

type RedisConfig struct {
	URL      string `mapstructure:"REDIS_URL"`
	Password string `mapstructure:"REDIS_PASSWORD"`
	DB       int    `mapstructure:"REDIS_DB"`
}

type JWTConfig struct {
	Secret               string        `mapstructure:"JWT_SECRET"`
	AccessTokenDuration  time.Duration `mapstructure:"JWT_ACCESS_TOKEN_DURATION"`
	RefreshTokenDuration time.Duration `mapstructure:"JWT_REFRESH_TOKEN_DURATION"`
	Issuer               string        `mapstructure:"JWT_ISSUER"`
}

type CORSConfig struct {
	AllowOrigins []string `mapstructure:"CORS_ALLOW_ORIGINS"`
	AllowMethods []string `mapstructure:"CORS_ALLOW_METHODS"`
	AllowHeaders []string `mapstructure:"CORS_ALLOW_HEADERS"`
}

type SecurityConfig struct {
	BCryptCost          int           `mapstructure:"BCRYPT_COST"`
	MaxLoginAttempts    int           `mapstructure:"MAX_LOGIN_ATTEMPTS"`
	LockoutDuration     time.Duration `mapstructure:"LOCKOUT_DURATION"`
	PasswordMinLength   int           `mapstructure:"PASSWORD_MIN_LENGTH"`
	PasswordRequireUpper bool         `mapstructure:"PASSWORD_REQUIRE_UPPER"`
	PasswordRequireLower bool         `mapstructure:"PASSWORD_REQUIRE_LOWER"`
	PasswordRequireDigit bool         `mapstructure:"PASSWORD_REQUIRE_DIGIT"`
	PasswordRequireSpecial bool       `mapstructure:"PASSWORD_REQUIRE_SPECIAL"`
}

// Load 加载配置
func Load() (*Config, error) {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")
	viper.AddConfigPath("/etc/component-agent/")

	// 设置默认值
	setDefaults()

	// 读取环境变量
	viper.AutomaticEnv()

	// 读取配置文件
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, err
		}
	}

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
	// 验证JWT密钥
	if config.JWT.Secret == "" {
		return fmt.Errorf("JWT_SECRET environment variable is required")
	}

	// 验证密码是否足够强
	if len(config.JWT.Secret) < 32 {
		log.Printf("WARNING: JWT_SECRET is too short (%d chars), recommend at least 32 characters", len(config.JWT.Secret))
	}

	return nil
}

func setDefaults() {
	// 服务器配置
	viper.SetDefault("ENVIRONMENT", "development")
	viper.SetDefault("PORT", "8001")
	viper.SetDefault("READ_TIMEOUT", 30*time.Second)
	viper.SetDefault("WRITE_TIMEOUT", 30*time.Second)
	viper.SetDefault("IDLE_TIMEOUT", 120*time.Second)

	// 数据库配置
	viper.SetDefault("DATABASE_URL", "postgresql://postgres:password@localhost:5432/component_agent")
	viper.SetDefault("DB_MAX_OPEN_CONNECTIONS", 25)
	viper.SetDefault("DB_MAX_IDLE_CONNECTIONS", 5)
	viper.SetDefault("DB_CONNECTION_LIFETIME", 5*time.Minute)

	// Redis配置
	viper.SetDefault("REDIS_URL", "redis://localhost:6379/0")
	viper.SetDefault("REDIS_PASSWORD", "")
	viper.SetDefault("REDIS_DB", 0)

	// JWT配置 - 生产环境必须设置JWT_SECRET环境变量
	viper.SetDefault("JWT_SECRET", "")
	viper.SetDefault("JWT_ACCESS_TOKEN_DURATION", 15*time.Minute)
	viper.SetDefault("JWT_REFRESH_TOKEN_DURATION", 7*24*time.Hour)
	viper.SetDefault("JWT_ISSUER", "component-agent-auth")

	// CORS配置
	viper.SetDefault("CORS_ALLOW_ORIGINS", []string{
		"http://localhost:3000",
		"http://localhost:8080",
		"http://127.0.0.1:3000",
		"http://127.0.0.1:8080",
	})
	viper.SetDefault("CORS_ALLOW_METHODS", []string{"GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"})
	viper.SetDefault("CORS_ALLOW_HEADERS", []string{
		"Origin",
		"Content-Type",
		"Accept",
		"Authorization",
		"X-Requested-With",
		"X-CSRF-Token",
	})

	// 安全配置
	viper.SetDefault("BCRYPT_COST", 12)
	viper.SetDefault("MAX_LOGIN_ATTEMPTS", 5)
	viper.SetDefault("LOCKOUT_DURATION", 15*time.Minute)
	viper.SetDefault("PASSWORD_MIN_LENGTH", 8)
	viper.SetDefault("PASSWORD_REQUIRE_UPPER", true)
	viper.SetDefault("PASSWORD_REQUIRE_LOWER", true)
	viper.SetDefault("PASSWORD_REQUIRE_DIGIT", true)
	viper.SetDefault("PASSWORD_REQUIRE_SPECIAL", true)
}