import os

class SERPTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY", "")

    def _fallback_search(self, query: str, num: int = 5) -> str:
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num))
            if not results:
                return "No search results found."
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r.get('title','')}\n   {r.get('body','')}\n   URL: {r.get('href','')}")
            return "\n\n".join(lines)
        except Exception as exc:
            return f"Search failed: {exc}"

    def search(self, query: str, num: int = 5) -> str:
        print("  [SERP] Using DuckDuckGo")
        return self._fallback_search(query, num)
