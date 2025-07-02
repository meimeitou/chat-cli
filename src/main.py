"""Main CLI module (moved to src)."""

import click
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from .client import OpenAIClient

console = Console()

@click.command()
@click.argument('message', required=False)
@click.option('--interactive', '-i', is_flag=True, help='启动交互模式')
@click.option('--system', '-s', help='系统提示词')
@click.option('--config', 'show_config', is_flag=True, help='启动配置向导')
@click.version_option(version='0.1.0')
def cli(message, interactive, system, show_config):
    """
    OpenAI兼容 AI 命令行聊天工具
    
    使用示例:
    
    chat-cli "你好，请介绍一下自己"
    
    chat-cli --interactive  # 交互模式
    
    chat-cli --config  # 配置API密钥
    """
    # 如果要配置，运行配置向导
    if show_config:
        run_config_command()
        return
    
    # 执行聊天功能
    run_chat_command(message, interactive, system)


def run_config_command():
    """运行配置向导"""
    console.print(Panel("🔧 OpenAI兼容 API 配置向导", style="bold blue"))
    
    # 检查现有配置
    config_dir = Path.home() / ".config" / "chat-cli"
    config_file = config_dir / "env"
    
    current_config = {}
    if config_file.exists():
        console.print(f"[yellow]发现现有配置文件: {config_file}[/yellow]")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        current_config[key.strip()] = value.strip()
        except Exception as e:
            console.print(f"[red]读取现有配置失败: {e}[/red]")
    
    # 交互式收集配置信息
    config_items = [
        {
            'key': 'OPENAI_API_KEY',
            'prompt': 'OpenAI API Key',
            'required': True,
            'help': '获取方式:\n  - OpenAI: https://platform.openai.com/api-keys\n  - DeepSeek: https://platform.deepseek.com/\n  - 其他兼容服务的API密钥'
        },
        {
            'key': 'OPENAI_BASE_URL',
            'prompt': 'API Base URL',
            'default': 'https://api.openai.com/v1',
            'required': False,
            'help': '常用服务:\n  - OpenAI官方: https://api.openai.com/v1\n  - DeepSeek: https://api.deepseek.com\n  - 本地服务: http://localhost:8000/v1'
        },
        {
            'key': 'OPENAI_MODEL',
            'prompt': 'Model Name',
            'default': 'gpt-3.5-turbo',
            'required': False,
            'help': '常用模型:\n  - OpenAI: gpt-3.5-turbo, gpt-4, gpt-4-turbo\n  - DeepSeek: deepseek-chat\n  - 其他: 根据服务商文档'
        }
    ]
    
    new_config = {}
    
    for item in config_items:
        key = item['key']
        prompt_text = item['prompt']
        current_value = current_config.get(key, '')
        default_value = item.get('default', '')
        
        # 构建提示信息
        if current_value:
            if 'API_KEY' in key:
                # 隐藏API Key显示
                display_value = current_value[:4] + "..." + current_value[-4:] if len(current_value) > 8 else current_value
                prompt_text += f" (当前: {display_value})"
            else:
                prompt_text += f" (当前: {current_value})"
        elif default_value:
            prompt_text += f" (默认: {default_value})"
        
        if item.get('help'):
            console.print(f"[dim]{item['help']}[/dim]")
        
        # 获取用户输入
        while True:
            try:
                if current_value:
                    # 有现有值时，允许用户回车保持不变
                    value = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]", default="", show_default=False)
                    if not value:  # 用户直接回车，保持现有值
                        value = current_value
                else:
                    # 没有现有值时
                    value = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]", default=default_value)
                
                if item['required'] and not value:
                    console.print("[red]此配置项为必填项，请提供有效值[/red]")
                    continue
                
                new_config[key] = value
                break
            except KeyboardInterrupt:
                console.print("\n[yellow]配置已取消[/yellow]")
                sys.exit(0)
    
    # 显示配置总结
    console.print("\n" + "="*50)
    console.print("[bold green]配置总结:[/bold green]")
    for key, value in new_config.items():
        if 'API_KEY' in key:
            display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else value
            console.print(f"  {key}: {display_value}")
        else:
            console.print(f"  {key}: {value}")
    
    # 确认保存
    if not Confirm.ask("\n[bold yellow]确认保存配置?[/bold yellow]"):
        console.print("[yellow]配置已取消[/yellow]")
        return
    
    # 创建配置目录
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入配置文件
    try:
        config_content = f"""# OpenAI兼容 API 配置
# 此文件由 chat-cli --config 命令生成
# 配置时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OPENAI_API_KEY={new_config['OPENAI_API_KEY']}
OPENAI_BASE_URL={new_config['OPENAI_BASE_URL']}
OPENAI_MODEL={new_config['OPENAI_MODEL']}
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        console.print(f"[bold green]✅ 配置已保存到: {config_file}[/bold green]")
        console.print("[dim]提示: 现在您可以使用 chat-cli 开始聊天了！[/dim]")
        
        # 测试配置
        console.print("\n[bold cyan]🧪 测试配置...[/bold cyan]")
        try:
            # 重新加载环境变量
            from .client import load_env_files
            load_env_files()
            
            # 尝试初始化客户端
            client = OpenAIClient()
            console.print("[bold green]✅ 配置测试成功！[/bold green]")
        except Exception as e:
            console.print(f"[red]❌ 配置测试失败: {e}[/red]")
            console.print("[yellow]请检查API Key和Base URL是否正确[/yellow]")
    
    except Exception as e:
        console.print(f"[red]保存配置失败: {e}[/red]")
        sys.exit(1)


def run_chat_command(message, interactive, system):
    """执行聊天命令的核心逻辑"""
    try:
        client = OpenAIClient()
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        console.print("[yellow]请设置 OPENAI_API_KEY 环境变量[/yellow]")
        console.print("请使用 'chat-cli --config' 命令进行配置")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]初始化失败: {e}[/red]")
        sys.exit(1)
    
    if interactive:
        run_interactive_mode(client, system)
    elif message:
        run_single_message(client, message, system)
    else:
        console.print("请提供消息或使用 --interactive 模式")
        console.print("使用 --help 查看帮助信息")


def run_single_message(client: OpenAIClient, message: str, system_prompt: str = None):
    response = client.chat(message, system_prompt)
    console.print(Panel(Text(response, style="bold"), title="🤖 AI Assistant"))

def run_interactive_mode(client: OpenAIClient, system_prompt: str = None):
    console.print(Panel("进入交互模式，输入 'exit' 退出。", title="🤖 AI Assistant"))
    history = []
    if system_prompt:
        history.append({"role": "system", "content": system_prompt})
    else:
        history.append({"role": "system", "content": "You are a helpful assistant"})
    while True:
        user_input = Prompt.ask("[bold green]你[/bold green]")
        if user_input.strip().lower() in ["exit", "quit", ":q", "q"]:
            console.print("[yellow]已退出交互模式[/yellow]")
            break
        history.append({"role": "user", "content": user_input})
        try:
            response = client.chat_with_history(history)
            history.append({"role": "assistant", "content": response})
            console.print(Panel(Text(response, style="bold"), title="🤖 AI Assistant"))
        except Exception as e:
            console.print(f"[red]API调用失败: {e}[/red]")
