"""
Einstiegspunkt der GUI-Anwendung. Wird bei python -m mein_projekt ausgeführt.
Koordiniert den Start, enthält aber keine eigene Fachlogik (Bereich C konform).
"""
import os
from .datenbank_modul import init_datenbank
from .gui_modul import starte_app


def bereite_ordner_vor() -> None:
    """Hilfsfunktion: Stellt sicher, dass die Arbeitsordner existieren."""
    os.makedirs("daten", exist_ok=True)
    os.makedirs("bilder", exist_ok=True)


def main() -> None:
    """Orchestriert den Start des Programms."""
    print("Starte Kühlschrank-Manager mit grafischer Oberfläche...")
    
    # 1. Infrastruktur sichern
    bereite_ordner_vor()
    init_datenbank()
    
    # 2. GUI laden (Das Programm pausiert hier, bis das Fenster geschlossen wird)
    starte_app()
    
    print("Programm beendet.")


# KO-Kriterium: Main-Aufruf
if __name__ == "__main__":
    main()