import os
import glob
import pandas as pd
import base64
import requests
import time
from playwright.sync_api import sync_playwright

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava"

def get_screenshot_base64(url, page):
    try:
        # Add scheme if missing
        if not url.startswith('http'):
            url = 'http://' + url
            
        print(f"  [>] Loading {url}...")
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        # Wait a bit for images/fonts to render
        page.wait_for_timeout(2000)
        
        # Take a screenshot
        screenshot_bytes = page.screenshot(type='jpeg', quality=60)
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    except Exception as e:
        print(f"  [!] Failed to load {url}: {e}")
        return None

def evaluate_design_with_ollama(base64_image):
    prompt = """You are an expert web designer. Look at this website. 
Is the design OUTDATED (looks old, from the 2000s or early 2010s, bad UI) or MODERN (clean, current, good UI)? 
Answer strictly with only the word 'OUTDATED' or 'MODERN'. Do not add any other text."""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [base64_image],
        "stream": False
    }
    
    try:
        print("  [>] Analyzing design with local Llava model...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json().get('response', '').strip().upper()
        if "MODERN" in result:
            return "MODERN"
        elif "OUTDATED" in result:
            return "OUTDATED"
        return "UNKNOWN"
    except Exception as e:
        print(f"  [!] Ollama evaluation failed: {e}")
        return "UNKNOWN"

def main():
    print("\n--- AI Vision Design Evaluator ---")
    csv_files = glob.glob("data/raw/*_with_emails.csv")
    
    if not csv_files:
        print("No processed lead files found. Run scraper and email scraper first.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        for file in csv_files:
            print(f"\nProcessing file: {file}")
            df = pd.read_csv(file)
            updated = False
            
            for index, row in df.iterrows():
                status = str(row.get('Lead Status', ''))
                if "Not a Lead" in status:
                    continue # Already rejected
                
                url = str(row.get('Website', ''))
                if not url or url.lower() == 'nan':
                    continue
                
                print(f"\nEvaluating: {row.get('Name')}")
                b64_img = get_screenshot_base64(url, page)
                
                if b64_img:
                    design_judgement = evaluate_design_with_ollama(b64_img)
                    print(f"  [=] AI Verdict: {design_judgement}")
                    
                    if design_judgement == "MODERN":
                        df.at[index, 'Lead Status'] = "Not a Lead (Modern Design)"
                        updated = True
                    elif design_judgement == "OUTDATED":
                        # We append this so the email generator can use it if it wants, 
                        # but it's not strictly necessary. 
                        # We just don't mark it as 'Not a Lead'.
                        df.at[index, 'Lead Status'] = "Lead - Outdated Design"
                        updated = True
            
            if updated:
                df.to_csv(file, index=False)
                print(f"Saved design evaluations to {file}")
            else:
                print("No updates needed for this file.")
                
        browser.close()

if __name__ == "__main__":
    main()
