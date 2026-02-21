package handlers

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/finance-service/internal/config"
	"component-agent/finance-service/internal/encryption"
)

type ExpenseHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewExpenseHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *ExpenseHandler {
	return &ExpenseHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

// 报销类型
type ExpenseType string

const (
	ExpenseTypeTravel    ExpenseType = "travel"    // 差旅
	ExpenseTypeOffice    ExpenseType = "office"    // 办公用品
	ExpenseTypeCommunication ExpenseType = "communication" // 通讯
	ExpenseTypeTraining  ExpenseType = "training"  // 培训
	ExpenseTypeEntertainment ExpenseType = "entertainment" // 招待
	ExpenseTypeOther    ExpenseType = "other"    // 其他
)

// 报销状态
type ExpenseStatus string

const (
	ExpenseStatusPending   ExpenseStatus = "pending"   // 待审批
	ExpenseStatusApproved  ExpenseStatus = "approved"  // 已批准
	ExpenseStatusRejected  ExpenseStatus = "rejected"   // 已拒绝
	ExpenseStatusPaid     ExpenseStatus = "paid"      // 已付款
)

// Expense 报销单
type Expense struct {
	ID          string        `json:"id"`
	UserID      string        `json:"user_id"`
	Type        ExpenseType  `json:"type"`
	Amount      float64      `json:"amount"`
	Currency    string        `json:"currency"`
	Description string        `json:"description"`
	Status      ExpenseStatus `json:"status"`
	ReceiptURL  string        `json:"receipt_url,omitempty"`
	ApprovedBy  *string       `json:"approved_by,omitempty"`
	ApprovedAt  *time.Time    `json:"approved_at,omitempty"`
	PaymentAt   *time.Time    `json:"payment_at,omitempty"`
	Notes       string        `json:"notes,omitempty"`
	CreatedAt   time.Time     `json:"created_at"`
	UpdatedAt   time.Time     `json:"updated_at"`
}

type CreateExpenseRequest struct {
	Type        ExpenseType `json:"type" binding:"required"`
	Amount      float64    `json:"amount" binding:"required,gt=0"`
	Currency    string     `json:"currency"`
	Description string     `json:"description" binding:"required"`
	ReceiptURL  string     `json:"receipt_url"`
}

type UpdateExpenseRequest struct {
	Type        ExpenseType  `json:"type"`
	Amount      float64     `json:"amount"`
	Currency    string      `json:"currency"`
	Description string      `json:"description"`
	ReceiptURL  string      `json:"receipt_url"`
	Notes       string      `json:"notes"`
}

type ReviewExpenseRequest struct {
	Notes string `json:"notes"`
}

func (h *ExpenseHandler) ListExpenses(c *gin.Context) {
	// 获取查询参数
	status := c.Query("status")
	userID := c.Query("user_id")
	expenseType := c.Query("type")
	page := c.DefaultQuery("page", "1")
	pageSize := c.DefaultQuery("page_size", "20")

	// 构建查询
	query := `
		SELECT id, user_id, type, amount, currency, description, status,
		       receipt_url, approved_by, approved_at, payment_at, notes,
		       created_at, updated_at
		FROM expenses
		WHERE 1=1
	`
	args := []interface{}{}
	argIndex := 0

	if status != "" {
		argIndex++
		query += fmt.Sprintf(" AND status = $%d", argIndex)
		args = append(args, status)
	}
	if userID != "" {
		argIndex++
		query += fmt.Sprintf(" AND user_id = $%d", argIndex)
		args = append(args, userID)
	}
	if expenseType != "" {
		argIndex++
		query += fmt.Sprintf(" AND type = $%d", argIndex)
		args = append(args, expenseType)
	}

	argIndex++
	query += fmt.Sprintf(" ORDER BY created_at DESC LIMIT $%d OFFSET $%d", argIndex, argIndex+1)
	args = append(args, pageSize, (page-1)*pageSize)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var expenses []Expense
	for rows.Next() {
		var expense Expense
		err := rows.Scan(
			&expense.ID, &expense.UserID, &expense.Type, &expense.Amount,
			&expense.Currency, &expense.Description, &expense.Status,
			&expense.ReceiptURL, &expense.ApprovedBy, &expense.ApprovedAt,
			&expense.PaymentAt, &expense.Notes, &expense.CreatedAt, &expense.UpdatedAt,
		)
		if err != nil {
			continue
		}
		expenses = append(expenses, expense)
	}

	if expenses == nil {
		expenses = []Expense{}
	}

	c.JSON(http.StatusOK, gin.H{
		"expenses": expenses,
		"page":     page,
		"page_size": pageSize,
	})
}

func (h *ExpenseHandler) GetExpense(c *gin.Context) {
	id := c.Param("id")

	var expense Expense
	err := h.db.QueryRow(`
		SELECT id, user_id, type, amount, currency, description, status,
		       receipt_url, approved_by, approved_at, payment_at, notes,
		       created_at, updated_at
		FROM expenses WHERE id = $1
	`, id).Scan(
		&expense.ID, &expense.UserID, &expense.Type, &expense.Amount,
		&expense.Currency, &expense.Description, &expense.Status,
		&expense.ReceiptURL, &expense.ApprovedBy, &expense.ApprovedAt,
		&expense.PaymentAt, &expense.Notes, &expense.CreatedAt, &expense.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "报销单不存在"})
		return
	}
	if err != nil {
		h.logger.Error("查询报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	c.JSON(http.StatusOK, expense)
}

func (h *ExpenseHandler) CreateExpense(c *gin.Context) {
	var req CreateExpenseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	// 获取当前用户ID
	userID, _ := c.Get("user_id")
	userIDStr, _ := userID.(string)

	if userIDStr == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未授权"})
		return
	}

	// 生成ID
	id := generateUUID()

	// 默认货币
	if req.Currency == "" {
		req.Currency = "CNY"
	}

	// 插入数据库
	_, err := h.db.Exec(`
		INSERT INTO expenses (id, user_id, type, amount, currency, description, status, receipt_url, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`, id, userIDStr, req.Type, req.Amount, req.Currency, req.Description, ExpenseStatusPending, req.ReceiptURL, time.Now(), time.Now())

	if err != nil {
		h.logger.Error("创建报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建失败"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"id":      id,
		"message": "报销单创建成功",
	})
}

