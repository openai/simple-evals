import time
import httpx

from eval_types import SearchResultProvider, SearchResult

class BingSampler(SearchResultProvider):
    """Sample from Bing's Web Search API endpoint"""
    
    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_url: str = "https://api.bing.microsoft.com/v7.0/search",
    ):
        self.api_key = api_key
        self.max_retries = max_retries
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Ocp-Apim-Subscription-Key": api_key},
            timeout=60.0,
        )

    def __call__(self, query: str) -> SearchResult:
        trial = 0
        while True:
            try:
                response = self.client.get(
                    "",
                    params={
                        "q": query,
                        "responseFilter": "Webpages",
                        "textFormat": "Raw"
                    }
                )
                if response.status_code != 200:
                    raise Exception(f"Search failed: {response.text}")
                    
                data = response.json()
                return data.get("webPages", {}).get("value", [])
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
                title = result.get('name', '')
                url = result.get('url', '')
                snippet = result.get('snippet', '')
                formatted_results.append(
                    f"[{title}]({url})\n{snippet}\n"
                )
        return "\n---\n".join(formatted_results)
