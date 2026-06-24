# 📍 Local Lead Generator (Automated Regional Lead Scraper)

*Read this in [English](README.md)*

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![React](https://img.shields.io/badge/React-Next.js-black.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Local Lead Generator** ist eine automatisierte, hocheffiziente Lead-Generierungs-Pipeline, die speziell für lokale Unternehmen und Webentwicklungs-Agenturen entwickelt wurde.

> 🐾 **Origin Story (Entstehungsgeschichte):** Dieses Projekt startete ursprünglich unter dem Namen "AnimalLeadGen" als Nischen-Tool, um regionale Unternehmen rund ums Tier (wie Hundefriseure) zu finden. Da die Pipeline extrem effektiv war, wurde das Projekt zu einem gigantischen Multi-Branchen-Scraper weiterentwickelt, der jeden lokalen Unternehmenssektor analysieren kann.

Das Tool sucht automatisch auf Google Maps nach regionalen Unternehmen (z.B. "Handwerk Darmstadt"), analysiert deren Webpräsenz über Google PageSpeed Insights, extrahiert verifizierte Kontaktdaten und bereitet automatisierte, hochgradig personalisierte Kaltakquise-Kampagnen vor.

## 🚀 Hauptfunktionen

- **Automatisierte Lokale Suche:** Nutzt die Google Places API, um Unternehmen in spezifischen Regionen zu finden.
- **Smarte PageSpeed-Analyse:** Bewertet automatisch die mobile Performance der gefundenen Websites.
- **Intelligenter E-Mail-Scraper:** Durchsucht Startseiten, Impressum und Kontaktseiten und ignoriert dabei aktiv "falsche" Adressen (z.B. `wix.com`, `wordpress.com` oder Bild-Dateiendungen).
- **Automatisierte Outreach-Pipeline:** Generiert hochgradig personalisierte E-Mail-Entwürfe, die passgenau auf die spezifischen Schwachstellen der Website des Leads zugeschnitten sind.
- **Vermeidung von Duplikaten:** Nutzt ein globales Blacklist-System, das sicherstellt, dass bereits bearbeitete Unternehmen bei zukünftigen Suchen komplett übersprungen werden. Das spart API-Kontingente und Zeit.
- **Web-Dashboard:** Eine Next.js-basierte Web-Oberfläche zur reibungslosen Verwaltung der Leads.

## 📈 Entwicklungsverlauf & Verbesserungen

Dieses Projekt wird aktiv weiterentwickelt. Hier sind einige unserer neuesten, großen Verbesserungen:

*   **[Update 1] Intelligenter Duplikat-Filter:** Implementierung eines robusten `global_blacklist.csv`-Systems. Das Skript speichert nun jedes analysierte Unternehmen sofort zwischen, sodass überlappende Suchen keine redundanten API-Limits verbrauchen.
*   **[Update 2] Smarteres E-Mail-Scraping:** `email_scraper.py` wurde komplett überarbeitet. Anstatt alles mit einem `@`-Symbol zu erfassen, überspringt das Skript nun Baukasten-Domains, filtert gängige Bilddateiendungen heraus und priorisiert aktiv E-Mails, die mit der Zieldomain übereinstimmen.
*   **[Update 3] Regionale Mail-Vorlagen:** Die `generate_drafts.py`-Engine wurde aktualisiert, um lokalisiertere, persönlichere E-Mail-Vorlagen zu erstellen, die langsame/veraltete Websites in der spezifischen Region (z.B. Darmstadt) ansprechen.
*   **[Update 4] Sicherheitsüberarbeitung:** Robuste `.env`-Verwaltung für Gmail-App-Passwörter und Google API-Schlüssel integriert.

## 🔒 Sicherheits- & Datenschutzhinweis

**Sicherheit hat für dieses Projekt höchste Priorität.**
*   Alle sensiblen Zugangsdaten, einschließlich Google Places API Keys, Google PageSpeed API Keys und Google Workspace App Passwörter, werden streng über lokale `.env`-Variablen gespeichert.
*   Die `.env`-Datei sowie der gesamte `data/`-Ordner (der die gescrapten CSV-Dateien und Blacklists enthält) sind über die `.gitignore` dauerhaft ausgeschlossen.
*   **Es werden niemals Kundendaten oder API-Schlüssel im öffentlichen Repository preisgegeben.**

## 🛠 Nutzung

1. Suche nach Unternehmen mit `python src/main.py`.
2. Extrahiere verifizierte E-Mails mit `python src/email_scraper.py`.
3. Generiere lokalisierte Outreach-E-Mails mit `python src/generate_drafts.py`.
4. Sende automatisierte E-Mails mit `python src/automated_sender.py`.
