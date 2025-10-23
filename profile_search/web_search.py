"""
General Web Search Module

Provides functionality to perform general web searches to enhance
profile information beyond LinkedIn.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class WebSearcher:
    """Perform general web searches to enhance profile information."""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.serp_api_key = os.getenv("SERP_API_KEY")

    async def search_person(
        self,
        name: str,
        additional_context: Optional[str] = None,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Perform a general web search for a person.

        Args:
            name: Person's name
            additional_context: Additional search context (company, title, etc.)
            num_results: Number of results to return

        Returns:
            Dictionary containing search results
        """
        logger.info(f"Performing web search for: {name}")

        # Build search query
        query = name
        if additional_context:
            query = f"{name} {additional_context}"

        results = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "results": [],
            "search_method": None,
            "success": False
        }

        # Try Google Custom Search first
        if self.google_api_key and self.google_cse_id:
            try:
                google_results = await self._search_via_google(query, num_results)
                if google_results:
                    results["results"].extend(google_results)
                    results["search_method"] = "google_cse"
                    results["success"] = True
                    logger.info(f"Found {len(google_results)} web results via Google CSE")
            except Exception as e:
                logger.error(f"Google CSE search failed: {e}")

        # Try SerpAPI as fallback
        if not results["success"] and self.serp_api_key:
            try:
                serp_results = await self._search_via_serpapi(query, num_results)
                if serp_results:
                    results["results"].extend(serp_results)
                    results["search_method"] = "serpapi"
                    results["success"] = True
                    logger.info(f"Found {len(serp_results)} web results via SerpAPI")
            except Exception as e:
                logger.error(f"SerpAPI search failed: {e}")

        return results

    async def _search_via_google(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10)  # Google CSE max is 10 per request
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    for item in data.get("items", []):
                        result = {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "display_url": item.get("displayLink", ""),
                            "source": "google_cse"
                        }
                        results.append(result)

                    return results
                else:
                    error_text = await response.text()
                    logger.error(f"Google API error: {response.status} - {error_text}")
                    return []

    async def _search_via_serpapi(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search using SerpAPI."""
        url = "https://serpapi.com/search"
        params = {
            "api_key": self.serp_api_key,
            "q": query,
            "num": num_results,
            "engine": "google"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    for result in data.get("organic_results", []):
                        result_data = {
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "display_url": result.get("displayed_link", ""),
                            "source": "serpapi"
                        }
                        results.append(result_data)

                    return results
                else:
                    logger.error(f"SerpAPI error: {response.status}")
                    return []

    async def search_news(
        self,
        name: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for news articles mentioning the person.

        Args:
            name: Person's name
            additional_context: Additional search context

        Returns:
            Dictionary containing news search results
        """
        query = f"{name} news"
        if additional_context:
            query = f"{name} {additional_context} news"

        logger.info(f"Searching news for: {name}")

        results = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "articles": [],
            "success": False
        }

        if self.serp_api_key:
            try:
                url = "https://serpapi.com/search"
                params = {
                    "api_key": self.serp_api_key,
                    "q": query,
                    "tbm": "nws",  # News search
                    "num": 10,
                    "engine": "google"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            for article in data.get("news_results", []):
                                article_data = {
                                    "title": article.get("title", ""),
                                    "url": article.get("link", ""),
                                    "snippet": article.get("snippet", ""),
                                    "source": article.get("source", ""),
                                    "date": article.get("date", "")
                                }
                                results["articles"].append(article_data)

                            results["success"] = True
                            logger.info(f"Found {len(results['articles'])} news articles")
            except Exception as e:
                logger.error(f"News search failed: {e}")

        return results


async def test_web_search():
    """Test function for web search."""
    searcher = WebSearcher()
    results = await searcher.search_person(
        name="Satya Nadella",
        additional_context="Microsoft CEO"
    )
    print(f"Found {len(results['results'])} web results")
    for result in results['results'][:3]:
        print(f"\n- {result['title']}")
        print(f"  URL: {result['url']}")
        print(f"  Snippet: {result['snippet'][:100]}...")


if __name__ == "__main__":
    asyncio.run(test_web_search())
