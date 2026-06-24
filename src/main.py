import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
PLACES_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PAGESPEED_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")

def search_businesses(query, location):
    """
    Searches for businesses using Google Places API (Text Search).
    """
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri"
    }
    data = {
        "textQuery": f"{query} in {location}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json().get("places", [])
        else:
            print(f"Error fetching places: {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection error fetching places: {e}")
        return []

def get_pagespeed_score(url):
    """
    Fetches the mobile performance score from Google PageSpeed Insights API.
    """
    if not url:
        return None
    
    # Ensure URL has a scheme
    if not url.startswith("http"):
        url = "https://" + url
        
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={PAGESPEED_KEY}&strategy=mobile"
    try:
        # Increased timeout to 60s as PageSpeed can be slow
        response = requests.get(api_url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
            return score * 100 if score is not None else None
        elif response.status_code == 429:
            print(f"Rate limit hit for {url}. Skipping...")
        elif response.status_code == 400:
             print(f"Invalid URL for PageSpeed test: {url}")
        else:
            print(f"PageSpeed error {response.status_code} for {url}")
    except requests.exceptions.Timeout:
        print(f"Timeout checking {url} (Site might be too slow to test).")
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return None

def evaluate_lead(place):
    """
    Evaluates a business and returns its lead status and score.
    """
    name = place.get("displayName", {}).get("text", "Unknown")
    address = place.get("formattedAddress", "N/A")
    phone = place.get("nationalPhoneNumber", "N/A")
    website = place.get("websiteUri")
    
    lead_status = "Not a Lead"
    performance_score = None
    
    if not website:
        lead_status = "High Priority Lead - No Website"
    else:
        print(f"Analyzing: {name}...")
        # Small delay to avoid hitting Google's rate limits too fast
        time.sleep(1)
        performance_score = get_pagespeed_score(website)
        
        if performance_score is None:
            lead_status = "Check Manually (Analysis Failed)"
        elif performance_score < 60:
            lead_status = "Lead - Poor Performance"
        else:
            lead_status = "Not a Lead (Good Performance)"
            
    return {
        "Name": name,
        "Address": address,
        "Phone": phone,
        "Website": website if website else "None",
        "Lead Status": lead_status,
        "Performance Score": f"{performance_score:.1f}" if performance_score is not None else "N/A"
    }

BLACKLIST_FILE = "data/global_blacklist.csv"

def get_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        return set(pd.read_csv(BLACKLIST_FILE)['Name'].tolist())
    return set()

def update_blacklist(names):
    if not names: return
    new_entries = pd.DataFrame([{"Name": n, "Date": datetime.now().strftime("%Y-%m-%d")} for n in names])
    if os.path.exists(BLACKLIST_FILE):
        new_entries.to_csv(BLACKLIST_FILE, mode='a', header=False, index=False)
    else:
        new_entries.to_csv(BLACKLIST_FILE, index=False)

def main():
    if not PLACES_KEY or not PAGESPEED_KEY:
        print("\n[!] Error: API keys missing in .env file.")
        return

    print("\n--- Business Lead Generator ---")
    query = input("Business type (e.g. Schreinerei): ").strip()
    location = input("Location (e.g. Frankfurt): ").strip()
    
    if not query or not location:
        return

    blacklist = get_blacklist()
    print(f"\nSearching for '{query}' in '{location}'...")
    places = search_businesses(query, location)
    
    if not places:
        print("No businesses found.")
        return

    # Filter places based on blacklist
    new_places = [p for p in places if p.get("displayName", {}).get("text") not in blacklist]
    
    skipped = len(places) - len(new_places)
    if skipped > 0:
        print(f"Skipping {skipped} businesses already in blacklist.")
    
    if not new_places:
        print("All found businesses are already in your blacklist. Try another city or industry.")
        return

    print(f"Found {len(new_places)} new businesses. Analyzing websites...\n")
    
    leads = []
    processed_names = []
    
    for place in new_places:
        lead_info = evaluate_lead(place)
        leads.append(lead_info)
        processed_names.append(lead_info['Name'])
        
    # Sofort alle neu gefundenen Unternehmen in die Blacklist eintragen
    update_blacklist(processed_names)
        
    if leads:
        df = pd.DataFrame(leads)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"data/raw/leads_{query.replace(' ', '_')}_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\nDone! Results saved to: {filename}")
        print(f"Added {len(processed_names)} businesses to the global blacklist so they won't be searched again.")
    else:
        print("No leads found.")

if __name__ == "__main__":
    main()
