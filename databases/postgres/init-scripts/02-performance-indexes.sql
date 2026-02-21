-- ===================================
-- PostgreSQL 性能优化索引
-- ===================================
-- 此脚本为电子元器件代理商增值系统创建必要的数据库索引
-- 执行：psql -U postgres -d component_agent -f 02-performance-indexes.sql

-- ===================================
-- 订单表索引 (orders)
-- ===================================

-- 复合索引：订单状态 + 创建时间（用于订单列表查询）
CREATE INDEX IF NOT EXISTS idx_orders_status_created_at
ON orders(status, created_at DESC);

-- 索引：客户名称查询
CREATE INDEX IF NOT EXISTS idx_orders_customer_name
ON orders(customer_name);

-- 索引：订单来源 ID
CREATE INDEX IF NOT EXISTS idx_orders_source_id
ON orders(source_id);

-- 复合索引：待审核订单查询
CREATE INDEX IF NOT EXISTS idx_orders_review_status
ON orders(status, reviewed_by, reviewed_at)
WHERE status = 'pending';

-- 索引：OCR 置信度查询（用于筛选需要人工审核的订单）
CREATE INDEX IF NOT EXISTS idx_orders_ocr_confidence
ON orders(ocr_confidence)
WHERE ocr_confidence < 0.9;

-- 日期索引：用于统计查询
CREATE INDEX IF NOT EXISTS idx_orders_created_at_date
ON orders((created_at::date));

-- ===================================
-- 订单明细表索引 (order_items)
-- ===================================

-- 复合索引：订单 ID + 行号（用于订单详情查询）
CREATE INDEX IF NOT EXISTS idx_order_items_order_id_line
ON order_items(order_id, line_number);

-- 索引：元器件型号查询
CREATE INDEX IF NOT EXISTS idx_order_items_manufacturer
ON order_items(manufacturer);

-- 索引：审核状态查询
CREATE INDEX IF NOT EXISTS idx_order_items_review_status
ON order_items(review_status, ocr_confidence);

-- ===================================
-- 用户表索引 (users)
-- ===================================

-- 复合索引：用户名 + 激活状态（用于登录查询）
CREATE INDEX IF NOT EXISTS idx_users_username_active
ON users(username, is_active);

-- 索引：锁定时间（用于查询锁定账户）
CREATE INDEX IF NOT EXISTS idx_users_locked_until
ON users(locked_until)
WHERE locked_until IS NOT NULL;

-- 索引：最后登录时间（用于用户活跃度分析）
CREATE INDEX IF NOT EXISTS idx_users_last_login
ON users(last_login_at DESC);

-- ===================================
-- 用户会话表索引 (user_sessions)
-- ===================================

-- 复合索引：用户 ID + 过期时间（用于会话清理）
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_expires
ON user_sessions(user_id, expires_at);

-- ===================================
-- 报销表索引 (expenses) - 财务服务
-- ===================================

-- 复合索引：用户 ID + 状态（用于报销列表查询）
CREATE INDEX IF NOT EXISTS idx_expenses_user_status
ON expenses(user_id, status);

-- 复合索引：状态 + 创建时间（用于审批列表）
CREATE INDEX IF NOT EXISTS idx_expenses_status_created
ON expenses(status, created_at DESC);

-- 索引：审批人查询
CREATE INDEX IF NOT EXISTS idx_expenses_approved_by
ON expenses(approved_by);

-- 索引：支付时间查询
CREATE INDEX IF NOT EXISTS idx_expenses_payment_at
ON expenses(payment_at);

-- ===================================
-- 工资表索引 (salaries) - 财务服务
-- ===================================

-- 索引：状态查询
CREATE INDEX IF NOT EXISTS idx_salaries_status
ON salaries(status);

-- 索引：支付时间查询
CREATE INDEX IF NOT EXISTS idx_salaries_paid_at
ON salaries(paid_at);

-- ===================================
-- 对账表索引 (reconciliations) - 财务服务
-- ===================================

-- 索引：客户名称查询
CREATE INDEX IF NOT EXISTS idx_reconciliations_customer
ON reconciliations(customer_name);

-- 索引：确认人查询
CREATE INDEX IF NOT EXISTS idx_reconciliations_confirmed
ON reconciliations(confirmed_by, confirmed_at);

-- 索引：支付日期查询
CREATE INDEX IF NOT EXISTS idx_reconciliations_payment_date
ON reconciliations(payment_date);

