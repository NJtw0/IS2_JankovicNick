"""
Fachmodul für Texterkennung (OCR) und KI-Verarbeitung.
Liest Bilder mit Tesseract aus und strukturiert die Daten mit einer lokalen KI (Ollama).
"""
import re
import json
import pytesseract
from PIL import Image
import ollama

# Tesseract-Pfad für Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def lese_text_aus_bild(bild_pfad: str) -> str:
    """Extrahiert den rohen Text aus einem Bild."""
    try:
        bild = Image.open(bild_pfad)
        # Verwende das deutsche Sprachpaket für Umlaute
        rohtext = pytesseract.image_to_string(bild, lang='deu')
        return rohtext
    except Exception as e:
        print(f"Fehler bei der Bildverarbeitung: {e}")
        return ""


def parse_rezept_mit_ki(rohtext: str) -> dict:
    """
    Übergibt den unsauberen OCR-Text an Llama 3.2, um ein sauberes, 
    fehlerfreies JSON-Format mit Zutaten und Schritten zu generieren.
    """
    if not rohtext.strip():
        return {}

    prompt = f"""
    Du bist ein präziser Daten-Extraktor. Extrahiere aus dem folgenden unsauberen OCR-Text eines Rezepts den Namen, die Zutaten und die Zubereitungsschritte.
    Antworte AUSSCHLIESSLICH mit einem validen JSON-Objekt. Keine Erklärungen davor oder danach.
    Format-Beispiel:
    {{
      "name": "Name des Rezepts",
      "zutaten": [
        {{"name": "Mehl", "menge": 250.0, "einheit": "g"}},
        {{"name": "Eier", "menge": 2.0, "einheit": "Stück"}}
      ],
      "schritte": ["Erster Schritt...", "Zweiter Schritt..."]
    }}
    
    Hier ist der zu verarbeitende Text:
    {rohtext}
    """
    
    try:
        # Aufruf des lokalen Llama 3.2 Modells
        antwort = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        content = antwort['message']['content']
        
        # Sicherheits-Check: Falls die KI Markdown-Codeblöcke (```json) mitsendet
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
            
        return json.loads(content)
    except Exception as e:
        print(f"Fehler bei der KI-Verarbeitung: {e}")
        return {}