"""Main CLI module (moved to src)."""

import click
import sys
import os
import platform
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.markdown import Markdown
from .client import OpenAIClient

console = Console()

def is_terminal_compatible():
    """检测终端是否兼容复杂渲染"""
    # 检查终端类型
    term = os.getenv('TERM', '').lower()
    term_program = os.getenv('TERM_PROGRAM', '').lower()
    
    # VS Code 终端（包括远程开发）支持复杂渲染
    if term_program == 'vscode':
        return True
    
    # 其他现代终端也支持复杂渲染
    modern_terminals = [
        'wezterm',
        'alacritty',
        'kitty',
        'windows terminal',
        'gnome-terminal',
        'konsole',
        'terminal.app',  # macOS Terminal 实际上也支持基本的复杂渲染
    ]
    
    if term_program in modern_terminals:
        return True
        # 检查是否在SSH连接中
    if os.getenv('SSH_CLIENT') or os.getenv('SSH_TTY'):
        return False
    # 检查 TERM 环境变量中的现代终端特征
    if any(modern_term in term for modern_term in ['xterm-256color', 'screen-256color', 'tmux-256color']):
        return True
    
    # 已知可能有问题的终端
    problematic_terms = [
        'screen',  # 基本的 screen 环境
        'linux',   # 基本的 Linux 控制台
        'dumb',    # 哑终端
    ]
    
    # 检查是否在问题终端中
    if term in problematic_terms:
        return False
    
    # 默认情况下，假设现代终端都支持复杂渲染
    # 除非明确检测到不支持的环境
    return True

def get_config_dir():
    """获取跨平台配置目录"""
    if platform.system() == "Windows":
        # Windows: 使用 APPDATA 目录
        appdata = os.getenv('APPDATA')
        if appdata:
            return Path(appdata) / "chat-cli"
        else:
            # 回退到用户目录
            return Path.home() / "AppData" / "Roaming" / "chat-cli"
    elif platform.system() == "Darwin":
        # macOS: 使用标准应用程序支持目录
        return Path.home() / "Library" / "Application Support" / "chat-cli"
    else:
        # Linux/Unix: 使用 XDG 标准或 .config
        xdg_config_home = os.getenv('XDG_CONFIG_HOME')
        if xdg_config_home:
            return Path(xdg_config_home) / "chat-cli"
        else:
            return Path.home() / ".config" / "chat-cli"

@click.command()
@click.argument('message', required=False)
@click.option('--interactive', '-i', is_flag=True, help='启动交互模式')
@click.option('--system', '-s', help='系统提示词')
@click.option('--config', 'show_config', is_flag=True, help='显示当前配置并提供修改选项')
@click.option('--disable-stream', is_flag=True, help='禁用流式输出（默认启用）')
@click.option('--simple-stream', is_flag=True, help='强制使用简化的流式输出（解决终端显示问题）')
@click.version_option(version='0.1.0')
def cli(message, interactive, system, show_config, disable_stream, simple_stream):
    """
    OpenAI兼容 AI 命令行聊天工具
    
    使用示例:
    
    chat-cli "你好，请介绍一下自己"
    
    chat-cli --interactive  # 交互模式
    
    chat-cli --disable-stream "请介绍一下自己"  # 禁用流式输出
    
    chat-cli --simple-stream "请介绍一下自己"  # 简化流式输出（兼容性更好）
    
    chat-cli --config  # 查看配置并可选择修改
    """
    # 如果要配置，运行配置向导
    if show_config:
        run_config_command()
        return
    
    # 执行聊天功能
    # 默认启用流式输出，除非用户明确禁用
    stream = not disable_stream
    run_chat_command(message, interactive, system, stream, simple_stream)


def run_config_command():
    """运行配置管理命令"""
    console.print(Panel("🔧 OpenAI兼容 API 配置管理", style="bold blue"))
    
    # 先显示当前配置
    show_current_config()
    
    # 询问是否要修改配置
    if Confirm.ask("\n[bold yellow]是否要修改配置?[/bold yellow]"):
        run_config_wizard()
    else:
        console.print("[green]配置未修改[/green]")


