# ClickHouse Blog Fetcher

Auto-updating static site that displays the 10 most recent blog posts from [clickhouse.com/blog](https://clickhouse.com/blog).

## How it works

- `fetch_posts.py` scrapes the ClickHouse blog listing and individual post pages
- Generates a static `public/index.html` with the latest 10 posts
- GitHub Actions runs daily to keep content fresh
- Deployed on Vercel for instant updates

## Tech

- Python 3 + curl for scraping
- Pure HTML/CSS (zero JS, zero frameworks)
- GitHub Actions for daily refresh
- Vercel for hosting
