"""
LinkedIn Profile Search Module

Provides functionality to search for LinkedIn profiles using multiple approaches:
1. LinkedIn API (official - requires approval)
2. Google Custom Search API (searches LinkedIn via Google)
3. Web scraping (backup - use with caution and respect rate limits)
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class LinkedInSearcher:
    """Search for LinkedIn profiles using multiple methods."""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.serp_api_key = os.getenv("SERP_API_KEY")

    async def search_profile(
        self,
        name: str,
        company: Optional[str] = None,
        location: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for LinkedIn profiles with given parameters.

        Args:
            name: Person's name
            company: Company name (optional)
            location: Location (optional)
            title: Job title (optional)

        Returns:
            Dictionary containing search results and metadata
        """
        logger.info(f"Searching LinkedIn for: {name}")

        # Build search query
        query_parts = [name, "LinkedIn"]
        if company:
            query_parts.append(company)
        if title:
            query_parts.append(title)
        if location:
            query_parts.append(location)

        query = " ".join(query_parts)

        # Try multiple search methods
        results = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "profiles": [],
            "search_method": None,
            "success": False
        }

        # Method 1: Try Google Custom Search (most reliable)
        if self.google_api_key and self.google_cse_id:
            try:
                google_results = await self._search_via_google(query)
                if google_results:
                    results["profiles"].extend(google_results)
                    results["search_method"] = "google_cse"
                    results["success"] = True
                    logger.info(f"Found {len(google_results)} profiles via Google CSE")
            except Exception as e:
                logger.error(f"Google CSE search failed: {e}")

        # Method 2: Try SerpAPI (alternative)
        if not results["success"] and self.serp_api_key:
            try:
                serp_results = await self._search_via_serpapi(query)
                if serp_results:
                    results["profiles"].extend(serp_results)
                    results["search_method"] = "serpapi"
                    results["success"] = True
                    logger.info(f"Found {len(serp_results)} profiles via SerpAPI")
            except Exception as e:
                logger.error(f"SerpAPI search failed: {e}")

        return results

    async def _search_via_google(self, query: str) -> List[Dict[str, Any]]:
        """Search LinkedIn profiles using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": f"site:linkedin.com/in/ {query}",
            "num": 10
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    profiles = []

                    for item in data.get("items", []):
                        profile = {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "google_cse"
                        }
                        profiles.append(profile)

                    return profiles
                else:
                    error_text = await response.text()
                    logger.error(f"Google API error: {response.status} - {error_text}")
                    return []

    async def _search_via_serpapi(self, query: str) -> List[Dict[str, Any]]:
        """Search LinkedIn profiles using SerpAPI."""
        url = "https://serpapi.com/search"
        params = {
            "api_key": self.serp_api_key,
            "q": f"site:linkedin.com/in/ {query}",
            "num": 10,
            "engine": "google"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    profiles = []

                    for result in data.get("organic_results", []):
                        profile = {
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "source": "serpapi"
                        }
                        profiles.append(profile)

                    return profiles
                else:
                    logger.error(f"SerpAPI error: {response.status}")
                    return []

    def extract_profile_info(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured information from profile data.

        Args:
            profile_data: Raw profile data from search

        Returns:
            Structured profile information
        """
        # Extract name from title (usually in format "Name - Title at Company | LinkedIn")
        title = profile_data.get("title", "")
        name = title.split("-")[0].strip() if "-" in title else title.split("|")[0].strip()

        # Extract info from snippet
        snippet = profile_data.get("snippet", "")

        return {
            "name": name,
            "linkedin_url": profile_data.get("url", ""),
            "description": snippet,
            "title": title,
            "raw_data": profile_data
        }


async def test_linkedin_search():
    """Test function for LinkedIn search."""
    searcher = LinkedInSearcher()
    results = await searcher.search_profile(
        name="Satya Nadella",
        company="Microsoft"
    )
    print(f"Found {len(results['profiles'])} profiles")
    for profile in results['profiles']:
        print(f"\n- {profile['title']}")
        print(f"  URL: {profile['url']}")
        print(f"  Snippet: {profile['snippet'][:100]}...")


if __name__ == "__main__":
    asyncio.run(test_linkedin_search())
