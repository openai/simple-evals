import os
import time
import requests
from typing import Any

from eval_types import MessageList, SamplerBase, SamplerResponse


class AliyunSampler(SamplerBase):
    """
    Sample from Alibaba Cloud's DashScope API
    """

    def __init__(
        self,
        model: str = "qwen-plus",
        api_key: str | None = None,
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key or os.environ.get("PROXY_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either as parameter or via PROXY_API_KEY environment variable")
        
        self.url = os.environ.get("PROXY_SERVER_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "url"

    def _handle_image(
        self,
        image: str,
        encoding: str = "base64",
        format: str = "png",
        fovea: int = 768,
    ):
        new_image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{format};{encoding},{image}",
            },
        }
        return new_image

    def _handle_text(self, text: str):
        return {"type": "text", "text": text}

    def _pack_message(self, role: str, content: Any):
        return {"role": str(role), "content": content}

    def __call__(self, message_list: MessageList) -> SamplerResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to DashScope format
        converted_messages = []
        for msg in message_list:
            role = msg["role"]
            content = msg["content"]
            
            # Handle both string content and mixed content
            if isinstance(content, str):
                converted_messages.append({"role": role, "content": content})
            elif isinstance(content, list):
                # Handle list of content (text and images)
                for item in content:
                    if item["type"] == "text":
                        converted_messages.append({"role": role, "content": item["text"]})
                    elif item["type"] == "image_url":
                        # For now, we'll convert image URLs to text mentions
                        converted_messages.append({"role": role, "content": "[Image]"})

        payload = {
            "model": self.model,
            "input": {
                "messages": converted_messages
            },
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        }

        trial = 0
        while True:
            try:
                response = requests.post(self.url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    print(f"Error from API: {response.status_code} - {response.text}")
                    raise Exception(f"API request failed with status {response.status_code}")
                
                result = response.json()
                
                # Extract the actual content from the response
                content = result.get("output", {}).get("text", "")
                if not content:
                    # Try alternative paths based on API response format
                    choices = result.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                
                if not content:
                    raise ValueError(f"DashScope API returned empty response: {result}")
                
                # Get usage information if available
                usage_info = result.get("usage", {})
                
                return SamplerResponse(
                    response_text=content,
                    response_metadata={"usage": usage_info},
                    actual_queried_message_list=message_list,
                )
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                exception_backoff = 2**trial  # exponential backoff
                print(f"Retrying after {exception_backoff} seconds", e)
                time.sleep(exception_backoff)
                trial += 1
            except Exception as e:
                print(f"General error: {e}")
                exception_backoff = 2**trial  # exponential backoff
                print(f"Retrying after {exception_backoff} seconds", e)
                time.sleep(exception_backoff)
                trial += 1