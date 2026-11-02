"""Web search for JARVIS using DuckDuckGo HTML scraping.

Provides real-time search capabilities without requiring API keys.
"""

import asyncio
import re
import urllib.parse
from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup


DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


async def search_web(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """Search the web using DuckDuckGo and return results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of dicts with 'title', 'url', 'snippet' keys
    """
    if not query or not query.strip():
        return []

    query = query.strip()
    if len(query) > 500:
        query = query[:500]

    params = {"q": query, "kl": "us-en"}
    headers = {"User-Agent": USER_AGENT}

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(DUCKDUCKGO_HTML, data=params, headers=headers) as response:
                if response.status != 200:
                    return [{"error": f"Search failed with status {response.status}"}]
                html = await response.text()
    except asyncio.TimeoutError:
        return [{"error": "Search request timed out"}]
    except aiohttp.ClientError as e:
        return [{"error": f"Search request failed: {type(e).__name__}"}]

    return _parse_results(html, max_results)


def _parse_results(html: str, max_results: int) -> List[Dict[str, str]]:
    """Parse DuckDuckGo HTML results."""
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.select(".result__body"):
        if len(results) >= max_results:
            break

        title_elem = result.select_one(".result__title a")
        snippet_elem = result.select_one(".result__snippet")

        if not title_elem:
            continue

        title = title_elem.get_text(strip=True)
        url = title_elem.get("href", "")

        # Clean up DuckDuckGo redirect URLs
        if url.startswith("//duckduckgo.com/l/?uddg="):
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if "uddg" in params:
                url = params["uddg"][0]

        snippet = ""
        if snippet_elem:
            snippet = snippet_elem.get_text(strip=True)[:300]

        if title and url:
            results.append({"title": title, "url": url, "snippet": snippet})

    return results


async def search_news(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """Search for news using DuckDuckGo news section."""
    return await search_web(f"{query} news", max_results)


def format_results_for_llm(results: List[Dict[str, str]]) -> str:
    """Format search results for LLM consumption."""
    if not results:
        return "No results found."

    if "error" in results[0]:
        return f"Search error: {results[0]['error']}"

    lines = ["Search results:"]
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result['title']}")
        lines.append(f"   URL: {result['url']}")
        if result.get("snippet"):
            lines.append(f"   Snippet: {result['snippet']}")
        lines.append("")

    return "\n".join(lines)