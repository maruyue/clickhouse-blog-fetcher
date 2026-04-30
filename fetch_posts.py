#!/usr/bin/env python3
"""
Fetch latest 10 blog posts from ClickHouse blog and generate index.html
"""
import subprocess, re, json, sys
from datetime import datetime

BLOG_LIST_URL = "https://clickhouse.com/blog"
BLOG_URL_PREFIX = "https://clickhouse.com"
OUTPUT_FILE = "public/index.html"

def fetch_url(url, max_tries=3):
    """Fetch URL content with retry"""
    for _ in range(max_tries):
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        if result.stdout:
            return result.stdout
    return None

def get_blog_urls(html):
    """Extract blog post URLs from the listing page"""
    urls = re.findall(r'href="(/blog/[^"]+)"', html)
    # Filter out the main blog page and duplicates
    seen = set()
    blog_urls = []
    for u in urls:
        if u != '/blog' and u not in seen and len(u) > 7:
            seen.add(u)
            blog_urls.append(BLOG_URL_PREFIX + u)
    return blog_urls[:15]  # Get a few extra in case some fail

def get_blog_info(url):
    """Fetch individual blog page and extract title, date, description"""
    html = fetch_url(url)
    if not html:
        return None
    
    title = ""
    date_str = ""
    
    # Extract title
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        title = title_match.group(1).replace('| ClickHouse', '').strip()
        title = title.replace('&#x27;', "'").replace('&amp;', '&')
    
    # Look for date in meta tags or JSON-LD
    date_match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
    if date_match:
        date_str = date_match.group(1)[:10]
    
    if not date_str:
        date_match = re.search(r'<time[^>]*datetime="([^"]+)"', html)
        if date_match:
            date_str = date_match.group(1)[:10]
    
    if not date_str:
        date_match = re.search(r'"dateModified"\s*:\s*"([^"]+)"', html)
        if date_match:
            date_str = date_match.group(1)[:10]
    
    # Format date
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            date_str = dt.strftime("%b %d, %Y")
        except:
            pass
    
    return {"title": title, "url": url, "date": date_str}

def main():
    print("Fetching ClickHouse blog listing...")
    html = fetch_url(BLOG_LIST_URL)
    
    if not html:
        print("Failed to fetch blog listing, using fallback URLs")
        # Fallback: manually fetched URLs from earlier
        blog_urls = [
            f"{BLOG_URL_PREFIX}/blog/{slug}" for slug in [
                "clickhousectl-compare-versions",
                "google-next-2026-recap", 
                "pg_clickhouse-whats-new-april-2026",
                "elasticsearch-log-analytics-clickhouse",
                "google-antigravity",
                "google-lakehouse-runtime",
                "google-axion",
                "clickhouse-expands-strategic-collaboration-with-google-cloud",
                "index-sharding-clickhouse-cloud-petabyte-scale-indexing",
                "terraform-ga"
            ]
        ]
    else:
        blog_urls = get_blog_urls(html)
    
    print(f"Found {len(blog_urls)} blog URLs, fetching details...")
    
    posts = []
    for url in blog_urls:
        print(f"  Fetching: {url}")
        info = get_blog_info(url)
        if info and info["title"]:
            posts.append(info)
            print(f"    ✓ {info['title'][:70]}")
        if len(posts) >= 10:
            break
    
    print(f"\nSuccessfully fetched {len(posts)} posts")
    
    # Save to JSON
    with open("public/posts.json", "w") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "posts": posts
        }, f, indent=2, ensure_ascii=False)
    
    # Generate HTML
    generate_html(posts)
    print(f"Generated {OUTPUT_FILE}")

def generate_html(posts):
    cards_html = ""
    for i, post in enumerate(posts):
        date_badge = f'<span class="date">{post["date"]}</span>' if post["date"] else ""
        cards_html += f"""
        <a href="{post['url']}" target="_blank" rel="noopener" class="card">
            <div class="card-number">{i+1:02d}</div>
            <div class="card-content">
                <h2>{post['title']}</h2>
                <div class="card-meta">
                    {date_badge}
                    <span class="source">clickhouse.com →</span>
                </div>
            </div>
        </a>"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest ClickHouse Blog Posts</title>
    <meta name="description" content="The latest 10 blog posts from ClickHouse engineering blog.">
    <meta property="og:title" content="Latest ClickHouse Blog Posts">
    <meta property="og:description" content="Auto-updated daily. The latest 10 posts from the ClickHouse engineering blog.">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 60px 20px 40px;
            text-align: center;
            border-bottom: 2px solid #f0c040;
        }}
        .header h1 {{
            font-size: 2.2rem;
            color: #f0c040;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header .subtitle {{
            color: #a0a0a0;
            font-size: 1rem;
        }}
        .header .logo {{
            margin-bottom: 15px;
            opacity: 0.9;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        .card {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            background: #141414;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 12px;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s ease;
        }}
        .card:hover {{
            border-color: #f0c040;
            background: #1a1a1a;
            transform: translateX(4px);
        }}
        .card-number {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #f0c040;
            min-width: 40px;
            opacity: 0.7;
        }}
        .card-content h2 {{
            font-size: 1.15rem;
            color: #ffffff;
            margin-bottom: 8px;
            line-height: 1.4;
            font-weight: 600;
        }}
        .card-meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.85rem;
            color: #888;
        }}
        .date {{
            color: #f0c040;
            font-weight: 500;
        }}
        .source {{
            color: #666;
            font-size: 0.8rem;
        }}
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #555;
            font-size: 0.85rem;
        }}
        .footer a {{
            color: #f0c040;
            text-decoration: none;
        }}
        .updated {{
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            margin-bottom: 20px;
        }}
        @media (max-width: 600px) {{
            .header h1 {{ font-size: 1.6rem; }}
            .card {{ padding: 16px; gap: 12px; }}
            .card-content h2 {{ font-size: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="8" fill="#f0c040"/>
                <text x="24" y="31" text-anchor="middle" font-size="22" font-weight="800" fill="#0a0a0a">CH</text>
            </svg>
        </div>
        <h1>Latest ClickHouse Blog Posts</h1>
        <p class="subtitle">Auto-updated daily · The 10 most recent posts from clickhouse.com/blog</p>
    </div>
    
    <div class="container">
        <p class="updated">🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
        {cards_html}
    </div>
    
    <div class="footer">
        <p>Content sourced from <a href="https://clickhouse.com/blog" target="_blank">clickhouse.com/blog</a></p>
        <p style="margin-top:4px;">Built with ♥ · <a href="https://github.com/maruyue/clickhouse-blog-fetcher" target="_blank">View on GitHub</a></p>
    </div>
</body>
</html>"""
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()
