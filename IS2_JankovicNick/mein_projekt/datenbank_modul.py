"""
Fachmodul für die Datenbankanbindung.
Verwaltet SQLite-Operationen für den Lagerbestand und die Einkaufsliste.
"""
import sqlite3
import os

BASIS_ORDNER = os.path.dirname(__file__)
DATEN_ORDNER = os.path.join(BASIS_ORDNER, "daten")
DATENBANK_PFAD = os.path.join(DATEN_ORDNER, "bestandsmanagement.db")

os.makedirs(DATEN_ORDNER, exist_ok=True)


def normiere_einheit(menge: float, einheit: str) -> tuple:
    """Normiert die Mengenangaben und Einheiten für eine einheitliche Speicherung."""
    e_klein = einheit.strip().lower()
    if e_klein in ['kg', 'kilo', 'kilogramm']:
        return menge * 1000.0, 'g'
    elif e_klein in ['g', 'gramm', 'gr']: 
        return menge, 'g'
    elif e_klein in ['l', 'liter', 'lit']:
        return menge * 1000.0, 'ml'
    elif e_klein in ['ml', 'milliliter']: 
        return menge, 'ml'
    elif e_klein in ['stück', 'stk', 'st', 'x']:
        return menge, 'Stück'
    elif e_klein in ['dose', 'dosen', 'packung', 'prise', 'el', 'tl', 'bund']:
        return menge, e_klein.title()
    else: 
        return menge, 'Stück'


def init_datenbank() -> None:
    """Initialisiert die SQLite-Datenbank und erstellt notwendige Tabellen."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS bestand (produkt_name TEXT PRIMARY KEY, menge REAL, einheit TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS einkaufsliste (produkt_name TEXT PRIMARY KEY, menge REAL, einheit TEXT)")
    verbindung.commit()
    verbindung.close()


def lagerbestand_aktualisieren(produkt_name: str, menge: float, einheit: str) -> None:
    """Aktualisiert den Lagerbestand eines Produkts in der Datenbank."""
    produkt_name = produkt_name.strip().title()
    norm_menge, norm_einheit = normiere_einheit(menge, einheit)
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("SELECT menge FROM bestand WHERE produkt_name = ?", (produkt_name,))
    ergebnis = cursor.fetchone()
    
    if ergebnis:
        neue_menge = ergebnis[0] + norm_menge
        if neue_menge <= 0: 
            cursor.execute("DELETE FROM bestand WHERE produkt_name = ?", (produkt_name,))
        else: 
            cursor.execute("UPDATE bestand SET menge = ? WHERE produkt_name = ?", (neue_menge, produkt_name))
    else:
        if norm_menge > 0:
            cursor.execute("INSERT INTO bestand (produkt_name, menge, einheit) VALUES (?, ?, ?)", (produkt_name, norm_menge, norm_einheit))
    verbindung.commit()
    verbindung.close()


def hole_lagerbestand() -> list:
    """Ruft den gesamten Lagerbestand aus der Datenbank ab."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("SELECT produkt_name, menge, einheit FROM bestand ORDER BY produkt_name")
    daten = cursor.fetchall()
    verbindung.close()
    return daten


def einkaufsliste_aktualisieren(produkt_name: str, menge: float, einheit: str) -> None:
    """Aktualisiert die Einkaufsliste für ein spezifisches Produkt."""
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
            cursor.execute("UPDATE einkaufsliste SET menge = ? WHERE produkt_name = ?", (neue_menge, produkt_name))
    else:
        if norm_menge > 0:
            cursor.execute("INSERT INTO einkaufsliste (produkt_name, menge, einheit) VALUES (?, ?, ?)", (produkt_name, norm_menge, norm_einheit))
    verbindung.commit()
    verbindung.close()


def hole_einkaufsliste() -> list:
    """Ruft die gesamte Einkaufsliste aus der Datenbank ab."""
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    cursor.execute("SELECT produkt_name, menge, einheit FROM einkaufsliste ORDER BY produkt_name")
    daten = cursor.fetchall()
    verbindung.close()
    return daten


def bearbeite_bestand_produkt(alter_name: str, neuer_name: str, neue_menge: float, neue_einheit: str) -> None:
    """Bearbeitet ein bestehendes Produkt im Lagerbestand oder löscht es."""
    neuer_name = neuer_name.strip().title()
    norm_menge, norm_einheit = normiere_einheit(neue_menge, neue_einheit)
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()
    
    if norm_menge <= 0: 
        cursor.execute("DELETE FROM bestand WHERE produkt_name = ?", (alter_name,))
    else: 
        cursor.execute("UPDATE bestand SET produkt_name = ?, menge = ?, einheit = ? WHERE produkt_name = ?", (neuer_name, norm_menge, norm_einheit, alter_name))
    verbindung.commit()
    verbindung.close()


if __name__ == "__main__":
    print("Starte Datenbank-Testlauf...")
    init_datenbank()
    
    print("Lege Testdaten an...")
    lagerbestand_aktualisieren("Test-Apfel", 5.0, "Stück")
    lagerbestand_aktualisieren("Test-Mehl", 1.5, "kg") 
    
    print("\nAktueller Bestand (nur Test-Artikel):")
    for produkt, menge, einheit in hole_lagerbestand():
        if "Test-" in produkt:
            print(f" -> {produkt}: {menge} {einheit}")
            
    print("\nBereinige Testdaten...")
    bearbeite_bestand_produkt("Test-Apfel", "Test-Apfel", 0, "Stück")
    bearbeite_bestand_produkt("Test-Mehl", "Test-Mehl", 0, "g")
    
    print("Testlauf erfolgreich beendet.")