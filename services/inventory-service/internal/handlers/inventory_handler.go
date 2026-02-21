package handlers

import (
	"database/sql"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/inventory-service/internal/config"
)

// InventoryHandler 库存处理器
type InventoryHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewInventoryHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *InventoryHandler {
	return &InventoryHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

// Inventory 库存
type Inventory struct {
	ID             string    `json:"id"`
	MPN            string    `json:"mpn"`
	Manufacturer   string    `json:"manufacturer"`
	Warehouse     string    `json:"warehouse"`
	Location      string    `json:"location"`
	Quantity      int       `json:"quantity"`
	ReservedQty   int       `json:"reserved_qty"`
	AvailableQty  int       `json:"available_qty"`
	MinStockLevel int       `json:"min_stock_level"`
	MaxStockLevel int       `json:"max_stock_level"`
	ReorderPoint  int       `json:"reorder_point"`
	UnitCost      float64   `json:"unit_cost"`
	Currency      string    `json:"currency"`
	Status        string    `json:"status"`
	LastCountDate time.Time `json:"last_count_date"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}

type CreateInventoryRequest struct {
	MPN            string  `json:"mpn" binding:"required"`
	Manufacturer   string  `json:"manufacturer" binding:"required"`
	Warehouse      string  `json:"warehouse" binding:"required"`
	Location       string  `json:"location"`
	Quantity       int     `json:"quantity" binding:"gte=0"`
	MinStockLevel  int     `json:"min_stock_level"`
	MaxStockLevel  int     `json:"max_stock_level"`
	ReorderPoint   int     `json:"reorder_point"`
	UnitCost       float64 `json:"unit_cost"`
	Currency       string  `json:"currency"`
}

type AdjustInventoryRequest struct {
	MPN          string  `json:"mpn" binding:"required"`
	Warehouse    string  `json:"warehouse" binding:"required"`
	AdjustQty    int     `json:"adjust_qty" binding:"required"`
	AdjustType   string  `json:"adjust_type" binding:"required"` // in, out, adjustment
	Reason       string  `json:"reason"`
}

func (h *InventoryHandler) ListInventory(c *gin.Context) {
	warehouse := c.Query("warehouse")
	mpn := c.Query("mpn")
	lowStock := c.Query("low_stock")

	query := `
		SELECT id, mpn, manufacturer, warehouse, location, quantity, reserved_qty,
		       available_qty, min_stock_level, max_stock_level, reorder_point,
		       unit_cost, currency, status, last_count_date, created_at, updated_at
		FROM inventory
		WHERE 1=1
	`
	args := []interface{}{}
	argIndex := 0

	if warehouse != "" {
		argIndex++
		query += fmt.Sprintf(" AND warehouse = $%d", argIndex)
		args = append(args, warehouse)
	}
	if mpn != "" {
		argIndex++
		query += fmt.Sprintf(" AND mpn = $%d", argIndex)
		args = append(args, mpn)
	}
	if lowStock == "true" {
		query += " AND quantity <= reorder_point"
	}

	query += " ORDER BY updated_at DESC LIMIT 100"

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var inventories []Inventory
	for rows.Next() {
		var inv Inventory
		err := rows.Scan(
			&inv.ID, &inv.MPN, &inv.Manufacturer, &inv.Warehouse, &inv.Location,
			&inv.Quantity, &inv.ReservedQty, &inv.AvailableQty, &inv.MinStockLevel,
			&inv.MaxStockLevel, &inv.ReorderPoint, &inv.UnitCost, &inv.Currency,
			&inv.Status, &inv.LastCountDate, &inv.CreatedAt, &inv.UpdatedAt,
		)
		if err != nil {
			continue
		}
		inventories = append(inventories, inv)
	}

	if inventories == nil {
		inventories = []Inventory{}
	}

	c.JSON(http.StatusOK, gin.H{"inventory": inventories})
}

func (h *InventoryHandler) GetInventory(c *gin.Context) {
	id := c.Param("id")

	var inv Inventory
	err := h.db.QueryRow(`
		SELECT id, mpn, manufacturer, warehouse, location, quantity, reserved_qty,
		       available_qty, min_stock_level, max_stock_level, reorder_point,
		       unit_cost, currency, status, last_count_date, created_at, updated_at
		FROM inventory WHERE id = $1
	`, id).Scan(
		&inv.ID, &inv.MPN, &inv.Manufacturer, &inv.Warehouse, &inv.Location,
		&inv.Quantity, &inv.ReservedQty, &inv.AvailableQty, &inv.MinStockLevel,
		&inv.MaxStockLevel, &inv.ReorderPoint, &inv.UnitCost, &inv.Currency,
		&inv.Status, &inv.LastCountDate, &inv.CreatedAt, &inv.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "库存记录不存在"})
		return
	}
	if err != nil {
		h.logger.Error("查询库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	c.JSON(http.StatusOK, inv)
}

func (h *InventoryHandler) CreateInventory(c *gin.Context) {
	var req CreateInventoryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	id := generateUUID()
	now := time.Now()

	if req.Currency == "" {
		req.Currency = "CNY"
	}

	_, err := h.db.Exec(`
		INSERT INTO inventory (id, mpn, manufacturer, warehouse, location, quantity,
			reserved_qty, available_qty, min_stock_level, max_stock_level, reorder_point,
			unit_cost, currency, status, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, 0, $6, $7, $8, $9, $10, $11, 'active', $12, $12)
	`, id, req.MPN, req.Manufacturer, req.Warehouse, req.Location, req.Quantity,
		req.MinStockLevel, req.MaxStockLevel, req.ReorderPoint, req.UnitCost, req.Currency, now)

	if err != nil {
		h.logger.Error("创建库存记录失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建失败"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id, "message": "创建成功"})
}

func (h *InventoryHandler) UpdateInventory(c *gin.Context) {
	id := c.Param("id")

	var req CreateInventoryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	now := time.Now()

	_, err := h.db.Exec(`
		UPDATE inventory
		SET mpn = COALESCE(NULLIF($1, ''), mpn),
		    manufacturer = COALESCE(NULLIF($2, ''), manufacturer),
		    warehouse = COALESCE(NULLIF($3, ''), warehouse),
		    location = COALESCE(NULLIF($4, ''), location),
		    min_stock_level = COALESCE(NULLIF($5, 0), min_stock_level),
		    max_stock_level = COALESCE(NULLIF($6, 0), max_stock_level),
		    reorder_point = COALESCE(NULLIF($7, 0), reorder_point),
		    unit_cost = COALESCE(NULLIF($8, 0), unit_cost),
		    updated_at = $9
		WHERE id = $10
	`, req.MPN, req.Manufacturer, req.Warehouse, req.Location,
		req.MinStockLevel, req.MaxStockLevel, req.ReorderPoint, req.UnitCost, now, id)

	if err != nil {
		h.logger.Error("更新库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "更新成功"})
}

func (h *InventoryHandler) DeleteInventory(c *gin.Context) {
	id := c.Param("id")

	result, err := h.db.Exec("DELETE FROM inventory WHERE id = $1", id)
	if err != nil {
		h.logger.Error("删除库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除失败"})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "库存记录不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "删除成功"})
}

func (h *InventoryHandler) AdjustInventory(c *gin.Context) {
	var req AdjustInventoryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	// 验证调整类型
	validTypes := map[string]bool{"in": true, "out": true, "adjustment": true}
	if !validTypes[req.AdjustType] {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的调整类型"})
		return
	}

	// 查询现有库存
	var currentQty int
	err := h.db.QueryRow(`
		SELECT quantity FROM inventory
		WHERE mpn = $1 AND warehouse = $2
	`, req.MPN, req.Warehouse).Scan(&currentQty)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "库存记录不存在"})
		return
	}
	if err != nil {
		h.logger.Error("查询库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}

	// 计算新数量
	newQty := currentQty
	switch req.AdjustType {
	case "in":
		newQty = currentQty + req.AdjustQty
	case "out":
		newQty = currentQty - req.AdjustQty
	case "adjustment":
		newQty = req.AdjustQty
	}

	if newQty < 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "库存不能为负数"})
		return
	}

	now := time.Now()

	// 更新库存
	_, err = h.db.Exec(`
		UPDATE inventory
		SET quantity = $1, available_qty = $1 - reserved_qty, updated_at = $2
		WHERE mpn = $3 AND warehouse = $4
	`, newQty, now, req.MPN, req.Warehouse)

	if err != nil {
		h.logger.Error("调整库存失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "调整失败"})
		return
	}

	// 记录调整历史（待实现）

	c.JSON(http.StatusOK, gin.H{
		"message":     "调整成功",
		"old_qty":    currentQty,
		"new_qty":    newQty,
		"adjust_qty": req.AdjustQty,
	})
}

// generateUUID 生成UUID
func generateUUID() string {
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
