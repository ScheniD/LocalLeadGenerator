import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
PAGESPEED_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")

def get_detailed_metrics(url):
    # Ensure URL is a string and handle NaN values
    if not isinstance(url, str) or not url or url == "None" or not url.startswith("http"):
        return None
    
    print(f"Deep-Analysis for: {url}...")
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={PAGESPEED_KEY}&strategy=mobile"
    
    try:
        response = requests.get(api_url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            audits = data.get("lighthouseResult", {}).get("audits", {})
            
            # Key Metrics
            lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
            tbt = audits.get("total-blocking-time", {}).get("displayValue", "N/A")
            cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
            speed_index = audits.get("speed-index", {}).get("displayValue", "N/A")
            
            return {
                "LCP": lcp, # Sichtbarkeit des Hauptinhalts
                "TBT": tbt, # Blockierzeit (Interaktivität)
                "CLS": cls, # Visuelle Stabilität
                "SpeedIndex": speed_index
            }
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
    return None

def main():
    import glob
    import sys
    
    if len(sys.argv) > 1:
        files = [sys.argv[1]]
    else:
        files = glob.glob("data/raw/*_with_emails.csv")
    
    for file in files:
        print(f"\nProcessing {file}...")
        df = pd.read_csv(file)
        
        # New columns
        for col in ["LCP", "TBT", "CLS", "SpeedIndex"]:
            if col not in df.columns:
                df[col] = "N/A"
            else:
                df[col] = df[col].astype(str)

        for index, row in df.iterrows():
            # Skip if already contacted or not a lead or no website
            if row.get('Contacted') == "Yes":
                continue

            if row['Website'] != "None" and row['Lead Status'] != "Not a Lead":
                # Check if we already have data to save API calls
                if pd.isna(df.at[index, 'LCP']) or df.at[index, 'LCP'] == "N/A":
                    details = get_detailed_metrics(row['Website'])
                    if details:
                        for key, val in details.items():
                            df.at[index, key] = val
                        print(f"  -> {row['Name']}: LCP: {details['LCP']}, TBT: {details['TBT']}")
                        # Save after each success
                        df.to_csv(file, index=False)
                    else:
                        print(f"  -> {row['Name']}: Failed to get details.")
                    time.sleep(1) # Rate limit protection

        print(f"Updated {file} with technical details.")

if __name__ == "__main__":
    main()
