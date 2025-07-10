import feedparser
import requests
import hashlib
import json
import time
import pathlib
import re
from readability import Document
from bs4 import BeautifulSoup
from tqdm import tqdm


FEED_FILE = pathlib.Path("feeds.txt")          
OUT_DIR   = pathlib.Path("data/json")
OUT_DIR.mkdir(parents=True, exist_ok=True)
WS_SPLIT = re.compile(r"\s+")
HEADERS = {"User-Agent": "Mozilla/5.0 (mini-search bot)"}


def clean_html(html: str, url: str) -> str | None:
    """Return clean text or None if unreadable."""
    try:
        doc  = Document(html)
        text = BeautifulSoup(doc.summary(), "lxml").get_text(separator="\n")
        if text.strip():
            return text
    except Exception:
        pass  # fall back below

    # fallback: strip all tags, return raw body text
    soup = BeautifulSoup(html, "lxml")
    body = soup.body.get_text(separator="\n") if soup.body else ""
    return body.strip() or None


def load_feeds() -> dict[str, str]:
    """Parse feeds.txt; whitespace (space or tab) is the separator."""
    feeds: dict[str, str] = {}
    with FEED_FILE.open() as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # split on first run of whitespace
            parts = WS_SPLIT.split(line, maxsplit=1)
            if len(parts) != 2:
                print(f"WARNING: Skipping malformed line: {raw.rstrip()}")
                continue
            name, url = parts
            feeds[name] = url
    return feeds



def scrape_feeds(feeds: dict[str, str], out_dir="data/json"):
    out_path = pathlib.Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for name, url in feeds.items():
        print(f"Fetching feed: {name} …")
        entries = feedparser.parse(url)["entries"]

        # tqdm shows progress through all posts in this feed
        MAXLEN = 20
        COUNTER = 0
        SMALL_CRAWL = False
        for entry in tqdm(entries, desc=f"{name} posts", leave=False):
            if SMALL_CRAWL:
                if COUNTER > MAXLEN:
                    break
                else:
                    COUNTER += 1

            link = entry["link"]
            try:
                resp = requests.get(
                    link,
                    headers=HEADERS,
                    timeout=10,
                    allow_redirects=True,
                )
                if resp.status_code != 200 or not resp.text.strip():
                    print(f"WARNING: Skip {resp.status_code} {link}")
                    continue

                text = clean_html(resp.text, link)
                if not text:
                    print(f"WARNING: Unparseable {link}")
                    continue

            except requests.exceptions.RequestException as e:
                print(f"Error {link}: {e}")
                continue

            fname = hashlib.md5(link.encode()).hexdigest() + ".json"
            with open(out_path / fname, "w") as f:
                json.dump(
                    {"id": link, "title": entry["title"], "body": text},
                    f,
                    ensure_ascii=False
                )
            time.sleep(0.1)


if __name__ == "__main__":
    from pathlib import Path
    feeds = {}
    with Path("feeds.txt").open() as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"): 
                continue
            name, url = WS_SPLIT.split(line, maxsplit=1)
            feeds[name] = url
    scrape_feeds(feeds)
