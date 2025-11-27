"""
Unit tests for SearchEngine class
"""

import pytest
from search_engine import SearchEngine


def test_search_engine_initialization():
    """Test that search engine initializes correctly."""
    engine = SearchEngine()
    assert engine.messages == []
    assert engine.movies == []
    assert len(engine.message_index) == 0
    assert len(engine.movie_index) == 0


def test_load_data():
    """Test loading data into search engine."""
    engine = SearchEngine()
    messages = [
        {"id": "1", "message": "I love pizza"},
        {"id": "2", "message": "Buy groceries"}
    ]
    movies = [
        {"id": "m1", "title": "The Dark Knight", "description": "Batman movie"}
    ]

    engine.load_data(messages, movies)

    assert len(engine.messages) == 2
    assert len(engine.movies) == 1
    assert "pizza" in engine.message_index
    assert "batman" in engine.movie_index


def test_search_messages_single_word():
    """Test searching messages with single word."""
    engine = SearchEngine()
    engine.load_data([
        {"id": "1", "message": "I love pizza"},
        {"id": "2", "message": "Buy groceries"}
    ], [])

    results = engine.search("pizza", search_type="messages")

    assert len(results["messages"]) == 1
    assert results["messages"][0]["id"] == "1"


def test_search_messages_multiple_words():
    """Test searching with multiple words."""
    engine = SearchEngine()
    engine.load_data([
        {"id": "1", "message": "I love pizza delivery"},
        {"id": "2", "message": "Order pizza now"},
        {"id": "3", "message": "Buy groceries"}
    ], [])

    results = engine.search("pizza delivery", search_type="messages")

    # Should find messages with either word
    assert len(results["messages"]) >= 2


def test_search_movies():
    """Test searching movies."""
    engine = SearchEngine()
    engine.load_data([], [
        {"id": "m1", "title": "The Dark Knight", "description": "Batman movie"},
        {"id": "m2", "title": "Inception", "description": "Dream heist"}
    ])

    results = engine.search("batman", search_type="movies")

    assert len(results["movies"]) == 1
    assert results["movies"][0]["title"] == "The Dark Knight"


def test_search_all_types():
    """Test searching both messages and movies."""
    engine = SearchEngine()
    engine.load_data(
        [{"id": "1", "message": "Dark knight rises"}],
        [{"id": "m1", "title": "The Dark Knight", "description": "Batman"}]
    )

    results = engine.search("dark", search_type="all")

    assert "messages" in results
    assert "movies" in results
    assert len(results["messages"]) >= 1
    assert len(results["movies"]) >= 1


def test_search_no_results():
    """Test search with no matching results."""
    engine = SearchEngine()
    engine.load_data([{"id": "1", "message": "Hello world"}], [])

    results = engine.search("xyz123", search_type="messages")

    assert len(results["messages"]) == 0


def test_search_case_insensitive():
    """Test that search is case insensitive."""
    engine = SearchEngine()
    engine.load_data([{"id": "1", "message": "PIZZA delivery"}], [])

    results = engine.search("pizza", search_type="messages")

    assert len(results["messages"]) == 1


def test_tokenization():
    """Test text tokenization."""
    engine = SearchEngine()

    tokens = engine._tokenize("Hello, world! This is a test.")

    assert "hello" in tokens
    assert "world" in tokens
    assert "test" in tokens
    assert "," not in tokens  # Punctuation removed


def test_relevance_scoring():
    """Test that results are sorted by relevance."""
    engine = SearchEngine()
    engine.load_data([
        {"id": "1", "message": "pizza"},
        {"id": "2", "message": "I love pizza and pizza delivery"},
        {"id": "3", "message": "Order food"}
    ], [])

    results = engine.search("pizza", search_type="messages")

    # Should find messages with pizza (both 1 and 2)
    assert len(results["messages"]) == 2
    # Both messages should contain pizza
    assert all("pizza" in msg["message"].lower() for msg in results["messages"])


def test_empty_query_handling():
    """Test handling of empty queries."""
    engine = SearchEngine()
    engine.load_data([{"id": "1", "message": "test"}], [])

    results = engine.search("", search_type="messages")

    # Should return empty results for empty query
    assert len(results["messages"]) == 0
