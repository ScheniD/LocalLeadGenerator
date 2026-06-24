# 📍 Local Lead Generator (Automated Regional Lead Scraper)

*Read this in [German / Deutsch](README.de.md)*
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![React](https://img.shields.io/badge/React-Next.js-black.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Local Lead Generator** is an automated, highly efficient lead generation pipeline designed for local businesses and web development agencies. 

> 🐾 **Origin Story:** This project originally started under the name "AnimalLeadGen" as a niche tool to find regional pet-related businesses (like dog groomers / Hundefriseure). As the pipeline proved to be highly effective, it was generalized and scaled into a multi-industry scraper capable of analyzing any local business sector.

The tool automatically searches Google Maps for regional businesses (e.g., "Handwerk Darmstadt"), analyzes their web presence via Google PageSpeed Insights, extracts verified contact data, and prepares automated, highly personalized cold-email campaigns.

## 🚀 Key Features

- **Automated Local Search:** Uses the Google Places API to find businesses in specific regions.
- **Smart PageSpeed Analysis:** Automatically evaluates the mobile performance of found websites.
- **AI Vision Design Evaluator (NEW!):** Automatically spins up a headless browser (Playwright), takes a screenshot of the lead's website, and sends it to a completely free, local Open-Source AI model (Ollama + Llava). If the AI determines the website looks "modern", it removes the lead to avoid embarrassing pitches!
- **Intelligent Email Scraper:** Scrapes the homepage and legal/contact pages while actively ignoring false positives (e.g., `wix.com`, `wordpress.com`, or image extensions).
- **Automated Outreach Pipeline:** Generates highly personalized cold-email drafts tailored to the specific weak points of the lead's website.
- **Duplicate Prevention:** Uses a global blacklist system to ensure that previously processed businesses are completely skipped in future searches, saving API quotas and time.
- **Web Dashboard:** A Next.js-based web interface to manage leads seamlessly.

## 📈 Development History & Improvements

This project is under active development. Here are some of our latest major improvements:

*   **[Update 1] Intelligent Duplicate Filtering:** Implemented a robust `global_blacklist.csv` system. The script now instantly caches every evaluated business, ensuring that overlapping searches don't consume redundant API limits.
*   **[Update 2] Smarter Email Scraping:** Completely overhauled `email_scraper.py`. Instead of capturing everything with an `@` symbol, the script now skips builder domains, filters out common image extensions, and actively prioritizes emails that match the target domain.
*   **[Update 3] Regional Outreach Templates:** Updated the `generate_drafts.py` engine to construct more localized, conversational email templates that highlight slow/outdated websites in the specific area (e.g., Darmstadt).
*   **[Update 4] Security Overhaul:** Integrated robust `.env` handling for Gmail App Passwords and Google API Keys. 

## 🔒 Security & Privacy Notice

**Security is the highest priority for this project.**
*   All sensitive credentials, including Google Places API Keys, Google PageSpeed API Keys, and Google Workspace App Passwords, are stored strictly via local `.env` variables.
*   The `.env` file, as well as the entire `data/` folder (which contains the scraped CSV files and blacklists), are permanently excluded via `.gitignore`. 
*   **No client data or API keys will ever be exposed to the public repository.**

## 🛠 Usage

1. Search for businesses using `python src/main.py`.
2. Extract verified emails using `python src/email_scraper.py`.
3. Generate localized outreach emails using `python src/generate_drafts.py`.
4. Send automated emails via `python src/automated_sender.py`.
