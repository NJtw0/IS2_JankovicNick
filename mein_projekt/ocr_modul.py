import json
import pytesseract
from PIL import Image
import ollama

# Pfad zu Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def lese_text_aus_bild(bild_pfad: str) -> str:
    """Extrahiert den rohen Text aus einem Bild mittels Tesseract."""
    try:
        bild = Image.open(bild_pfad)
        return pytesseract.image_to_string(bild, lang='deu')
    except Exception as e:
        print(f"Fehler bei der Bildverarbeitung: {e}")
        return ""


def _get_rezept_prompt(rohtext: str) -> str:
    """Gibt den strukturierten KI-Prompt zurück."""
    return f"""Du bist ein präziser Daten-Extraktor. Extrahiere aus dem folgenden unsauberen OCR-Text eines Rezepts den Namen, die Zutaten, die Portionenzahl und die Zubereitungsschritte.

STRIKTE REGELN FÜR ZUTATEN:
1. Der "name" darf AUSSCHLIESSLICH das Lebensmittel selbst enthalten (z.B. "Salz", "Pfeffer", "Zwiebel").
2. Schreibe NIEMALS Zahlen oder das Wort "None" in den Zutaten-Namen.
3. Wenn im Text keine Menge oder Einheit steht (z.B. bei "Salz"), setze die menge auf 1.0 und die einheit auf "Stück" oder "Prise".
4. Extrahiere die Portionenzahl aus Angaben wie:
   - "für 4 Personen"
   - "4 Portionen"
   - "Serves 2"
5. Falls keine Portionenzahl gefunden wird, setze portionen auf 1.

Das Ergebnis MUSS exakt diesem JSON entsprechen:
{{
  "name": "Name des Rezepts",
  "portionen": 4,
  "zutaten": [
    {{"name": "Mehl", "menge": 250.0, "einheit": "g"}},
    {{"name": "Salz", "menge": 1.0, "einheit": "Prise"}}
  ],
  "schritte": ["Erster Schritt...", "Zweiter Schritt..."]
}}

Hier ist der OCR-Text:
{rohtext}
"""


def _bereinige_zutatennamen(daten: dict) -> dict:
    """Putzt None und Zahlen aus Zutatennamen."""
    if "zutaten" in daten:
        for zutat in daten["zutaten"]:
            if "name" in zutat and isinstance(zutat["name"], str):
                name = zutat["name"].replace("None", "").lstrip('0123456789. ')
                zutat["name"] = name.strip()

    portionen = daten.get("portionen", 1)

    try:
        portionen = int(portionen)
        if portionen < 1:
            portionen = 1
    except ValueError:
        portionen = 1

    daten["portionen"] = portionen

    return daten


def parse_rezept_mit_ki(rohtext: str) -> dict:
    """Übergibt OCR-Text an Gemma und gibt strukturiertes JSON zurück."""
    if not rohtext.strip():
        return {}

    try:
        antwort = ollama.chat(
            model='gemma3:4b',
            messages=[{
                'role': 'user',
                'content': _get_rezept_prompt(rohtext)
            }],
            format='json'
        )

        daten = json.loads(antwort['message']['content'])
        return _bereinige_zutatennamen(daten)

    except Exception as e:
        print(f"Fehler bei der KI-Verarbeitung: {e}")
        return {}


if __name__ == "__main__":
    print("Starte OCR-Modul Testlauf...")

    unsauberer_ocr_text = """
    REZEPT FUER APFELKUCHEN
    Für 4 Portionen

    Zutatenliste:
    1. 500g Mehl
    2. None Salz
    3. 4 Stück frische Äpfel

    Zubereitung:
    Zuerst das Mehl sieben.
    Danach Äpfel schneiden.
    Bei 180 Grad backen.
    """

    print("Sende unsauberen Text an das lokale Modell (gemma3:4b)...")
    print("-" * 40)

    try:
        test_ergebnis = parse_rezept_mit_ki(unsauberer_ocr_text)

        print("\nStrukturiertes JSON-Ergebnis:")
        print(json.dumps(test_ergebnis, indent=4, ensure_ascii=False))
        print("-" * 40)

    except Exception as fehler:
        print(f"\n[!] Testlauf abgebrochen. Fehler: {fehler}")