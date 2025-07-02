"""Test OpenAI client."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.client import OpenAIClient, load_env_files


class TestEnvLoading:
    """Test environment variable loading functionality."""
    
    def test_load_env_files_global_only(self):
        """Test loading environment variables from global config only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the home directory
            config_dir = Path(temp_dir) / ".config" / "chat-cli"
            config_dir.mkdir(parents=True)
            global_env_file = config_dir / "env"
            global_env_file.write_text("TEST_VAR=global_value\n")
            
            with patch('src.client.Path.home', return_value=Path(temp_dir)):
                with patch.dict(os.environ, {}, clear=True):
                    load_env_files()
                    assert os.getenv('TEST_VAR') == 'global_value'
    
    def test_load_env_files_priority(self):
        """Test that local .env overrides global config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create global config
            config_dir = Path(temp_dir) / ".config" / "chat-cli"
            config_dir.mkdir(parents=True)
            global_env_file = config_dir / "env"
            global_env_file.write_text("TEST_VAR=global_value\nGLOBAL_ONLY=global_only\n")
            
            # Create local .env
            local_env_file = Path(temp_dir) / ".env"
            local_env_file.write_text("TEST_VAR=local_value\n")
            
            with patch('src.client.Path.home', return_value=Path(temp_dir)):
                with patch('src.client.load_dotenv') as mock_load_dotenv:
                    def mock_load_side_effect(path=None, override=False):
                        if path and path.name == "env":
                            os.environ['TEST_VAR'] = 'global_value'
                            os.environ['GLOBAL_ONLY'] = 'global_only'
                        elif not path:  # local .env
                            if override:
                                os.environ['TEST_VAR'] = 'local_value'
                    
                    mock_load_dotenv.side_effect = mock_load_side_effect
                    
                    with patch.dict(os.environ, {}, clear=True):
                        load_env_files()
                        assert os.getenv('TEST_VAR') == 'local_value'  # local overrides
                        assert os.getenv('GLOBAL_ONLY') == 'global_only'  # global preserved


class TestOpenAIClient:
    """Test OpenAI client functionality."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}, clear=True)
    @patch('src.client.OpenAI')
    def test_client_initialization(self, mock_openai):
        """Test client initialization."""
        client = OpenAIClient()
        assert client.api_key == 'test-key'
        assert client.base_url == 'https://api.openai.com/v1'
        assert client.model == 'gpt-3.5-turbo'
        mock_openai.assert_called_once()
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                OpenAIClient()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}, clear=True)
    @patch('src.client.OpenAI')
    def test_chat_success(self, mock_openai):
        """Test successful chat."""
        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient()
        response = client.chat("Hello")
        
        assert response == "Hello! How can I help you?"
        mock_client_instance.chat.completions.create.assert_called_once()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}, clear=True)
    @patch('src.client.OpenAI')
    def test_chat_with_system_prompt(self, mock_openai):
        """Test chat with custom system prompt."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        client = OpenAIClient()
        response = client.chat("Hello", "You are a test assistant")
        
        # Check that the call was made with the custom system prompt
        call_args = mock_client_instance.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'You are a test assistant'
