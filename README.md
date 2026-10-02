# 📦 Bestandsmanagement System mit lokaler KI

Ein intelligentes, modulares Python-Desktop-Programm zur Verwaltung von Vorräten, Einkaufslisten und Rezepten. Das Highlight dieses Projekts ist der **KI-Rezept-Scanner**: Mithilfe von lokaler Texterkennung (Tesseract OCR) und einem lokalen großen Sprachmodell (Gemma3:4b via Ollama) können abfotografierte Rezepte vollautomatisch ausgelesen, strukturiert und in die Datenbank übernommen werden.

---

## Verwendung

* **❄️ Intelligente Bestandsverwaltung:** Produkte hinzufügen, bearbeiten und visualisieren (Balkendiagramm). Die Umrechnung von Einheiten (z.B. kg in g oder l in ml) erfolgt vollautomatisch im Hintergrund.
* **🛒 Smarter Einkaufszettel:** Fehlende Zutaten flexibel notieren, per E-Mail ans Handy schicken und nach dem Einkauf mit einem Klick ("Alles auf einmal einräumen") in den Bestand überführen. Artikel können zudem komfortabel und ersatzlos gelöscht werden.
* **🍽️ Rezept-Management:** Übersicht aller Rezepte inklusive automatischem Abgleich mit dem aktuellen Lagerbestand (✅ Kochbar / ❌ Zutaten fehlen). Rezepte können auf eine gewünschte Personenzahl skaliert werden; die benötigten Zutaten werden dabei automatisch berechnet und können bei Bedarf direkt auf die Einkaufsliste gesetzt werden. Beim Ausführen der Funktion "Kochen" werden die exakten Zutatenmengen automatisch vom Bestand abgezogen.
* **📸 KI-Rezept-Scanner:** Bilder von Rezepten scannen. Die KI extrahiert und formatiert Namen, Zutaten und Zubereitungsschritte vollautomatisch.
* **🌗 Modernes UI-Design:** Dynamische und barrierefreie grafische Oberfläche auf Basis von ttk-Widgets, die sich dank sv-ttk automatisch an den Light- und Dark-Mode des Betriebssystems anpasst (inklusive manuellem Toggle-Button).

---

## 🛠️ Systemvoraussetzungen

Da dieses Projekt **vollständig lokal und datenschutzfreundlich** (ohne Cloud-APIs) arbeitet, müssen vor dem ersten Start zwei externe Programme auf dem System eingerichtet sein:

1. **Tesseract OCR (Texterkennung)**
   * **Download:** [UB Mannheim Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
   * **Installationspfad:** Zwingend unter `C:\Program Files\Tesseract-OCR` installieren (Standardpfad).
   * **Sprachpaket:** Die deutsche Trainingsdatei [deu.traineddata](https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata) herunterladen und in den Ordner `C:\Program Files\Tesseract-OCR\tessdata` ablegen, damit Umlaute und spezifische Begriffe fehlerfrei erkannt werden.
2. **Ollama (Lokale KI)**
   * **Download:** [ollama.com](https://ollama.com/download)
   * **Modell laden:** Nach der Installation in einem normalen Terminal den Befehl `ollama run gemma3:4b` ausführen, um das benötigte Sprachmodell (Gemma3:4b, 3B) herunterzuladen. Ollama muss während der Programmnutzung im Hintergrund aktiv sein.

---

## Installation

Das Projekt ist nach modernen Python-Standards gekapselt und sollte in einer sauberen virtuellen Umgebung ausgeführt werden. 

*Hinweis: Falls das Projekt in einem Cloud-Synchronisationsordner (wie iCloud oder OneDrive) liegt, kann es bei der Installation zu Dateisperren kommen. Es wird dringend empfohlen, das Projekt in einem rein lokalen Verzeichnis auszuführen.*

### 1. Umgebung einrichten und aktivieren

Öffne ein Terminal (PowerShell / CMD) im Hauptverzeichnis des Projekts (wo sich diese README.md befindet):

    # Virtuelle Umgebung erstellen
    python -m venv .venv

    # Umgebung aktivieren (Windows PowerShell)
    .\.venv\Scripts\activate

*Tipp bei Windows-Sicherheitsmeldungen:* Falls die Ausführung von Skripten blockiert wird, behebt der Befehl `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` das Problem dauerhaft für den aktuellen Benutzer.

### 2. Abhängigkeiten installieren

    pip install -r requirements.txt

Die requirements.txt installiert alle benötigten externen Frameworks (pytesseract, pillow, ollama, sv-ttk, matplotlib). Standardbibliotheken wie tkinter, sqlite3 oder json sind bereits fest in Python integriert.

### 3. Programm starten

Das Programm ist als modulares Python-Paket aufgebaut. Der Start erfolgt über das Hauptverzeichnis mit folgendem Befehl:

    python -m mein_projekt

---

## 📂 Projektstruktur (Architektur)

Das Projekt folgt der vorgegebenen Modularbeit-Struktur (K6):

```text
IS2_JankovicNick/
 ├── mein_projekt/              # Paket-Ordner
 │    ├── __init__.py           # Paket-Markierung
 │    ├── __main__.py           # Einstiegspunkt (Dirigent)
 │    ├── datenbank_modul.py    # SQLite-Logik & Einheiten-Normierung
 │    ├── export_modul.py       # CSV- & E-Mail-Export
 │    ├── gui_modul.py          # View-Layer & Event-Handling
 │    ├── ocr_modul.py          # Bild-OCR & KI-Extraktion
 │    ├── rezept_modul.py       # Rezept-Logik, Skalierung & Bestandsabgleich
 │    ├── visualisierung_modul.py # Matplotlib-Diagramme
 │    ├── bilder/               # Rezept-Fotos für OCR-Tests
 │    └── daten/                # DB, Rezepte (JSON) & Exporte
 ├── README.md                  # Diese Dokumentation
 ├── AI.md                      # KI-Reflexion
 └── requirements.txt           # Bibliotheken
```
---

## 👨‍💻 Autor

**Nick Jankovic** Modul: Informationssysteme 2 (IS2) / Modularbeit  
Datum: Juni 2026