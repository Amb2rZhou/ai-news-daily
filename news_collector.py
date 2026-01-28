import time
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from urllib.parse import urljoin

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_rss(feeds, hours=24):
    """Collect articles from RSS feeds published within the last `hours` hours."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    for feed_info in feeds:
        name = feed_info["name"]
        url = feed_info["url"]
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                if published and published < cutoff:
                    continue

                summary = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text(strip=True)[:200]

                articles.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "source": name,
                    "summary": summary,
                    "published": published,
                })
        except Exception as e:
            print(f"[WARN] Failed to fetch RSS '{name}': {e}")

    return articles


def scrape_web(targets):
    """Scrape news headlines from web pages."""
    articles = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for target in targets:
        name = target["name"]
        url = target["url"]
        selector = target["selector"]
        base_url = target.get("base_url", "")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            elements = soup.select(selector)[:15]

            for el in elements:
                title = el.get_text(strip=True)
                link = el.get("href", "")
                if link and not link.startswith("http"):
                    link = urljoin(base_url, link)

                if title:
                    articles.append({
                        "title": title,
                        "link": link,
                        "source": name,
                        "summary": "",
                        "published": None,
                    })
        except Exception as e:
            print(f"[WARN] Failed to scrape '{name}': {e}")

    return articles


def deduplicate(articles, threshold=0.7):
    """Remove duplicate articles based on title similarity."""
    unique = []
    for article in articles:
        is_dup = False
        for existing in unique:
            ratio = SequenceMatcher(
                None, article["title"].lower(), existing["title"].lower()
            ).ratio()
            if ratio > threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(article)
    return unique


def categorize(articles, categories):
    """Categorize articles by matching keywords in title and summary."""
    categorized = {cat: [] for cat in categories}
    categorized["其他"] = []

    for article in articles:
        text = (article["title"] + " " + article.get("summary", "")).lower()
        matched = False
        for cat, keywords in categories.items():
            if any(kw.lower() in text for kw in keywords):
                categorized[cat].append(article)
                matched = True
                break
        if not matched:
            categorized["其他"].append(article)

    # Remove empty categories
    return {cat: arts for cat, arts in categorized.items() if arts}


def collect_all(config_path="config.yaml"):
    """Main collection pipeline: fetch, deduplicate, categorize."""
    config = load_config(config_path)

    print("Collecting RSS feeds...")
    rss_articles = collect_rss(config.get("rss_feeds", []))
    print(f"  Found {len(rss_articles)} articles from RSS")

    print("Scraping web sources...")
    web_articles = scrape_web(config.get("web_scrape_targets", []))
    print(f"  Found {len(web_articles)} articles from web scraping")

    all_articles = rss_articles + web_articles
    print(f"Total articles before dedup: {len(all_articles)}")

    all_articles = deduplicate(all_articles)
    print(f"Total articles after dedup: {len(all_articles)}")

    categories = config.get("categories", {})
    categorized = categorize(all_articles, categories)

    for cat, arts in categorized.items():
        print(f"  [{cat}]: {len(arts)} articles")

    return categorized
