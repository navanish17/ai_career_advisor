from typing import List, Dict
import httpx
from bs4 import BeautifulSoup


class WebFetchService:

    @staticmethod
    async def fetch_pages(urls: List[str]) -> List[Dict]:
        """
        Fetch web pages safely and return cleaned text.
        Output format:
        [
          {
            "url": "...",
            "text": "clean extracted text"
          }
        ]
        """

        results = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for url in urls:
                try:
                    response = await client.get(url)

                    if response.status_code != 200:
                        continue

                    soup = BeautifulSoup(response.text, "html.parser")

                    # remove scripts & styles
                    for tag in soup(["script", "style", "noscript"]):
                        tag.decompose()

                    text = soup.get_text(separator=" ", strip=True)

                    if len(text) < 300:
                        continue  # skip useless pages

                    results.append({
                        "url": url,
                        "text": text[:8000]  # limit size for LLM
                    })

                except Exception:
                    continue  # fail-safe, never crash

        return results
