# 📰 AI Smart Press - Urdu News Scraper & Automation

This project automatically scrapes **Urdu news articles** from top sources like **BBC Urdu**, **ARY News**, and **Express News**, filters recent articles, and stores them in a structured **JSON file**. The data will later be used to train a **multilingual abstractive summarization model (mT5)** for generating Urdu news summaries.

## 🔧 Features

- ✅ Scrapes title, full article, image, and date from Urdu news sites
- ⏱️ Runs **automatically twice daily** using **GitHub Actions**
- 🧠 Prepares data for **mT5 model training**
- 📱 Will be integrated into a **Flutter mobile app**
- 💾 Saves data in `all_articles.json` (latest 300 articles, last 4 days)

## 📂 Tech Stack

- **Python** (Scraper logic)
- **BeautifulSoup** / **Feedparser** (Web scraping)
- **GitHub Actions** (CI/CD automation)
- **JSON** (Data storage)
- **mT5** (Summarization model - coming soon)

## 🛠️ How It Works

1. Parses RSS feeds from news sites.
2. Scrapes article content from URLs.
3. Filters duplicates and old data (keeps last 4 days, max 300 articles).
4. Saves structured data to `all_articles.json`.
5. GitHub Action triggers this script automatically at 8AM and 8PM (PKT).

## 📦 Automation Setup (GitHub Actions)

- The scraper runs via `scrap.yml` workflow.
- No local server or PC needed — it runs in the cloud (GitHub-hosted runner).
- Only the latest articles are kept to keep the file light and relevant.

## 📌 Future Goals

- 🔄 Connect real-time JSON to Flutter app
- 🧠 Train and deploy mT5 summarization model
- 🔊 Add Urdu Text-to-Speech
- 🌐 Host summarizer model via Hugging Face or custom API



