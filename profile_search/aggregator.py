"""
Profile Aggregator Module

Aggregates data from multiple sources (LinkedIn, web search, news)
and creates comprehensive profile reports.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from .linkedin_search import LinkedInSearcher
from .web_search import WebSearcher

logger = logging.getLogger(__name__)


class ProfileAggregator:
    """Aggregate profile data from multiple sources."""

    def __init__(self):
        self.linkedin_searcher = LinkedInSearcher()
        self.web_searcher = WebSearcher()

    async def search_and_aggregate(
        self,
        name: str,
        company: Optional[str] = None,
        title: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for a person across multiple sources and aggregate results.

        Args:
            name: Person's name
            company: Company name (optional)
            title: Job title (optional)
            location: Location (optional)

        Returns:
            Aggregated profile data
        """
        logger.info(f"Starting comprehensive search for: {name}")

        # Build context for web search
        context_parts = []
        if company:
            context_parts.append(company)
        if title:
            context_parts.append(title)
        if location:
            context_parts.append(location)
        context = " ".join(context_parts)

        # Run searches in parallel
        linkedin_task = self.linkedin_searcher.search_profile(
            name=name,
            company=company,
            title=title,
            location=location
        )
        web_task = self.web_searcher.search_person(
            name=name,
            additional_context=context
        )
        news_task = self.web_searcher.search_news(
            name=name,
            additional_context=context
        )

        linkedin_results, web_results, news_results = await asyncio.gather(
            linkedin_task,
            web_task,
            news_task,
            return_exceptions=True
        )

        # Handle any exceptions
        if isinstance(linkedin_results, Exception):
            logger.error(f"LinkedIn search error: {linkedin_results}")
            linkedin_results = {"success": False, "profiles": []}

        if isinstance(web_results, Exception):
            logger.error(f"Web search error: {web_results}")
            web_results = {"success": False, "results": []}

        if isinstance(news_results, Exception):
            logger.error(f"News search error: {news_results}")
            news_results = {"success": False, "articles": []}

        # Aggregate results
        aggregated = {
            "search_query": {
                "name": name,
                "company": company,
                "title": title,
                "location": location
            },
            "timestamp": datetime.utcnow().isoformat(),
            "linkedin": {
                "success": linkedin_results.get("success", False),
                "profiles": linkedin_results.get("profiles", []),
                "count": len(linkedin_results.get("profiles", []))
            },
            "web_search": {
                "success": web_results.get("success", False),
                "results": web_results.get("results", []),
                "count": len(web_results.get("results", []))
            },
            "news": {
                "success": news_results.get("success", False),
                "articles": news_results.get("articles", []),
                "count": len(news_results.get("articles", []))
            },
            "summary": self._create_summary(linkedin_results, web_results, news_results)
        }

        logger.info(
            f"Search completed: {aggregated['linkedin']['count']} LinkedIn profiles, "
            f"{aggregated['web_search']['count']} web results, "
            f"{aggregated['news']['count']} news articles"
        )

        return aggregated

    def _create_summary(
        self,
        linkedin_results: Dict,
        web_results: Dict,
        news_results: Dict
    ) -> Dict[str, Any]:
        """Create a summary of search results."""
        total_results = (
            len(linkedin_results.get("profiles", [])) +
            len(web_results.get("results", [])) +
            len(news_results.get("articles", []))
        )

        # Get top LinkedIn profile
        top_linkedin = None
        if linkedin_results.get("profiles"):
            top_linkedin = linkedin_results["profiles"][0]

        # Get top web results
        top_web_results = web_results.get("results", [])[:3]

        # Get recent news
        recent_news = news_results.get("articles", [])[:3]

        return {
            "total_results": total_results,
            "has_linkedin_profile": bool(linkedin_results.get("profiles")),
            "has_web_presence": bool(web_results.get("results")),
            "has_news_coverage": bool(news_results.get("articles")),
            "top_linkedin_profile": top_linkedin,
            "top_web_results": top_web_results,
            "recent_news": recent_news
        }


