@echo off
cd /d "D:\scraper-project"

python articles_scraper.py

:: Check if file actually changed
git add -A
git diff-index --quiet HEAD -- || (
    git commit -m "Auto-update: %date% %time%"
    git push origin main
)
timeout /t 8