# Chat CLI

🤖 一个基于OpenAI兼容API的命令行聊天工具，支持单次问答和交互模式。

## ✨ 特性

- 🔥 **单次问答模式** - 快速获取AI回答
- 💬 **交互聊天模式** - 持续对话，保持上下文
- ⚡ **流式输出** - 实时显示AI回复过程，如真人打字
- 🎨 **美观的终端输出** - 使用Rich库提供彩色和格式化输出
- ⚙️ **自定义系统提示词** - 定制AI行为和角色
- 🔧 **交互式配置向导** - 简单易用的API配置
- 🌐 **OpenAI兼容API支持** - 支持OpenAI、Claude、通义千问等多种AI服务
- 📦 **多种安装方式** - Poetry、pip、一键脚本
- 🧪 **完整测试覆盖** - 单元测试保证代码质量
- 🛠️ **开发友好** - 标准化项目结构和工具链

## 📋 系统要求

- Python 3.8.1+
- OpenAI兼容API密钥（OpenAI、Claude、通义千问等）

## 🚀 快速安装

### 方式一：一键安装脚本（推荐）

```bash
# Linux/macOS
chmod +x install.sh
./install.sh

# Windows
install.bat
```

### 方式二：使用 Poetry（开发推荐）

```bash
# 安装Poetry（如果还没有）
curl -sSL https://install.python-poetry.org | python3 -

# 克隆项目
git clone <repository-url>
cd chat-cli

# 安装依赖
poetry install

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件，添加你的 API Key
```

### 方式三：使用 pip

```bash
git clone <repository-url>
cd chat-cli

# 安装依赖
pip install -e .

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件，添加你的 API Key
```

## ⚙️ 配置

本工具支持多种环境变量配置方式，按优先级顺序：

### 1. 交互式配置（推荐）

使用内置的配置向导快速设置：

```bash
# 启动配置向导
chat-cli --config

# 或使用Poetry
poetry run chat-cli --config
```

配置向导将引导您：

1. 输入 API Key
2. 设置 API Base URL（可选）
3. 选择模型名称（可选）
4. 自动保存到 `~/.config/chat-cli/env`
5. 自动测试配置是否有效

### 2. 本地项目配置（优先级高）

在项目根目录创建 `.env` 文件：

```env
# OpenAI兼容 API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. 全局用户配置（优先级低）

在用户配置目录创建配置文件：`~/.config/chat-cli/env`

```env
# 全局 OpenAI兼容 API 配置
OPENAI_API_KEY=your_global_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### 配置说明

- **优先级**: 本地 `.env` 文件的设置会覆盖全局配置文件的设置
- **全局配置**: 适合在多个项目间共享相同的API配置
- **本地配置**: 适合为特定项目定制配置（如使用不同的模型）

### 常用API服务配置示例

#### OpenAI官方

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

#### 通义千问

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
```

#### 本地模型服务

```env
OPENAI_API_KEY=any-key-for-local
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_MODEL=llama-2-7b-chat
```

## 📖 使用说明

### 基本使用

```bash
# 单次问答
chat-cli "你好，请介绍一下自己"

# 使用Poetry运行（开发环境）
poetry run chat-cli "你好，请介绍一下自己"
```

### 交互模式

```bash
# 启动交互模式
chat-cli --interactive

# 或使用简写
chat-cli -i

# Poetry环境
poetry run chat-cli --interactive
```

在交互模式中：

- 输入消息进行对话
- 输入 `exit`、`quit`、`:q` 或 `q` 退出
- 对话会保持上下文

### 自定义系统提示词

```bash
# 单次对话使用自定义系统提示
chat-cli --system "你是一个专业的编程助手" "如何学习Python？"

# 交互模式使用自定义系统提示
chat-cli --interactive --system "你是一个友善的聊天机器人"
```

### 🔥 流式输出（默认启用）

默认启用流式输出！支持实时显示AI回复过程，就像真人在打字一样：

```bash
# 默认流式输出
chat-cli "请详细介绍一下Python编程语言"

# 交互模式默认流式输出
chat-cli --interactive

# 禁用流式输出（传统模式）
chat-cli --disable-stream "请介绍Python"

# 交互模式禁用流式输出
chat-cli --interactive --disable-stream

# 结合系统提示
chat-cli --system "你是编程助手" "解释一下递归算法"
```

**流式输出的优势：**

- ✨ 立即看到响应开始，无需等待
- 🎭 更自然的对话体验
- ⚡ 可随时中断长回复（Ctrl+C）
- 🧠 减少等待焦虑，提升用户体验

**适用场景：**

- 长文本生成（文章、代码解释）
- 实时编程助手
- 创意写作和头脑风暴
- 任何需要即时反馈的场景

### 配置管理

```bash
# 运行配置向导
chat-cli --config

# 查看帮助
chat-cli --help
```

## 🎯 使用场景

### 日常对话

```bash
chat-cli "今天天气怎么样？"
```

### 编程助手

```bash
chat-cli --system "你是Python专家" "解释一下装饰器的用法"
```

### 创意写作

```bash
chat-cli --system "你是创意写作助手" --interactive
```

### 学习辅导

```bash
chat-cli --system "你是耐心的老师，用简单的语言解释复杂概念" "什么是量子计算？"
```

## 🧪 开发

### 环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd chat-cli

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试
poetry run pytest tests/test_client.py

# 测试覆盖率
poetry run pytest --cov=src
```

### 代码质量

```bash
# 代码格式化
poetry run black src tests

# 代码检查
poetry run flake8 src tests

# 类型检查（如果配置）
poetry run mypy src
```

## 📁 项目结构

```txt
chat-cli/
├── src/                   # 源代码
│   ├── __init__.py
│   ├── main.py           # CLI入口
│   └── client.py         # API客户端
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_main.py
│   └── test_client.py
├── .env.example          # 环境变量示例
├── .gitignore           # Git忽略文件
├── Makefile             # 开发命令
├── pyproject.toml       # Poetry配置
├── setup.py             # setuptools配置
├── README.md            # 项目文档
├── install.sh           # Linux/macOS安装脚本
└── install.bat          # Windows安装脚本
```

## 🐛 故障排除

### 常见问题

**1. API Key错误**

```
错误: OPENAI_API_KEY environment variable is required
```

解决方案：运行 `chat-cli --config` 进行配置

**2. 网络连接问题**

```
API call failed: Connection error
```

解决方案：检查网络连接和API Base URL配置

**3. 模型不支持**

```
API call failed: Model not found
```

解决方案：检查模型名称是否正确，或联系API服务提供商

### 获取帮助

- 使用 `chat-cli --help` 查看命令帮助
- 检查 [OpenAI API文档](https://platform.openai.com/docs)
- 检查对应AI服务的API文档

## 📄 许可证

MIT License

## 🤝 贡献

欢迎贡献代码！请查看贡献指南。

## 🔗 相关链接

- [OpenAI API](https://platform.openai.com/)
- [通义千问 API](https://dashscope.aliyuncs.com/)
- [Poetry文档](https://python-poetry.org/docs/)
- [Click框架](https://click.palletsprojects.com/)
- [Rich库](https://rich.readthedocs.io/)
