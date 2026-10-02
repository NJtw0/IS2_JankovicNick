import matplotlib.pyplot as plt

def _extrahiere_chart_daten(bestand_liste: list) -> tuple:
    """Interne Hilfsfunktion: Bereitet die Rohdaten für Matplotlib auf."""
    return [e[0] for e in bestand_liste], [e[1] for e in bestand_liste]

def erstelle_bestand_balkendiagramm(bestand_liste: list) -> None:
    """Erstellt und zeigt ein Balkendiagramm des Bestands."""
    if not bestand_liste:
        return
    produkte, mengen = _extrahiere_chart_daten(bestand_liste)
    
    plt.figure(figsize=(10, 6))
    plt.bar(produkte, mengen, color='skyblue', edgecolor='black')
    
    plt.title('Aktueller Bestand', fontsize=14)
    plt.ylabel('Menge', fontsize=12)
    plt.xticks(rotation=45, ha='right') 
    
    plt.tight_layout()
    plt.show()

def speichere_diagramm_als_bild(bestand_liste: list, dateiname: str) -> bool:
    """Speichert das Diagramm als Bilddatei."""
    if not bestand_liste: 
        return False
    produkte, mengen = _extrahiere_chart_daten(bestand_liste)
    
    plt.figure(figsize=(10, 6))
    plt.bar(produkte, mengen, color='lightgreen', edgecolor='black')
    
    plt.title('Automatischer Bestandsreport')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(dateiname)
    plt.close()
    return True

if __name__ == "__main__":
    # --- ISOLIERTER TESTLAUF FÜR DIE VISUALISIERUNG ---
    print("Starte Visualisierungs-Testlauf...")
    
    # Künstlicher Lagerbestand mit unterschiedlichen Mengen und langen Namen
    demo_lagerbestand = [
        ("Kirschtomaten", 15.0, "Stück"),
        ("Weizenmehl", 2.5, "kg"),
        ("Haltbare Vollmilch", 4.0, "Liter"),
        ("Rinderhackfleisch", 500.0, "g"),
        ("Goudakäse Am Stück", 1.0, "Block")
    ]
    
    test_bild_name = "test_bestandsreport.png"
    
    # 1. Teste den automatischen Bildexport im Hintergrund
    print(f"1. Teste Bildexport im Hintergrund nach '{test_bild_name}'...")
    if speichere_diagramm_als_bild(demo_lagerbestand, test_bild_name):
        print(f" -> Erfolg! Bild wurde im Projektordner erstellt.")
    else:
        print(" -> Fehler beim Bildexport.")
        
    # 2. Teste das interaktive UI-Fenster
    print("\n2. Öffne interaktives Diagramm-Fenster...")
    print("(Schließe das Diagramm-Fenster, um den Testlauf zu beenden.)")
    
    # Ruft die Hauptfunktion auf, die auch die GUI nutzt
    erstelle_bestand_balkendiagramm(demo_lagerbestand)
    
    print("Testlauf erfolgreich beendet.")