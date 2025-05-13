@echo off
cd /d "D:\scraper-project"
python scraper.py
git add -A
git commit -m "Auto-update: New articles %date% %time%"
git push origin main
timeout /t 10