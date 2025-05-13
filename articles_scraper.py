import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import hashlib
import json

# Initialize variables
output_file = "all_articles.json"
existing_articles = []
existing_guids = set()

# Load existing articles if file exists
if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            existing_articles = json.load(f)
        existing_guids = {article['guid'] for article in existing_articles}
        print(f"📂 Loaded {len(existing_articles)} existing articles from storage")
    except Exception as e:
        print(f"⚠️ Error loading existing articles: {str(e)}")

all_articles = []

# BBC Urdu Scraper 
def scrape_bbc():
    print("\n📢 Scraping BBC Urdu...")
    RSS_URL = "https://feeds.bbci.co.uk/urdu/rss.xml"
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        guid = entry.id
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid}")
            continue
            
        link = entry.link
        title = entry.title
        pub_date = entry.published if "published" in entry else ""

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(link, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")

            article_body = soup.find_all("p", class_="bbc-1gjryo4 e17g058b0")
            if not article_body:
                print(f"❌ Skipped (No article body): {link}")
                continue

            full_text = "\n".join([p.get_text() for p in article_body])
            meta_img = soup.find("meta", property="og:image")
            image_url = meta_img["content"] if meta_img and meta_img.get("content") else ""

            if full_text.strip():
                all_articles.append({
                    "guid": guid,
                    "title": title,
                    "link": link,
                    "image_url": image_url,
                    "article": full_text.strip(),
                    "published_date": pub_date,
                    "source": "BBC Urdu"
                })
                print(f"✅ Added new article: {title}")
        except Exception as e:
            print(f"⚠️ Error processing BBC article {link}: {str(e)}")

# ARY Urdu Scraper 
def scrape_ary():
    print("\n📢 Scraping ARY Urdu...")
    RSS_URL = "https://urdu.arynews.tv/feed/"
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        guid = entry.link
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid}")
            continue
            
        link = entry.link
        title = entry.title
        pub_date = entry.published if "published" in entry else ""

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(link, headers=headers)
            soup = BeautifulSoup(res.content, "html.parser")

            article_container = soup.find("div", class_="td_block_wrap tdb_single_content tdi_102 td-pb-border-top td_block_template_1 td-post-content tagdiv-type")
            if not article_container:
                print(f"❌ Skipped (No main div): {link}")
                continue

            p_tags = article_container.find_all("p")
            full_text = "\n".join(p.get_text() for p in p_tags)

            meta_img = soup.find("meta", property="og:image")
            image_url = meta_img["content"] if meta_img and meta_img.get("content") else ""

            if full_text.strip():
                all_articles.append({
                    "guid": guid,
                    "title": title,
                    "link": link,
                    "image_url": image_url,
                    "article": full_text.strip(),
                    "published_date": pub_date,
                    "source": "ARY Urdu"
                })
                print(f"✅ Added new article: {title}")
        except Exception as e:
            print(f"⚠️ Error processing ARY article {link}: {str(e)}")

# Express Urdu Scraper 
def scrape_express():
    print("\n📢 Scraping Express Urdu...")
    RSS_URL = "https://www.express.pk/feed/"
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        link = entry.link
        guid = hashlib.md5(link.encode('utf-8')).hexdigest()
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid}")
            continue
            
        title = entry.title
        pub_date = entry.published if "published" in entry else ""

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(link, headers=headers)
            soup = BeautifulSoup(res.content, "html.parser")

            all_p_tags = soup.find_all("span", class_="story-text")
            paragraphs = []
            for div in all_p_tags:
                paragraphs.extend(div.find_all("p"))

            full_text = "\n".join(p.get_text() for p in paragraphs)

            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

            if full_text.strip():
                all_articles.append({
                    "guid": guid,
                    "title": title,
                    "link": link,
                    "image_url": image_url,
                    "article": full_text.strip(),
                    "published_date": pub_date,
                    "source": "Express Urdu"
                })
                print(f"✅ Added new article: {title}")
        except Exception as e:
            print(f"⚠️ Error processing Express article {link}: {str(e)}")

# Execute scrapers
scrape_bbc()
scrape_ary()
scrape_express()

# Combine old and new articles
combined_articles = existing_articles + all_articles

# Save updated list
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined_articles, f, ensure_ascii=False, indent=4)
    print(f"\n🎉 Success! Added {len(all_articles)} new articles. Total articles: {len(combined_articles)}")
except Exception as e:
    print(f"⚠️ Error saving articles: {str(e)}")