def show_current_config():
    """显示当前配置内容"""
    console.print(Panel("📋 当前配置信息", style="bold cyan"))
    
    # 检查配置文件 - 使用跨平台配置目录
    config_dir = get_config_dir()
    config_file = config_dir / "env"
    
    # 检查本地 .env 文件
    local_env_file = Path(".env")
    
    current_config = {}
    config_sources = []
    
    # 读取全局配置
    if config_file.exists():
        config_sources.append(f"全局配置: {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        current_config[key.strip()] = {
                            'value': value.strip(),
                            'source': '全局配置'
                        }
        except Exception as e:
            console.print(f"[red]读取全局配置失败: {e}[/red]")
    
    # 读取本地配置 (会覆盖全局配置)
    if local_env_file.exists():
        config_sources.append(f"本地配置: {local_env_file.absolute()}")
        try:
            with open(local_env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        current_config[key.strip()] = {
                            'value': value.strip(),
                            'source': '本地配置'
                        }
        except Exception as e:
            console.print(f"[red]读取本地配置失败: {e}[/red]")
    
    # 检查环境变量 (会覆盖文件配置)
    env_vars = ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_MODEL']
    for var in env_vars:
        env_value = os.getenv(var)
        if env_value:
            if var not in current_config or current_config[var]['value'] != env_value:
                current_config[var] = {
                    'value': env_value,
                    'source': '环境变量'
                }
    
    # 显示配置来源
    if config_sources:
        console.print("[bold green]配置文件:[/bold green]")
        for source in config_sources:
            console.print(f"  • {source}")
        console.print()
    
    # 显示配置内容
    if current_config:
        console.print("[bold green]配置项:[/bold green]")
        
        config_items = [
            ('OPENAI_API_KEY', 'API 密钥', True),
            ('OPENAI_BASE_URL', 'API 基础URL', False),
            ('OPENAI_MODEL', '模型名称', False)
        ]
        
        for key, description, is_sensitive in config_items:
            if key in current_config:
                value = current_config[key]['value']
                source = current_config[key]['source']
                
                if is_sensitive and value:
                    # 隐藏敏感信息
                    display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                else:
                    display_value = value
                
                console.print(f"  • [bold cyan]{description}[/bold cyan]: {display_value}")
                console.print(f"    [dim]来源: {source}[/dim]")
            else:
                console.print(f"  • [bold cyan]{description}[/bold cyan]: [red]未设置[/red]")
        
        console.print()
        
        # 测试当前配置
        console.print("[bold cyan]🧪 配置测试:[/bold cyan]")
        try:
            # 重新加载环境变量
            from .client import load_env_files
            load_env_files()
            
            # 尝试初始化客户端
            client = OpenAIClient()
            console.print("  [bold green]✅ 配置有效，可以正常使用[/bold green]")
        except Exception as e:
            console.print(f"  [red]❌ 配置测试失败: {e}[/red]")
            console.print("  [yellow]建议修改配置以修复问题[/yellow]")
    else:
        console.print("[yellow]未找到任何配置信息[/yellow]")
        console.print("需要进行初始配置")


def run_config_wizard():
    """运行配置向导"""
    console.print(Panel("🔧 配置向导", style="bold blue"))
    
    # 检查现有配置 - 使用跨平台配置目录
    config_dir = get_config_dir()
    config_file = config_dir / "env"
    
    current_config = {}
    if config_file.exists():
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
            'help': '获取方式:\n  - OpenAI: https://platform.openai.com/api-keys\n  - 通义千问: https://dashscope.aliyuncs.com/\n  - 其他兼容服务的API密钥'
        },
        {
            'key': 'OPENAI_BASE_URL',
            'prompt': 'API Base URL',
            'default': 'https://api.openai.com/v1',
            'required': False,
            'help': '常用服务:\n  - OpenAI官方: https://api.openai.com/v1\n  - 通义千问: https://dashscope.aliyuncs.com/compatible-mode/v1\n  - 本地服务: http://localhost:8000/v1'
        },
        {
            'key': 'OPENAI_MODEL',
            'prompt': 'Model Name',
            'default': 'gpt-3.5-turbo',
            'required': False,
            'help': '常用模型:\n  - OpenAI: gpt-3.5-turbo, gpt-4, gpt-4-turbo\n  - 通义千问: qwen-plus, qwen-max\n  - 其他: 根据服务商文档'
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


def run_chat_command(message, interactive, system, stream=False, simple_stream=False):
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
        run_interactive_mode(client, system, stream, simple_stream)
    elif message:
        run_single_message(client, message, system, stream, simple_stream)
    else:
        console.print("请提供消息或使用 --interactive 模式")
        console.print("使用 --help 查看帮助信息")


def run_single_message(client: OpenAIClient, message: str, system_prompt: str = None, stream: bool = False, simple_stream: bool = False):
    """运行单次问答模式"""
    if stream:
        # 检查是否使用简化流式输出
        # 如果用户明确指定了 --simple-stream，则强制使用简化模式
        # 否则根据终端兼容性自动判断
        if simple_stream:
            use_simple = True
        else:
            use_simple = not is_terminal_compatible()
        
        if use_simple:
            # 简化的流式输出，避免复杂渲染
            console.print("[bold blue]🤖 AI Assistant:[/bold blue]")
            console.print()
            
            full_response = ""
            try:
                for chunk in client.chat_stream(message, system_prompt):
                    full_response += chunk
                    # 直接输出字符，不使用Panel
                    console.print(chunk, end="", highlight=False)
                
                console.print()  # 换行
                console.print()  # 空行
                
            except Exception as e:
                console.print(f"[red]API调用失败: {e}[/red]")
        else:
            # 使用Rich Panel的流式输出（优化版本）
            full_response = ""
            try:
                # 创建一个初始的Panel
                panel = Panel(
                    Text("正在思考中...", style="dim italic"),
                    title="🤖 AI Assistant (流式输出)",
                    border_style="blue"
                )
                
                # 降低刷新频率，提高稳定性
                with Live(panel, console=console, refresh_per_second=4) as live:
                    for chunk in client.chat_stream(message, system_prompt):
                        full_response += chunk
                        # 实时更新Panel内容
                        live.update(Panel(
                            Text(full_response, style="bold"),
                            title="🤖 AI Assistant (流式输出)",
                            border_style="blue"
                        ))
                
                console.print()  # 添加一个空行
                
            except Exception as e:
                console.print(f"[red]API调用失败: {e}[/red]")
    else:
        try:
            response = client.chat(message, system_prompt)
            console.print(Panel(Text(response, style="bold"), title="🤖 AI Assistant"))
        except Exception as e:
            console.print(f"[red]API调用失败: {e}[/red]")

def run_interactive_mode(client: OpenAIClient, system_prompt: str = None, stream: bool = False, simple_stream: bool = False):
    """运行交互模式"""
    # 检查是否使用简化流式输出
    # 如果用户明确指定了 --simple-stream，则强制使用简化模式
    # 否则根据终端兼容性自动判断
    if simple_stream:
        use_simple = True
    else:
        use_simple = not is_terminal_compatible()
    
    if stream:
        if use_simple:
            console.print(Panel("进入交互模式（简化流式输出），输入 'exit' 退出。", title="🤖 AI Assistant"))
        else:
            console.print(Panel("进入交互模式（流式输出），输入 'exit' 退出。", title="🤖 AI Assistant"))
    else:
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
            if stream:
                if use_simple:
                    # 简化的流式输出
                    console.print("[bold blue]🤖 AI Assistant:[/bold blue]")
                    console.print()
                    
                    full_response = ""
                    for chunk in client.chat_with_history_stream(history):
                        full_response += chunk
                        console.print(chunk, end="", highlight=False)
                    
                    console.print()  # 换行
                    console.print()  # 空行
                    history.append({"role": "assistant", "content": full_response})
                else:
                    # 使用Rich Panel的流式输出（优化版本）
                    full_response = ""
                    # 创建初始Panel
                    panel = Panel(
                        Text("正在思考中...", style="dim italic"),
                        title="🤖 AI Assistant",
                        border_style="blue"
                    )
                    
                    # 降低刷新频率
                    with Live(panel, console=console, refresh_per_second=4) as live:
                        for chunk in client.chat_with_history_stream(history):
                            full_response += chunk
                            # 实时更新Panel内容
                            live.update(Panel(
                                Text(full_response, style="bold"),
                                title="🤖 AI Assistant",
                                border_style="blue"
                            ))
                    
                    console.print()  # 添加空行
                    history.append({"role": "assistant", "content": full_response})
            else:
                response = client.chat_with_history(history)
                history.append({"role": "assistant", "content": response})
                console.print(Panel(Text(response, style="bold"), title="🤖 AI Assistant"))
        except Exception as e:
            console.print(f"[red]API调用失败: {e}[/red]")
