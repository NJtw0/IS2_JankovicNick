"""
Fachmodul für die visuelle Aufbereitung der Bestandsdaten.
Erstellt Diagramme zur Übersicht des Kühlschrankinhalts.
"""
import matplotlib.pyplot as plt

def erstelle_bestand_balkendiagramm(bestand_liste: list) -> None:
    """
    Erstellt ein Balkendiagramm, das die absoluten Mengen der 
    Lebensmittel im Kühlschrank anzeigt.
    
    Args:
        bestand_liste (list): Liste von Tupeln (produkt_name, menge, einheit).
    """
    if not bestand_liste:
        print("Der Kühlschrank ist leer, kein Diagramm möglich.")
        return

    # Daten für das Diagramm entpacken
    produkte = [eintrag[0] for eintrag in bestand_liste]
    mengen = [eintrag[1] for eintrag in bestand_liste]

    plt.figure(figsize=(10, 6))
    plt.bar(produkte, mengen, color='skyblue', edgecolor='black')
    
    plt.title('Aktueller Kühlschrankbestand', fontsize=16)
    plt.xlabel('Produkte', fontsize=12)
    plt.ylabel('Menge', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Diagramm anzeigen und danach den Speicher freigeben
    plt.tight_layout()
    plt.show()


def erstelle_kategorie_kreisdiagramm(kategorie_daten: dict) -> None:
    """
    Erstellt ein Kreisdiagramm zur prozentualen Verteilung der
    Lebensmittel-Kategorien (z.B. wie viel Obst vs. Gemüse).
    
    Args:
        kategorie_daten (dict): Dictionary mit Kategorien und ihren Anteilen 
                                z.B. {'Gemüse': 5, 'Milchprodukte': 3}.
    """
    if not kategorie_daten:
        print("Keine Kategoriedaten vorhanden.")
        return

    kategorien = list(kategorie_daten.keys())
    werte = list(kategorie_daten.values())

    plt.figure(figsize=(8, 8))
    plt.pie(werte, labels=kategorien, autopct='%1.1f%%', startangle=140, 
            colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    
    plt.title('Bestandsverteilung nach Kategorien', fontsize=16)
    plt.show()


def speichere_diagramm_als_bild(bestand_liste: list, dateiname: str) -> bool:
    """
    Generiert ein Bestands-Balkendiagramm und speichert es direkt als
    Bilddatei ab, ohne es dem Nutzer auf dem Bildschirm anzuzeigen.
    
    Args:
        bestand_liste (list): Die aktuellen Kühlschrankdaten.
        dateiname (str): Der gewünschte Dateiname (z.B. 'bestand.png').
        
    Returns:
        bool: True, wenn erfolgreich gespeichert wurde, sonst False.
    """
    if not bestand_liste:
        return False
        
    produkte = [eintrag[0] for eintrag in bestand_liste]
    mengen = [eintrag[1] for eintrag in bestand_liste]

    plt.figure(figsize=(10, 6))
    plt.bar(produkte, mengen, color='lightgreen')
    plt.title('Automatischer Bestandsreport')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    try:
        plt.savefig(dateiname)
        plt.close() # Verhindert, dass das Bild im Hintergrund offen bleibt
        return True
    except Exception as e:
        print(f"Fehler beim Speichern des Diagramms: {e}")
        return False


# Main-Guard für die isolierte Testbarkeit laut Kriterienkatalog
if __name__ == "__main__":
    print("--- Isolierter Modultest für visualisierung_modul.py ---")
    
    # 1. Testdaten vorbereiten (Mocking)
    test_bestand = [
        ("Milch", 2.0, "Liter"),
        ("Eier", 6.0, "Stück"),
        ("Spaghetti", 500.0, "g"),
        ("Tomaten", 6.0, "Stück"),
        ("Käse", 250.0, "g")
    ]
    
    test_kategorien = {
        "Milchprodukte": 3,
        "Getreide": 1,
        "Gemüse": 1
    }
    
    # 2. Funktionen testen
    print("Erstelle Balkendiagramm (Fenster sollte sich öffnen)...")
    erstelle_bestand_balkendiagramm(test_bestand)
    
    print("Erstelle Kreisdiagramm (Fenster sollte sich öffnen)...")
    erstelle_kategorie_kreisdiagramm(test_kategorien)
    
    import os
    os.makedirs("bilder", exist_ok=True) # Zur Sicherheit

    # 3. Speichertest
    erfolg = speichere_diagramm_als_bild(test_bestand, "bilder/test_report.png")
    if erfolg:
        print("Testbild erfolgreich als 'test_report.png' im Ordner 'bilder' gespeichert!")