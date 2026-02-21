package handlers

import (
	"database/sql"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/finance-service/internal/config"
)

// SalaryType 工资类型
type SalaryType string

const (
	SalaryTypeBase     SalaryType = "base"     // 基本工资
	SalaryTypePerformance SalaryType = "performance" // 绩效奖金
	SalaryTypeBonus    SalaryType = "bonus"    // 奖金
	SalaryTypeCommission SalaryType = "commission" // 提成
	SalaryTypeAllowance SalaryType = "allowance" // 补贴
)

// Salary 工资记录
type Salary struct {
	ID         string     `json:"id"`
	UserID     string     `json:"user_id"`
	Type       SalaryType `json:"type"`
	Amount     float64    `json:"amount"`
	Currency   string     `json:"currency"`
	Month      string     `json:"month"` // 格式：YYYY-MM
	Reason     string     `json:"reason"`
	Status     string     `json:"status"` // pending, approved, paid
	PaidBy     *string    `json:"paid_by,omitempty"`
	PaidAt     *time.Time `json:"paid_at,omitempty"`
	Notes      string     `json:"notes,omitempty"`
	CreatedAt  time.Time  `json:"created_at"`
	UpdatedAt  time.Time  `json:"updated_at"`
}

type CreateSalaryRequest struct {
	UserID   string     `json:"user_id" binding:"required"`
	Type     SalaryType `json:"type" binding:"required"`
	Amount   float64    `json:"amount" binding:"required,gt=0"`
	Currency string     `json:"currency"`
	Month    string     `json:"month" binding:"required"`
	Reason   string     `json:"reason"`
}

type UpdateSalaryRequest struct {
	Type   SalaryType `json:"type"`
	Amount float64    `json:"amount"`
	Currency string  `json:"currency"`
	Month  string    `json:"month"`
	Reason string    `json:"reason"`
	Notes  string    `json:"notes"`
}

type SalaryHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewSalaryHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *SalaryHandler {
	return &SalaryHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

func (h *SalaryHandler) ListSalaries(c *gin.Context) {
	// 获取查询参数
	userID := c.Query("user_id")
	salaryType := c.Query("type")
	month := c.Query("month")
	status := c.Query("status")
	page := c.DefaultQuery("page", "1")
	pageSize := c.DefaultQuery("page_size", "20")

	// 构建查询
	query := `
		SELECT id, user_id, type, amount, currency, month, reason, status,
		       paid_by, paid_at, notes, created_at, updated_at
		FROM salaries
		WHERE 1=1
	`
	args := []interface{}{}
	argIndex := 0

	if status != "" {
		argIndex++
		query += " AND status = $" + string(rune(argIndex+'0'))
		args = append(args, status)
	}
	if userID != "" {
		argIndex++
		query += " AND user_id = $" + string(rune(argIndex+'0'))
		args = append(args, userID)
	}
	if salaryType != "" {
		argIndex++
		query += " AND type = $" + string(rune(argIndex+'0'))
		args = append(args, salaryType)
	}
	if month != "" {
		argIndex++
		query += " AND month = $" + string(rune(argIndex+'0'))
		args = append(args, month)
	}

	argIndex++
	query += " ORDER BY month DESC, created_at DESC LIMIT $" + string(rune(argIndex+'0'))
	args = append(args, pageSize)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询工资记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var salaries []Salary
	for rows.Next() {
		var salary Salary
		var paidBy sql.NullString
		var paidAt sql.NullTime

		err := rows.Scan(
			&salary.ID, &salary.UserID, &salary.Type, &salary.Amount,
			&salary.Currency, &salary.Month, &salary.Reason, &salary.Status,
			&paidBy, &paidAt, &salary.Notes, &salary.CreatedAt, &salary.UpdatedAt,
		)
		if err != nil {
			continue
		}

		if paidBy.Valid {
			salary.PaidBy = &paidBy.String
		}
		if paidAt.Valid {
			salary.PaidAt = &paidAt.Time
		}

		salaries = append(salaries, salary)
	}

	if salaries == nil {
		salaries = []Salary{}
	}

	c.JSON(200, gin.H{
		"salaries":  salaries,
		"page":      page,
		"page_size": pageSize,
	})
}

func (h *SalaryHandler) GetSalary(c *gin.Context) {
	id := c.Param("id")

	var salary Salary
	var paidBy sql.NullString
	var paidAt sql.NullTime

	err := h.db.QueryRow(`
		SELECT id, user_id, type, amount, currency, month, reason, status,
		       paid_by, paid_at, notes, created_at, updated_at
		FROM salaries WHERE id = $1
	`, id).Scan(
		&salary.ID, &salary.UserID, &salary.Type, &salary.Amount,
		&salary.Currency, &salary.Month, &salary.Reason, &salary.Status,
		&paidBy, &paidAt, &salary.Notes, &salary.CreatedAt, &salary.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		c.JSON(404, gin.H{"error": "工资记录不存在"})
		return
	}
	if err != nil {
		h.logger.Error("查询工资记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "查询失败"})
		return
	}

	if paidBy.Valid {
		salary.PaidBy = &paidBy.String
	}
	if paidAt.Valid {
		salary.PaidAt = &paidAt.Time
	}

	c.JSON(200, salary)
}

func (h *SalaryHandler) CreateSalary(c *gin.Context) {
	var req CreateSalaryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": "无效的请求数据"})
		return
	}

	// 默认货币
	if req.Currency == "" {
		req.Currency = "CNY"
	}

	id := generateUUID()
	now := time.Now()

	_, err := h.db.Exec(`
		INSERT INTO salaries (id, user_id, type, amount, currency, month, reason, status, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`, id, req.UserID, req.Type, req.Amount, req.Currency, req.Month, req.Reason, "pending", now, now)

	if err != nil {
		h.logger.Error("创建工资记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "创建失败"})
		return
	}

	c.JSON(201, gin.H{
		"id":      id,
		"message": "工资记录创建成功",
	})
}

func (h *SalaryHandler) UpdateSalary(c *gin.Context) {
	id := c.Param("id")

	var req UpdateSalaryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": "无效的请求数据"})
		return
	}

	// 检查是否存在
	var exists bool
	err := h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM salaries WHERE id = $1)", id).Scan(&exists)
	if err != nil || !exists {
		c.JSON(404, gin.H{"error": "工资记录不存在"})
		return
	}

	now := time.Now()

	_, err = h.db.Exec(`
		UPDATE salaries
		SET type = COALESCE(NULLIF($1, ''), type),
		    amount = COALESCE(NULLIF($2, 0), amount),
		    currency = COALESCE(NULLIF($3, ''), currency),
		    month = COALESCE(NULLIF($4, ''), month),
		    reason = COALESCE(NULLIF($5, ''), reason),
		    notes = COALESCE(NULLIF($6, ''), notes),
		    updated_at = $7
		WHERE id = $8
	`, req.Type, req.Amount, req.Currency, req.Month, req.Reason, req.Notes, now, id)

	if err != nil {
		h.logger.Error("更新工资记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "更新失败"})
		return
	}

	c.JSON(200, gin.H{"message": "更新成功"})
}

func (h *SalaryHandler) DeleteSalary(c *gin.Context) {
	id := c.Param("id")

	result, err := h.db.Exec("DELETE FROM salaries WHERE id = $1", id)
	if err != nil {
		h.logger.Error("删除工资记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "删除失败"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(404, gin.H{"error": "工资记录不存在"})
		return
	}

	c.JSON(200, gin.H{"message": "删除成功"})
}
