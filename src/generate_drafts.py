import pandas as pd
import os
import glob

def create_email_draft(row):
    name = row.get('Name', 'Inhaber')
    website = row.get('Website', 'Ihrer Website')
    score = row.get('Performance Score', 'N/A')
    address = row.get('Address', 'Ihrem Standort')
    phone = row.get('Phone', 'Ihrer Nummer')
    status = row.get('Lead Status', '')
    
    # Extract city from address if possible
    city = "Ihrer Region"
    if isinstance(address, str):
        parts = address.split(',')
        if len(parts) >= 2:
            city_part = parts[-2].strip()
            city = ''.join([i for i in city_part if not i.isdigit()]).strip()

    lcp = row.get('LCP', 'N/A')
    tbt = row.get('TBT', 'N/A')
    cls = row.get('CLS', 'N/A')
    
    tech_info = ""
    if lcp != "N/A" and lcp != "":
        tech_info = f"""Was das für Sie bedeutet:
- Ladezeit (LCP): {lcp} (Kunden springen oft ab, wenn die Seite nicht sofort lädt)
- Interaktivität (TBT): {tbt} (Die Zeit, in der die Seite auf Klicks gar nicht reagiert)
- Visuelle Stabilität (CLS): {cls} (Inhalte springen beim Laden hin und her)
"""

    if "No Website" in status:
        subject = f"Online-Präsenz von {name} in {city}"
        argument = (
            f"ich bin neulich auf Ihren Betrieb {name} aufmerksam geworden. Mir ist dabei aufgefallen, dass Sie aktuell noch keine eigene Website nutzen.\n\n"
            f"Da ich viel in {city} unterwegs bin, weiß ich, dass viele Kunden heute zuerst kurz auf dem Handy nachschauen, bevor sie anrufen oder vorbeikommen. "
            "Ohne eigene Seite landet man dann oft direkt bei der Konkurrenz, was schade ist."
        )
    else:
        subject = f"Kurze Frage zur Website von {name}"
        
        try:
            score_val = float(score)
            score_display = f"{score_val:.0f}/100"
        except:
            score_display = "nicht optimal"
            
        argument = f"""ich komme ganz aus der Nähe und mir ist bei der Suche nach regionalen Unternehmen in {city} Ihre Website aufgefallen. Ihr Angebot sieht super aus, allerdings ist mir als Webentwickler direkt ins Auge gesprungen, dass Ihre Internetseite ({website}) technisch schon etwas in die Jahre gekommen ist.

Auf dem Smartphone lädt sie leider sehr langsam (Google bewertet die Performance aktuell mit {score_display}) und das Design wirkt, als wäre es schon ein paar Jahre alt. Das ist wirklich schade, weil Ihnen dadurch hier in der Region jeden Tag wertvolle Neukunden abspringen, noch bevor sie Sie überhaupt kontaktiert haben.

Da ich direkt hier aus der Gegend komme, helfe ich lokalen Betrieben dabei, ihre Seiten schnell, unkompliziert und modern auf den neuesten Stand zu bringen – ohne dass es Sie ein Vermögen kostet."""

    email_body = f"""Betreff: {subject}

Hallo,

{argument}

Ich bin Dominik Schenitzki, Informatik-Student, und helfe Betrieben hier in der Region dabei, ihren digitalen Auftritt technisch sauber aufzustellen. Mein Fokus liegt dabei auf schnellen, modernen Seiten, die auch wirklich neue Kunden bringen.

Ich biete Ihnen an, dass wir uns Ihre Seite (oder den Plan für eine neue) mal kurz gemeinsam anschauen. Ich gebe Ihnen eine ehrliche Einschätzung zu den Top-Schwachstellen und wie man diese einfach behebt.

Hätten Sie nächste Woche Zeit für ein kurzes Telefonat?

Beste Grüße,

Dominik Schenitzki
https://dtechsolutions.eu/
"""
    return email_body

def main():
    output_dir = "data/drafts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    csv_files = glob.glob("*_with_emails.csv")
    
    if not csv_files:
        print("Keine Dateien mit E-Mails gefunden. Bitte erst den Scraper laufen lassen.")
        return

    for file in csv_files:
        df = pd.read_csv(file)
        category = file.split('_')[1] # e.g. "Hundefriseur"
        
        for index, row in df.iterrows():
            if row.get('Lead Status') == "Not a Lead":
                continue
                
            email_content = create_email_draft(row)
            
            # Create a safe filename
            safe_name = "".join([c for c in str(row['Name']) if c.isalnum() or c==' ']).rstrip()
            filename = f"{output_dir}/{category}_{safe_name.replace(' ', '_')}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(email_content)
                
        print(f"Entwürfe für {file} erstellt.")

if __name__ == "__main__":
    main()
