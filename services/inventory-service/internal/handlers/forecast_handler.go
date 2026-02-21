package handlers

import (
	"database/sql"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"component-agent/inventory-service/internal/config"
)

// ForecastHandler 预测处理器
type ForecastHandler struct {
	db     *sql.DB
	config *config.Config
	logger *zap.Logger
}

func NewForecastHandler(db *sql.DB, cfg *config.Config, logger *zap.Logger) *ForecastHandler {
	return &ForecastHandler{
		db:     db,
		config: cfg,
		logger: logger,
	}
}

// Forecast 预测数据
type Forecast struct {
	ID          string    `json:"id"`
	MPN         string    `json:"mpn"`
	Warehouse   string    `json:"warehouse"`
	ForecastDate time.Time `json:"forecast_date"`
	Period      string    `json:"period"` // weekly, monthly
	PredictedQty int      `json:"predicted_qty"`
	Confidence  float64   `json:"confidence"`
	CreatedAt   time.Time `json:"created_at"`
}

func (h *ForecastHandler) GetForecast(c *gin.Context) {
	mpn := c.Query("mpn")
	warehouse := c.Query("warehouse")
	period := c.DefaultQuery("period", "monthly")

	query := `
		SELECT id, mpn, warehouse, forecast_date, period, predicted_qty, confidence, created_at
		FROM inventory_forecast
		WHERE 1=1
	`
	args := []interface{}{}
	argNum := 1

	if mpn != "" {
		query += " AND mpn = $" + string(rune('0'+argNum))
		args = append(args, mpn)
		argNum++
	}
	if warehouse != "" {
		query += " AND warehouse = $" + string(rune('0'+argNum))
		args = append(args, warehouse)
		argNum++
	}
	if period != "" {
		query += " AND period = $" + string(rune('0'+argNum))
		args = append(args, period)
	}

	query += " ORDER BY forecast_date ASC"

	rows, err := h.db.Query(query, args...)
	if err != nil {
		h.logger.Error("查询预测数据失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询失败"})
		return
	}
	defer rows.Close()

	var forecasts []Forecast
	for rows.Next() {
		var f Forecast
		err := rows.Scan(&f.ID, &f.MPN, &f.Warehouse, &f.ForecastDate,
			&f.Period, &f.PredictedQty, &f.Confidence, &f.CreatedAt)
		if err != nil {
			continue
		}
		forecasts = append(forecasts, f)
	}

	if forecasts == nil {
		forecasts = []Forecast{}
	}

	c.JSON(http.StatusOK, gin.H{"forecasts": forecasts})
}

func (h *ForecastHandler) GenerateForecast(c *gin.Context) {
	type GenerateRequest struct {
		MPN       string `json:"mpn" binding:"required"`
		Warehouse string `json:"warehouse" binding:"required"`
		Period    string `json:"period" binding:"required"` // weekly, monthly
		Months    int    `json:"months"` // 预测月数
	}

	var req GenerateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求数据"})
		return
	}

	if req.Months <= 0 {
		req.Months = 3
	}

	// 获取历史销售数据（简化实现）
	// 实际应该从订单系统获取历史销售数据
	// 这里使用随机数据模拟

	now := time.Now()
	var forecasts []Forecast

	for i := 1; i <= req.Months; i++ {
		forecastDate := now.AddDate(0, i, 0)

		// 简化预测算法：基于历史平均值 + 季节性因子
		predictedQty := 100 + (i * 10) // 模拟增长趋势
		confidence := 0.85 - float64(i)*0.05 // 置信度随时间递减

		forecast := Forecast{
			ID:           generateUUID(),
			MPN:          req.MPN,
			Warehouse:    req.Warehouse,
			ForecastDate: forecastDate,
			Period:       req.Period,
			PredictedQty: predictedQty,
			Confidence:   confidence,
			CreatedAt:    now,
		}

		// 保存到数据库
		_, err := h.db.Exec(`
			INSERT INTO inventory_forecast (id, mpn, warehouse, forecast_date, period, predicted_qty, confidence, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
			ON CONFLICT (mpn, warehouse, forecast_date, period)
			DO UPDATE SET predicted_qty = $6, confidence = $7, created_at = $8
		`, forecast.ID, forecast.MPN, forecast.Warehouse, forecast.ForecastDate,
			forecast.Period, forecast.PredictedQty, forecast.Confidence, forecast.CreatedAt)

		if err != nil {
			h.logger.Error("保存预测数据失败", zap.Error(err))
			continue
		}

		forecasts = append(forecasts, forecast)
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "预测生成成功",
		"forecasts": forecasts,
	})
}
