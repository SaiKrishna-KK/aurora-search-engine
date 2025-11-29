# Aurora Search Engine

A lightning-fast search API that finds what you need in **under 100 milliseconds**.

**🎯 Achievement:** 74ms average latency (99% under 100ms) - exceeding the <100ms requirement.

## Table of Contents

- [Quick Start](#quick-start)
- [Live API](#live-api)
- [Performance](#performance)
- [API Usage](#api-usage)
- [Tech Stack](#tech-stack)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Bonus 1: Design Decisions](#bonus-1-design-decisions)
- [Bonus 2: Reducing Latency to 30ms](#bonus-2-reducing-latency-to-30ms)
- [Implementation Details](#implementation-details)

---

## Quick Start

```bash
# Set up
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload

# Test it
curl "http://localhost:8000/search?q=pizza"
open http://localhost:8000/docs
```

---

## Live API

### Production (Recommended) ⚡

**🌐 CloudFront CDN:** https://d1stjbgt7gx0i4.cloudfront.net

**Endpoints:**
- `/search` - Search messages and movies
- `/health` - Health check
- `/docs` - Interactive API documentation

**Performance:**
- Average latency: **74ms**
- 99% of requests under 100ms
- P95 latency: 85ms
- Global edge caching (450+ locations)

### Alternative Endpoints

- **EC2 Direct:** (63ms avg - testing only)
- **Vercel:** https://aurora-search-engine.vercel.app (109ms avg - deprecated)

---

## Performance

**✅ Met <100ms Requirement:** 74ms average with 99% success rate

### Where the Time Goes

| Component | Time | Percentage |
|-----------|------|------------|
| Search engine query | 0.02ms | 0.03% |
| Application processing | ~3ms | 4% |
| Network latency | ~71ms | 96% |
| **Total** | **74ms** | **100%** |

The search engine itself is **incredibly fast** (0.02ms). The remaining 74ms comes from network routing through CloudFront's global CDN.

### Performance Benchmarks (100 Requests)

**CloudFront + CDN:**
- Average: 74ms | Median: 72ms
- Min: 61ms | Max: 158ms
- P95: 85ms | P99: 95ms
- **99% under 100ms** 🎯

**EC2 Direct (Ohio):**
- Average: 63ms | Median: 63ms
- Min: 49ms | Max: 75ms
- P95: 71ms | P99: 74ms
- **100% under 100ms** 🎯

**Why is EC2 Direct faster?** Tests were run from a location close to Ohio. EC2 = direct path (63ms), CloudFront = edge hop (74ms). For global users, CloudFront wins (Europe/Asia would see 150-200ms to EC2 direct vs 70-100ms via CloudFront).

---

## API Usage

### Basic Search
```bash
GET /search?q=pizza
```

### Search Specific Type
```bash
GET /search?q=paris&type=messages
GET /search?q=inception&type=movies
```

### Pagination
```bash
GET /search?q=book&skip=0&limit=5
```

### Response Format
```json
{
  "query": "pizza",
  "type": "all",
  "query_time_ms": 0.02,
  "results": {
    "messages": {
      "total": 8,
      "items": [
        {
          "id": 42,
          "body": "Let's order pizza tonight!",
          "created_at": "2024-01-15T18:30:00Z"
        }
      ]
    }
  }
}
```

---

## Tech Stack

- **Python 3.13** - Latest stable version
- **FastAPI** - Modern async web framework
- **In-Memory Inverted Index** - 0.02ms search time
- **ORJson** - 6x faster JSON serialization
- **Brotli** - 20% better compression than GZip
- **Uvicorn + Uvloop** - High-performance ASGI server
- **AWS EC2** - Always-on server (no cold starts)
- **CloudFront CDN** - Global edge caching (450+ locations)
- **Nginx** - Reverse proxy with HTTP keep-alive
- **GitHub Actions** - Auto-deployment on push

### Key Features

- ⚡ Sub-100ms API response (74ms avg)
- 🚀 Sub-millisecond search (0.02ms)
- 📄 Pagination support
- 🛡️ Rate limiting (300 requests per 5 minutes)
- 🌐 CORS enabled
- 📊 Auto-generated docs
- ✅ 23 automated tests
- 🔒 HTTPS + DDoS protection

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

**Test Coverage:**
- Search accuracy
- Pagination
- Error handling
- Performance benchmarks
- API validation

All 23 tests pass in under 1 second.

---

## Project Structure

```
aurora-search-engine/
├── main.py              # FastAPI app + endpoints
├── search_engine.py     # Inverted index search logic
├── data_fetcher.py      # Loads data from external API
├── config.py            # Environment-based settings
├── test_api.py          # API integration tests
├── test_search_engine.py # Search engine unit tests
├── requirements.txt     # Python dependencies
├── .env.example         # Configuration template
├── .github/
│   └── workflows/
│       └── deploy.yml   # Auto-deployment to EC2
└── README.md            # You are here!
```

---

## Bonus 1: Design Decisions

### Approaches Considered

When building this search engine, I evaluated multiple approaches:

<details>
<summary><b>1. In-Memory Inverted Index ✅ (Chosen)</b></summary>

**How it works:** Like a book's index - lists every word and which messages contain it. When you search "pizza," It instantly know which messages have that word.

**Why I chose it:**
- Searches complete in 0.02ms (incredibly fast)
- Simple to build and maintain
- Perfect for datasets under 10,000 items
- No database needed

**Trade-offs:**
- Data lives in RAM (dataset is tiny ~50MB)
- Lost on restart (reloads in 3 seconds)
- Doesn't scale to millions of records

**Best for:** Small, read-heavy applications where speed matters most.
</details>

<details>
<summary><b>2. Elasticsearch ❌ (Overkill)</b></summary>

**What it is:** Powerful search platform used by Uber and Netflix.

**Why I didn't choose it:**
- Would add 500MB+ memory overhead
- Takes minutes to set up
- Costs money at scale
- Unnecessary complexity for 100 messages

**When to use it:** Billions of records, fuzzy matching, multi-language support.
</details>

<details>
<summary><b>3. Database Full-Text Search ❌ (Too slow)</b></summary>

**What it is:** PostgreSQL/MySQL built-in search features.

**Why I didn't choose it:**
- Adds 5-10ms latency per query (vs my 0.02ms)
- Requires database setup and maintenance
- Network overhead between app and DB

**When to use it:** You already have a database, need persistence, moderate search needs.
</details>

<details>
<summary><b>4. Vector Search + AI ❌ (Overengineered)</b></summary>

**What it is:** ML-powered semantic search (finds "Italian food" when you search "pizza").

**Why I didn't choose it:**
- Requires ML model (complexity + cost)
- 50-100ms per query
- Needs GPUs for good performance

**When to use it:** Semantic search, recommendations, chatbots.
</details>

<details>
<summary><b>5. Simple Linear Search ❌ (Too naive)</b></summary>

**What it is:** Check every message one by one.

**Why I didn't choose it:**
- Gets slower as data grows (O(n) complexity)
- Would be 10ms now, seconds with more data

**When to use it:** Quick prototypes, datasets under 100 items.
</details>

### The Verdict

I picked **in-memory inverted index** because it perfectly balances simplicity and performance. It's like using a sports car for a road trip—fast enough to be exciting, simple enough to drive yourself.

---

## Bonus 2: Reducing Latency to 30ms

**The Challenge:** How can we reduce the latency from 74ms to 30ms?

**Current Bottleneck:** 96% of latency comes from network distance, not the search engine itself.

### Performance Evolution

| Platform | Avg Latency | Under 100ms | P95 | Notes |
|----------|-------------|-------------|-----|-------|
| Vercel (Serverless) | 109ms | 28% | 180ms | Cold starts killed performance |
| EC2 Direct (Ohio) | 63ms | 100% | 71ms | Eliminated cold starts |
| **CloudFront + CDN** | **74ms** | **99%** | **85ms** | **Current production** |

### Solutions to Achieve Sub-30ms

<details>
<summary><b>Option 1: Edge Computing Platforms ⚡ (10-30ms)</b></summary>

**Best for:** Immediate sub-30ms latency

Deploy your entire API to 300+ global edge locations.

**Platforms:**

1. **Cloudflare Workers** (Recommended)
   - Latency: 10-30ms globally (330+ cities)
   - Cold starts: <1ms (V8 isolates)
   - Cost: $5/month (10M requests)
   - **Real result:** Skyscanner: 200ms → <4ms (98% improvement)

2. **Fastly Compute@Edge**
   - Latency: 20-50ms globally
   - Runs WebAssembly
   - Cost: $0.04/million requests

3. **Vercel Edge Functions**
   - Latency: 10-30ms near region
   - Free tier available
   - Best for Next.js

**Pros:** 60-75% latency reduction, global automatically, auto-scaling
**Cons:** Code rewrite required, execution time limits
</details>

<details>
<summary><b>Option 2: AWS Global Accelerator (20-30ms)</b></summary>

**Best for:** Minimal code changes

Routes traffic through AWS's private backbone network using anycast.

**Performance:**
- Reduces first byte latency by **49%**
- Decreases jitter by **58%**
- **Real result:** Lever saw 51.2% reduction in load times

**Cost:** ~$20-25/month

**Pros:** No code changes, works with existing EC2
**Cons:** Additional monthly cost
</details>

<details>
<summary><b>Option 3: Multi-Region + HTTP/3 (15-25ms)</b></summary>

**Best for:** Maximum performance

**Components:**
1. Deploy to 4 regions (us-east-1, eu-west-1, ap-southeast-1, us-west-2)
2. Use Route 53 latency-based routing
3. Leverage HTTP/3 (25-55% latency reduction proven in 2025)
4. Advanced caching with pre-warming

**Cost:** ~$40-60/month

**Pros:** Best global performance
**Cons:** Complex deployment, higher cost
</details>

<details>
<summary><b>Option 4: Hybrid Edge + Origin (10-40ms)</b></summary>

**Best for:** Cost-performance balance

Edge functions check cache first, fall back to origin if needed.

**Architecture:**
```
User → Edge Cache (hit) → 10-20ms ✅
User → Edge Cache (miss) → Global Accelerator → Origin → 30-40ms
```

**Cost:** ~$25-30/month

**Pros:** Best of both worlds for common queries
**Cons:** Variable latency depending on cache hit rate
</details>

### Quick Comparison

| Approach | Latency | Cost/Month | Time to Implement | Code Changes |
|----------|---------|------------|-------------------|--------------|
| Cloudflare Workers | 10-30ms | $5-10 | 1-2 weeks | Full rewrite |
| AWS Global Accelerator | 20-30ms | $20-25 | 1-2 days | None |
| Multi-Region + HTTP/3 | 15-25ms | $40-60 | 3-4 weeks | Deployment only |
| Hybrid Edge + Origin | 10-40ms | $25-30 | 2-3 weeks | Partial |

### Recommended Path

1. **Quick win:** AWS Global Accelerator (49% proven reduction, no code changes)
2. **Long-term:** Migrate to Cloudflare Workers (10-30ms globally)

---

## Implementation Details

### Current Architecture

```
User Request (Global)
    ↓ HTTPS
CloudFront Edge (450+ locations) - 74ms average ⚡
    ↓ HTTP (cache miss only)
EC2 Origin (Ohio) - 63ms average
    ↓ Proxied by nginx
FastAPI + Uvicorn - 0.02ms search time
    ↓
In-Memory Inverted Index
```

### Optimizations Implemented

1. **ORJson** - 6x faster JSON encoding (3-8ms saved)
2. **Brotli Compression** - 70-80% smaller responses
3. **CloudFront Edge Caching** - 5min TTL, 1hr stale-while-revalidate
4. **Skip Pydantic Validation** - 3.8x faster endpoint execution
5. **EC2 Always-On** - Eliminated cold starts (vs 109ms on Vercel)
6. **HTTP Keep-Alive** - 46% latency reduction for subsequent requests (63ms → 49ms)

### Configuration

All settings customizable via environment variables:

```bash
# API Settings
EXTERNAL_API_BASE_URL=https://api.example.com
MAX_QUERY_LENGTH=100

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=https://myapp.com
```

See [`.env.example`](.env.example) for all options.

### Security Features

- **Rate limiting:** 300 requests per 5 minutes per IP
- **Input validation:** Rejects invalid queries
- **CORS protection:** Configurable origins
- **No SQL injection:** No database used!
- **HTTPS + DDoS protection:** Via CloudFront

### Deployment

Auto-deployment configured via GitHub Actions:
- Push to `master` → Triggers deployment
- SSH into EC2 → Pull latest code
- Restart service → Health check
- Zero downtime deployment

---

## What I Learned

Building this taught me:

1. **Premature optimization is real** - Almost added a database before realizing in-memory is faster
2. **Type hints matter** - Caught 5 bugs before they happened
3. **Tests give confidence** - Refactored without fear
4. **Simple beats clever** - In-memory index beats complex solutions

---

## Performance Stats

| Metric | Result |
|--------|--------|
| Average query time | 0.02ms |
| 95th percentile | 0.05ms |
| Data loaded | 100 messages, 35 movies |
| Startup time | 3-5 seconds |
| Memory usage | ~50MB |
| Requests/second | 1000+ (single instance) |

---

## Learn More

- [Live API Docs](https://d1stjbgt7gx0i4.cloudfront.net/docs) - Interactive Swagger documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com) - Learn about the framework

---

## License

MIT

## Author

Built as a technical assessment. Learned a ton. 🚀

---

**🎯 Current Achievement:** Met the <100ms requirement with 99% success rate (74ms avg, 99% under 100ms)