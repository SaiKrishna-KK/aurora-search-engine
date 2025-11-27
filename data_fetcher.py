"""
Data Fetcher Module
This module fetches all messages and movies from the external API at startup.
"""

import httpx
from typing import List, Dict
import asyncio

from config import settings


async def fetch_all_messages() -> List[Dict]:
    """
    Fetch all messages from the API with pagination.
    The API returns 100 messages per page by default.
    """
    all_messages = []
    skip = 0
    limit = 100

    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT, follow_redirects=True) as client:
        while True:
            try:
                response = await client.get(
                    f"{settings.EXTERNAL_API_BASE_URL}/messages/",
                    params={"skip": skip, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()

                messages = data.get("items", [])
                if not messages:
                    # No more messages to fetch
                    break

                all_messages.extend(messages)

                # Check if we've fetched all messages
                total = data.get("total", 0)
                if len(all_messages) >= total:
                    break

                skip += limit

            except httpx.HTTPStatusError as e:
                if e.response.status_code in [400, 401, 402, 405]:
                    # API doesn't allow this pagination offset (payment required or forbidden), stop here
                    print(f"⚠️ API pagination limit reached at {len(all_messages)} messages")
                    break
                raise

    print(f"✓ Fetched {len(all_messages)} messages")
    return all_messages


async def fetch_all_movies() -> List[Dict]:
    """
    Fetch all movies from the API.
    There are only 35 movies, so we can fetch them all at once.
    """
    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(
            f"{settings.EXTERNAL_API_BASE_URL}/movies/",
            params={"skip": 0, "limit": 100}
        )
        response.raise_for_status()
        data = response.json()

    movies = data.get("items", [])
    print(f"✓ Fetched {len(movies)} movies")
    return movies


async def fetch_all_data():
    """
    Fetch both messages and movies concurrently.
    """
    messages, movies = await asyncio.gather(
        fetch_all_messages(),
        fetch_all_movies()
    )
    return {"messages": messages, "movies": movies}