class ReportGenerator:
    """Generate formatted reports from aggregated profile data."""

    def generate_text_report(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable text report.

        Args:
            profile_data: Aggregated profile data

        Returns:
            Formatted text report
        """
        query = profile_data["search_query"]
        name = query["name"]

        report_lines = [
            "=" * 80,
            f"PROFILE SEARCH REPORT: {name}",
            "=" * 80,
            "",
            "SEARCH PARAMETERS:",
            f"  Name: {name}",
        ]

        if query.get("company"):
            report_lines.append(f"  Company: {query['company']}")
        if query.get("title"):
            report_lines.append(f"  Title: {query['title']}")
        if query.get("location"):
            report_lines.append(f"  Location: {query['location']}")

        report_lines.extend([
            "",
            f"  Search Date: {profile_data['timestamp']}",
            "",
            "=" * 80,
            "SUMMARY:",
            "=" * 80,
        ])

        summary = profile_data["summary"]
        report_lines.append(f"  Total Results Found: {summary['total_results']}")
        report_lines.append(f"  LinkedIn Profile: {'✓ Found' if summary['has_linkedin_profile'] else '✗ Not Found'}")
        report_lines.append(f"  Web Presence: {'✓ Found' if summary['has_web_presence'] else '✗ Not Found'}")
        report_lines.append(f"  News Coverage: {'✓ Found' if summary['has_news_coverage'] else '✗ Not Found'}")

        # LinkedIn Section
        report_lines.extend([
            "",
            "=" * 80,
            "LINKEDIN PROFILES:",
            "=" * 80,
        ])

        linkedin = profile_data["linkedin"]
        if linkedin["success"] and linkedin["profiles"]:
            for i, profile in enumerate(linkedin["profiles"][:5], 1):
                report_lines.extend([
                    "",
                    f"{i}. {profile.get('title', 'No title')}",
                    f"   URL: {profile.get('url', 'No URL')}",
                    f"   {profile.get('snippet', 'No description')[:200]}...",
                ])
        else:
            report_lines.append("\n  No LinkedIn profiles found.")

        # Web Search Section
        report_lines.extend([
            "",
            "=" * 80,
            "WEB SEARCH RESULTS:",
            "=" * 80,
        ])

        web = profile_data["web_search"]
        if web["success"] and web["results"]:
            for i, result in enumerate(web["results"][:5], 1):
                report_lines.extend([
                    "",
                    f"{i}. {result.get('title', 'No title')}",
                    f"   URL: {result.get('url', 'No URL')}",
                    f"   {result.get('snippet', 'No description')[:200]}...",
                ])
        else:
            report_lines.append("\n  No web results found.")

        # News Section
        report_lines.extend([
            "",
            "=" * 80,
            "NEWS & MEDIA COVERAGE:",
            "=" * 80,
        ])

        news = profile_data["news"]
        if news["success"] and news["articles"]:
            for i, article in enumerate(news["articles"][:5], 1):
                report_lines.extend([
                    "",
                    f"{i}. {article.get('title', 'No title')}",
                    f"   Source: {article.get('source', 'Unknown')}",
                    f"   Date: {article.get('date', 'Unknown')}",
                    f"   URL: {article.get('url', 'No URL')}",
                    f"   {article.get('snippet', 'No description')[:200]}...",
                ])
        else:
            report_lines.append("\n  No news coverage found.")

        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])

        return "\n".join(report_lines)

    def generate_json_report(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a JSON-formatted report.

        Args:
            profile_data: Aggregated profile data

        Returns:
            JSON-serializable report
        """
        # The profile_data is already in a good JSON format
        return profile_data

    def generate_markdown_report(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a Markdown-formatted report.

        Args:
            profile_data: Aggregated profile data

        Returns:
            Markdown formatted report
        """
        query = profile_data["search_query"]
        name = query["name"]

        md_lines = [
            f"# Profile Search Report: {name}",
            "",
            "## Search Parameters",
            f"- **Name:** {name}",
        ]

        if query.get("company"):
            md_lines.append(f"- **Company:** {query['company']}")
        if query.get("title"):
            md_lines.append(f"- **Title:** {query['title']}")
        if query.get("location"):
            md_lines.append(f"- **Location:** {query['location']}")

        md_lines.extend([
            f"- **Search Date:** {profile_data['timestamp']}",
            "",
            "## Summary",
        ])

        summary = profile_data["summary"]
        md_lines.extend([
            f"- **Total Results:** {summary['total_results']}",
            f"- **LinkedIn Profile:** {'✓ Found' if summary['has_linkedin_profile'] else '✗ Not Found'}",
            f"- **Web Presence:** {'✓ Found' if summary['has_web_presence'] else '✗ Not Found'}",
            f"- **News Coverage:** {'✓ Found' if summary['has_news_coverage'] else '✗ Not Found'}",
            "",
            "## LinkedIn Profiles",
        ])

        linkedin = profile_data["linkedin"]
        if linkedin["success"] and linkedin["profiles"]:
            for i, profile in enumerate(linkedin["profiles"][:5], 1):
                md_lines.extend([
                    f"### {i}. {profile.get('title', 'No title')}",
                    f"**URL:** [{profile.get('url', 'No URL')}]({profile.get('url', '#')})",
                    "",
                    f"{profile.get('snippet', 'No description')}",
                    "",
                ])
        else:
            md_lines.append("*No LinkedIn profiles found.*")

        md_lines.extend([
            "",
            "## Web Search Results",
        ])

        web = profile_data["web_search"]
        if web["success"] and web["results"]:
            for i, result in enumerate(web["results"][:5], 1):
                md_lines.extend([
                    f"### {i}. {result.get('title', 'No title')}",
                    f"**URL:** [{result.get('url', 'No URL')}]({result.get('url', '#')})",
                    "",
                    f"{result.get('snippet', 'No description')}",
                    "",
                ])
        else:
            md_lines.append("*No web results found.*")

        md_lines.extend([
            "",
            "## News & Media Coverage",
        ])

        news = profile_data["news"]
        if news["success"] and news["articles"]:
            for i, article in enumerate(news["articles"][:5], 1):
                md_lines.extend([
                    f"### {i}. {article.get('title', 'No title')}",
                    f"- **Source:** {article.get('source', 'Unknown')}",
                    f"- **Date:** {article.get('date', 'Unknown')}",
                    f"- **URL:** [{article.get('url', 'No URL')}]({article.get('url', '#')})",
                    "",
                    f"{article.get('snippet', 'No description')}",
                    "",
                ])
        else:
            md_lines.append("*No news coverage found.*")

        return "\n".join(md_lines)


async def test_aggregator():
    """Test the profile aggregator."""
    aggregator = ProfileAggregator()
    report_gen = ReportGenerator()

    profile_data = await aggregator.search_and_aggregate(
        name="Satya Nadella",
        company="Microsoft",
        title="CEO"
    )

    print("\n" + "=" * 80)
    print("TEXT REPORT:")
    print("=" * 80)
    print(report_gen.generate_text_report(profile_data))


if __name__ == "__main__":
    asyncio.run(test_aggregator())
