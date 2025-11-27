"""
Search Engine Module
This module provides fast in-memory search across messages and movies.
"""

from typing import List, Dict
import re
from collections import defaultdict


class SearchEngine:
    """
    In-memory search engine using inverted index for fast lookups.
    """

    def __init__(self):
        self.messages = []
        self.movies = []
        self.message_index = defaultdict(set)  # word -> set of message indices
        self.movie_index = defaultdict(set)    # word -> set of movie indices

    def load_data(self, messages: List[Dict], movies: List[Dict]):
        """
        Load data and build search indices.
        """
        self.messages = messages
        self.movies = movies
        self._build_message_index()
        self._build_movie_index()
        print(f"✓ Search engine ready with {len(messages)} messages and {len(movies)} movies")

    def _tokenize(self, text: str) -> List[str]:
        """
        Convert text to lowercase tokens (words).
        """
        # Remove special characters and split into words
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return words

    def _build_message_index(self):
        """
        Build inverted index for messages.
        Index maps each word to the set of message indices that contain it.
        """
        for idx, message in enumerate(self.messages):
            # Index the message content
            text = message.get("message", "")
            # Also index user_name for better search
            user_name = message.get("user_name", "")
            combined_text = f"{text} {user_name}"

            words = self._tokenize(combined_text)
            for word in words:
                self.message_index[word].add(idx)

    def _build_movie_index(self):
        """
        Build inverted index for movies.
        """
        for idx, movie in enumerate(self.movies):
            # Index title and description
            title = movie.get("title", "")
            description = movie.get("description", "")
            combined_text = f"{title} {description}"

            words = self._tokenize(combined_text)
            for word in words:
                self.movie_index[word].add(idx)

    def search(self, query: str, search_type: str = "all") -> Dict:
        """
        Search for query in messages and/or movies.

        Args:
            query: Search query string
            search_type: "messages", "movies", or "all"

        Returns:
            Dictionary with search results
        """
        if not query or not query.strip():
            return {"messages": [], "movies": []}

        query_words = self._tokenize(query)
        if not query_words:
            return {"messages": [], "movies": []}

        results = {}

        if search_type in ["messages", "all"]:
            message_results = self._search_messages(query_words)
            results["messages"] = message_results

        if search_type in ["movies", "all"]:
            movie_results = self._search_movies(query_words)
            results["movies"] = movie_results

        return results

    def _search_messages(self, query_words: List[str]) -> List[Dict]:
        """
        Search messages using inverted index.
        Returns messages that contain ANY of the query words (OR search).
        """
        matching_indices = set()

        for word in query_words:
            if word in self.message_index:
                matching_indices.update(self.message_index[word])

        # Get the actual message objects
        results = [self.messages[idx] for idx in matching_indices]

        # Score and sort by relevance (how many query words match)
        results = self._score_and_sort(results, query_words, "message")

        return results

    def _search_movies(self, query_words: List[str]) -> List[Dict]:
        """
        Search movies using inverted index.
        """
        matching_indices = set()

        for word in query_words:
            if word in self.movie_index:
                matching_indices.update(self.movie_index[word])

        results = [self.movies[idx] for idx in matching_indices]

        # Score by relevance
        results = self._score_and_sort(results, query_words, "movie")

        return results

    def _score_and_sort(self, results: List[Dict], query_words: List[str], result_type: str) -> List[Dict]:
        """
        Score results by how many query words they contain and sort by score.
        """
        scored_results = []

        for item in results:
            if result_type == "message":
                text = f"{item.get('message', '')} {item.get('user_name', '')}"
            else:  # movie
                text = f"{item.get('title', '')} {item.get('description', '')}"

            text_lower = text.lower()

            # Count how many query words appear in the text
            score = sum(1 for word in query_words if word in text_lower)

            scored_results.append((score, item))

        # Sort by score (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # Return just the items without scores
        return [item for score, item in scored_results]


# Global search engine instance
search_engine = SearchEngine()
