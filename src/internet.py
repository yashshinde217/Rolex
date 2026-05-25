"""
internet.py — V2 Phase 3: Internet

Gives Rolex live knowledge beyond what LLaMA was trained on.
All tools are free, no API keys required.

Capabilities:
  - Web search      (DuckDuckGo)
  - Page reader     (fetch and summarise any URL)
  - Weather         (wttr.in — free, no key)
  - News            (Google News RSS — free, no key)
  - Wikipedia       (Wikipedia REST API — free, no key)
  - YouTube summary (youtube-transcript-api — free, no key)
  - Smart routing   (auto-decides if internet is needed)

Requirements:
    pip install duckduckgo-search beautifulsoup4 lxml youtube-transcript-api
"""

import re
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from bs4 import BeautifulSoup

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YT_AVAILABLE = True
except ImportError:
    YT_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────────────────────

MAX_SEARCH_RESULTS  = 4      # Number of DuckDuckGo results to fetch
MAX_PAGE_CHARS      = 4000   # Max characters scraped from a webpage
MAX_WIKI_CHARS      = 2000   # Max characters from Wikipedia summary
MAX_NEWS_ITEMS      = 5      # Number of news headlines to return
MAX_YT_CHARS        = 3000   # Max transcript characters for YouTube summary
REQUEST_TIMEOUT     = 10     # Seconds before giving up on a web request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ─── Trigger detection ────────────────────────────────────────────────────────

SEARCH_TRIGGERS = [
    "search for", "search", "look up", "find information",
    "what is the latest", "what are the latest", "recent news",
    "who won", "what happened", "tell me about",
    "current", "today", "this week", "right now", "live",
]

WEATHER_TRIGGERS = [
    "weather", "temperature", "forecast", "rain", "sunny",
    "hot", "cold", "climate today", "what's it like outside",
]

NEWS_TRIGGERS = [
    "news", "headlines", "what's happening", "top stories",
    "latest news", "morning briefing", "what's new",
]

WIKI_TRIGGERS = [
    "wikipedia", "who is", "who was", "what is a", "what are",
    "define", "history of", "explain", "tell me about",
]

URL_TRIGGERS = [
    "open this link", "read this link", "summarise this url",
    "summarize this url", "read this page", "open this url",
    "fetch this", "what's on this page",
]

YT_TRIGGERS = [
    "youtube.com", "youtu.be", "summarise this video",
    "summarize this video", "what's this video about",
]


def is_internet_request(text: str) -> bool:
    """Returns True if the query likely needs live internet data."""
    lowered = text.lower()
    all_triggers = (SEARCH_TRIGGERS + WEATHER_TRIGGERS + NEWS_TRIGGERS +
                    WIKI_TRIGGERS + URL_TRIGGERS + YT_TRIGGERS)
    return any(t in lowered for t in all_triggers)


def detect_intent(text: str) -> str:
    """
    Classify the internet request type.
    Returns one of: 'weather', 'news', 'wikipedia', 'url', 'youtube', 'search'
    """
    lowered = text.lower()

    if any(t in lowered for t in WEATHER_TRIGGERS):
        return "weather"
    if any(t in lowered for t in NEWS_TRIGGERS):
        return "news"
    if re.search(r"https?://", lowered):
        if "youtube.com" in lowered or "youtu.be" in lowered:
            return "youtube"
        return "url"
    if any(t in lowered for t in YT_TRIGGERS):
        return "youtube"
    if any(t in lowered for t in WIKI_TRIGGERS):
        return "wikipedia"
    return "search"


# ─── Internet class ───────────────────────────────────────────────────────────

