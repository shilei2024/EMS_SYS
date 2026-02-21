#!/bin/bash

# ===================================
# 元器件商城系统 - 快速部署脚本
# ===================================
# 使用方法:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/EMS_SYS/main/scripts/deploy.sh | bash
#
# 国内服务器加速:
#   export USE_MIRROR=true && curl -fsSL https://get.daocloud.io/docker | sh
#   curl -fsSL https://cdn.jsdelivr.net/gh/YOUR_USERNAME/EMS_SYS@main/scripts/deploy.sh | bash
# ===================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 用户运行此脚本"
    exit 1
fi

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        log_info "检测到操作系统：$OS"
    else
        log_error "无法检测操作系统"
        exit 1
    fi
}

# 安装 Docker（支持国内镜像）
install_docker() {
    log_info "正在安装 Docker..."

    # 检测网络，如果访问 Docker 官方源失败则使用镜像
    if ! curl -s --connect-timeout 5 https://download.docker.com > /dev/null 2>&1; then
        log_info "检测到网络访问受限，使用国内镜像源..."
        USE_MIRROR=true
    fi

    if [ "$USE_MIRROR" = "true" ]; then
        # 使用 DaoCloud 镜像
        log_info "使用 DaoCloud 镜像安装 Docker..."
        curl -sSL https://get.daocloud.io/docker | sh
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt update
        apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

        # 添加 Docker GPG 密钥（使用阿里云镜像）
        curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

        # 添加 Docker 仓库
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        apt update
        apt install -y docker-ce docker-ce-cli containerd.io

    elif [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
        yum install -y yum-utils
        yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io
    fi

    systemctl start docker
    systemctl enable docker

    log_info "Docker 安装完成"
}

# 安装 Docker Compose（支持国内镜像）
install_docker_compose() {
    log_info "正在安装 Docker Compose..."

    COMPOSE_VERSION="v2.24.0"

    # 使用国内镜像下载
    if [ "$USE_MIRROR" = "true" ]; then
        curl -L "https://cdn.daocloud.io/docker-compose/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    else
        curl -L "https://ghproxy.com/https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    fi

    chmod +x /usr/local/bin/docker-compose

    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    log_info "Docker Compose 安装完成：$(docker-compose --version)"
}

# 配置 Docker 镜像加速
configure_docker_mirror() {
    log_info "正在配置 Docker 镜像加速..."

    mkdir -p /etc/docker

    cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

    systemctl daemon-reload
    systemctl restart docker

    log_info "Docker 镜像加速配置完成"
}

# 克隆项目代码
clone_repository() {
    log_info "正在克隆项目代码..."

    REPO_URL=${1:-"https://github.com/YOUR_USERNAME/EMS_SYS.git"}

    if [ -d "/opt/EMS_SYS" ]; then
        log_warn "/opt/EMS_SYS 目录已存在"
        read -p "是否删除并重新克隆？(y/n): " confirm
        if [ "$confirm" = "y" ]; then
            rm -rf /opt/EMS_SYS
        else
            return
        fi
    fi

    cd /opt
    git clone $REPO_URL

    log_info "项目代码克隆完成"
}

# 配置环境变量
configure_env() {
    log_info "正在配置环境变量..."

    cd /opt/EMS_SYS

    # 复制环境配置文件
    cp .env.example .env

    # 生成随机密钥
    JWT_SECRET=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    REDIS_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)
    POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

    # 更新环境变量
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET}/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=${REDIS_PASSWORD}/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PASSWORD}/" .env

    log_info "环境变量配置完成"
    log_warn "请保存以下密钥信息："
    echo "  JWT_SECRET: ${JWT_SECRET}"
    echo "  REDIS_PASSWORD: ${REDIS_PASSWORD}"
    echo "  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
}

# 启动服务
start_services() {
    log_info "正在启动服务..."

    cd /opt/EMS_SYS

    docker compose -f docker-compose.prod.yml pull
    docker compose -f docker-compose.prod.yml up -d

    log_info "服务启动完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态："

    cd /opt/EMS_SYS

    docker compose -f docker-compose.prod.yml ps

    echo ""
    log_info "访问地址："
    echo "  外部门户：http://$(curl -s ifconfig.me)"
    echo "  内部管理：http://$(curl -s ifconfig.me):3001"
    echo "  Grafana:   http://$(curl -s ifconfig.me):3003"
}

# 主函数
main() {
    echo "======================================"
    echo "  元器件商城系统 - 快速部署脚本"
    echo "======================================"
    echo ""

    detect_os
    install_docker
    install_docker_compose
    configure_docker_mirror
    clone_repository "$1"
    configure_env
    start_services
    show_status

    echo ""
    echo "======================================"
    echo "  部署完成！"
    echo "======================================"
    echo ""
    log_info "查看日志：cd /opt/EMS_SYS && docker compose logs -f"
    log_info "停止服务：docker compose -f docker-compose.prod.yml down"
    log_info "重启服务：docker compose -f docker-compose.prod.yml restart"
}

# 执行主函数
main "$@"