-- ===================================
-- 库存表索引 (inventory) - 库存服务
-- ===================================

-- 复合索引：型号 + 仓库（用于库存查询）
CREATE INDEX IF NOT EXISTS idx_inventory_mpn_warehouse
ON inventory(mpn, warehouse);

-- 索引：状态查询
CREATE INDEX IF NOT EXISTS idx_inventory_status
ON inventory(status);

-- 部分索引：低库存预警查询
CREATE INDEX IF NOT EXISTS idx_inventory_low_stock
ON inventory(quantity, reorder_point)
WHERE quantity <= reorder_point;

-- 索引：分类查询
CREATE INDEX IF NOT EXISTS idx_inventory_category
ON inventory(category);

-- ===================================
-- 库存预警表索引 (inventory_alerts) - 库存服务
-- ===================================

-- 复合索引：状态 + 预警类型
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_status_type
ON inventory_alerts(status, alert_type);

-- 索引：型号查询
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_mpn
ON inventory_alerts(mpn);

-- 索引：创建时间（用于最新预警查询）
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_created
ON inventory_alerts(created_at DESC);

-- ===================================
-- 库存预测表索引 (inventory_forecast) - 库存服务
-- ===================================

-- 复合索引：型号 + 仓库 + 周期
CREATE INDEX IF NOT EXISTS idx_inventory_forecast_mpn_period
ON inventory_forecast(mpn, warehouse, period, forecast_date);

-- ===================================
-- LLM 提供商表索引 (llm_providers) - 模型网关
-- ===================================

-- 复合索引：启用状态 + 优先级
CREATE INDEX IF NOT EXISTS idx_llm_providers_enabled
ON llm_providers(is_enabled, priority);

-- 索引：健康状态查询
CREATE INDEX IF NOT EXISTS idx_llm_providers_health
ON llm_providers(health_status, last_health_check);

-- ===================================
-- LLM 模型表索引 (llm_models) - 模型网关
-- ===================================

-- 复合索引：提供商 ID + 启用状态
CREATE INDEX IF NOT EXISTS idx_llm_models_enabled
ON llm_models(provider_id, is_enabled);

-- ===================================
-- 审计日志表索引 (audit_logs)
-- ===================================

-- 索引：用户 ID 查询
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id
ON audit_logs(user_id);

-- 复合索引：资源类型 + 资源 ID
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource
ON audit_logs(resource_type, resource_id);

-- 索引：创建时间（用于审计日志清理）
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
ON audit_logs(created_at DESC);

-- 索引：操作类型查询
CREATE INDEX IF NOT EXISTS idx_audit_logs_action
ON audit_logs(action);

-- ===================================
-- 物化视图：订单统计（可选，用于提升统计性能）
-- ===================================

-- 创建订单统计物化视图
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_order_stats AS
SELECT
    status,
    COUNT(*) as count,
    SUM(total_amount) as total_amount,
    AVG(ocr_confidence) as avg_confidence,
    DATE(created_at) as order_date
FROM orders
GROUP BY status, DATE(created_at);

-- 为物化视图创建索引
CREATE INDEX IF NOT EXISTS idx_mv_order_stats_status
ON mv_order_stats(status);

CREATE INDEX IF NOT EXISTS idx_mv_order_stats_date
ON mv_order_stats(order_date DESC);

-- 刷新物化视图的函数
CREATE OR REPLACE FUNCTION refresh_order_stats_view()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_order_stats;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（可选，自动刷新物化视图）
-- DROP TRIGGER IF EXISTS trg_refresh_order_stats ON orders;
-- CREATE TRIGGER trg_refresh_order_stats
-- AFTER INSERT OR UPDATE OR DELETE ON orders
-- EXECUTE FUNCTION refresh_order_stats_view();

-- ===================================
-- 索引创建完成后的分析
-- ===================================

-- 分析所有表以更新统计信息
ANALYZE orders;
ANALYZE order_items;
ANALYZE users;
ANALYZE user_sessions;
ANALYZE expenses;
ANALYZE salaries;
ANALYZE reconciliations;
ANALYZE inventory;
ANALYZE inventory_alerts;
ANALYZE inventory_forecast;
ANALYZE audit_logs;
ANALYZE llm_providers;
ANALYZE llm_models;

-- 显示索引使用情况统计
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;
