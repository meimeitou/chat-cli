"""Test main CLI functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from src.main import cli


class TestCLI:
    """Test CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.main.OpenAIClient')
    def test_cli_single_message(self, mock_client_class):
        """Test CLI with single message."""
        # Mock the client
        mock_client = Mock()
        mock_client.chat.return_value = "Test response"
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(cli, ['Hello'])
        
        assert result.exit_code == 0
        mock_client.chat.assert_called_once_with('Hello', None)
    
    @patch('src.main.OpenAIClient')
    def test_cli_with_system_prompt(self, mock_client_class):
        """Test CLI with system prompt."""
        mock_client = Mock()
        mock_client.chat.return_value = "Test response"
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(cli, ['--system', 'You are helpful', 'Hello'])
        
        assert result.exit_code == 0
        mock_client.chat.assert_called_once_with('Hello', 'You are helpful')
    
    def test_cli_no_arguments(self):
        """Test CLI without arguments."""
        result = self.runner.invoke(cli, [])
        
        assert result.exit_code == 0
        assert "请提供消息或使用 --interactive 模式" in result.output
    
    @patch('src.main.OpenAIClient')
    def test_cli_api_key_missing(self, mock_client_class):
        """Test CLI when API key is missing."""
        mock_client_class.side_effect = ValueError("OPENAI_API_KEY environment variable is required")
        
        result = self.runner.invoke(cli, ['Hello'])
        
        assert result.exit_code == 1
        assert "请设置 OPENAI_API_KEY 环境变量" in result.output
