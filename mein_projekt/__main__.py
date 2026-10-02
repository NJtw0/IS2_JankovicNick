"""
Einstiegspunkt der GUI-Anwendung.
"""
import os

from . import datenbank_modul
from . import gui_modul
from . import ocr_modul
from . import rezept_modul
from . import visualisierung_modul
from . import export_modul

def bereite_ordner_vor() -> None:
    """Stellt sicher, dass die benötigten Arbeitsordner existieren."""
    basis = os.path.dirname(__file__)
    os.makedirs(os.path.join(basis, "daten"), exist_ok=True)
    os.makedirs(os.path.join(basis, "bilder"), exist_ok=True)

def main() -> None:
    """Orchestriert den Ablauf."""
    bereite_ordner_vor()
    # Wir rufen die Funktionen über die Modul-Namespaces auf
    datenbank_modul.init_datenbank()
    gui_modul.starte_app()

if __name__ == "__main__":
    main()