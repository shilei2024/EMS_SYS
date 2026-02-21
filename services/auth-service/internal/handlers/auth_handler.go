package handlers

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"
	"golang.org/x/crypto/bcrypt"

	"component-agent/auth-service/internal/config"
)

type AuthHandler struct {
	db     *sql.DB
	redis  *redis.Client
	config *config.Config
	logger *zap.Logger
}

func NewAuthHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *AuthHandler {
	// 初始化 Redis 客户端
	var redisClient *redis.Client
	if cfg.Redis.URL != "" {
		redisClient = redis.NewClient(&redis.Options{
			Addr:     cfg.Redis.URL,
			Password: cfg.Redis.Password,
			DB:       cfg.Redis.DB,
		})
	}

	return &AuthHandler{
		db:     db,
		redis:  redisClient,
		config: cfg,
		logger: logger,
	}
}

// LoginRequest 登录请求
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// LoginResponse 登录响应
type LoginResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token,omitempty"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int64  `json:"expires_in"`
	UserID       string `json:"user_id"`
	Username     string `json:"username"`
	Role         string `json:"role"`
}

// Login 用户登录
func (h *AuthHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// 查询用户
	var userID, username, passwordHash, role string
	var isActive bool
	var failedAttempts int
	var lockedUntil *time.Time

	query := `
		SELECT u.id, u.username, u.password_hash, u.is_active,
			   u.failed_login_attempts, u.locked_until, r.name as role_name
		FROM users u
		LEFT JOIN roles r ON u.role_id = r.id
		WHERE u.username = $1 OR u.email = $1
	`

	err := h.db.QueryRow(query, req.Username).Scan(
		&userID, &username, &passwordHash, &isActive,
		&failedAttempts, &lockedUntil, &role,
	)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	} else if err != nil {
		h.logger.Error("Database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 检查账户是否锁定
	if lockedUntil != nil && lockedUntil.After(time.Now()) {
		c.JSON(http.StatusForbidden, gin.H{
			"error":      "Account is locked",
			"locked_until": lockedUntil.Format(time.RFC3339),
		})
		return
	}

	// 检查账户是否激活
	if !isActive {
		c.JSON(http.StatusForbidden, gin.H{"error": "Account is inactive"})
		return
	}

	// 验证密码
	if err := bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte(req.Password)); err != nil {
		// 密码错误，增加失败尝试次数
		h.handleFailedLogin(username, failedAttempts)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// 登录成功，重置失败尝试次数
	h.resetFailedLoginAttempts(username)

	// 更新最后登录时间
	h.updateLastLogin(userID)

	// 生成JWT令牌
	accessToken, err := h.generateAccessToken(userID, username, role)
	if err != nil {
		h.logger.Error("Failed to generate access token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	refreshToken, err := h.generateRefreshToken(userID)
	if err != nil {
		h.logger.Error("Failed to generate refresh token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 保存刷新令牌到数据库
	if err := h.saveRefreshToken(userID, refreshToken); err != nil {
		h.logger.Error("Failed to save refresh token", zap.Error(err))
		// 继续返回访问令牌，只是刷新令牌可能无法使用
	}

	response := LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    int64(h.config.JWT.AccessTokenDuration.Seconds()),
		UserID:       userID,
		Username:     username,
		Role:         role,
	}

	c.JSON(http.StatusOK, response)
}

// Register 用户注册
func (h *AuthHandler) Register(c *gin.Context) {
	type RegisterRequest struct {
		Username string `json:"username" binding:"required"`
		Email    string `json:"email" binding:"required,email"`
		Password string `json:"password" binding:"required"`
		FullName string `json:"full_name"`
		Phone    string `json:"phone"`
	}

	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// 验证密码强度
	if !h.validatePassword(req.Password) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Password does not meet requirements",
		})
		return
	}

	// 检查用户名和邮箱是否已存在
	var count int
	h.db.QueryRow("SELECT COUNT(*) FROM users WHERE username = $1 OR email = $2",
		req.Username, req.Email).Scan(&count)

	if count > 0 {
		c.JSON(http.StatusConflict, gin.H{"error": "Username or email already exists"})
		return
	}

	// 哈希密码
	passwordHash, err := bcrypt.GenerateFromPassword([]byte(req.Password), h.config.Security.BCryptCost)
	if err != nil {
		h.logger.Error("Failed to hash password", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 获取默认角色ID（普通用户）
	var roleID int
	h.db.QueryRow("SELECT id FROM roles WHERE name = '普通用户'").Scan(&roleID)

	// 插入用户
	query := `
		INSERT INTO users (username, email, password_hash, full_name, phone, role_id)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id
	`

	var userID string
	err = h.db.QueryRow(query, req.Username, req.Email, string(passwordHash),
		req.FullName, req.Phone, roleID).Scan(&userID)

	if err != nil {
		h.logger.Error("Failed to create user", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message": "User registered successfully",
		"user_id": userID,
	})
}

// RefreshToken 刷新访问令牌
func (h *AuthHandler) RefreshToken(c *gin.Context) {
	type RefreshRequest struct {
		RefreshToken string `json:"refresh_token" binding:"required"`
	}

	var req RefreshRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// 验证刷新令牌并获取用户信息
	userID, err := h.validateRefreshToken(req.RefreshToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid refresh token"})
		return
	}

	// 查询用户信息
	var username, role string
	query := `
		SELECT u.username, r.name
		FROM users u
		LEFT JOIN roles r ON u.role_id = r.id
		WHERE u.id = $1 AND u.is_active = true
	`

	err = h.db.QueryRow(query, userID).Scan(&username, &role)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not found or inactive"})
		return
	}

	// 生成新的访问令牌
	accessToken, err := h.generateAccessToken(userID, username, role)
	if err != nil {
		h.logger.Error("Failed to generate access token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"access_token": accessToken,
		"token_type":   "Bearer",
		"expires_in":   int64(h.config.JWT.AccessTokenDuration.Seconds()),
	})
}

// Logout 用户登出
func (h *AuthHandler) Logout(c *gin.Context) {
	// 获取用户ID（从JWT中间件设置的上下文）
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	// 删除用户的刷新令牌
	_, err := h.db.Exec("DELETE FROM user_sessions WHERE user_id = $1", userID)
	if err != nil {
		h.logger.Error("Failed to delete user sessions", zap.Error(err))
	}

	// 将当前令牌加入黑名单（从请求头获取）
	tokenID := c.GetHeader("X-Token-ID")
	if tokenID != "" && h.redis != nil {
		// 获取令牌剩余有效期
		expiresIn := 15 * time.Minute // 默认 15 分钟
		h.addTokenToBlacklist(tokenID, expiresIn)
	}

	// 删除 Redis 中的用户会话和缓存
	if h.redis != nil {
		h.deleteUserCache(userID.(string))
	}

	c.JSON(http.StatusOK, gin.H{"message": "Logged out successfully"})
}

// 辅助方法
func (h *AuthHandler) handleFailedLogin(username string, currentAttempts int) {
	newAttempts := currentAttempts + 1

	// 使用 Redis 缓存失败计数和账户锁定状态
	if h.redis != nil {
		h.cacheLoginFailed(username, h.config.Security.MaxLoginAttempts, h.config.Security.LockoutDuration)
	}

	var query string
	if newAttempts >= h.config.Security.MaxLoginAttempts {
		// 锁定账户
		lockDuration := h.config.Security.LockoutDuration
		lockedUntil := time.Now().Add(lockDuration)
		query = `
			UPDATE users
			SET failed_login_attempts = $1, locked_until = $2
			WHERE username = $3
		`
		h.db.Exec(query, newAttempts, lockedUntil, username)
	} else {
		query = `
			UPDATE users
			SET failed_login_attempts = $1
			WHERE username = $2
		`
		h.db.Exec(query, newAttempts, username)
	}
}

func (h *AuthHandler) resetFailedLoginAttempts(username string) {
	query := `
		UPDATE users
		SET failed_login_attempts = 0, locked_until = NULL
		WHERE username = $1
	`
	h.db.Exec(query, username)

	// 同时清除 Redis 中的失败计数
	if h.redis != nil {
		h.resetFailedLoginCount(username)
	}
}

func (h *AuthHandler) updateLastLogin(userID string) {
	query := `UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = $1`
	h.db.Exec(query, userID)
}

func (h *AuthHandler) generateAccessToken(userID, username, role string) (string, error) {
	claims := jwt.MapClaims{
		"sub":  userID,
		"name": username,
		"role": role,
		"iss":  h.config.JWT.Issuer,
		"exp":  time.Now().Add(h.config.JWT.AccessTokenDuration).Unix(),
		"iat":  time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(h.config.JWT.Secret))
}

func (h *AuthHandler) generateRefreshToken(userID string) (string, error) {
	claims := jwt.MapClaims{
		"sub": userID,
		"iss": h.config.JWT.Issuer,
		"exp": time.Now().Add(h.config.JWT.RefreshTokenDuration).Unix(),
		"iat": time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(h.config.JWT.Secret))
}

func (h *AuthHandler) saveRefreshToken(userID, token string) error {
	// 存储token的bcrypt哈希值，而不是原始token
	tokenHash, err := bcrypt.GenerateFromPassword([]byte(token), h.config.Security.BCryptCost)
	if err != nil {
		return err
	}

	query := `
		INSERT INTO user_sessions (user_id, token_hash, expires_at)
		VALUES ($1, $2, $3)
	`
	expiresAt := time.Now().Add(h.config.JWT.RefreshTokenDuration)
	_, err = h.db.Exec(query, userID, string(tokenHash), expiresAt)
	return err
}

func (h *AuthHandler) validateRefreshToken(token string) (string, error) {
	// 解析token
	parsedToken, err := jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(h.config.JWT.Secret), nil
	})

	if err != nil || !parsedToken.Valid {
		return "", err
	}

	// 验证claims
	claims, ok := parsedToken.Claims.(jwt.MapClaims)
	if !ok {
		return "", jwt.ErrTokenInvalidClaims
	}

	userID, ok := claims["sub"].(string)
	if !ok {
		return "", jwt.ErrTokenInvalidClaims
	}

	// 从数据库获取所有有效的刷新令牌哈希
	query := `SELECT token_hash FROM user_sessions WHERE user_id = $1 AND expires_at > CURRENT_TIMESTAMP`
	rows, err := h.db.Query(query, userID)
	if err != nil {
		return "", err
	}
	defer rows.Close()

	var tokenHash string
	tokenValid := false

	for rows.Next() {
		if err := rows.Scan(&tokenHash); err != nil {
			continue
		}

		// 使用bcrypt验证token是否匹配哈希
		if err := bcrypt.CompareHashAndPassword([]byte(tokenHash), []byte(token)); err == nil {
			tokenValid = true
			break
		}
	}

	if !tokenValid {
		return "", jwt.ErrTokenInvalidId
	}

	return userID, nil
}

