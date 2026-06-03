"""
Fachmodul für den Datenexport.
Ermöglicht es, den Kühlschrankbestand oder Einkaufslisten als CSV oder TXT zu speichern.
"""
import csv

def formatiere_export_zeile(produkt_name: str, menge: float, einheit: str) -> list:
    """
    Bereitet einen Datensatz für den CSV-Export vor, indem Zahlen auf zwei
    Nachkommastellen gerundet und Texte bereinigt werden.

    Args:
        produkt_name (str): Der Name des Produkts.
        menge (float): Die vorhandene oder benötigte Menge.
        einheit (str): Die Maßeinheit.

    Returns:
        list: Eine formatierte Liste für die CSV-Zeile.
    """
    schoene_menge = round(menge, 2)
    sauberer_name = produkt_name.strip().title()
    return [sauberer_name, schoene_menge, einheit]


def exportiere_bestand_als_csv(bestand_liste: list, dateiname: str) -> bool:
    """
    Speichert die übergebene Bestandsliste in einer strukturierten CSV-Datei,
    die in Excel oder anderen Programmen weiterverarbeitet werden kann.

    Args:
        bestand_liste (list): Die Daten aus der Datenbank (Name, Menge, Einheit).
        dateiname (str): Der gewünschte Dateiname (z.B. 'bestand.csv').

    Returns:
        bool: True bei erfolgreichem Export, False bei einem Fehler.
    """
    if not bestand_liste:
        print("Keine Daten zum Exportieren vorhanden.")
        return False

    try:
        # newline='' verhindert leere Zeilen zwischen den Einträgen unter Windows
        with open(dateiname, mode='w', newline='', encoding='utf-8') as datei:
            writer = csv.writer(datei, delimiter=';')
            
            # Kopfzeile schreiben
            writer.writerow(["Produktname", "Menge", "Einheit"])

            # Datenzeilen schreiben
            for produkt, menge, einheit in bestand_liste:
                zeile = formatiere_export_zeile(produkt, menge, einheit)
                writer.writerow(zeile)
                
        return True
    except Exception as fehler:
        print(f"Fehler beim CSV-Export: {fehler}")
        return False


def exportiere_einkaufsliste_als_txt(einkaufsliste: list, dateiname: str) -> bool:
    """
    Erstellt eine simple Textdatei, die man sich z. B. aufs Smartphone 
    schicken kann, um sie im Supermarkt abzuhaken.

    Args:
        einkaufsliste (list): Die benötigten Produkte.
        dateiname (str): Der Name der Textdatei (z.B. 'einkauf.txt').

    Returns:
        bool: True, wenn die Datei fehlerfrei geschrieben wurde.
    """
    if not einkaufsliste:
        return False

    try:
        with open(dateiname, mode='w', encoding='utf-8') as datei:
            datei.write("--- DEIN EINKAUFSZETTEL ---\n\n")
            
            for produkt, menge, einheit in einkaufsliste:
                datei.write(f"[ ] {produkt}: {menge} {einheit}\n")
                
        return True
    except Exception as fehler:
        print(f"Fehler beim TXT-Export: {fehler}")
        return False


# Main-Guard für die isolierte Testbarkeit laut Bewertungsbereich B
if __name__ == "__main__":
    print("--- Isolierter Modultest für export_modul.py ---")
    
    # Testdaten (Simulierter Warenkorb)
    test_daten = [
        ("Milch", 2.0, "Liter"),
        ("Eier", 6.0, "Stück"),
        ("Mehl", 1000.0, "g")
    ]

    import os
    os.makedirs("daten", exist_ok=True) # Zur Sicherheit

    # Test 1: CSV Export
    if exportiere_bestand_als_csv(test_daten, "daten/test_bestand.csv"):
        print("CSV-Export war erfolgreich! Datei 'test_bestand.csv' wurde im Ordner 'daten' erstellt.")

    # Test 2: TXT Export (Einkaufsliste)
    if exportiere_einkaufsliste_als_txt(test_daten, "daten/test_einkauf.txt"):
        print("TXT-Export war erfolgreich! Datei 'test_einkauf.txt' wurde im Ordner 'daten' erstellt.")