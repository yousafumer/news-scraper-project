import feedparser
import requests
from bs4 import BeautifulSoup
import os
import hashlib
import json
from datetime import datetime, timedelta, timezone  

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"
CUTOFF_DAYS = 4
output_file = "all_articles.json"
MAX_ARTICLES = 300  # Safety cap to prevent bloat

def get_valid_date(date_str):
    """Parse date with UTC timezone"""
    try:
        parsed = datetime.strptime(date_str, DATE_FORMAT).replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)

def clean_existing_articles():
    """Load and filter existing articles with UTC cutoff"""
    existing_articles = []
    existing_guids = set()
    removed_count = 0
    
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
                
            original_count = len(existing_articles)
            cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
            filtered = []
            
            for article in existing_articles:
                try:
                    article_date = get_valid_date(article['published_date'])
                    if article_date > cutoff:
                        filtered.append(article)
                    else:
                        removed_count += 1  
                except Exception as e:
                    print(f"⚠️ Error processing article: {str(e)}")
                    continue  # Keep problematic articles temporarily
                    
            existing_articles = filtered
            existing_guids = {a['guid'] for a in existing_articles}
            print(f"🧹 Removed {removed_count} old articles (kept {len(existing_articles)}/{original_count})")
            
        except Exception as e:
            print(f"🚨 Critical error loading JSON: {str(e)}")
            # Attempt recovery
            if os.path.exists(output_file):
                os.rename(output_file, f"backup_{datetime.now().strftime('%Y%m%d')}.json")
            print("🆕 Starting fresh with empty dataset")
    
    return existing_articles, existing_guids
existing_articles, existing_guids = clean_existing_articles()
all_articles = []


def scrape_bbc():
    print("\n📢 Scraping BBC Urdu...")
    feed = feedparser.parse("https://feeds.bbci.co.uk/urdu/rss.xml")

    for entry in feed.entries:
        guid = entry.id
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid[:15]}...")
            continue
            
        try:
      
            pub_date = get_valid_date(entry.get('published')).strftime(DATE_FORMAT)
            
   
            res = requests.get(entry.link, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            body = "\n".join([p.get_text() for p in soup.find_all("p", class_="bbc-1gjryo4 e17g058b0")])
            
            if body.strip():
                all_articles.append({
                    "guid": guid,
                    "title": entry.title,
                    "link": entry.link,
                    "image_url": (soup.find("meta", property="og:image") or {}).get("content", ""),
                    "article": body.strip(),
                    "published_date": pub_date,
                    "source": "BBC Urdu"
                })
                print(f"✅ Added: {entry.title[:30]}...")
                
        except Exception as e:
            print(f"⚠️ BBC Error: {str(e)}")


def scrape_ary():
    print("\n📢 Scraping ARY Urdu...")
    feed = feedparser.parse("https://urdu.arynews.tv/feed/")

    for entry in feed.entries:
        guid = entry.link
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid[:15]}...")
            continue
            
        try:
            pub_date = get_valid_date(entry.get('published')).strftime(DATE_FORMAT)
            
            res = requests.get(entry.link, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.content, "html.parser")
            container = soup.find("div", class_="td_block_wrap tdb_single_content tdi_102 td-pb-border-top td_block_template_1 td-post-content tagdiv-type")
            
            if container:
                body = "\n".join(p.get_text() for p in container.find_all("p"))
                
                all_articles.append({
                    "guid": guid,
                    "title": entry.title,
                    "link": entry.link,
                    "image_url": (soup.find("meta", property="og:image") or {}).get("content", ""),
                    "article": body.strip(),
                    "published_date": pub_date,
                    "source": "ARY Urdu"
                })
                print(f"✅ Added: {entry.title[:30]}...")
                
        except Exception as e:
            print(f"⚠️ ARY Error: {str(e)}")


def scrape_express():
    print("\n📢 Scraping Express Urdu...")
    feed = feedparser.parse("https://www.express.pk/feed/")

    for entry in feed.entries:
        guid = hashlib.md5(entry.link.encode()).hexdigest()
        if guid in existing_guids:
            print(f"⏩ Skipping duplicate: {guid[:15]}...")
            continue
            
        try:
            pub_date = get_valid_date(entry.get('published')).strftime(DATE_FORMAT)
            
            res = requests.get(entry.link, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.content, "html.parser")
            paragraphs = [p.get_text() for div in soup.find_all("span", class_="story-text") for p in div.find_all("p")]
            
            if paragraphs:
                all_articles.append({
                    "guid": guid,
                    "title": entry.title,
                    "link": entry.link,
                    "image_url": (soup.find("img") or {}).get("src", ""),
                    "article": "\n".join(paragraphs).strip(),
                    "published_date": pub_date,
                    "source": "Express Urdu"
                })
                print(f"✅ Added: {entry.title[:30]}...")
                
        except Exception as e:
            print(f"⚠️ Express Error: {str(e)}")



if __name__ == "__main__":
    existing_articles, existing_guids = clean_existing_articles()
    all_articles = []
    
    scrape_bbc()
    scrape_ary()
    scrape_express()

    try:
        combined = existing_articles + all_articles
        
        # SORT ARTICLES NEWEST FIRST (critical fix)
        combined.sort(key=lambda a: get_valid_date(a['published_date']), reverse=True)
        
        if len(combined) > MAX_ARTICLES:
            combined = combined[:MAX_ARTICLES]  # Keep newest 300
            print(f"⚠️ Truncated to {MAX_ARTICLES} newest articles")
        
        # Now get actual oldest article
        oldest_article = min(get_valid_date(a['published_date']) for a in combined)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=4)
            
        print(f"\n✅ Success! Total articles: {len(combined)}")
        print(f"• Previously kept: {len(existing_articles)}")
        print(f"• Newly added: {len(all_articles)}")
        print(f"• Actual oldest article: {oldest_article.strftime(DATE_FORMAT)}")
        
    except Exception as e:
        print(f"🔥 Critical save error: {str(e)}")