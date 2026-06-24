import pandas as pd
import requests
import re
import os
import glob
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Regex for finding emails
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

BLACKLISTED_DOMAINS = [
    'wix.com', 'wixpress.com', 'wordpress.com', 'sentry.io', 'example.com', 
    'domain.com', 'email.com', 'google.com', 'sitedomain.com'
]
BLACKLISTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']

def get_emails_from_text(text, base_url):
    raw_emails = list(set(re.findall(EMAIL_REGEX, text)))
    valid_emails = []
    
    domain_name = ""
    if base_url and isinstance(base_url, str):
        domain_name = urlparse(base_url).netloc.replace('www.', '').lower()
        
    for email in raw_emails:
        email = email.lower()
        # Exclude blacklisted domains
        if any(email.endswith(f"@{d}") for d in BLACKLISTED_DOMAINS):
            continue
        # Exclude false positives matching image file extensions
        if any(email.endswith(ext) for ext in BLACKLISTED_EXTENSIONS):
            continue
        valid_emails.append(email)
        
    # Sort valid emails to prioritize those matching the site's domain
    if domain_name:
        valid_emails.sort(key=lambda x: domain_name in x, reverse=True)
        
    return list(set(valid_emails))[:2] # Return max 2 to avoid spam

def find_contact_links(soup, base_url):
    contact_keywords = ['kontakt', 'contact', 'impressum', 'about', 'über', 'legal']
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.lower()
        if any(keyword in text or keyword in href.lower() for keyword in contact_keywords):
            full_url = urljoin(base_url, href)
            # Ensure the link is on the same domain
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
    return list(set(links))

def scrape_website(url):
    # Ensure URL is a string
    if not isinstance(url, str):
        return []
        
    if not url or url == "None" or not url.startswith("http"):
        return []

    print(f"Scraping: {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        emails = get_emails_from_text(response.text, url)
        
        # If no emails on homepage, try contact pages
        if not emails:
            contact_links = find_contact_links(soup, url)
            for link in contact_links[:3]: # Limit to top 3 links
                try:
                    res = requests.get(link, headers=HEADERS, timeout=10)
                    if res.status_code == 200:
                        emails.extend(get_emails_from_text(res.text, url))
                        if emails:
                            break
                except:
                    continue
                    
        return list(set(emails))[:2]
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def main():
    csv_files = glob.glob("data/raw/leads_*.csv")
    if not csv_files:
        print("No CSV files found in data/raw/.")
        return

    for file in csv_files:
        if "_with_emails" in file:
            continue
            
        print(f"\nProcessing file: {file}")
        df = pd.read_csv(file)
        
        if 'Email' not in df.columns:
            df['Email'] = ""

        for index, row in df.iterrows():
            # Only scrape if we have a website and don't have an email yet
            if row['Website'] != "None" and (pd.isna(row['Email']) or row['Email'] == ""):
                found_emails = scrape_website(row['Website'])
                if found_emails:
                    email_str = ", ".join(found_emails)
                    df.at[index, 'Email'] = email_str
                    print(f"  Found: {email_str}")
                else:
                    print("  No email found.")
                
                # Small delay to be polite
                time.sleep(1)

        output_file = file.replace(".csv", "_with_emails.csv")
        # Filter out rows where Email is empty or NaN
        df_with_emails = df[df['Email'].notna() & (df['Email'] != "")]
        df_with_emails.to_csv(output_file, index=False)
        print(f"Updated results saved to: {output_file} (Removed {len(df) - len(df_with_emails)} leads without email)")

if __name__ == "__main__":
    main()