func (h *AuthHandler) validatePassword(password string) bool {
	// 检查最小长度
	if len(password) < h.config.Security.PasswordMinLength {
		return false
	}

	// 根据配置检查密码复杂度
	hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
	hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
	hasDigit := regexp.MustCompile(`\d`).MatchString(password)
	hasSpecial := regexp.MustCompile(`[!@#$%^&*(),.?":{}|<>]`).MatchString(password)

	// 应用配置要求
	if h.config.Security.PasswordRequireUpper && !hasUpper {
		return false
	}
	if h.config.Security.PasswordRequireLower && !hasLower {
		return false
	}
	if h.config.Security.PasswordRequireDigit && !hasDigit {
		return false
	}
	if h.config.Security.PasswordRequireSpecial && !hasSpecial {
		return false
	}

	return true
}

// ListSessions 获取用户会话列表
func (h *AuthHandler) ListSessions(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	query := `
		SELECT id, device_info, ip_address, created_at, expires_at
		FROM user_sessions
		WHERE user_id = $1 AND expires_at > CURRENT_TIMESTAMP
		ORDER BY created_at DESC
	`

	rows, err := h.db.Query(query, userID)
	if err != nil {
		h.logger.Error("Failed to query sessions", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer rows.Close()

	var sessions []gin.H
	for rows.Next() {
		var id, ipAddress string
		var deviceInfo []byte
		var createdAt, expiresAt time.Time

		if err := rows.Scan(&id, &deviceInfo, &ipAddress, &createdAt, &expiresAt); err != nil {
			continue
		}

		sessions = append(sessions, gin.H{
			"id":          id,
			"device_info": string(deviceInfo),
			"ip_address":  ipAddress,
			"created_at":  createdAt.Format(time.RFC3339),
			"expires_at":  expiresAt.Format(time.RFC3339),
		})
	}

	c.JSON(http.StatusOK, gin.H{"sessions": sessions})
}

// RevokeSession 撤销会话
func (h *AuthHandler) RevokeSession(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	sessionID := c.Param("id")

	query := `
		DELETE FROM user_sessions
		WHERE id = $1 AND user_id = $2
	`

	result, err := h.db.Exec(query, sessionID, userID)
	if err != nil {
		h.logger.Error("Failed to revoke session", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Session revoked successfully"})
}

// ForgotPassword 忘记密码
func (h *AuthHandler) ForgotPassword(c *gin.Context) {
	type ForgotPasswordRequest struct {
		Email string `json:"email" binding:"required,email"`
	}

	var req ForgotPasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// 检查邮箱是否存在
	var userID, username string
	query := `SELECT id, username FROM users WHERE email = $1 AND is_active = true`
	err := h.db.QueryRow(query, req.Email).Scan(&userID, &username)

	if err == sql.ErrNoRows {
		// 为了安全，不透露邮箱是否存在
		c.JSON(http.StatusOK, gin.H{
			"message": "If the email exists, a password reset link has been sent",
		})
		return
	} else if err != nil {
		h.logger.Error("Database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 生成密码重置令牌（在实际应用中应该发送邮件）
	resetToken, err := h.generatePasswordResetToken(userID)
	if err != nil {
		h.logger.Error("Failed to generate reset token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 这里应该发送邮件，现在只是返回令牌（仅用于开发环境）
	if h.config.Environment == "development" {
		c.JSON(http.StatusOK, gin.H{
			"message":    "Password reset token generated (development only)",
			"reset_token": resetToken,
			"user_id":    userID,
		})
	} else {
		c.JSON(http.StatusOK, gin.H{
			"message": "If the email exists, a password reset link has been sent",
		})
	}
}

// ResetPassword 重置密码
func (h *AuthHandler) ResetPassword(c *gin.Context) {
	type ResetPasswordRequest struct {
		Token       string `json:"token" binding:"required"`
		NewPassword string `json:"new_password" binding:"required"`
	}

	var req ResetPasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// 验证密码强度
	if !h.validatePassword(req.NewPassword) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Password does not meet requirements",
		})
		return
	}

	// 验证重置令牌并获取用户ID
	userID, err := h.validatePasswordResetToken(req.Token)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid or expired reset token"})
		return
	}

	// 更新密码
	passwordHash, err := bcrypt.GenerateFromPassword([]byte(req.NewPassword), h.config.Security.BCryptCost)
	if err != nil {
		h.logger.Error("Failed to hash password", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	query := `UPDATE users SET password_hash = $1 WHERE id = $2`
	_, err = h.db.Exec(query, string(passwordHash), userID)
	if err != nil {
		h.logger.Error("Failed to update password", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// 删除用户的现有会话（强制重新登录）
	h.db.Exec("DELETE FROM user_sessions WHERE user_id = $1", userID)

	c.JSON(http.StatusOK, gin.H{"message": "Password reset successfully"})
}

func (h *AuthHandler) generatePasswordResetToken(userID string) (string, error) {
	claims := jwt.MapClaims{
		"sub": userID,
		"iss": h.config.JWT.Issuer,
		"exp": time.Now().Add(1 * time.Hour).Unix(), // 1小时有效期
		"iat": time.Now().Unix(),
		"type": "password_reset",
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(h.config.JWT.Secret))
}

func (h *AuthHandler) validatePasswordResetToken(token string) (string, error) {
	parsedToken, err := jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(h.config.JWT.Secret), nil
	})

	if err != nil || !parsedToken.Valid {
		return "", err
	}

	claims, ok := parsedToken.Claims.(jwt.MapClaims)
	if !ok {
		return "", jwt.ErrTokenInvalidClaims
	}

	// 检查令牌类型
	tokenType, ok := claims["type"].(string)
	if !ok || tokenType != "password_reset" {
		return "", jwt.ErrTokenInvalidId
	}

	userID, ok := claims["sub"].(string)
	if !ok {
		return "", jwt.ErrTokenInvalidClaims
	}

	return userID, nil
}

// ==================== Redis 缓存方法 ====================

// cacheUserSession 缓存用户会话
func (h *AuthHandler) cacheUserSession(userID, sessionID string, ttl time.Duration) error {
	if h.redis == nil {
		return nil // Redis 未配置，跳过缓存
	}

	ctx := context.Background()
	key := fmt.Sprintf("session:%s", sessionID)

	sessionData := map[string]interface{}{
		"user_id":    userID,
		"session_id": sessionID,
		"created_at": time.Now().Unix(),
	}

	data, err := json.Marshal(sessionData)
	if err != nil {
		return err
	}

	return h.redis.Set(ctx, key, data, ttl).Err()
}

// getUserSession 获取用户会话
func (h *AuthHandler) getUserSession(sessionID string) (map[string]interface{}, error) {
	if h.redis == nil {
		return nil, fmt.Errorf("Redis not configured")
	}

	ctx := context.Background()
	key := fmt.Sprintf("session:%s", sessionID)

	data, err := h.redis.Get(ctx, key).Bytes()
	if err != nil {
		return nil, err
	}

	var session map[string]interface{}
	if err := json.Unmarshal(data, &session); err != nil {
		return nil, err
	}

	return session, nil
}

// deleteUserSession 删除用户会话（登出时使用）
func (h *AuthHandler) deleteUserSession(sessionID string) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("session:%s", sessionID)
	return h.redis.Del(ctx, key).Err()
}

// addTokenToBlacklist 将 JWT 令牌加入黑名单（用于登出）
func (h *AuthHandler) addTokenToBlacklist(tokenID string, ttl time.Duration) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("token:blacklist:%s", tokenID)
	return h.redis.Set(ctx, key, "1", ttl).Err()
}

// isTokenBlacklisted 检查令牌是否在黑名单中
func (h *AuthHandler) isTokenBlacklisted(tokenID string) (bool, error) {
	if h.redis == nil {
		return false, nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("token:blacklist:%s", tokenID)
	result, err := h.redis.Exists(ctx, key).Result()
	if err != nil {
		return false, err
	}
	return result > 0, nil
}

// cacheLoginFailed 缓存登录失败次数
func (h *AuthHandler) cacheLoginFailed(username string, maxAttempts int, lockoutDuration time.Duration) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("login:failed:%s", username)

	// 增加失败计数
	count, err := h.redis.Incr(ctx, key).Result()
	if err != nil {
		return err
	}

	// 如果是第一次失败，设置过期时间
	if count == 1 {
		h.redis.Expire(ctx, key, lockoutDuration)
	}

	// 如果达到最大失败次数，锁定账户
	if int(count) >= maxAttempts {
		lockKey := fmt.Sprintf("account:locked:%s", username)
		h.redis.Set(ctx, lockKey, "1", lockoutDuration)
	}

	return nil
}

// getFailedLoginCount 获取登录失败次数
func (h *AuthHandler) getFailedLoginCount(username string) (int, error) {
	if h.redis == nil {
		return 0, fmt.Errorf("Redis not configured")
	}

	ctx := context.Background()
	key := fmt.Sprintf("login:failed:%s", username)

	count, err := h.redis.Get(ctx, key).Int()
	if err == redis.Nil {
		return 0, nil
	}
	return count, err
}

// resetFailedLoginCount 重置登录失败次数
func (h *AuthHandler) resetFailedLoginCount(username string) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("login:failed:%s", username)
	return h.redis.Del(ctx, key).Err()
}

// isAccountLocked 检查账户是否被锁定
func (h *AuthHandler) isAccountLocked(username string) (bool, error) {
	if h.redis == nil {
		return false, nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("account:locked:%s", username)
	result, err := h.redis.Exists(ctx, key).Result()
	if err != nil {
		return false, err
	}
	return result > 0, nil
}

// getLockRemainingTime 获取账户锁定剩余时间
func (h *AuthHandler) getLockRemainingTime(username string) (time.Duration, error) {
	if h.redis == nil {
		return 0, fmt.Errorf("Redis not configured")
	}

	ctx := context.Background()
	key := fmt.Sprintf("account:locked:%s", username)
	ttl, err := h.redis.TTL(ctx, key).Result()
	if err != nil {
		return 0, err
	}
	return ttl, nil
}

// cacheUserInfo 缓存用户信息
func (h *AuthHandler) cacheUserInfo(userID string, userInfo map[string]interface{}, ttl time.Duration) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("user:info:%s", userID)

	data, err := json.Marshal(userInfo)
	if err != nil {
		return err
	}

	return h.redis.Set(ctx, key, data, ttl).Err()
}

// getUserInfo 获取缓存的用户信息
func (h *AuthHandler) getUserInfo(userID string) (map[string]interface{}, error) {
	if h.redis == nil {
		return nil, fmt.Errorf("Redis not configured")
	}

	ctx := context.Background()
	key := fmt.Sprintf("user:info:%s", userID)

	data, err := h.redis.Get(ctx, key).Bytes()
	if err != nil {
		return nil, err
	}

	var userInfo map[string]interface{}
	if err := json.Unmarshal(data, &userInfo); err != nil {
		return nil, err
	}

	return userInfo, nil
}

// deleteUserCache 删除用户缓存
func (h *AuthHandler) deleteUserCache(userID string) error {
	if h.redis == nil {
		return nil
	}

	ctx := context.Background()
	key := fmt.Sprintf("user:info:%s", userID)
	return h.redis.Del(ctx, key).Err()
}