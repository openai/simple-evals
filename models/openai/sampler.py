import base64
import time
from typing import Any, Optional, Dict, List
from openai import OpenAI
from logging import getLogger

from typings import MessageList
from models.base import SamplerBase

logger = getLogger(__name__)

MAX_ALLOWED_TRIALS = 5

class OpenAISampler(SamplerBase):
    """
    Sample from OpenAI's chat completion API
    """

    def __init__(
        self,
        model: str,
        system_message: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ):
        self.client = OpenAI() # using api_key=os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "url"

    def _handle_image(
        self, image: str, encoding: str = "base64", format: str = "png", fovea: int = 768
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

    def __call__(self, message_list: MessageList) -> str:
        if self.system_message:
            message_list = [self._pack_message("system", self.system_message)] + message_list
        
        trial = 0
        while trial < MAX_ALLOWED_TRIALS:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=message_list,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                exception_backoff = 2**trial  # expontial back off
                logger.warn(
                    f"Rate limit exception so wait and retry {trial} after {exception_backoff} sec",
                    e,
                )
                time.sleep(exception_backoff)
                trial += 1

class GPT4oSampler(OpenAISampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.5, max_tokens: int = 1024):
        super().__init__(
            model="gpt-4o",
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )

class GPT4TurboSampler(OpenAISampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.5, max_tokens: int = 1024):
        super().__init__(
            model="gpt-4-turbo",
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
       )

class GPT3_5TurboSampler(OpenAISampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.5, max_tokens: int = 1024):
        super().__init__(
            model="gpt-3.5-turbo",
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )