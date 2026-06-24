import os
import yagmail
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD") # User needs to create an "App Password"

def send_outreach_email(recipient_email, subject, body, lead_name):
    """
    Sends an email using yagmail.
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("[!] Gmail credentials missing in .env")
        return False

    try:
        yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=body
        )
        print(f"  [OK] Email sent to: {lead_name} ({recipient_email})")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to send to {lead_name}: {e}")
        return False

BLACKLIST_FILE = "data/global_blacklist.csv"

def update_blacklist(lead_name):
    """
    Adds a lead name to the global blacklist to prevent duplicate outreach.
    """
    new_entry = pd.DataFrame([{"Name": lead_name, "Date": time.strftime("%Y-%m-%d")}])
    if os.path.exists(BLACKLIST_FILE):
        new_entry.to_csv(BLACKLIST_FILE, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(BLACKLIST_FILE, index=False)

def process_and_send(csv_file, limit=50, lead_type="all"):
    """
    Reads leads from CSV, filters them based on type, and sends emails.
    lead_type options: "all", "no_website", "poor_performance"
    """
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    
    # Base filter: Must have an email and not be marked "Not a Lead"
    mask = (
        (df['Lead Status'].str.contains("Lead", na=False)) & 
        (df['Email'].notna()) & 
        (df['Email'] != "")
    )
    
    # Specific filters
    if lead_type == "no_website":
        mask = mask & (df['Lead Status'].str.contains("No Website", na=False))
        print(">>> Filter: Nur Unternehmen OHNE Website.")
    elif lead_type == "poor_performance":
        mask = mask & (df['Lead Status'].str.contains("Poor Performance", na=False))
        print(">>> Filter: Nur Unternehmen mit SCHLECHTEM Score.")
    
    leads_to_contact = df[mask]
    
    print(f"\nFilter angewendet: {len(leads_to_contact)} passende Leads mit E-Mail gefunden.")
    
    sent_count = 0
    for index, row in leads_to_contact.iterrows():
        # Check if already contacted in this specific file
        if row.get('Contacted') == "Yes":
            continue

        if sent_count >= limit:
            print(f"\nReached limit of {limit} emails for this run.")
            break
            
        # We use the existing logic from generate_drafts.py but integrated
        from generate_drafts import create_email_draft
        
        full_draft = create_email_draft(row)
        
        # Split subject and body
        lines = full_draft.split('\n')
        subject = lines[0].replace("Betreff: ", "").strip()
        body = "\n".join(lines[2:]) # Skip subject and empty line
        
        emails = [e.strip() for e in str(row['Email']).split(',')]
        primary_email = emails[0] # Take the first found email
        
        success = send_outreach_email(primary_email, subject, body, row['Name'])
        if success:
            sent_count += 1
            # Update CSV to mark as contacted
            df.at[index, 'Contacted'] = "Yes"
            df.at[index, 'Contacted_At'] = time.strftime("%Y-%m-%d %H:%M:%S")
            # Also update Global Blacklist
            update_blacklist(row['Name'])
        
        # Polite delay between emails
        time.sleep(5)
    
    # Save progress back to CSV
    df.to_csv(csv_file, index=False)
    print(f"\nFinished. Sent {sent_count} emails.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python automated_sender.py <leads_csv_file> [limit] [lead_type]")
    else:
        csv_file = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        lead_type = sys.argv[3] if len(sys.argv) > 3 else "all"
        process_and_send(csv_file, limit, lead_type)
