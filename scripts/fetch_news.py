#!/usr/bin/env python3
"""Fetch AI/tech/world news from Google News RSS feeds and write data.json. Stdlib only."""
import json, re, sys, time, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

BLOCKED_SOURCES = ("facebook", "instagram", "threads.net", "biggo", "tiktok", "pinterest")

FEEDS = {
    "ai": ("الذكاء الاصطناعي", [
        ("https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1+%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A+when:2d&hl=ar&gl=EG&ceid=EG:ar", "ar"),
        ("https://news.google.com/rss/search?q=artificial+intelligence+OR+OpenAI+OR+ChatGPT+when:1d&hl=en-US&gl=US&ceid=US:en", "en"),
    ]),
    "tech": ("التكنولوجيا", [
        ("https://news.google.com/rss/search?q=%D8%AA%D9%83%D9%86%D9%88%D9%84%D9%88%D8%AC%D9%8A%D8%A7+OR+%D8%AA%D9%82%D9%86%D9%8A%D8%A9+when:2d&hl=ar&gl=EG&ceid=EG:ar", "ar"),
        ("https://news.google.com/rss/search?q=technology+when:1d&hl=en-US&gl=US&ceid=US:en", "en"),
    ]),
    "tools": ("أدوات ذكية", [
        ("https://news.google.com/rss/search?q=AI+tools+OR+%22AI+app%22+when:3d&hl=en-US&gl=US&ceid=US:en", "en"),
        ("https://news.google.com/rss/search?q=%D8%A3%D8%AF%D9%88%D8%A7%D8%AA+%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1+%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A+when:7d&hl=ar&gl=EG&ceid=EG:ar", "ar"),
    ]),
    "inventions": ("اختراعات وابتكارات", [
        ("https://news.google.com/rss/search?q=%D8%A7%D8%AE%D8%AA%D8%B1%D8%A7%D8%B9+OR+%D8%A7%D8%A8%D8%AA%D9%83%D8%A7%D8%B1+when:3d&hl=ar&gl=EG&ceid=EG:ar", "ar"),
        ("https://news.google.com/rss/search?q=invention+OR+breakthrough+when:2d&hl=en-US&gl=US&ceid=US:en", "en"),
    ]),
    "world": ("أخبار العالم", [
        ("https://news.google.com/rss?hl=ar&gl=EG&ceid=EG:ar", "ar"),
        ("https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en", "en"),
    ]),
}

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) news-fetcher/1.0"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def clean_title(title, source):
    if source and title.endswith(" - " + source):
        title = title[: -(len(source) + 3)]
    return title.strip()

def main():
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "categories": []}
    for cid, (name, urls) in FEEDS.items():
        seen, items = set(), []
        for url, lang in urls:
            try:
                root = ET.fromstring(fetch(url))
            except Exception as e:
                print(f"feed failed {url}: {e}", file=sys.stderr)
                continue
            for it in root.iter("item"):
                t = it.find("title")
                if t is None or not t.text:
                    continue
                src_el = it.find("source")
                source = (src_el.text or "").strip() if src_el is not None else ""
                if any(b in source.lower() for b in BLOCKED_SOURCES):
                    continue
                title = clean_title(t.text, source)
                key = re.sub(r"\W+", "", title.lower())[:80]
                if not key or key in seen:
                    continue
                seen.add(key)
                link_el = it.find("link")
                pub = it.find("pubDate")
                try:
                    dt = parsedate_to_datetime(pub.text).astimezone(timezone.utc).isoformat() if pub is not None and pub.text else ""
                except Exception:
                    dt = ""
                items.append({"title": title, "link": link_el.text if link_el is not None else "",
                              "source": source, "date": dt, "lang": lang})
        items.sort(key=lambda x: x["date"], reverse=True)
        out["categories"].append({"id": cid, "name": name, "items": items[:40]})
        print(f"{cid}: {len(items)} items")
        time.sleep(1)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote data.json")

if __name__ == "__main__":
    main()
