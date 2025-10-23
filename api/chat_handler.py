"""
Chat Handler Module

Handles conversational interactions using OpenAI's API, allowing users
to ask follow-up questions about profile search results.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class ChatHandler:
    """Handle chat interactions with OpenAI."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Use the same model as voice agent

    async def handle_message(
        self,
        message: str,
        search_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle a chat message and generate a response.

        Args:
            message: User's message
            search_context: Context from recent search results
            chat_history: Previous chat messages

        Returns:
            Dictionary containing response and metadata
        """
        logger.info(f"Processing chat message: {message[:50]}...")

        # Build system prompt
        system_prompt = self._build_system_prompt(search_context)

        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history
        if chat_history:
            for entry in chat_history[-10:]:  # Last 10 messages
                messages.append({"role": "user", "content": entry["user_message"]})
                messages.append({"role": "assistant", "content": entry["assistant_message"]})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Generate response
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_message = response.choices[0].message.content

            # Extract sources if mentioned
            sources = self._extract_sources(assistant_message, search_context)

            return {
                "message": assistant_message,
                "sources": sources,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return {
                "message": "I apologize, but I encountered an error processing your request. Please try again.",
                "sources": None,
                "error": str(e)
            }

    def _build_system_prompt(self, search_context: Optional[Dict[str, Any]] = None) -> str:
        """Build the system prompt based on available context."""

        base_prompt = """You are a professional research assistant specialized in analyzing online profiles and helping users understand information about people's professional presence.

Your role is to:
1. Answer questions about profile search results clearly and accurately
2. Provide insights based on the available data
3. Help users understand the context and relevance of information
4. Suggest follow-up searches or clarifications when needed
5. Always maintain professional ethics and respect privacy

When discussing search results:
- Cite specific sources when providing information
- Distinguish between verified information and assumptions
- Be transparent about limitations in the data
- Respect privacy and ethical boundaries"""

        if search_context:
            results = search_context.get("results", {})
            query = results.get("search_query", {})

            context_info = f"""

CURRENT SEARCH CONTEXT:
You are currently helping with a search for: {query.get('name', 'Unknown')}

Available Data:
- LinkedIn Profiles: {results.get('linkedin', {}).get('count', 0)} found
- Web Results: {results.get('web_search', {}).get('count', 0)} found
- News Articles: {results.get('news', {}).get('count', 0)} found

Summary:
{self._format_summary(results.get('summary', {}))}

Use this context to answer the user's questions. Reference specific URLs and sources when relevant."""

            return base_prompt + context_info

        return base_prompt

    def _format_summary(self, summary: Dict[str, Any]) -> str:
        """Format the summary section for the prompt."""
        lines = []

        if summary.get("top_linkedin_profile"):
            profile = summary["top_linkedin_profile"]
            lines.append(f"Top LinkedIn Profile: {profile.get('title', 'N/A')}")
            lines.append(f"  URL: {profile.get('url', 'N/A')}")

        if summary.get("top_web_results"):
            lines.append("\nTop Web Results:")
            for i, result in enumerate(summary["top_web_results"][:3], 1):
                lines.append(f"  {i}. {result.get('title', 'N/A')}")
                lines.append(f"     {result.get('url', 'N/A')}")

        if summary.get("recent_news"):
            lines.append("\nRecent News:")
            for i, article in enumerate(summary["recent_news"][:3], 1):
                lines.append(f"  {i}. {article.get('title', 'N/A')}")

        return "\n".join(lines) if lines else "No detailed summary available"

    def _extract_sources(
        self,
        message: str,
        search_context: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, str]]]:
        """Extract source URLs mentioned in the response."""
        if not search_context:
            return None

        sources = []
        results = search_context.get("results", {})

        # Check LinkedIn profiles
        for profile in results.get("linkedin", {}).get("profiles", [])[:3]:
            if profile.get("url") and profile["url"] in message:
                sources.append({
                    "type": "linkedin",
                    "title": profile.get("title", "LinkedIn Profile"),
                    "url": profile.get("url")
                })

        # Check web results
        for result in results.get("web_search", {}).get("results", [])[:5]:
            if result.get("url") and result["url"] in message:
                sources.append({
                    "type": "web",
                    "title": result.get("title", "Web Result"),
                    "url": result.get("url")
                })

        # Check news articles
        for article in results.get("news", {}).get("articles", [])[:3]:
            if article.get("url") and article["url"] in message:
                sources.append({
                    "type": "news",
                    "title": article.get("title", "News Article"),
                    "url": article.get("url")
                })

        return sources if sources else None


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_chat():
        handler = ChatHandler()
        response = await handler.handle_message(
            message="Tell me about this person's background",
            search_context=None
        )
        print(f"Response: {response['message']}")

    asyncio.run(test_chat())
