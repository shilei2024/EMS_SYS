-- 电子元器件代理商增值系统 - 核心表结构初始化
-- Phase 1: 基础架构与核心服务
-- 创建时间: 2026-02-21

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== 用户与权限模块 ====================

-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '{}'::jsonb,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    department VARCHAR(50),
    role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户会话表
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_sessions_user_id (user_id),
    INDEX idx_user_sessions_expires_at (expires_at)
);

-- ==================== 模型配置模块 ====================

-- 大模型提供商配置表
CREATE TABLE llm_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    provider_type VARCHAR(20) NOT NULL, -- 'openai', 'anthropic', 'azure', 'local'
    api_base_url VARCHAR(255),
    api_key_encrypted TEXT, -- 加密存储
    default_model VARCHAR(100),
    priority INTEGER DEFAULT 1, -- 优先级，数字越小优先级越高
    is_enabled BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    cost_per_token DECIMAL(10,8),
    health_check_url VARCHAR(255),
    last_health_check TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown', -- 'healthy', 'unhealthy', 'degraded'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型配置表
CREATE TABLE llm_models (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES llm_providers(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    context_length INTEGER,
    max_tokens INTEGER,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    is_default BOOLEAN DEFAULT FALSE,
    is_enabled BOOLEAN DEFAULT TRUE,
    capabilities JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, model_name)
);

-- ==================== 订单模块 ====================

-- 订单源配置表
CREATE TABLE order_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(20) NOT NULL, -- 'api', 'imap', 'file', 'rpa', 'manual'
    config JSONB NOT NULL, -- 源配置信息
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单主表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) NOT NULL UNIQUE,
    source_id INTEGER REFERENCES order_sources(id) ON DELETE SET NULL,
    customer_name VARCHAR(200),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(20),
    total_amount DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'CNY',
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'review_needed', 'approved', 'rejected', 'completed'
    priority VARCHAR(10) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    ocr_confidence DECIMAL(5,4), -- OCR置信度
    ocr_raw_text TEXT, -- OCR原始文本
    ocr_structured_data JSONB, -- OCR结构化数据
    review_notes TEXT, -- 审核备注
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at)
);

-- 订单明细表
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    mpn VARCHAR(100), -- 制造商零件号
    manufacturer VARCHAR(100),
    description TEXT,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(15,4),
    total_price DECIMAL(15,2),
    ocr_confidence DECIMAL(5,4), -- 该行OCR置信度
    review_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'corrected', 'needs_review'
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_id, line_number),
    INDEX idx_order_items_mpn (mpn)
);

-- ==================== 审计日志模块 ====================

-- 审计日志表
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_resource (resource_type, resource_id),
    INDEX idx_audit_logs_created_at (created_at)
);

-- ==================== 系统配置模块 ====================

-- 系统配置表
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 初始化数据 ====================

-- 插入系统角色
INSERT INTO roles (name, description, permissions, is_system_role) VALUES
('超级管理员', '系统最高权限管理员', '{"*": "*"}', TRUE),
('订单管理员', '负责订单审核和管理', '{"orders": ["read", "update", "review"], "users": ["read"]}', FALSE),
('FAE工程师', '技术支持工程师', '{"components": ["read", "create", "update"], "datasheets": ["read", "upload"]}', FALSE),
('财务专员', '负责财务相关操作', '{"finance": ["read", "create", "update"], "orders": ["read"]}', FALSE),
('库存管理员', '负责库存管理', '{"inventory": ["read", "create", "update", "delete"], "orders": ["read"]}', FALSE),
('普通用户', '基础权限用户', '{"orders": ["read", "create"], "profile": ["read", "update"]}', FALSE)
ON CONFLICT (name) DO NOTHING;

-- 插入默认管理员用户 (密码: Admin@12345)
INSERT INTO users (username, email, password_hash, full_name, role_id, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd5L.DkQuzH5JJigP4UQYQzYtB6W6cJ7tZc6W3JO', '系统管理员',
 (SELECT id FROM roles WHERE name = '超级管理员'), TRUE)
ON CONFLICT (username) DO NOTHING;

-- 插入默认模型提供商配置 (API密钥需要实际部署时配置)
INSERT INTO llm_providers (name, provider_type, priority, is_enabled) VALUES
('openai_default', 'openai', 1, TRUE),
('anthropic_backup', 'anthropic', 2, TRUE),
('local_fallback', 'local', 3, TRUE)
ON CONFLICT (name) DO NOTHING;

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES
('system.name', '"电子元器件代理商增值系统"', '系统名称'),
('system.version', '"1.0.0"', '系统版本'),
('ocr.min_confidence', '0.75', 'OCR最小置信度阈值'),
('order.auto_approve_threshold', '0.9', '订单自动审核阈值'),
('security.login_attempts_limit', '5', '登录尝试次数限制'),
('security.session_timeout_hours', '8', '会话超时时间(小时)')
ON CONFLICT (config_key) DO NOTHING;

-- ==================== 创建更新触发器函数 ====================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为用户表创建触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为角色表创建触发器
DROP TRIGGER IF EXISTS update_roles_updated_at ON roles;
CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为订单表创建触发器
DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为订单明细表创建触发器
DROP TRIGGER IF EXISTS update_order_items_updated_at ON order_items;
CREATE TRIGGER update_order_items_updated_at
    BEFORE UPDATE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为系统配置表创建触发器
DROP TRIGGER IF EXISTS update_system_configs_updated_at ON system_configs;
CREATE TRIGGER update_system_configs_updated_at
    BEFORE UPDATE ON system_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==================== 创建索引优化查询性能 ====================

-- 用户查询优化
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
CREATE INDEX idx_users_role_active ON users(role_id, is_active);

-- 订单查询优化
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
CREATE INDEX idx_orders_status_priority ON orders(status, priority);

-- 审计日志查询优化
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- 打印初始化完成信息
SELECT '数据库核心表结构初始化完成' AS message;