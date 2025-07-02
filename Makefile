# Chat CLI Makefile
# 提供便捷的开发和部署命令

.PHONY: help install install-dev build test clean run lint format check-format publish dev-setup

# 默认目标
help:
	@echo "Chat CLI 项目管理命令"
	@echo "====================="
	@echo ""
	@echo "开发命令:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  dev-setup    - 完整开发环境设置"
	@echo "  run          - 运行CLI工具"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 格式化代码"
	@echo "  check-format - 检查代码格式"
	@echo ""
	@echo "构建命令:"
	@echo "  build        - 构建包"
	@echo "  clean        - 清理构建文件"
	@echo "  publish      - 发布到PyPI"
	@echo ""
	@echo "示例:"
	@echo "  make install"
	@echo "  make test"
	@echo "  make run ARGS='你好，请介绍一下自己'"
	@echo "  make run ARGS='--interactive'"

# 安装项目依赖
install:
	@echo "📦 安装项目依赖..."
	poetry install --only=main

# 安装开发依赖
install-dev:
	@echo "📦 安装开发依赖..."
	poetry install

# 完整开发环境设置
dev-setup: install-dev
	@echo "⚙️  设置开发环境..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 已创建.env配置文件"; \
		echo "⚠️  请编辑.env文件，添加你的 OpenAI 兼容 API Key"; \
	fi
	@echo "✅ 开发环境设置完成"

# 运行CLI工具
run:
	@echo "🚀 运行Chat CLI..."
	poetry run chat-cli $(ARGS)

# 运行测试
test:
	@echo "🧪 运行测试..."
	poetry run pytest tests/ -v --cov=chat_cli --cov-report=term-missing

# 代码检查
lint:
	@echo "🔍 代码检查..."
	poetry run flake8 chat_cli tests
	@echo "✅ 代码检查通过"

# 格式化代码
format:
	@echo "✨ 格式化代码..."
	poetry run black chat_cli tests
	@echo "✅ 代码格式化完成"

# 检查代码格式
check-format:
	@echo "🔍 检查代码格式..."
	poetry run black --check chat_cli tests

# 构建包
build: clean
	@echo "🔨 构建包..."
	poetry build
	@echo "✅ 构建完成，输出在dist/目录"

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成"

# 发布到PyPI
publish: build
	@echo "📤 发布到PyPI..."
	poetry publish
	@echo "✅ 发布完成"

# 交互模式
interactive:
	@echo "🤖 启动交互模式..."
	poetry run chat-cli --interactive

# 显示项目信息
info:
	@echo "📊 项目信息:"
	@echo "============"
	poetry show --tree
	@echo ""
	@echo "📝 项目版本:"
	poetry version
	@echo ""
	@echo "🐍 Python版本:"
	poetry run python --version
	@echo ""
	@echo "📦 已安装包:"
	poetry show

# 更新依赖
update:
	@echo "🔄 更新依赖..."
	poetry update
	@echo "✅ 依赖更新完成"

# 安全检查
security:
	@echo "🔒 安全检查..."
	poetry run pip-audit
	@echo "✅ 安全检查完成"

# 代码覆盖率报告
coverage:
	@echo "📊 生成覆盖率报告..."
	poetry run pytest tests/ --cov=chat_cli --cov-report=html
	@echo "✅ 覆盖率报告生成完成，查看htmlcov/index.html"

# 一键部署开发环境
deploy-dev: dev-setup test
	@echo "🚀 开发环境部署完成"
	@echo "现在可以使用: make run ARGS='你好'"

# 一键生产构建
deploy-prod: clean test build
	@echo "🏗️ 生产构建完成"
	@echo "包文件在dist/目录中"
