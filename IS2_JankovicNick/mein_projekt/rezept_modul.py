"""
Fachmodul für die Verarbeitung von Rezepten.
Liest die statischen Rezeptdaten ein und vergleicht sie mit dem Kühlschrankbestand.
"""
import json

def lade_rezepte_aus_datei(dateipfad: str) -> list:
    """
    Liest die Rezeptsammlung aus einer angegebenen JSON-Datei ein.
    
    Args:
        dateipfad (str): Der relative oder absolute Pfad zur JSON-Datei.
        
    Returns:
        list: Eine Liste von Dictionaries, die die Rezepte repräsentieren.
    """
    try:
        with open(dateipfad, 'r', encoding='utf-8') as datei:
            rezepte_daten = json.load(datei)
            return rezepte_daten
    except FileNotFoundError:
        print(f"Fehler: Die Datei {dateipfad} wurde nicht gefunden.")
        return []

def wandle_bestand_in_dictionary(bestand_liste: list) -> dict:
    """
    Hilfsfunktion, die die Datenbank-Liste (produkt_name, menge, einheit)
    in ein Dictionary umwandelt, um schnellere Zugriffe zu ermöglichen.
    
    Args:
        bestand_liste (list): Die Ausgabe aus datenbank_modul.hole_kuehlschrank_bestand().
        
    Returns:
        dict: Ein Dictionary der Form {'produkt_name': menge}.
    """
    bestand_dict = {}
    for produkt_name, menge, einheit in bestand_liste:
        bestand_dict[produkt_name] = menge
    return bestand_dict

def ermittle_kochbare_rezepte(rezepte_daten: list, aktueller_bestand: list) -> list:
    """
    Prüft für jedes Rezept, ob alle benötigten Zutaten in ausreichender Menge
    im Kühlschrank vorhanden sind.
    
    Args:
        rezepte_daten (list): Die eingelesenen JSON-Rezepte.
        aktueller_bestand (list): Die Liste der aktuellen Kühlschrank-Inhalte.
        
    Returns:
        list: Eine Liste mit den Namen der Rezepte, die sofort kochbar sind.
    """
    bestand_dict = wandle_bestand_in_dictionary(aktueller_bestand)
    kochbare_rezepte = []

    for rezept in rezepte_daten:
        ist_komplett_kochbar = True
        
        for zutat in rezept["zutaten"]:
            benoetigte_menge = zutat["menge"]
            # Holt die vorhandene Menge; falls nicht im Kühlschrank, dann 0.0
            vorhandene_menge = bestand_dict.get(zutat["name"], 0.0)
            
            if vorhandene_menge < benoetigte_menge:
                ist_komplett_kochbar = False
                break # Eine fehlende Zutat reicht, um das Rezept auszuschließen
                
        if ist_komplett_kochbar:
            kochbare_rezepte.append(rezept["name"])
            
    return kochbare_rezepte

# Isolierter Testblock gemäß Prüfungsanforderungen
if __name__ == "__main__":
    print("--- Isolierter Modultest für rezept_modul.py ---")
    
    # 1. Wir mocken (simulieren) den Kühlschrankbestand, um die DB nicht zwingend zu brauchen
    test_bestand = [
        ("Spaghetti", 500.0, "g"),
        ("Speck", 150.0, "g"),
        ("Ei", 4.0, "Stück"),
        ("Parmesan", 100.0, "g"),
        ("Milch", 1.0, "Liter")
    ]
    
    # 2. Wir mocken ein kleines Rezeptbuch direkt als Variable,
    # um das Modul auch ohne die .json Datei sofort testbar zu machen.
    test_rezepte = [
        {
            "name": "Spaghetti Carbonara",
            "zutaten": [
                {"name": "Spaghetti", "menge": 200, "einheit": "g"},
                {"name": "Speck", "menge": 100, "einheit": "g"},
                {"name": "Ei", "menge": 2, "einheit": "Stück"},
                {"name": "Parmesan", "menge": 50, "einheit": "g"}
            ]
        },
        {
            "name": "Pancakes",
            "zutaten": [
                {"name": "Mehl", "menge": 200, "einheit": "g"},
                {"name": "Milch", "menge": 0.3, "einheit": "Liter"}
            ]
        }
    ]
    
    # 3. Logik testen
    ergebnis = ermittle_kochbare_rezepte(test_rezepte, test_bestand)
    print(f"Vorhandener Bestand: {test_bestand}")
    print(f"Davon kochbare Rezepte: {ergebnis}")
    # Erwartung: Carbonara ist kochbar, Pancakes nicht (Mehl fehlt).