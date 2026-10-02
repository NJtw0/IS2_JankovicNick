"""
Fachmodul für den Daten-Export.
Trennt die Export-Logik strikt von der Benutzeroberfläche (Separation of Concerns).
"""
import csv
import urllib.parse
import webbrowser

def formatiere_export_zeile(produkt_name: str, menge: float, einheit: str) -> list:
    """Bereitet eine Datenzeile für den CSV-Export vor."""
    schoene_menge = round(menge, 2)
    sauberer_name = produkt_name.strip().title()
    return [sauberer_name, schoene_menge, einheit]


def exportiere_bestand_als_csv(bestand_liste: list, dateiname: str) -> bool:
    """Exportiert den übergebenen Bestand als CSV-Datei."""
    if not bestand_liste:
        return False
    try:
        with open(dateiname, mode='w', newline='', encoding='utf-8') as datei:
            writer = csv.writer(datei, delimiter=';')
            writer.writerow(["Produktname", "Menge", "Einheit"])
            for p, m, e in bestand_liste:
                writer.writerow(formatiere_export_zeile(p, m, e))
        return True
    except Exception as fehler:
        print(f"Fehler beim CSV-Export: {fehler}")
        return False


def sende_einkaufsliste_per_mail(liste: list) -> bool:
    """Sendet die Einkaufsliste über den Standard-Mailclient."""
    if not liste:
        return False
    
    body = "Hallo!\n\nHier ist mein aktueller Einkaufszettel:\n\n"
    for prod, menge, einh in liste:
        body += f"- [ ] {menge} {einh} {prod}\n"
        
    try:
        subj = urllib.parse.quote("Mein Einkaufszettel 🛒")
        body_enc = urllib.parse.quote(body)
        webbrowser.open(f"mailto:?subject={subj}&body={body_enc}")
        return True
    except Exception as e:
        print(f"Fehler beim Mail-Export: {e}")
        return False


if __name__ == "__main__":
    # --- ISOLIERTER TESTLAUF FÜR EXPORT-LOGIK ---
    print("Starte Export-Testlauf...")
    
    demo_bestand = [
        ("Vollkornbrot", 1.0, "Stück"),
        ("Hafermilch", 2.5, "Liter"),
        ("Bio-Eier", 10.0, "Stück")
    ]
    test_datei = "demo_export.csv"
    
    print(f"Exportiere {len(demo_bestand)} Artikel nach {test_datei}...")
    if exportiere_bestand_als_csv(demo_bestand, test_datei):
        print("\nExport erfolgreich! Lese Datei zur Kontrolle:")
        print("-" * 30)
        try:
            with open(test_datei, "r", encoding="utf-8") as f:
                print(f.read().strip())
        except Exception as e:
            print(f"Fehler beim Lesen: {e}")
        print("-" * 30)
    else:
        print("Export fehlgeschlagen.")