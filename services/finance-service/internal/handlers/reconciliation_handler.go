package handlers

import (
	"database/sql"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/finance-service/internal/config"
)

// ReconciliationStatus 对账状态
type ReconciliationStatus string

const (
	ReconciliationStatusPending   ReconciliationStatus = "pending"   // 待对账
	ReconciliationStatusConfirmed ReconciliationStatus = "confirmed" // 已确认
	ReconciliationStatusDisputed  ReconciliationStatus = "disputed"  // 有争议
)

// Reconciliation 销售对账记录
type Reconciliation struct {
	ID             string               `json:"id"`
	OrderID        string               `json:"order_id"`
	CustomerID     string               `json:"customer_id"`
	CustomerName   string               `json:"customer_name"`
	Amount         float64              `json:"amount"`
	Currency       string               `json:"currency"`
	Period         string               `json:"period"` // 对账周期：YYYY-MM
	Status         ReconciliationStatus `json:"status"`
	ConfirmedBy    *string              `json:"confirmed_by,omitempty"`
	ConfirmedAt    *time.Time           `json:"confirmed_at,omitempty"`
	DisputeReason  string               `json:"dispute_reason,omitempty"`
	Notes          string               `json:"notes,omitempty"`
	AttachmentURL  string               `json:"attachment_url,omitempty"`
	CreatedAt      time.Time            `json:"created_at"`
	UpdatedAt      time.Time            `json:"updated_at"`
}

type CreateReconciliationRequest struct {
	OrderID       string `json:"order_id" binding:"required"`
	CustomerID    string `json:"customer_id" binding:"required"`
	CustomerName  string `json:"customer_name" binding:"required"`
	Amount        float64 `json:"amount" binding:"required,gt=0"`
	Currency      string `json:"currency"`
	Period        string `json:"period" binding:"required"`
	AttachmentURL string `json:"attachment_url"`
}

type ConfirmReconciliationRequest struct {
	Notes string `json:"notes"`
}

type DisputeReconciliationRequest struct {
	Reason string `json:"reason" binding:"required"`
	Notes  string `json:"notes"`
}

type ReconciliationHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewReconciliationHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *ReconciliationHandler {
	return &ReconciliationHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

func (h *ReconciliationHandler) ListReconciliations(c *gin.Context) {
	// 获取查询参数
	customerID := c.Query("customer_id")
	status := c.Query("status")
	period := c.Query("period")
	page := c.DefaultQuery("page", "1")
	pageSize := c.DefaultQuery("page_size", "20")

	query := `
		SELECT id, order_id, customer_id, customer_name, amount, currency,
		       period, status, confirmed_by, confirmed_at, dispute_reason,
		       notes, attachment_url, created_at, updated_at
		FROM reconciliations
		WHERE 1=1
	`
	args := []interface{}{}
	argIndex := 0

	if status != "" {
		argIndex++
		query += " AND status = $" + string(rune(argIndex+'0'))
		args = append(args, status)
	}
	if customerID != "" {
		argIndex++
		query += " AND customer_id = $" + string(rune(argIndex+'0'))
		args = append(args, customerID)
	}
	if period != "" {
		argIndex++
		query += " AND period = $" + string(rune(argIndex+'0'))
		args = append(args, period)
	}

	argIndex++
	query += " ORDER BY period DESC, created_at DESC LIMIT $" + string(rune(argIndex+'0'))
	args = append(args, pageSize)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询对账记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var reconciliations []Reconciliation
	for rows.Next() {
		var rec Reconciliation
		var confirmedBy sql.NullString
		var confirmedAt sql.NullTime

		err := rows.Scan(
			&rec.ID, &rec.OrderID, &rec.CustomerID, &rec.CustomerName,
			&rec.Amount, &rec.Currency, &rec.Period, &rec.Status,
			&confirmedBy, &confirmedAt, &rec.DisputeReason, &rec.Notes,
			&rec.AttachmentURL, &rec.CreatedAt, &rec.UpdatedAt,
		)
		if err != nil {
			continue
		}

		if confirmedBy.Valid {
			rec.ConfirmedBy = &confirmedBy.String
		}
		if confirmedAt.Valid {
			rec.ConfirmedAt = &confirmedAt.Time
		}

		reconciliations = append(reconciliations, rec)
	}

	if reconciliations == nil {
		reconciliations = []Reconciliation{}
	}

	c.JSON(200, gin.H{
		"reconciliations": reconciliations,
		"page":            page,
		"page_size":       pageSize,
	})
}

func (h *ReconciliationHandler) GetReconciliation(c *gin.Context) {
	id := c.Param("id")

	var rec Reconciliation
	var confirmedBy sql.NullString
	var confirmedAt sql.NullTime

	err := h.db.QueryRow(`
		SELECT id, order_id, customer_id, customer_name, amount, currency,
		       period, status, confirmed_by, confirmed_at, dispute_reason,
		       notes, attachment_url, created_at, updated_at
		FROM reconciliations WHERE id = $1
	`, id).Scan(
		&rec.ID, &rec.OrderID, &rec.CustomerID, &rec.CustomerName,
		&rec.Amount, &rec.Currency, &rec.Period, &rec.Status,
		&confirmedBy, &confirmedAt, &rec.DisputeReason, &rec.Notes,
		&rec.AttachmentURL, &rec.CreatedAt, &rec.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		c.JSON(404, gin.H{"error": "对账记录不存在"})
		return
	}
	if err != nil {
		h.logger.Error("查询对账记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "查询失败"})
		return
	}

	if confirmedBy.Valid {
		rec.ConfirmedBy = &confirmedBy.String
	}
	if confirmedAt.Valid {
		rec.ConfirmedAt = &confirmedAt.Time
	}

	c.JSON(200, rec)
}

func (h *ReconciliationHandler) CreateReconciliation(c *gin.Context) {
	var req CreateReconciliationRequest
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
		INSERT INTO reconciliations (id, order_id, customer_id, customer_name, amount, currency, period, status, attachment_url, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
	`, id, req.OrderID, req.CustomerID, req.CustomerName, req.Amount, req.Currency, req.Period, ReconciliationStatusPending, req.AttachmentURL, now, now)

	if err != nil {
		h.logger.Error("创建对账记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "创建失败"})
		return
	}

	c.JSON(201, gin.H{
		"id":      id,
		"message": "对账记录创建成功",
	})
}

func (h *ReconciliationHandler) ConfirmReconciliation(c *gin.Context) {
	id := c.Param("id")

	var req ConfirmReconciliationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": "无效的请求数据"})
		return
	}

	// 获取确认人 ID
	confirmerID, _ := c.Get("user_id")
	confirmerIDStr, _ := confirmerID.(string)

	now := time.Now()

	_, err := h.db.Exec(`
		UPDATE reconciliations
		SET status = $1, confirmed_by = $2, confirmed_at = $3, notes = COALESCE(NULLIF($4, ''), notes), updated_at = $3
		WHERE id = $5
	`, ReconciliationStatusConfirmed, confirmerIDStr, now, req.Notes, id)

	if err != nil {
		h.logger.Error("确认对账记录失败", zap.Error(err))
		c.JSON(500, gin.H{"error": "确认失败"})
		return
	}

	c.JSON(200, gin.H{"message": "确认成功"})
}
