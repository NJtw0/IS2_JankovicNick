"""
Fachmodul für die Verarbeitung von Rezepten.
Lädt JSON-Daten, vergleicht sie mit dem Bestand und speichert neue Rezepte ab.
"""
import json
import os
# Wir importieren unsere schlaue Umrechnungsfunktion aus dem Datenbank-Modul!
from .datenbank_modul import normiere_einheit


def lade_rezepte_aus_datei(dateipfad: str = "daten/rezepte.json") -> list:
    """Lädt die Liste aller Rezepte aus der JSON-Datei."""
    try:
        with open(dateipfad, 'r', encoding='utf-8') as datei:
            return json.load(datei)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Fehler beim Lesen der JSON-Datei. Ist das Format korrekt?")
        return []


def ermittle_kochbare_rezepte(rezepte_liste: list, aktueller_bestand: list) -> list:
    """Prüft, welche Rezepte mit dem normierten Kühlschrankbestand kochbar sind."""
    # .strip() sichert uns ab, falls beim Speichern mal ein Leerzeichen übersehen wurde
    bestand_dict = {produkt.strip().lower(): menge for produkt, menge, einheit in aktueller_bestand}
    kochbare_rezepte = []

    for rezept in rezepte_liste:
        kann_gekocht_werden = True
        
        for zutat in rezept.get('zutaten', []):
            # 1. Leerzeichen der KI entfernen!
            zutat_name = zutat.get('name', '').strip().lower()
            rohe_menge = float(zutat.get('menge', 1.0))
            rohe_einheit = zutat.get('einheit', 'Stück')

            # 2. Die Rezept-Zutat in unsere Haupteinheiten (g/ml) umrechnen!
            norm_menge, _ = normiere_einheit(rohe_menge, rohe_einheit)

            # 3. Jetzt fair vergleichen
            if zutat_name not in bestand_dict or bestand_dict[zutat_name] < norm_menge:
                kann_gekocht_werden = False
                break
        
        if kann_gekocht_werden:
            kochbare_rezepte.append(rezept.get('name'))

    return kochbare_rezepte


def speichere_neues_rezept(neues_rezept: dict, dateipfad: str = "daten/rezepte.json") -> bool:
    """Hängt ein neu generiertes Rezept an die JSON-Datei an."""
    if not neues_rezept:
        return False

    try:
        rezepte = lade_rezepte_aus_datei(dateipfad)
        rezepte.append(neues_rezept)
        
        with open(dateipfad, 'w', encoding='utf-8') as datei:
            json.dump(rezepte, datei, indent=4, ensure_ascii=False)
            
        return True
    except Exception as fehler:
        print(f"Fehler beim Speichern in JSON: {fehler}")
        return False