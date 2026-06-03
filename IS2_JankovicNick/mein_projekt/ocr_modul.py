"""
Fachmodul für die optische Zeichenerkennung (OCR).
Liest Bilder von Rezepten ein, erkennt den Text und filtert Zutaten heraus.
"""
import re
import pytesseract
from PIL import Image

def lese_text_aus_bild(bild_pfad: str) -> str:
    """
    Lädt ein Bild von der Festplatte und führt eine optische Zeichenerkennung durch.
    
    Args:
        bild_pfad (str): Der relative oder absolute Pfad zur Bilddatei.
        
    Returns:
        str: Der erkannte Text aus dem Bild. Gibt einen Leerstring bei Fehler zurück.
    """
    try:
        # Öffnet das Bild mit der Pillow-Bibliothek
        rezept_bild = Image.open(bild_pfad)
        # Nutzt Tesseract, um den Text (idealerweise auf Deutsch) zu extrahieren
        erkannter_text = pytesseract.image_to_string(rezept_bild, lang='deu')
        return erkannter_text
    except Exception as fehler:
        print(f"Fehler bei der Bildverarbeitung von {bild_pfad}: {fehler}")
        return ""

def bereinige_erkannten_text(rohtext: str) -> list:
    """
    Nimmt den rohen OCR-Text, zerlegt ihn in Zeilen und entfernt leere Zeilen.
    
    Args:
        rohtext (str): Der unformatierte Text aus der Bilderkennung.
        
    Returns:
        list: Eine Liste von bereinigten Textzeilen.
    """
    alle_zeilen = rohtext.split('\n')
    bereinigte_zeilen = []
    
    for zeile in alle_zeilen:
        saubere_zeile = zeile.strip()
        # Nur Zeilen behalten, die nicht komplett leer sind
        if saubere_zeile:
            bereinigte_zeilen.append(saubere_zeile)
            
    return bereinigte_zeilen

def extrahiere_zutaten_liste(text_zeilen: list) -> list:
    """
    Filtert aus den Textzeilen mögliche Zutaten heraus. 
    Nimmt an, dass Zutatenzeilen mit einer Ziffer (Menge) beginnen.
    
    Args:
        text_zeilen (list): Die bereinigten Textzeilen aus dem Rezept.
        
    Returns:
        list: Eine Liste der erkannten Zutaten.
    """
    gefundene_zutaten = []
    # Regulärer Ausdruck: Sucht Zeilen, die mit einer Ziffer (\d) beginnen
    such_muster = r"^\d+.*"
    
    for zeile in text_zeilen:
        if re.match(such_muster, zeile):
            gefundene_zutaten.append(zeile)
            
    return gefundene_zutaten

# Isolierter Testblock für die automatische Code-Prüfung und Manuelle Tests
if __name__ == "__main__":
    print("--- Isolierter Modultest für ocr_modul.py ---")
    
    # Da wir für den Test nicht zwingend ein echtes Bild voraussetzen wollen,
    # simulieren wir das Verhalten der pytesseract-Ausgabe.
    mock_ocr_text = """
    Omas Pfannkuchen Rezept
    
    Zutaten:
    250 g Mehl
    2 Eier
    0.5 Liter Milch
    Prise Salz
    
    Zubereitung:
    Alles gut verrühren und in der Pfanne ausbacken.
    """
    
    print("Simulierter Rohtext aus dem Bild:")
    print(mock_ocr_text)
    print("-" * 30)
    
    zeilen_liste = bereinige_erkannten_text(mock_ocr_text)
    zutaten = extrahiere_zutaten_liste(zeilen_liste)
    
    print(f"Gefundene Zutaten-Zeilen: {zutaten}")