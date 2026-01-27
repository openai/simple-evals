import os
import time
import requests
from typing import Any

from eval_types import MessageList, SamplerBase, SamplerResponse


class WandouSampler(SamplerBase):
    """
    Sample from your custom Wandou model API
    """

    def __init__(
        self,
        model: str = "wandou-custom-model",
        api_endpoint: str = os.environ.get("WANDOU_API_ENDPOINT", ""),
        api_key: str = os.environ.get("WANDOU_API_KEY", ""),
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        self.api_endpoint = api_endpoint
        if not self.api_endpoint:
            raise ValueError("Wandou API endpoint must be provided via WANDOU_API_ENDPOINT environment variable")
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Wandou API key must be provided via WANDOU_API_KEY environment variable")
        
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
        
        # Convert messages to your Wandou model format
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
            "messages": converted_messages,  # Adjust this based on your API format
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        trial = 0
        while True:
            try:
                response = requests.post(self.api_endpoint, headers=headers, json=payload)
                
                if response.status_code != 200:
                    print(f"Error from Wandou API: {response.status_code} - {response.text}")
                    raise Exception(f"Wandou API request failed with status {response.status_code}")
                
                result = response.json()
                
                # Extract the actual content from the response
                # Adjust this based on your API response format
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    # Alternative extraction based on common API formats
                    content = result.get("output", {}).get("text", "")
                
                if not content:
                    raise ValueError(f"Wandou API returned empty response: {result}")
                
                # Get usage information if available
                usage_info = result.get("usage", {})
                
                return SamplerResponse(
                    response_text=content,
                    response_metadata={"usage": usage_info},
                    actual_queried_message_list=message_list,
                )
            except requests.exceptions.RequestException as e:
                print(f"Wandou API request failed: {e}")
                exception_backoff = 2**trial  # exponential backoff
                print(f"Retrying after {exception_backoff} seconds", e)
                time.sleep(exception_backoff)
                trial += 1
            except Exception as e:
                print(f"General error with Wandou model: {e}")
                exception_backoff = 2**trial  # exponential backoff
                print(f"Retrying after {exception_backoff} seconds", e)
                time.sleep(exception_backoff)
                trial += 1