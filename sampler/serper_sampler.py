import time
import httpx

from eval_types import SearchResultProvider, SearchResult

class SerperSampler(SearchResultProvider):
    """Sample from Serper's Google search API endpoint"""
    
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_url: str = "https://google.serper.dev",
    ):
        self.api_key = api_key
        self.max_retries = max_retries
        self.client = httpx.Client(
            base_url=base_url,
            headers={"X-API-KEY": api_key},
            timeout=60.0,
        )

    def __call__(self, query: str) -> SearchResult:
        trial = 0
        while True:
            try:
                response = self.client.post(
                    "/search",
                    json={"q": query}
                )
                if response.status_code != 200:
                    raise Exception(f"Search failed: {response.text}")
                    
                data = response.json()
                return data.get("organic", [])
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
                link = result.get('link', '')
                snippet = result.get('snippet', '')
                formatted_results.append(
                    f"[{title}]({link})\n{snippet}\n"
                )
        return "\n---\n".join(formatted_results)