func (h *ExpenseHandler) UpdateExpense(c *gin.Context) {
	id := c.Param("id")

	var req UpdateExpenseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	// 检查是否存在
	var exists bool
	err := h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM expenses WHERE id = $1)", id).Scan(&exists)
	if err != nil || !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "报销单不存在"})
		return
	}

	// 更新
	_, err = h.db.Exec(`
		UPDATE expenses
		SET type = COALESCE(NULLIF($1, ''), type),
		    amount = COALESCE(NULLIF($2, 0), amount),
		    currency = COALESCE(NULLIF($3, ''), currency),
		    description = COALESCE(NULLIF($4, ''), description),
		    receipt_url = COALESCE(NULLIF($5, ''), receipt_url),
		    notes = COALESCE(NULLIF($6, ''), notes),
		    updated_at = $7
		WHERE id = $8
	`, req.Type, req.Amount, req.Currency, req.Description, req.ReceiptURL, req.Notes, time.Now(), id)

	if err != nil {
		h.logger.Error("更新报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "更新成功"})
}

func (h *ExpenseHandler) DeleteExpense(c *gin.Context) {
	id := c.Param("id")

	result, err := h.db.Exec("DELETE FROM expenses WHERE id = $1", id)
	if err != nil {
		h.logger.Error("删除报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除失败"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "报销单不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "删除成功"})
}

func (h *ExpenseHandler) ApproveExpense(c *gin.Context) {
	id := c.Param("id")

	var req ReviewExpenseRequest
	c.ShouldBindJSON(&req)

	// 获取审批人ID
	approverID, _ := c.Get("user_id")
	approverIDStr, _ := approverID.(string)

	now := time.Now()

	_, err := h.db.Exec(`
		UPDATE expenses
		SET status = $1, approved_by = $2, approved_at = $3, notes = COALESCE(NULLIF($4, ''), notes), updated_at = $3
		WHERE id = $5
	`, ExpenseStatusApproved, approverIDStr, now, req.Notes, id)

	if err != nil {
		h.logger.Error("审批报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "审批失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "审批通过"})
}

func (h *ExpenseHandler) RejectExpense(c *gin.Context) {
	id := c.Param("id")

	var req ReviewExpenseRequest
	c.ShouldBindJSON(&req)

	// 获取审批人ID
	approverID, _ := c.Get("user_id")
	approverIDStr, _ := approverID.(string)

	now := time.Now()

	_, err := h.db.Exec(`
		UPDATE expenses
		SET status = $1, approved_by = $2, approved_at = $3, notes = COALESCE(NULLIF($4, ''), notes), updated_at = $3
		WHERE id = $5
	`, ExpenseStatusRejected, approverIDStr, now, req.Notes, id)

	if err != nil {
		h.logger.Error("拒绝报销单失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "操作失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "已拒绝"})
}

// 辅助函数：生成UUID
func generateUUID() string {
	// 简化实现，实际应使用uuid库
	return time.Now().Format("20060102150405") + randomString(8)
}

func randomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[time.Now().UnixNano()%int64(len(letters))]
		time.Sleep(time.Nanosecond)
	}
	return string(b)
}

// 避免未使用导入错误
var _ = json.Marshal
