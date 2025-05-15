import os
import time
from typing import Any
from datetime import datetime, timedelta
import subprocess
import base64

from google import genai
from google.genai.types import HttpOptions, Part, Content

from eval_types import MessageList, SamplerBase

class GeminiSampler(SamplerBase):
    """
    Sample from Google's Gemini API
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-001",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        project_id: str | None = None,
        location: str = "us-central1",
        api_key: str | None = None,
        use_gemini_grounding: bool = False,
    ):
        self.project_id = project_id
        self.location = location
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.token_expiry = None
        self.use_gemini_grounding = use_gemini_grounding
        # self._refresh_token_if_needed()
        
        # Initialize the Gemini client
        if self.api_key:
            # Use API key authentication
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=HttpOptions(api_version="v1")
            )
        else:
            # self._refresh_token_if_needed()
            # Use Vertex AI authentication
            if not self.project_id or not self.location:
                raise ValueError("Project ID and location must be provided for Vertex AI mode when API key is not used.")
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
        response = self.client.models.generate_content(
            model=model,
            contents="How does AI work?",
        )
        print(response.text)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _pack_message(self, role: str, content: Any):
        """Pack a message in the standard format expected by eval scripts."""
        return {"role": str(role), "content": content}

    def _refresh_token_if_needed(self):
        """Refresh the Google Cloud token if it's expired or about to expire (within 5 minutes).
        This is primarily for scenarios where ADC isn't fully set up and explicit token fetching is a fallback,
        and when not using an API key and not in a Vertex AI context where project_id implies ADC.
        """
        if not self.api_key and not self.project_id:
            current_time = datetime.now()
            if not self.token_expiry or current_time + timedelta(minutes=5) >= self.token_expiry:
                try:
                    print("Attempting to fetch new token from gcloud (fallback mechanism).")
                    result = subprocess.run(
                        "gcloud auth print-access-token",
                        capture_output=True,
                        text=True,
                        check=True,
                        shell=True
                    )
                    os.environ["GOOGLE_API_KEY"] = result.stdout.strip()
                    os.environ["API_KEY"] = result.stdout.strip()
                    print(f"Fetched token via gcloud (expires in ~1 hour). Note: SDK should ideally use ADC via gcloud setup.")
                    self.token_expiry = current_time + timedelta(minutes=55)
                except FileNotFoundError:
                    print("gcloud command not found. Please ensure gcloud SDK is installed and in your PATH for fallback token refresh.")
                except subprocess.CalledProcessError as e:
                    print(f"Error fetching token from gcloud: {e}. Fallback token refresh failed.")

    def _convert_messages(self, message_list: MessageList) -> list[Content]:
        """Convert MessageList format to Gemini API's expected format (list of Content objects).
        Simplified for text-to-text only.
        """
        converted_contents: list[Content] = []
        for msg in message_list:
            role = msg.get("role", "user").lower()
            content = msg.get("content")

            # Map 'assistant' role to 'model' for Gemini
            if role == "assistant":
                role = "model"
            
            # Ensure role is either 'user' or 'model'
            if role not in ["user", "model"]:
                print(f"Warning: Invalid role '{role}' encountered. Defaulting to 'user'.")
                role = "user"

            parts_list: list[Part] = [] # Ensure this is a list of Part objects

            if isinstance(content, str):
                # For simple text content, wrap it in a Part object
                parts_list.append(Part(text=content))
            elif isinstance(content, list):
                # For list content (potentially from multimodal, but we'll only process text parts)
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content = item.get("text", "")
                        if text_content: # Only add if text is not empty
                            parts_list.append(Part(text=text_content))
                    # Other types (like image_url) are ignored as per simplification request
            else:
                print(f"Warning: Skipping message with unknown or non-string/non-list content type: {type(content)}")
                continue # Skip this message

            if parts_list: # Only add if there are actual parts to send
                converted_contents.append(Content(role=role, parts=parts_list))
            else:
                print(f"Warning: Message from role '{role}' resulted in no parts and was skipped.")
        
        return converted_contents

    def __call__(self, message_list: MessageList) -> str:
        trial = 0
        while True:
            try:
                # self._refresh_token_if_needed()
                
                contents = self._convert_messages(message_list)
                
                if not contents:
                    print("Warning: No content to send after message conversion. Returning empty string.")
                    return ""

                generation_config = {
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }

                if self.use_gemini_grounding:
                    from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
                    google_search_tool = Tool(
                        google_search = GoogleSearch()
                    )

                    print("INFO: Gemini grounding is enabled (conceptual).")
                    generation_config["tools"] = [google_search_tool]
                    # generation_config["google_search"] = GoogleSearch()

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=generation_config,
                )
                # print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)
                return response.text
            except Exception as e:
                print(f"Error during API call (trial {trial+1}): {e}")
                trial += 1
                if trial >= 5:
                    print("Maximum retries reached. Raising exception.")
                    raise e
                
                exception_backoff = 2**trial
                print(
                    f"Rate limit or other exception. Waiting {exception_backoff} sec before retry {trial+1}...",
                )
                time.sleep(exception_backoff) 