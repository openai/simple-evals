import time

import anthropic
from anthropic import AnthropicVertex

from eval_types import MessageList, SamplerBase

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


class ClaudeVertexCompletionSampler(SamplerBase):
    """
    Sample from Claude API
    """

    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        system_message: str | None = None,
        temperature: float = 0.0,  # default in Anthropic example
        max_tokens: int = 1024,
        location: str = "us-east5",
        project_id: str = "{your-project-id}",
    ):
        self.api_key_name = "ANTHROPIC_API_KEY"
        self.client = AnthropicVertex(region=location, project_id=project_id)
        # using api_key=os.environ.get("ANTHROPIC_API_KEY") # please set your API_KEY
        self.model = model
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.image_format = "base64"
        message = self.client.messages.create(
            max_tokens=1024,
            messages=[
            {
                "role": "user",
                "content": "Send me a recipe for banana bread.",
            }
            ],
            model=self.model
            )
        print(message.model_dump_json(indent=2))

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

    def _convert_messages(self, message_list: MessageList) -> list[dict]:
        processed_api_messages = []
        for original_message in message_list:
            role = original_message.get("role")
            content = original_message.get("content")

            if role not in ["user", "assistant"]:
                print(f"Warning: Skipping message with unsupported role '{role}'. Only 'user' and 'assistant' roles are processed for the 'messages' parameter.")
                continue

            api_content: str | list = "" # Placeholder, will be updated

            if isinstance(content, str):
                api_content = content
            elif isinstance(content, list):
                api_content_parts = []
                for part in content:
                    part_type = part.get("type")
                    if part_type == "text":
                        text = part.get("text")
                        if text:
                            api_content_parts.append(self._handle_text(text))
                    elif part_type == "image_url":
                        image_url_spec = part.get("image_url")
                        if image_url_spec and "url" in image_url_spec:
                            image_url_data = image_url_spec["url"]
                            if image_url_data.startswith("data:image/") and ";base64," in image_url_data:
                                try:
                                    header, base64_data = image_url_data.split(",", 1)
                                    # header is "data:image/<format>;base64"
                                    mime_part = header.split(":")[1].split(";")[0] # "image/<format>"
                                    image_format = mime_part.split("/")[1] # "<format>"
                                    api_content_parts.append(
                                        self._handle_image(
                                            image=base64_data,
                                            encoding="base64",
                                            format=image_format,
                                        )
                                    )
                                except (ValueError, IndexError) as e:
                                    print(f"Warning: Could not parse image_url data URI '{image_url_data}': {e}")
                            else:
                                print(f"Warning: Unsupported image_url format: {image_url_data}. Expected 'data:image/<format>;base64,<data>'.")
                        else:
                            print(f"Warning: Skipping image part with missing or invalid 'image_url' spec: {part}")
                    else:
                        print(f"Warning: Skipping unsupported part type '{part_type}' in message content.")
                
                if not api_content_parts:
                    print(f"Warning: Message from role '{role}' resulted in no content parts after processing. Skipping message.")
                    continue
                api_content = api_content_parts
            else:
                print(f"Warning: Skipping message from role '{role}' with unsupported content type: {type(content)}. Expected str or list.")
                continue
            
            processed_api_messages.append({"role": str(role), "content": api_content})

        return processed_api_messages

    def __call__(self, message_list: MessageList) -> str:
        # Convert the input message_list to the format expected by Anthropic API
        api_messages = self._convert_messages(message_list)

        if not api_messages:
            # If, after conversion, there are no messages to send
            print("Warning: No valid messages to send to Claude API after conversion. Returning empty string.")
            return ""
            
        trial = 0
        while True:
            try:
                message = self.client.messages.create(
                    model=self.model,
                    system=self.system_message,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=api_messages,  # Use the converted messages
                )
                # Assuming Claude's response structure provides content in a list,
                # and we need the text from the first content block.
                if message.content and isinstance(message.content, list) and len(message.content) > 0 and message.content[0].type == "text":
                    return message.content[0].text
                else:
                    # Handle cases where response might not be as expected or is empty
                    print(f"Warning: Unexpected response content structure from Claude API: {message.content}")
                    return "" # Or raise an error, or return a string representation
            except anthropic.RateLimitError as e:
                exception_backoff = 2**trial  # expontial back off
                print(
                    f"Rate limit exception so wait and retry {trial} after {exception_backoff} sec",
                    e,
                )
                time.sleep(exception_backoff)
                trial += 1
            # unknown error shall throw exception
