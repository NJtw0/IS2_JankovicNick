"""
Einstiegspunkt der Anwendung. Wird bei python -m mein_projekt ausgeführt.
Koordiniert alle Fachmodule, enthält aber keine eigene Fachlogik.
"""
# Standard-Bibliotheken
import os

# Relative Imports deiner eigenen Fachmodule (Pflicht für Bereich C)
from .datenbank_modul import init_datenbank, kuehlschrank_bestand_aktualisieren, hole_kuehlschrank_bestand
from .ocr_modul import lese_text_aus_bild, bereinige_erkannten_text, extrahiere_zutaten_liste
from .rezept_modul import lade_rezepte_aus_datei, ermittle_kochbare_rezepte
from .visualisierung_modul import erstelle_bestand_balkendiagramm
from .export_modul import exportiere_bestand_als_csv


def bereite_ordner_vor() -> None:
    """Hilfsfunktion: Stellt sicher, dass die Arbeitsordner existieren."""
    os.makedirs("daten", exist_ok=True)
    os.makedirs("bilder", exist_ok=True)


def main() -> None:
    """Orchestriert den gesamten Programmablauf (Der Dirigent)."""
    print("=== Bestandsmanagement-System & Rezept-Checker ===")
    
    # 1. Infrastruktur sichern
    bereite_ordner_vor()
    init_datenbank()
    print("[OK] Datenbank initialisiert.")

    # 2. Wir füllen den Kühlschrank beispielhaft auf (simulierter Einkauf)
    print("\n--- Schritt 1: Einkauf einräumen ---")
    kuehlschrank_bestand_aktualisieren("Milch", 2.0, "Liter")
    kuehlschrank_bestand_aktualisieren("Spaghetti", 500.0, "g")
    kuehlschrank_bestand_aktualisieren("Speck", 150.0, "g")
    kuehlschrank_bestand_aktualisieren("Ei", 4.0, "Stück")
    kuehlschrank_bestand_aktualisieren("Parmesan", 100.0, "g")
    
    aktueller_bestand = hole_kuehlschrank_bestand()
    print(f"Kühlschrank enthält: {len(aktueller_bestand)} verschiedene Produkte.")

    # 3. OCR: Rezeptbild verarbeiten
    print("\n--- Schritt 2: Neues Rezept scannen ---")
    bild_pfad = "bilder/test_rezept.jpg"
    
    # Prüfen, ob der Nutzer schon ein Bild in den Ordner gelegt hat
    if os.path.exists(bild_pfad):
        rohtext = lese_text_aus_bild(bild_pfad)
        zeilen = bereinige_erkannten_text(rohtext)
        gefundene_zutaten = extrahiere_zutaten_liste(zeilen)
        print("Erkannte Zutaten auf dem Bild:", gefundene_zutaten)
    else:
        print(f"Leg ein Bild unter '{bild_pfad}' ab, um den OCR-Scan live zu testen!")

    # 4. JSON-Abgleich: Was können wir heute kochen?
    print("\n--- Schritt 3: Rezeptabgleich ---")
    rezept_pfad = "daten/rezepte.json"
    
    # Wir legen dynamisch eine kleine Test-JSON an, falls sie noch nicht existiert
    if not os.path.exists(rezept_pfad):
        import json
        with open(rezept_pfad, 'w', encoding='utf-8') as f:
            json.dump([
                {"name": "Spaghetti Carbonara", "zutaten": [
                    {"name": "Spaghetti", "menge": 200, "einheit": "g"},
                    {"name": "Speck", "menge": 100, "einheit": "g"}
                ]}
            ], f)
            
    rezepte_daten = lade_rezepte_aus_datei(rezept_pfad)
    kochbar = ermittle_kochbare_rezepte(rezepte_daten, aktueller_bestand)
    print(f"Mit deinem aktuellen Bestand kannst du kochen: {kochbar}")

    # 5. Export der Daten
    print("\n--- Schritt 4: Datenexport ---")
    if exportiere_bestand_als_csv(aktueller_bestand, "daten/kuehlschrank_export.csv"):
        print("[OK] Bestandsliste als CSV in 'daten/' exportiert.")

    # 6. Visualisierung (Fenster öffnet sich)
    print("\n--- Schritt 5: Visualisierung ---")
    print("Öffne Diagramm... (Bitte Fenster schließen, um Programm zu beenden)")
    erstelle_bestand_balkendiagramm(aktueller_bestand)


# KO-Kriterium: Main-Aufruf
if __name__ == "__main__":
    main()