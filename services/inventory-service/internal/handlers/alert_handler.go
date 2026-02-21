package handlers

import (
	"database/sql"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/inventory-service/internal/config"
)

// AlertHandler 预警处理器
type AlertHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewAlertHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *AlertHandler {
	return &AlertHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

// InventoryAlert 库存预警
type InventoryAlert struct {
	ID          string    `json:"id"`
	AlertType   string    `json:"alert_type"` // low_stock, overstock, expiring, obsolete
	MPN         string    `json:"mpn"`
	Warehouse   string    `json:"warehouse"`
	CurrentQty  int       `json:"current_qty"`
	Threshold   int       `json:"threshold"`
	Message     string    `json:"message"`
	Severity    string    `json:"severity"` // critical, warning, info
	Status      string    `json:"status"` // active, acknowledged, resolved
	AcknowledgedBy string  `json:"acknowledged_by,omitempty"`
	AcknowledgedAt *time.Time `json:"acknowledged_at,omitempty"`
	ResolvedAt  *time.Time `json:"resolved_at,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

func (h *AlertHandler) ListAlerts(c *gin.Context) {
	status := c.DefaultQuery("status", "active")
	alertType := c.Query("alert_type")
	severity := c.Query("severity")

	query := `
		SELECT id, alert_type, mpn, warehouse, current_qty, threshold, message,
		       severity, status, acknowledged_by, acknowledged_at, resolved_at, created_at
		FROM inventory_alerts
		WHERE status = $1
	`
	args := []interface{}{status}
	argNum := 1

	if alertType != "" {
		argNum++
		query += " AND alert_type = $" + string(rune('0'+argNum))
		args = append(args, alertType)
	}
	if severity != "" {
		argNum++
		query += " AND severity = $" + string(rune('0'+argNum))
		args = append(args, severity)
	}

	query += " ORDER BY created_at DESC"

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询预警失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var alerts []InventoryAlert
	for rows.Next() {
		var a InventoryAlert
		err := rows.Scan(
			&a.ID, &a.AlertType, &a.MPN, &a.Warehouse, &a.CurrentQty,
			&a.Threshold, &a.Message, &a.Severity, &a.Status,
			&a.AcknowledgedBy, &a.AcknowledgedAt, &a.ResolvedAt, &a.CreatedAt,
		)
		if err != nil {
			continue
		}
		alerts = append(alerts, a)
	}

	if alerts == nil {
		alerts = []InventoryAlert{}
	}

	c.JSON(http.StatusOK, gin.H{"alerts": alerts})
}

func (h *AlertHandler) AcknowledgeAlert(c *gin.Context) {
	id := c.Param("id")

	// 获取当前用户
	userID, _ := c.Get("user_id")
	userIDStr, _ := userID.(string)
	if userIDStr == "" {
		userIDStr = "system"
	}

	now := time.Now()

	// 更新预警状态
	result, err := h.db.Exec(`
		UPDATE inventory_alerts
		SET status = 'acknowledged', acknowledged_by = $1, acknowledged_at = $2
		WHERE id = $3
	`, userIDStr, now, id)

	if err != nil {
		h.logger.Error("确认预警失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "确认失败"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "预警不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "预警已确认"})
}

// CheckAndGenerateAlerts 检查并生成预警
func (h *AlertHandler) CheckAndGenerateAlerts() {
	// 检查低库存预警
	h.checkLowStockAlerts()

	// 检查超库存预警
	h.checkOverstockAlerts()

	// 检查过期预警
	h.checkExpiringAlerts()
}

func (h *AlertHandler) checkLowStockAlerts() {
	// 查询低库存物料
	rows, err := h.db.Query(`
		SELECT id, mpn, warehouse, quantity, reorder_point, min_stock_level
		FROM inventory
		WHERE quantity <= reorder_point AND status = 'active'
	`)
	if err != nil {
		h.logger.Error("查询低库存失败", zap.Error(err))
		return
	}
	defer rows.Close()

	for rows.Next() {
		var id, mpn, warehouse string
		var quantity, reorderPoint, minStockLevel int

		err := rows.Scan(&id, &mpn, &warehouse, &quantity, &reorderPoint, &minStockLevel)
		if err != nil {
			continue
		}

		// 确定严重程度
		severity := "warning"
		if quantity <= minStockLevel {
			severity = "critical"
		}

		// 创建预警
		h.createAlert("low_stock", mpn, warehouse, quantity, reorderPoint,
			"库存低于补货点", severity)
	}
}

func (h *AlertHandler) checkOverstockAlerts() {
	// 查询超库存物料
	rows, err := h.db.Query(`
		SELECT id, mpn, warehouse, quantity, max_stock_level
		FROM inventory
		WHERE quantity >= max_stock_level AND status = 'active'
	`)
	if err != nil {
		h.logger.Error("查询超库存失败", zap.Error(err))
		return
	}
	defer rows.Close()

	for rows.Next() {
		var id, mpn, warehouse string
		var quantity, maxStockLevel int

		err := rows.Scan(&id, &mpn, &warehouse, &quantity, &maxStockLevel)
		if err != nil {
			continue
		}

		// 创建预警
		h.createAlert("overstock", mpn, warehouse, quantity, maxStockLevel,
			"库存超过最大库存", "warning")
	}
}

func (h *AlertHandler) checkExpiringAlerts() {
	// 检查过期物料（简化实现）
	// 实际需要根据批次信息判断
}

func (h *AlertHandler) createAlert(alertType, mpn, warehouse string, currentQty, threshold int, message, severity string) {
	id := generateUUID()
	now := time.Now()

	// 检查是否已存在相同类型的未确认预警
	var exists bool
	h.db.QueryRow(`
		SELECT EXISTS(
			SELECT 1 FROM inventory_alerts
			WHERE mpn = $1 AND warehouse = $2 AND alert_type = $3 AND status = 'active'
		)
	`, mpn, warehouse, alertType).Scan(&exists)

	if exists {
		return // 已存在预警，不重复创建
	}

	// 创建新预警
	h.db.Exec(`
		INSERT INTO inventory_alerts (id, alert_type, mpn, warehouse, current_qty, threshold, message, severity, status, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'active', $9)
	`, id, alertType, mpn, warehouse, currentQty, threshold, message, severity, now)
}
