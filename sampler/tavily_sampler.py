import time
import httpx

from eval_types import SearchResultProvider, SearchResult

class TavilySampler(SearchResultProvider):
    """Sample from Tavily's search API endpoint"""
    
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_url: str = "https://api.tavily.com",
    ):
        self.api_key = api_key
        self.max_retries = max_retries
        self.client = httpx.Client(
            base_url=base_url,
            headers={"api_key": api_key},
            timeout=60.0,
        )

    def __call__(self, query: str) -> SearchResult:
        trial = 0
        while True:
            try:
                response = self.client.post(
                    "/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "include_answer": True,
                        "search_depth": "basic"
                    }
                )
                if response.status_code != 200:
                    raise Exception(f"Search failed: {response.text}")
                    
                data = response.json()
                return data.get("results", [])
            except Exception as e:
                if trial >= self.max_retries:
                    print(f"Failed after {self.max_retries} retries: {str(e)}")
                    raise
                trial += 1
                time.sleep(2 ** trial)

    def __format_context__(self, results: SearchResult) -> str:
        formatted_results = []
        for result in results:
            if all(k in result for k in ['title', 'url', 'content']):
                formatted_results.append(
                    f"[{result['title']}]({result['url']})\n{result['content']}\n"
                )
        return "\n---\n".join(formatted_results)
