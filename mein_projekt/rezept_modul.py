"""
Fachmodul für die Verarbeitung von Rezepten.
"""
import json
import os
from .datenbank_modul import normiere_einheit

BASIS_ORDNER = os.path.dirname(__file__)
STANDARD_REZEPT_PFAD = os.path.join(BASIS_ORDNER, "daten", "rezepte.json")

def skaliere_zutaten(rezept: dict, portionen: int) -> list:
    """Gibt Zutatenliste mit auf gewünschte Portionen skalierten Mengen zurück."""
    original_portionen = int(rezept.get("portionen", 1))
    faktor = portionen / original_portionen

    neue_zutaten = []

    for zutat in rezept.get("zutaten", []):
        neue_zutaten.append({
            "name": zutat["name"],
            "einheit": zutat["einheit"],
            "menge": round(float(zutat["menge"]) * faktor, 2)
        })

    return neue_zutaten

def lade_rezepte_aus_datei(dateipfad: str = STANDARD_REZEPT_PFAD) -> list:
    """Lädt die gespeicherten Rezepte aus der JSON-Datei."""
    try:
        with open(dateipfad, 'r', encoding='utf-8') as datei:
            return json.load(datei)
    except Exception:
        return []


def ermittle_kochbare_rezepte(rezepte_liste: list, aktueller_bestand: list, aktive_portionen: dict = None) -> list:
    """Ermittelt, welche Rezepte mit dem aktuellen Lagerbestand kochbar sind."""
    if aktive_portionen is None:
        aktive_portionen = {}

    bestand_dict = {
        produkt.strip().lower(): menge
        for produkt, menge, einheit in aktueller_bestand
    }

    kochbare_rezepte = []

    for rezept in rezepte_liste:
        kann_gekocht_werden = True
        rezept_name = rezept.get("name")

        original_portionen = int(rezept.get("portionen", 1))
        aktuelle_portionen = aktive_portionen.get(rezept_name, original_portionen)
        faktor = aktuelle_portionen / original_portionen

        for zutat in rezept.get("zutaten", []):
            benoetigte_menge = float(zutat.get("menge", 1.0)) * faktor

            if bestand_dict.get(
                zutat.get("name", "").strip().lower(),
                0
            ) < benoetigte_menge:
                kann_gekocht_werden = False
                break

        if kann_gekocht_werden:
            kochbare_rezepte.append(rezept_name)

    return kochbare_rezepte

def ermittle_fehlende_zutaten(rezept: dict, aktueller_bestand: list, portionen: int = None) -> list:
    """Vergleicht Rezept-Zutaten mit Bestand und gibt fehlende Zutaten zurück."""
    
    if portionen is None:
        portionen = int(rezept.get("portionen", 1))

    bestand_dict = {
        produkt.strip().lower(): menge
        for produkt, menge, einheit in aktueller_bestand
    }

    fehlende = []
    skalierte_zutaten = skaliere_zutaten(rezept, portionen)

    for zutat in skalierte_zutaten:
        z_name = zutat["name"].strip().lower()
        benoetigt = zutat["menge"]
        vorhanden = bestand_dict.get(z_name, 0)

        if vorhanden < benoetigt:
            fehlmenge = benoetigt - vorhanden

            fehlende.append({
                "name": zutat["name"],
                "einheit": zutat["einheit"],
                "menge": round(fehlmenge, 2)
            })

    return fehlende

def baue_rezept_aus_text(name_raw: str, zutaten_raw: str, schritte_raw: str, portionen: int = 1) -> dict:
    """Parst unstrukturierten Text aus der GUI in ein fertiges Rezept-Dictionary."""
    neue_zutaten = []

    for zeile in zutaten_raw.strip().split("\n"):
        if not zeile.strip():
            continue

        teile = zeile.strip().split(maxsplit=2)

        if len(teile) >= 3:
            try:
                neue_zutaten.append({
                    "menge": float(teile[0]),
                    "einheit": teile[1],
                    "name": teile[2]
                })
            except ValueError:
                neue_zutaten.append({
                    "menge": 1.0,
                    "einheit": "Stück",
                    "name": zeile
                })
        else:
            neue_zutaten.append({
                "menge": 1.0,
                "einheit": "Stück",
                "name": zeile
            })

    neue_schritte = [s.strip() for s in schritte_raw.strip().split("\n") if s.strip()]

    return {
        "name": name_raw.strip(),
        "portionen": portionen,
        "zutaten": neue_zutaten,
        "schritte": neue_schritte
    }


def speichere_neues_rezept(neues_rezept: dict, dateipfad: str = STANDARD_REZEPT_PFAD) -> bool:
    """Speichert ein neues Rezept in der JSON-Datei ab."""
    try:
        rezepte = lade_rezepte_aus_datei(dateipfad)
        rezepte.append(neues_rezept)

        os.makedirs(os.path.dirname(dateipfad), exist_ok=True)

        with open(dateipfad, 'w', encoding='utf-8') as datei:
            json.dump(rezepte, datei, indent=4, ensure_ascii=False)

        return True
    except Exception:
        return False


def loesche_rezept(rezept_name: str, dateipfad: str = STANDARD_REZEPT_PFAD) -> bool:
    """Löscht ein Rezept anhand seines Namens sicher aus der JSON-Datei."""
    try:
        rezepte = lade_rezepte_aus_datei(dateipfad)
        neue_liste = [r for r in rezepte if r.get("name") != rezept_name]

        if len(rezepte) == len(neue_liste):
            return False

        with open(dateipfad, 'w', encoding='utf-8') as datei:
            json.dump(neue_liste, datei, indent=4, ensure_ascii=False)

        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("Starte Rezept-Testlauf...")

    demo_rezept = {
        "name": "Test-Pfannkuchen",
        "portionen": 4,
        "zutaten": [
            {"name": "Mehl", "menge": 250.0, "einheit": "g"},
            {"name": "Milch", "menge": 500.0, "einheit": "ml"}
        ],
        "schritte": ["Mischen.", "Braten."]
    }

    demo_bestand = [("Mehl", 1000.0, "g"), ("Milch", 200.0, "ml")]

    print("Speichere Demo-Rezept temporär...")
    test_pfad = "test_rezepte.json"
    speichere_neues_rezept(demo_rezept, test_pfad)

    print("\nPrüfe auf fehlende Zutaten:")
    fehlend = ermittle_fehlende_zutaten(demo_rezept, demo_bestand)

    for z in fehlend:
        print(f" -> Es fehlt noch: {z['menge']} {z['einheit']} {z['name']}")

    print("\nLösche Demo-Rezept...")
    loesche_rezept("Test-Pfannkuchen", test_pfad)
    print("Testlauf erfolgreich beendet.")