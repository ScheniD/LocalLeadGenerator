import subprocess
import os
import sys
import pandas as pd
import glob
from datetime import datetime

def run_step(command, description):
    print(f"\n>>> STARTE SCHRITT: {description}")
    try:
        # Wrap sys.executable in quotes to handle paths with spaces
        full_command = f'"{sys.executable}" {command}'
        result = subprocess.run(full_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Fehler in Schritt '{description}': {e}")
        return False

def get_latest_leads_file():
    # Find the newest CSV in the new data/raw directory
    files = [f for f in glob.glob("data/raw/leads_*.csv") if "_with_emails" not in f]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def main():
    print("="*50)
    print("      ANIMAL LEAD GENERATOR - FULL AUTOMATION")
    print("="*50)

    print("\nWas möchten Sie tun?")
    print("1: Neue Suche starten (Full Search)")
    print("2: Nur E-Mails senden (aus bestehender Datei)")
    mode = input("Auswahl (1/2): ") or "1"

    if mode == "1":
        # 1. Lead Search
        print("\n[1] Suche nach neuen Unternehmen...")
        if not run_step("src/main.py", "Lead Suche (Google Places)"):
            return

        # Find the file we just created
        leads_file = get_latest_leads_file()
        if not leads_file:
            print("[!] Keine neue Lead-Datei gefunden.")
            return

        print(f"\nNeue Leads gefunden in: {leads_file}")

        # 2. Email Scraping
        if not run_step("src/email_scraper.py", "E-Mail Adressen suchen"):
            return

        email_file = leads_file.replace(".csv", "_with_emails.csv")

        # 3. Technical Analysis (PageSpeed)
        if not run_step(f"src/enrich_details.py {email_file}", "Webseiten-Analyse (Performance)"):
            return
    else:
        # Direct Sending Mode
        files = glob.glob("data/raw/*_with_emails.csv")
        if not files:
            print("[!] Keine verarbeiteten Dateien in 'data/raw' gefunden.")
            return

        print("\nVerfügbare Dateien:")
        for i, f in enumerate(files):
            print(f"{i+1}: {os.path.basename(f)}")

        f_choice = input(f"Welche Datei nutzen? (1-{len(files)}): ")
        try:
            email_file = files[int(f_choice)-1]
        except:
            print("[!] Ungültige Auswahl.")
            return

    # 4. Automated Sending (Used in both modes)
    print("\n" + "!"*50)
    confirm = input(f"Sollen jetzt Emails an die Leads in '{email_file}' gesendet werden? (j/n): ")
    if confirm.lower() == 'j':
        print("\nWelche Leads möchten Sie kontaktieren?")
        print("1: Alle passenden Leads (Standard)")
        print("2: Nur Unternehmen OHNE Website (High Priority)")
        print("3: Nur Unternehmen mit SCHLECHTEM Performance-Score")
        choice = input("Auswahl (1/2/3): ") or "1"

        type_map = {"1": "all", "2": "no_website", "3": "poor_performance"}
        lead_type = type_map.get(choice, "all")

        limit = input("Wie viele Emails maximal senden? (Standard: 50): ") or "50"
        run_step(f"src/automated_sender.py {email_file} {limit} {lead_type}", f"E-Mail Versand (Filter: {lead_type}, Limit: {limit})")
    else:
        print(f"\nVersand übersprungen. Du findest die Entwürfe im Ordner 'data/drafts'.")

    print("\n" + "="*50)
    print("PROZESS ABGESCHLOSSEN.")
    print("="*50)

if __name__ == "__main__":
    main()
