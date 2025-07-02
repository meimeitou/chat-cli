#!/usr/bin/env python3
"""
Chat CLI 项目安装脚本
使用setuptools标准打包
"""

import sys
import subprocess
import shutil
import glob
from pathlib import Path
from setuptools import setup, find_packages

# 读取项目信息
project_root = Path(__file__).parent

def read_file(filename):
    """读取文件内容"""
    file_path = project_root / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def get_requirements():
    """从pyproject.toml获取依赖信息，如果失败则使用默认依赖"""
    try:
        import tomli
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'rb') as f:
                data = tomli.load(f)
                deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
                # 过滤掉python版本要求，转换为setuptools格式
                requirements = []
                for name, version in deps.items():
                    if name != 'python':
                        if isinstance(version, str):
                            if version.startswith('^'):
                                version = '>=' + version[1:]
                            requirements.append(f"{name}{version}")
                        else:
                            requirements.append(name)
                return requirements
    except ImportError:
        pass
    
    # 回退到默认依赖
    return [
        "openai>=1.0.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
    ]

def get_version():
    """从pyproject.toml获取版本信息，如果失败则使用默认版本"""
    try:
        import tomli
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'rb') as f:
                data = tomli.load(f)
                return data.get('tool', {}).get('poetry', {}).get('version', '0.1.0')
    except ImportError:
        pass
    
    return "0.1.0"

def setup_environment():
    """设置环境文件"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("📝 已创建.env配置文件")
        print("⚠️  请编辑.env文件，添加你的 OpenAI 兼容 API Key")

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)
        print("✅ 所有测试通过")
        return True
    except subprocess.CalledProcessError:
        print("❌ 测试失败")
        return False

def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    patterns = ['build', 'dist', '*.egg-info', '__pycache__', '.pytest_cache']
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            path_obj = Path(path)
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
    print("✅ 清理完成")

def print_help():
    """打印帮助信息"""
    print("""
Chat CLI 安装器 (setuptools版本)

用法:
    python setup.py [command]

自定义命令:
    test            运行测试
    clean           清理构建文件
    --help, -h      显示此帮助信息

Setuptools标准命令:
    install         标准安装到site-packages
    develop         开发模式安装 (可编辑)
    build           构建包
    sdist           构建源码包
    bdist_wheel     构建wheel包

推荐使用pip安装:
    pip install .                   # 标准安装
    pip install -e .                # 开发模式安装 (推荐)
    pip install -e .[dev]           # 安装包含开发依赖

构建和分发:
    python setup.py sdist          # 构建源码包
    python setup.py bdist_wheel    # 构建wheel包
    python setup.py build          # 构建但不安装

示例:
    pip install -e .                # 推荐的开发安装方式
    python setup.py develop        # 开发安装 (setuptools方式)
    python setup.py test           # 运行测试
    python setup.py clean          # 清理构建文件
""")

def print_usage():
    """显示使用说明"""
    print("\n" + "="*50)
    print("🚀 Chat CLI 安装完成!")
    print("="*50)
    print("\n📖 使用说明:")
    print("1. 编辑.env文件，添加你的 OpenAI 兼容 API Key:")
    print("   OPENAI_API_KEY=your_api_key_here")
    print("\n2. 使用命令:")
    print("   chat-cli '你好，请介绍一下自己'")
    print("   chat-cli --interactive")
    print("\n3. 获取更多帮助:")
    print("   chat-cli --help")
    print("\n4. 开发模式:")
    print("   pip install -e .         # 可编辑安装")
    print("   pip install -e .[dev]    # 包含开发依赖")
    print("\n🔗 项目地址: https://github.com/your-username/chat-cli")

def main():
    """主函数 - 处理命令行参数"""
    # 处理自定义命令
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ["--help", "-h"]:
            print_help()
            return
        
        elif command == "test":
            # 运行测试
            if run_tests():
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif command == "clean":
            # 清理构建文件
            clean_build()
            return
        
        elif command in ["install", "develop"]:
            # 在setuptools安装之前设置环境
            setup_environment()
    
    # 执行标准setuptools安装
    setup(
        name="chat-cli",
        version=get_version(),
        description="A CLI tool for chatting with OpenAI compatible AI services",
        long_description=read_file("README.md"),
        long_description_content_type="text/markdown",
        author="Your Name",
        author_email="your.email@example.com",
        url="https://github.com/your-username/chat-cli",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.8.1",
        install_requires=get_requirements(),
        extras_require={
            'dev': [
                'pytest>=7.4.0',
                'black>=23.0.0',
                'flake8>=6.0.0',
                'pytest-cov>=4.0.0',
                'tomli>=2.0.0',
            ]
        },
        entry_points={
            'console_scripts': [
                'chat-cli=src.main:cli',
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Communications :: Chat",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ],
        keywords="cli chat ai openai api chatbot",
        project_urls={
            "Bug Reports": "https://github.com/your-username/chat-cli/issues",
            "Source": "https://github.com/your-username/chat-cli",
            "Documentation": "https://github.com/your-username/chat-cli#readme",
        },
    )
    
    # 安装后设置
    if len(sys.argv) > 1 and sys.argv[1] in ["install", "develop"]:
        print_usage()

if __name__ == "__main__":
    main()
