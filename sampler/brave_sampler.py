import time
import logging
import httpx

from eval_types import SearchResultProvider, SearchResult

class BraveSampler(SearchResultProvider):
    """Sample from Brave's Web Search API endpoint"""
    
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_url: str = "https://api.search.brave.com/res/v1/web/search",
        max_query_length: int = 150
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.max_query_length = max_query_length
        self.client = httpx.Client(
            timeout=60.0,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
        )

    def _truncate_query(self, query: str) -> str:
        """Truncate query to max length while trying to keep it meaningful"""
        if len(query) <= self.max_query_length:
            return query
        
        # Try to truncate at last complete sentence.
        truncated = query[:self.max_query_length]
        last_period = truncated.rfind('.')
        if last_period > self.max_query_length // 2:
            return query[:last_period + 1]
        
        # Otherwise truncate at last complete word.
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return query[:last_space]
            
        return truncated

    def __call__(self, query: str) -> SearchResult:
        trial = 0
        truncated_query = self._truncate_query(query)
        
        while True:
            try:
                response = self.client.get(
                    self.base_url,
                    params={
                        "q": truncated_query,
                        "count": 10,
                        "text_decorations": False,
                        "text_format": "raw"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Return web results.
                return data.get("web", {}).get("results", [])
                
            except Exception as e:
                if trial >= self.max_retries:
                    print(f"Failed after {self.max_retries} retries: {str(e)}")
                    raise
                trial += 1
                time.sleep(2 ** trial)

    def __format_context__(self, results: SearchResult) -> str:
        formatted_results = []
        for result in results:
            if isinstance(result, dict):
                title = result.get('title', '')
                url = result.get('url', '')
                description = result.get('description', '')
                formatted_results.append(
                    f"[{title}]({url})\n{description}\n"
                )
        return "\n---\n".join(formatted_results)

    def close(self):
        self.client.close()