#!/bin/bash

# ===================================
# 快速安装 Docker 和 Docker Compose
# 专用于国内服务器优化
# ===================================
# 使用方法:
#   curl -fsSL https://cdn.daocloud.io/docker | bash
#   或
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/EMS_SYS/main/scripts/install-docker.sh | bash
# ===================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()    { echo -e "${BLUE}[STEP]${NC} $1"; }

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 用户运行此脚本（sudo bash $0）"
    exit 1
fi

log_step "=========================================="
log_step "  开始安装 Docker 和 Docker Compose"
log_step "=========================================="

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        log_info "检测到操作系统：$OS"
    else
        OS="unknown"
        log_warn "无法检测操作系统，尝试通用安装方法"
    fi
}

# 停止并移除旧的 Docker 版本
remove_old_docker() {
    log_info "检查并移除旧版本 Docker..."

    OLD_VERSIONS="docker docker-engine docker.io containerd runc"

    if command -v apt &> /dev/null; then
        for pkg in $OLD_VERSIONS; do
            if dpkg -l | grep -q "^ii  $pkg "; then
                log_info "移除旧版本：$pkg"
                apt-get remove -y "$pkg" || true
            fi
        done
    elif command -v yum &> /dev/null; then
        for pkg in $OLD_VERSIONS; do
            if rpm -q "$pkg" &> /dev/null; then
                log_info "移除旧版本：$pkg"
                yum remove -y "$pkg" || true
            fi
        done
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."

    if command -v apt &> /dev/null; then
        apt-get update
        apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release \
            software-properties-common
    elif command -v yum &> /dev/null; then
        yum install -y \
            yum-utils \
            device-mapper-persistent-data \
            lvm2
    fi
}

# 安装 Docker（使用国内镜像）
install_docker() {
    log_info "使用国内镜像安装 Docker..."

    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # 添加 GPG 密钥（使用阿里云）
        curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

        # 添加仓库
        echo \
          "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        # 安装
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io

    elif [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
        # 使用阿里云镜像源
        yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io

    else
        # 通用安装方法
        log_warn "使用通用安装方法..."
        curl -sSL https://get.daocloud.io/docker | sh
        return
    fi

    # 启动 Docker
    systemctl start docker
    systemctl enable docker

    log_info "Docker 安装完成：$(docker --version)"
}

# 安装 Docker Compose
install_docker_compose() {
    log_info "安装 Docker Compose..."

    COMPOSE_VERSION="v2.24.0"

    # 使用 DaoCloud 镜像下载
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -L "https://cdn.daocloud.io/docker-compose/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose

    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

    # 创建软链接（兼容旧版）
    ln -sf /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

    log_info "Docker Compose 安装完成：$(docker compose version)"
}

# 配置 Docker 镜像加速
configure_docker_mirror() {
    log_info "配置 Docker 镜像加速..."

    mkdir -p /etc/docker

    cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://dhub.kubesre.xyz"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

    # 重启 Docker
    systemctl daemon-reload
    systemctl restart docker

    log_info "Docker 镜像加速配置完成"
}

# 验证安装
verify_installation() {
    log_step "验证安装..."

    echo ""
    log_info "Docker 版本：$(docker --version)"
    log_info "Docker Compose 版本：$(docker-compose --version)"

    # 测试 Docker
    if docker run --rm hello-world &> /dev/null; then
        log_info "Docker 运行正常"
    else
        log_warn "Docker 测试容器运行失败，但可能不影响正常使用"
    fi

    echo ""
    log_step "=========================================="
    log_step "  安装完成！"
    log_step "=========================================="
    echo ""
    log_info "常用命令:"
    echo "  docker --version           # 查看 Docker 版本"
    echo "  docker-compose --version   # 查看 Docker Compose 版本"
    echo "  docker ps                  # 查看运行中的容器"
    echo "  docker images              # 查看镜像列表"
    echo ""
}

# 主函数
main() {
    detect_os
    remove_old_docker
    install_dependencies
    install_docker
    install_docker_compose
    configure_docker_mirror
    verify_installation
}

# 执行
main "$@"
