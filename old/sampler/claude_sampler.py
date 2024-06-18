import time

import anthropic

from ..types import MessageList, SamplerBase

CLAUDE_SYSTEM_MESSAGE_LMSYS = (
    "The assistant is Claude, created by Anthropic. The current date is "
    "{currentDateTime}. Claude's knowledge base was last updated in "
    "August 2023 and it answers user questions about events before "
    "August 2023 and after August 2023 the same way a highly informed "
    "individual from August 2023 would if they were talking to someone "
    "from {currentDateTime}. It should give concise responses to very "
    "simple questions, but provide thorough responses to more complex "
    "and open-ended questions. It is happy to help with writing, "
    "analysis, question answering, math, coding, and all sorts of other "
    "tasks. It uses markdown for coding. It does not mention this "
    "information about itself unless the information is directly "
    "pertinent to the human's query."
).format(currentDateTime="2024-04-01")
# reference: https://github.com/lm-sys/FastChat/blob/7899355ebe32117fdae83985cf8ee476d2f4243f/fastchat/conversation.py#L894


class ClaudeCompletionSampler(SamplerBase):
    """
    Sample from Claude API
    """

    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        system_message: str | None = None,
        temperature: float = 0.0,  # default in Anthropic example
        max_tokens: int = 1024,
    ):
        self.api_key_name = "ANTHROPIC_API_KEY"
        self.client = anthropic.Anthropic()
        # using api_key=os.environ.get("ANTHROPIC_API_KEY") # please set your API_KEY
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
