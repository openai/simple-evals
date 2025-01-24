import time
from typing import Any
import openai
from openai import OpenAI
from eval_types import SamplerBase, SearchResultProvider, MessageList

class ResultSampler(SamplerBase):
    """
    Sampler that uses rag to return a fixed result from a given search result provider
    """

    def __init__(self, provider: SearchResultProvider, temperature: float = 0.3, model_name: str = "gpt-4o-mini"):
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.client = OpenAI()
        self.system_prompt = """You synthesize information from search results and provides inline cited sources.
        REQUIREMENTS:
        - ONLY state information that's directly supported from relevant and recent sources and cite your sources.
        - USE at LEAST TWO, but preferably at least 3 sources.
        - Be VERY concise: Focus on the key points in 1-2 short paragraphs maximum.
        - If search results lack relevant information, clearly state this limitation.

        CITATION REQUIREMENTS:
        - Every numeric fact (dates, statistics, percentages, etc.), fact, or quote must have an inline citation in format ([Short source domain/host](url)).
        - Citations must be placed immediately after the fact they support."""

    def _handle_text(self, text: str):
        return {"type": "text", "text": text}

    def _pack_message(self, role: str, content: Any):
        return {"role": str(role), "content": content}

    def __call__(self, message_list: MessageList) -> str:
        query = self.__extract_query_from_messages__(message_list)
        search_results = self.provider.__call__(query)
        context = self.provider.__format_context__(search_results)
        return self.__make_rag_result__(query, context)
    
    def __make_rag_result__(self, query: str, context: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"User query: {query}\nProvide a focused and well rounded answer using these search results:\n{context}"}
        ]
        
        trial = 0
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=400
                )
                message = response.choices[0].message.content
                return message
            except openai.BadRequestError as e:
                print("Bad Request Error", e)
                return ""
            except Exception as e:
                exception_backoff = 2**trial
                print(f"Rate limit exception so wait and retry {trial} after {exception_backoff} sec", e)
                time.sleep(exception_backoff)
                trial += 1
