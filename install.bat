@echo off
REM Chat CLI Windows 安装脚本

echo 🤖 Chat CLI Windows 安装脚本
echo ============================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8.1+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

REM 检查是否在正确目录
if not exist "pyproject.toml" (
    echo ❌ 请在项目根目录下运行此脚本
    pause
    exit /b 1
)

REM 检查Poetry是否安装
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Poetry未安装，正在安装...
    curl -sSL https://install.python-poetry.org | python -
    if errorlevel 1 (
        echo ❌ Poetry安装失败
        echo 请手动安装Poetry: https://python-poetry.org/docs/#installation
        pause
        exit /b 1
    )
    echo ✅ Poetry安装成功
) else (
    echo ✅ Poetry已安装
    poetry --version
)

REM 安装依赖
echo.
echo 📦 安装项目依赖...
poetry install
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 设置环境文件
if not exist ".env" (
    copy ".env.example" ".env"
    echo ✅ 已创建.env配置文件
    echo ⚠️  请编辑.env文件，添加你的 OpenAI 兼容 API Key
) else (
    echo ℹ️  .env文件已存在
)

REM 运行测试
echo.
echo 🧪 运行测试...
poetry run pytest tests/ -v
if errorlevel 1 (
    echo ⚠️  部分测试失败，但不影响基本使用
) else (
    echo ✅ 所有测试通过
)

REM 显示使用说明
echo.
echo 🎉 安装完成！
echo ============
echo.
echo 📖 使用方法:
echo 1. 配置API Key:
echo    编辑.env文件，将OPENAI_API_KEY设置为你的API Key
echo.
echo 2. 基本使用:
echo    poetry run chat-cli "你好，请介绍一下自己"
echo    poetry run chat-cli --interactive
echo.
echo 3. 获取帮助:
echo    poetry run chat-cli --help
echo.
echo 🔗 更多信息请查看README.md
echo.
pause
