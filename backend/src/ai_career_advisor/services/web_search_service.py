from typing import List
import re

# NOTE:
# Abhi hum REAL Google API / SerpAPI use nahi kar rahe
# Ye controlled placeholder hai
# Next step me isko Gemini / Perplexity se connect karenge

ALLOWED_DOMAINS = [
    ".ac.in",
    ".edu.in",
    ".gov.in",
    "nirfindia.org",
    "josaa.nic.in",
    "collegedunia.com",
]


class WebSearchService:

    @staticmethod
    async def search(
        *,
        college_name: str,
        max_results: int = 5
    ) -> List[str]:
        """
        Controlled search URLs for a college.
        TEMP: static + predictable (no external dependency yet)
        """

        # TEMP deterministic URLs (safe start)
        urls = [
            f"https://{college_name.replace(' ', '').lower()}.ac.in",
            "https://josaa.nic.in",
            "https://www.collegedunia.com"
        ]

        # filter allowed domains only
        filtered = []
        for url in urls:
            for domain in ALLOWED_DOMAINS:
                if domain in url:
                    filtered.append(url)
                    break

        return filtered[:max_results]
