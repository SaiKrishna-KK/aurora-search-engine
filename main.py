"""
Aurora Search Engine API
A fast search engine for messages and movies.
"""

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import Optional
import orjson

from config import settings
from data_fetcher import fetch_all_data
from search_engine import search_engine


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup event: Load all data when the application starts.
    This runs once when the server starts up.
    """
    print("🚀 Starting Aurora Search Engine...")
    print("📡 Fetching data from external API...")

    # Fetch all data
    data = await fetch_all_data()

    # Load data into search engine
    search_engine.load_data(
        messages=data["messages"],
        movies=data["movies"]
    )

    print("✅ Aurora Search Engine is ready!")
    yield
    print("👋 Shutting down...")


# Create FastAPI app with ORJson for faster JSON serialization
app = FastAPI(
    title=settings.APP_NAME,
    description="Fast search API for messages and movies",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG,
    default_response_class=ORJSONResponse
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Brotli compression middleware (20% better compression than GZip)
app.add_middleware(BrotliMiddleware, minimum_size=1000, quality=4)

# Add CORS middleware
if settings.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": "Aurora Search Engine",
        "version": "1.0.0",
        "endpoints": {
            "/search": "Search messages and movies",
            "/docs": "API documentation"
        }
    }


@app.get("/search", response_model=None)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute" if settings.RATE_LIMIT_ENABLED else "1000/minute")
async def search(
    request: Request,
    response: Response,
    q: str = Query(..., description="Search query", min_length=1, max_length=settings.MAX_QUERY_LENGTH),
    type: Optional[str] = Query("all", description="Search type: 'messages', 'movies', or 'all'"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_RESULTS_PER_PAGE, description="Number of results to return")
):
    """
    Search endpoint.

    Args:
        q: Search query string (required)
        type: What to search - "messages", "movies", or "all" (default: "all")
        skip: Number of results to skip for pagination (default: 0)
        limit: Maximum number of results to return (default: 10, max: 100)

    Returns:
        JSON response with search results and metadata
    """
    # Record start time to measure performance
    start_time = time.time()

    # Validate search type
    if type not in ["messages", "movies", "all"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid type. Must be 'messages', 'movies', or 'all'"}
        )

    # Perform search
    results = search_engine.search(query=q, search_type=type)

    # Apply pagination
    paginated_results = {}

    if "messages" in results:
        total_messages = len(results["messages"])
        paginated_messages = results["messages"][skip:skip + limit]
        paginated_results["messages"] = {
            "total": total_messages,
            "items": paginated_messages
        }

    if "movies" in results:
        total_movies = len(results["movies"])
        paginated_movies = results["movies"][skip:skip + limit]
        paginated_results["movies"] = {
            "total": total_movies,
            "items": paginated_movies
        }

    # Calculate query time
    query_time_ms = round((time.time() - start_time) * 1000, 2)

    # Add edge caching headers for CDN/edge caching
    # Aggressive caching: 5 min cache, serve stale for 1 hour while revalidating
    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=3600"
    response.headers["CDN-Cache-Control"] = "public, max-age=300, stale-while-revalidate=3600"
    # Enable early hints for faster browser rendering
    response.headers["Accept-CH"] = "Sec-CH-UA, Sec-CH-UA-Mobile, Sec-CH-UA-Platform"

    # Build response
    response_data = {
        "query": q,
        "type": type,
        "query_time_ms": query_time_ms,
        "results": paginated_results
    }

    return response_data


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "messages_indexed": len(search_engine.messages),
        "movies_indexed": len(search_engine.movies)
    }
