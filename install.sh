#!/bin/bash

# Chat CLI 快速安装脚本
# 自动检测环境并安装

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🤖 Chat CLI 快速安装脚本"
    echo "========================"
    echo -e "${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python版本
check_python() {
    print_info "检查Python环境..."
    
    if ! command_exists python3; then
        print_error "Python3未安装，请先安装Python 3.8.1++"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    print_success "Python版本: $python_version"
    
    # 检查版本是否满足要求
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8, 1) else 1)"; then
        print_error "需要Python 3.8.1或更高版本，当前版本: $python_version"
        exit 1
    fi
}

# 检查并安装Poetry
setup_poetry() {
    if command_exists poetry; then
        print_success "Poetry已安装"
        poetry_version=$(poetry --version)
        print_info "Poetry版本: $poetry_version"
    else
        print_info "Poetry未安装，正在安装..."
        curl -sSL https://install.python-poetry.org | python3 -
        
        # 添加Poetry到PATH
        export PATH="$HOME/.local/bin:$PATH"
        
        if command_exists poetry; then
            print_success "Poetry安装成功"
        else
            print_warning "Poetry安装完成，但未添加到PATH"
            print_info "请手动添加 $HOME/.local/bin 到PATH环境变量"
            print_info "或重新打开终端"
        fi
    fi
}

# 安装项目依赖
install_dependencies() {
    print_info "安装项目依赖..."
    poetry install
    print_success "依赖安装完成"
}

# 设置环境配置
setup_environment() {
    print_info "设置环境配置..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "已创建.env配置文件"
        print_warning "请编辑.env文件，添加你的 OpenAI 兼容 API Key"
    else
        print_info ".env文件已存在"
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试验证安装..."
    
    if poetry run pytest tests/ -v; then
        print_success "所有测试通过"
    else
        print_warning "部分测试失败，但不影响基本使用"
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${GREEN}"
    echo "🎉 安装完成！"
    echo "============"
    echo -e "${NC}"
    
    echo "📖 使用方法:"
    echo "1. 配置API Key:"
    echo "   编辑.env文件，将OPENAI_API_KEY设置为你的API Key"
    echo ""
    echo "2. 基本使用:"
    echo "   poetry run chat-cli '你好，请介绍一下自己'"
    echo "   poetry run chat-cli --interactive"
    echo ""
    echo "3. 使用Makefile (推荐):"
    echo "   make run ARGS='你好'"
    echo "   make interactive"
    echo "   make test"
    echo ""
    echo "4. 获取帮助:"
    echo "   poetry run chat-cli --help"
    echo "   make help"
    echo ""
    echo "🔗 更多信息请查看README.md"
}

# 主安装流程
main() {
    print_header
    
    # 检查是否在正确的目录
    if [ ! -f "pyproject.toml" ]; then
        print_error "请在项目根目录下运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    check_python
    setup_poetry
    install_dependencies
    setup_environment
    
    # 可选：运行测试
    if [ "$1" != "--skip-tests" ]; then
        run_tests
    fi
    
    show_usage
}

# 处理命令行参数
case "${1:-}" in
    --help|-h)
        echo "Chat CLI 快速安装脚本"
        echo ""
        echo "用法:"
        echo "  $0                安装项目"
        echo "  $0 --skip-tests   安装项目但跳过测试"
        echo "  $0 --help         显示此帮助"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