class Internet:
    """
    Gives Rolex live internet access.
    All methods return a plain string ready to be spoken or printed.
    """

    # ── Web search ────────────────────────────────────────────────────────────

    def search(self, query: str) -> str:
        """DuckDuckGo web search — no API key, forever free."""
        if not DDGS_AVAILABLE:
            return (
                "Web search isn't available. "
                "Run: pip install duckduckgo-search"
            )

        # Strip trigger words to get clean query
        clean = re.sub(
            r"^(search for|search|look up|find|tell me about)\s+",
            "", query.strip(), flags=re.IGNORECASE
        ).strip()

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(clean, max_results=MAX_SEARCH_RESULTS))

            if not results:
                return f"I couldn't find anything for '{clean}'. Try rephrasing."

            lines = [f"Here's what I found for '{clean}':\n"]
            for i, r in enumerate(results, 1):
                title = r.get("title", "")
                body  = r.get("body",  "")
                lines.append(f"{i}. {title}\n   {body}\n")

            return "\n".join(lines).strip()

        except Exception as e:
            return f"Search failed: {e}. Check your internet connection."

    # ── Weather ───────────────────────────────────────────────────────────────

    def weather(self, query: str) -> str:
        """
        Fetch weather using wttr.in — completely free, no API key ever.
        Tries to extract a city name from the query.
        """
        # Try to extract location from query
        location = self._extract_location(query)
        if not location:
            location = "auto"   # wttr.in auto-detects from IP

        url = f"https://wttr.in/{quote(location)}?format=j1"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            current = data["current_condition"][0]
            area    = data["nearest_area"][0]

            city    = area["areaName"][0]["value"]
            country = area["country"][0]["value"]
            temp_c  = current["temp_C"]
            feels_c = current["FeelsLikeC"]
            desc    = current["weatherDesc"][0]["value"]
            humidity = current["humidity"]
            wind_kmph = current["windspeedKmph"]

            return (
                f"Weather in {city}, {country}:\n"
                f"  {desc}, {temp_c}°C (feels like {feels_c}°C)\n"
                f"  Humidity: {humidity}%  •  Wind: {wind_kmph} km/h"
            )

        except requests.exceptions.ConnectionError:
            return "Can't reach weather service. Check your internet connection."
        except Exception as e:
            return f"Couldn't get weather: {e}"

    def _extract_location(self, text: str) -> str:
        """Extract a city/location from a weather query."""
        patterns = [
            r"weather (?:in|for|at) ([a-zA-Z\s]+)",
            r"(?:in|at|for) ([a-zA-Z\s]+?)(?:\s+today|\s+now|\s+forecast|$)",
            r"([a-zA-Z\s]+) weather",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Filter out generic words
                skip = {"the", "current", "today", "now", "outside", "forecast"}
                if location.lower() not in skip and len(location) > 1:
                    return location
        return ""

    # ── News ──────────────────────────────────────────────────────────────────

    def news(self, query: str = "") -> str:
        """
        Fetch top headlines from Google News RSS — free, no key.
        Optionally filtered by topic if query contains one.
        """
        topic = self._extract_news_topic(query)
        if topic:
            url = f"https://news.google.com/rss/search?q={quote(topic)}&hl=en"
        else:
            url = "https://news.google.com/rss?hl=en&gl=IN&ceid=IN:en"

        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item")[:MAX_NEWS_ITEMS]

            if not items:
                return "Couldn't find any news right now. Try again shortly."

            label = f"Top news on '{topic}'" if topic else "Top headlines right now"
            lines = [f"{label}:\n"]
            for i, item in enumerate(items, 1):
                title  = item.findtext("title",       "").strip()
                source = item.findtext("source",      "").strip()
                title  = re.sub(r"\s*-\s*[\w\s]+$", "", title)  # strip source suffix
                lines.append(f"{i}. {title}" + (f"  [{source}]" if source else ""))

            return "\n".join(lines)

        except requests.exceptions.ConnectionError:
            return "Can't reach news service. Check your internet connection."
        except Exception as e:
            return f"Couldn't fetch news: {e}"

    def _extract_news_topic(self, text: str) -> str:
        """Pull a topic keyword out of a news request."""
        patterns = [
            r"news (?:about|on|regarding) ([a-zA-Z\s]+)",
            r"(?:latest|recent) ([a-zA-Z\s]+) news",
            r"headlines (?:about|on) ([a-zA-Z\s]+)",
        ]
        skip = {"news", "headlines", "latest", "today", "morning", "top", "stories"}
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                if topic.lower() not in skip:
                    return topic
        return ""

    # ── Wikipedia ─────────────────────────────────────────────────────────────

    def wikipedia(self, query: str) -> str:
        """
        Wikipedia REST API — free, no key ever needed.
        Returns a clean summary of the topic.
        """
        # Clean query to a search term
        clean = re.sub(
            r"^(who is|who was|what is a|what is|what are|define|tell me about|"
            r"history of|explain|wikipedia)\s+",
            "", query.strip(), flags=re.IGNORECASE
        ).strip()

        search_url  = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={quote(clean)}&limit=1&format=json"
        try:
            s_resp  = requests.get(search_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            results = s_resp.json()
            if not results[1]:
                return f"I couldn't find a Wikipedia article for '{clean}'."

            title       = results[1][0]
            summary_url = (f"https://en.wikipedia.org/w/api.php?action=query"
                           f"&titles={quote(title)}&prop=extracts&exintro&explaintext"
                           f"&format=json&redirects=1")
            p_resp  = requests.get(summary_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            pages   = p_resp.json()["query"]["pages"]
            extract = next(iter(pages.values())).get("extract", "")

            if not extract:
                return f"Wikipedia has an article on '{title}' but no summary was available."

            # Trim to max length at a sentence boundary
            if len(extract) > MAX_WIKI_CHARS:
                extract = extract[:MAX_WIKI_CHARS]
                last    = extract.rfind(". ")
                if last > 0:
                    extract = extract[:last + 1]

            return f"From Wikipedia — {title}:\n\n{extract}"

        except requests.exceptions.ConnectionError:
            return "Can't reach Wikipedia. Check your internet connection."
        except Exception as e:
            return f"Wikipedia lookup failed: {e}"

    # ── Page reader ───────────────────────────────────────────────────────────

    def read_page(self, query: str) -> str:
        """
        Extract a URL from the query and return readable text from that page.
        Uses BeautifulSoup to strip HTML noise.
        """
        url_match = re.search(r"https?://[^\s]+", query)
        if not url_match:
            return "I couldn't find a URL in what you said. Say the full link including https://"

        url = url_match.group(0)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            soup  = BeautifulSoup(resp.text, "lxml")

            # Remove noise tags
            for tag in soup(["script", "style", "nav", "footer",
                              "header", "aside", "form", "iframe"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            # Collapse whitespace
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            text  = "\n".join(lines)

            if len(text) > MAX_PAGE_CHARS:
                text = text[:MAX_PAGE_CHARS]
                last = text.rfind(". ")
                if last > 0:
                    text = text[:last + 1]
                text += "\n\n[Page truncated — showing first portion]"

            return f"Here's what I read from {url}:\n\n{text}"

        except requests.exceptions.ConnectionError:
            return f"Couldn't reach {url}. Check the link or your internet."
        except Exception as e:
            return f"Failed to read page: {e}"

    # ── YouTube summary ───────────────────────────────────────────────────────

    def youtube_summary(self, query: str) -> str:
        """
        Extract transcript from a YouTube video and return it for summarising.
        Requires youtube-transcript-api (pip install youtube-transcript-api).
        """
        if not YT_AVAILABLE:
            return (
                "YouTube summaries aren't available. "
                "Run: pip install youtube-transcript-api"
            )

        # Extract video ID
        video_id = self._extract_youtube_id(query)
        if not video_id:
            return "I couldn't find a YouTube video ID in what you said."

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([t["text"] for t in transcript_list])

            if len(text) > MAX_YT_CHARS:
                text = text[:MAX_YT_CHARS] + "..."

            return (
                f"Here's the transcript from YouTube video ({video_id}):\n\n{text}\n\n"
                f"[Ask me to summarise it if you'd like a shorter version]"
            )

        except Exception as e:
            return (
                f"Couldn't get transcript for that video: {e}\n"
                "The video might have no captions, or captions may be disabled."
            )

    def _extract_youtube_id(self, text: str) -> str:
        """Extract YouTube video ID from a URL or query."""
        patterns = [
            r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ""

    # ── Unified entry point ───────────────────────────────────────────────────

    def process(self, query: str) -> tuple[str, str]:
        """
        Auto-detect intent and route to the right tool.
        Returns (result_text, intent_label).
        """
        intent = detect_intent(query)

        if intent == "weather":
            return self.weather(query), "weather"
        elif intent == "news":
            return self.news(query), "news"
        elif intent == "wikipedia":
            return self.wikipedia(query), "wikipedia"
        elif intent == "url":
            return self.read_page(query), "url"
        elif intent == "youtube":
            return self.youtube_summary(query), "youtube"
        else:
            return self.search(query), "search"
