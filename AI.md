# Dokumentation über den Einsatz von Künstlicher Intelligenz (AI.md)

## 1. Verwendete Tools

| Tool | Einsatzbereich |
| :--- | :--- |
| **Gemini / ChatGPT** | Software-Architektur, Refactoring, Debugging & Modulstruktur |
| **Gemma 3 (4B) via Ollama** | Lokale Extraktion & Strukturierung von Rezeptdaten |
| **Tesseract OCR** | Texterkennung aus unstrukturierten Bilddateien |

## 2. Einsatz je Modul
* **GUI-Modul:** Generierung des anfänglichen Tkinter-Boilerplates und spätere Umstellung auf ttk-Widgets für den Dark Mode. Die KI half hier stark beim Layouting der Tabs und Event-Handling.
* **Architektur / __main__:** Beratung zur strikten Einhaltung der Kapselungsvorgaben (K6) und Erstellung plattformunabhängiger, dynamischer Pfade via `os.path.dirname(__file__)`.
* **OCR-Modul:** Konzeption des JSON-Modes von Ollama, um valide und parsebare Datenstrukturen zu erzwingen, sowie Hilfe bei der Text-Bereinigung.
* **Visualisierung_modul:** Generierung des syntaktischen Grundgerüsts für die Erstellung der Matplotlib-Balkendiagramme.
* **Datenbank/Rezept/Export:** Diese Fachmodule wurden primär manuell implementiert. Die KI wurde hier lediglich punktuell als Debugging-Assistenz bei Logikfehlern (z.B. Einheitenumrechnung) konsultiert.

## 3. Prompt-Beispiele

**Beispiel 1: Fehlerhafte KI-Generierung (Halluzination)**
* **Prompt:** *"Du hast mir die Tkinter-GUI generiert. Im Dark Mode erkennt man die Schrift auf den farbigen tk.Buttons jetzt aber nicht mehr. Wie muss ich den generierten Code umschreiben, damit er im Dark Mode lesbar bleibt?"*
* **Reflexion:** Dieser anfängliche Versuch der automatischen GUI-Generierung schlug fehl. Die KI halluzinierte einen funktionierenden Dark Mode herbei, nutzte aber veraltete `tk.Button`-Elemente mit hart codierten Hintergrundfarben (`bg="lightgreen"`), was zu massiven Darstellungsfehlern führte. Ich musste diesen Code manuell verwerfen und die KI in einem neuen Ansatz zwingen, stattdessen moderne `ttk`-Widgets in Kombination mit dem `sv-ttk` Theme zu nutzen, um das Problem endgültig zu beheben.

**Beispiel 2: Positives Ergebnis (Erfolgreicher Prompt)**
* **Prompt:** *"Mein Python-Code stürzt ab, wenn ich den Text von der Lokalen KI parsen will, weil das Modell manchmal Kommentare im JSON hinterlässt. Wie erzwinge ich perfektes JSON aus Ollama in Python?"*
* **Reflexion:** Dieser Prompt funktionierte auf Anhieb hervorragend. Die KI schlug direkt vor, den nativen Ollama-JSON-Mode (`format='json'`) als Parameter in den API-Aufruf einzubauen. Dadurch wurde das lokale LLM mathematisch dazu gezwungen, ausschließlich valide JSON-Strukturen auszugeben, wodurch der `JSONDecodeError` im System sofort und dauerhaft verschwand.

**Beispiel 3: Architektur-Design und Daten-Normierung (Effektive Strukturierung)**
* **Prompt:** *"Ich habe ein Modul für die Bestandsverwaltung. Wie kann ich unterschiedliche Einheiten wie 'kg', 'g', 'Liter' und 'ml' in einer SQLite-Datenbank so speichern, dass ich sie später mathematisch korrekt vergleichen kann, ohne das Datenmodell zu sprengen?"*
* **Reflexion**: Die KI schlug zunächst vor, die Einheiten als Text zu speichern und Berechnungen per CASE-Statement im SQL-Query zu machen. Das habe ich abgelehnt, da dies die Datenbank-Abfragen unnötig verlangsamt und fehleranfällig macht. Ich habe mich stattdessen für einen Ansatz entschieden, bei dem alle Mengen vor der Speicherung über eine normiere_einheit-Funktion in die Basiseinheiten (Gramm bzw. Milliliter) umgerechnet werden. Die KI hat diesen Architekturvorschlag anschließend validiert und mir geholfen, das Mapping-Dictionary in Python effizient zu schreiben.

**Beispiel 4: KI-Logikfehler und manuelle Korrektur**
* **Prompt:** *"Wie kann ich die eingescannten Aufzählungszeichen der Schritte (z.B. '1. ') aus dem OCR-Text in Python entfernen, bevor ich sie in der GUI anzeige?"*
* **Reflexion:** Die KI lieferte hierfür zunächst einen simplen `.lstrip('0123456789. ')` Befehl. Dies war ein Logikfehler der KI, da dadurch bei Schritttexten wie "15 Minuten backen" fälschlicherweise auch die "15" weggeschnitten wurde. Um das Problem präzise und fehlerfrei zu lösen, habe ich die KI-Lösung verworfen und einen regulären Ausdruck (`re.sub(r'^\d+[\.)]\s*', '', ...)`) implementiert, der nur Zahlen am Satzanfang entfernt.

## 4. Kritische Reflexion
Der Einsatz von generativen KI-Modellen hat den Entwicklungsprozess, insbesondere bei der Erstellung von Boilerplate-Code für die grafische Oberfläche, spürbar beschleunigt. Dennoch hat das vorliegende Projekt eindeutig gezeigt, dass der Output der KI stets kritisch validiert und häufig überarbeitet werden muss. 

Neben den im vorherigen Abschnitt genannten UI-Fehlern und Regex-Schwächen, versuchte die KI mich beispielsweise in der Konzeptionsphase davon zu überzeugen, das ressourcenintensive Framework `EasyOCR` anstelle von Tesseract zu nutzen. Dieser Vorschlag wurde von mir nach eigener Recherche aktiv abgelehnt: Da `EasyOCR` eine hohe GPU/VRAM-Auslastung aufweist, hätte es parallel zu einem lokal ausgeführten Ollama-LLM (gemma3:4b) auf einem Standard-Laptop zu massiven Performance-Einbrüchen geführt. Die letztendliche Verantwortung für Architektur, Stabilität und Code-Qualität lag somit zu jedem Zeitpunkt bei mir. Der KI-Assistent war ein nützliches Werkzeug, konnte aber ein solides Grundverständnis der Softwareentwicklung nicht ersetzen.

## 5. Selbsteinschätzung Urheberschaft
* **__main__.py:** Weitgehend eigenständig entwickelt, Struktur-Tipps zur Kapselung von der KI übernommen.
* **datenbank_modul.py:** Komplett eigenständig programmiert, SQL-Queries und Einheitenlogik manuell optimiert.
* **export_modul.py:** Komplett eigenständig ohne KI geschrieben.
* **gui_modul.py:** Grundgerüst ursprünglich von der KI generiert, anschließend aufgrund von Fehlern umfassend manuell korrigiert und refactored.
* **ocr_modul.py:** Konzept der KI-Anbindung (Ollama) übernommen, Fehlerbehandlung und Regex-Säuberung manuell implementiert.
* **rezept_modul.py:** Weitgehend eigenständig programmiert.
* **visualisierung_modul.py:** Code-Schnipsel für Matplotlib mit KI erstellt und in die Architektur eingepasst.