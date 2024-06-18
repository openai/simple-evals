import time
from typing import Optional

import anthropic

from typings import MessageList
from models.base import SamplerBase


class ClaudeCompletionSampler(SamplerBase):
    """
    Sample from Claude API
    """

    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        system_message: Optional[str] = None,
        temperature: float = 0.0,  # default in Anthropic example
        max_tokens: int = 1024,
    ):
        self.client = anthropic.Anthropic() # using api_key=os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "base64"

    def _handle_image(
        self, image: str, encoding: str = "base64", format: str = "png", fovea: int = 768
    ):
        new_image = {
            "type": "image",
            "source": {
                "type": encoding,
                "media_type": f"image/{format}",
                "data": image,
            },
        }
        return new_image

    def _handle_text(self, text):
        return {"type": "text", "text": text}

    def _pack_message(self, role, content):
        return {"role": str(role), "content": content}

    def __call__(self, message_list: MessageList) -> str:
        trial = 0
        while True:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    system=self.system_message,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=message_list,
                )
                return message.content[0].text
            except anthropic.RateLimitError as e:
                exception_backoff = 2**trial  # expontial back off
                print(
                    f"Rate limit exception so wait and retry {trial} after {exception_backoff} sec",
                    e,
                )
                time.sleep(exception_backoff)
                trial += 1
            # unknown error shall throw exception

class Claude3OpusSampler(ClaudeCompletionSampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 1024):
        super().__init__(model="claude-3-opus-20240229", system_message=system_message, temperature=temperature, max_tokens=max_tokens)

class Claude3SonnetSampler(ClaudeCompletionSampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 1024):
        super().__init__(model="claude-3-sonnet-20240229", system_message=system_message, temperature=temperature, max_tokens=max_tokens)

class Claude3HaikuSampler(ClaudeCompletionSampler):
    def __init__(self, system_message: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 1024):
        super().__init__(model="claude-3-haiku-20240229", system_message=system_message, temperature=temperature, max_tokens=max_tokens)