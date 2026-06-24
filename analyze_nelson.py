import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")
url = "https://www.thepilatesstudio.de/"
api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={KEY}&strategy=mobile"

print(f"Analyse läuft für {url}...")
try:
    r = requests.get(api_url, timeout=60)
    if r.status_code == 200:
        data = r.json()
        perf = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
        audits = data.get("lighthouseResult", {}).get("audits", {})
        
        print(f"\n--- Ergebnisse ---")
        print(f"Performance Score: {perf*100 if perf is not None else 'N/A'}")
        print(f"LCP: {audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A')}")
        print(f"TBT: {audits.get('total-blocking-time', {}).get('displayValue', 'N/A')}")
        print(f"CLS: {audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')}")
        print(f"Speed Index: {audits.get('speed-index', {}).get('displayValue', 'N/A')}")
    else:
        print(f"Fehler: {r.status_code}")
        print(r.text)
except Exception as e:
    print(f"Fehler bei der Analyse: {e}")
