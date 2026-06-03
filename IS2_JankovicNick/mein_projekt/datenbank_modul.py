"""
Fachmodul für die Datenbankanbindung.
Verwaltet SQLite-Operationen für den Kühlschrank und die Einkaufsliste.
Beinhaltet automatische Umrechnung von Einheiten (kg -> g, l -> ml) und Daten-Normalisierung.
"""
import sqlite3
import os

os.makedirs("daten", exist_ok=True)
DATENBANK_PFAD = "daten/bestandsmanagement.db"


def normiere_einheit(menge: float, einheit: str) -> tuple:
    """
    Rechnet gängige Einheiten in die Haupteinheiten (g, ml, Stück) um.
    Bei unbekannten Eingaben greift der Standardfall ('Stück').
    """
    e_klein = einheit.strip().lower()
    
    # Gewicht -> Haupteinheit: g
    if e_klein in ['kg', 'kilo', 'kilogramm']:
        return menge * 1000.0, 'g'
    elif e_klein in ['g', 'gramm', 'gr']:
        return menge, 'g'
        
    # Volumen -> Haupteinheit: ml
    elif e_klein in ['l', 'liter', 'lit']:
        return menge * 1000.0, 'ml'
    elif e_klein in ['ml', 'milliliter']:
        return menge, 'ml'
        
    # Zählbare Dinge -> Haupteinheit: Stück
    elif e_klein in ['stück', 'stk', 'st', 'x']:
        return menge, 'Stück'
        
    # Manche Einheiten wollen wir vielleicht behalten (optional)
    elif e_klein in ['dose', 'dosen', 'packung', 'prise', 'el', 'tl', 'bund']:
        return menge, e_klein.title()
        
    # Standardfall / Fallback für Tippfehler oder leere Eingaben
    else:
        return menge, 'Stück'


def init_datenbank() -> None:
    """Erstellt die Tabellen für Kühlschrank und Einkaufsliste, falls sie nicht existieren."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kuehlschrank (
            produkt_name TEXT PRIMARY KEY,
            menge REAL,
            einheit TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS einkaufsliste (
            produkt_name TEXT PRIMARY KEY,
            menge REAL,
            einheit TEXT
        )
    """)
    
    verbindung.commit()
    verbindung.close()


def kuehlschrank_bestand_aktualisieren(produkt_name: str, menge: float, einheit: str) -> None:
    """Fügt ein Produkt hinzu oder aktualisiert die Menge (Einheiten werden automatisch umgerechnet)."""
    produkt_name = produkt_name.strip().title()
    norm_menge, norm_einheit = normiere_einheit(menge, einheit)
    
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    
    # Prüfen, ob das Produkt schon da ist
    cursor.execute("SELECT menge, einheit FROM kuehlschrank WHERE produkt_name = ?", (produkt_name,))
    ergebnis = cursor.fetchone()
    
    if ergebnis:
        alte_menge = ergebnis[0]
        # Wenn die Einheit übereinstimmt, normal addieren
        neue_menge = alte_menge + norm_menge
        
        if neue_menge <= 0:
            cursor.execute("DELETE FROM kuehlschrank WHERE produkt_name = ?", (produkt_name,))
        else:
            cursor.execute("UPDATE kuehlschrank SET menge = ? WHERE produkt_name = ?", 
                           (neue_menge, produkt_name))
    else:
        if norm_menge > 0:
            cursor.execute("INSERT INTO kuehlschrank (produkt_name, menge, einheit) VALUES (?, ?, ?)", 
                           (produkt_name, norm_menge, norm_einheit))
            
    verbindung.commit()
    verbindung.close()


def hole_kuehlschrank_bestand() -> list:
    """Gibt den gesamten Bestand alphabetisch sortiert zurück."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("SELECT produkt_name, menge, einheit FROM kuehlschrank ORDER BY produkt_name")
    daten = cursor.fetchall()
    verbindung.close()
    return daten


def einkaufsliste_aktualisieren(produkt_name: str, menge: float, einheit: str) -> None:
    """Fügt ein Produkt zur Einkaufsliste hinzu oder aktualisiert es (mit Umrechnung)."""
    produkt_name = produkt_name.strip().title()
    norm_menge, norm_einheit = normiere_einheit(menge, einheit)
    
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    
    cursor.execute("SELECT menge FROM einkaufsliste WHERE produkt_name = ?", (produkt_name,))
    ergebnis = cursor.fetchone()
    
    if ergebnis:
        neue_menge = ergebnis[0] + norm_menge
        if neue_menge <= 0:
            cursor.execute("DELETE FROM einkaufsliste WHERE produkt_name = ?", (produkt_name,))
        else:
            cursor.execute("UPDATE einkaufsliste SET menge = ? WHERE produkt_name = ?", 
                           (neue_menge, produkt_name))
    else:
        if norm_menge > 0:
            cursor.execute("INSERT INTO einkaufsliste (produkt_name, menge, einheit) VALUES (?, ?, ?)", 
                           (produkt_name, norm_menge, norm_einheit))
            
    verbindung.commit()
    verbindung.close()


def hole_einkaufsliste() -> list:
    """Gibt die komplette Einkaufsliste alphabetisch sortiert zurück."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("SELECT produkt_name, menge, einheit FROM einkaufsliste ORDER BY produkt_name")
    daten = cursor.fetchall()
    verbindung.close()
    return daten


def bearbeite_kuehlschrank_produkt(alter_name: str, neuer_name: str, neue_menge: float, neue_einheit: str) -> None:
    """Überschreibt ein bestehendes Produkt explizit mit neuen Werten (wird ebenfalls umgerechnet)."""
    neuer_name = neuer_name.strip().title()
    norm_menge, norm_einheit = normiere_einheit(neue_menge, neue_einheit)
    
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    
    if norm_menge <= 0:
        cursor.execute("DELETE FROM kuehlschrank WHERE produkt_name = ?", (alter_name,))
    else:
        cursor.execute("""
            UPDATE kuehlschrank 
            SET produkt_name = ?, menge = ?, einheit = ? 
            WHERE produkt_name = ?
        """, (neuer_name, norm_menge, norm_einheit, alter_name))
        
    verbindung.commit()
    verbindung.close()


if __name__ == "__main__":
    print("Bitte starte das Programm über die __main__.py")