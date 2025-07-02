"""OpenAI compatible API client module."""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator
from openai import OpenAI
from dotenv import load_dotenv


def load_env_files():
    """Load environment variables from multiple sources."""
    # Load from global config directory first
    global_config_dir = Path.home() / ".config" / "chat-cli"
    global_env_file = global_config_dir / "env"
    
    if global_env_file.exists():
        load_dotenv(global_env_file)
    
    # Load from local .env file (this will override global settings)
    load_dotenv(override=True)


# Load environment variables from multiple sources
load_env_files()


class OpenAIClient:
    """OpenAI compatible API client."""
    
    def __init__(self):
        """Initialize the OpenAI compatible client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, message: str, system_prompt: Optional[str] = None, stream: bool = False):
        """Send a single message and get response."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant"})
        
        messages.append({"role": "user", "content": message})
        
        if stream:
            return self._chat_stream(messages)
        else:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                return response.choices[0].message.content
            except Exception as e:
                raise Exception(f"API call failed: {str(e)}")
    
    def chat_with_history(self, messages: List[Dict[str, str]], stream: bool = False):
        """Send messages with conversation history."""
        if stream:
            return self._chat_stream(messages)
        else:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                return response.choices[0].message.content
            except Exception as e:
                raise Exception(f"API call failed: {str(e)}")
    
    def _chat_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Handle streaming chat completion."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield content
                    
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def chat_stream(self, message: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Send a single message and get streaming response."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant"})
        
        messages.append({"role": "user", "content": message})
        
        return self._chat_stream(messages)
    
    def chat_with_history_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Send messages with conversation history and get streaming response."""
        return self._chat_stream(messages)
