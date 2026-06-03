"""
Dieses Fachmodul verwaltet die lokale SQLite-Datenbank für das
Bestandsmanagement-System (Kühlschrank und Einkaufsliste).
"""
import sqlite3
import os

# Stellt sicher, dass der Ordner existiert, falls man das Modul isoliert testet
os.makedirs("daten", exist_ok=True) 

DATENBANK_PFAD = "daten/bestandsmanagement.db"

def init_datenbank() -> None:
    """
    Initialisiert die Datenbanktabellen für den Kühlschrank und die Einkaufsliste,
    falls diese noch nicht im Dateisystem existieren.
    """
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()

    # Tabelle für den aktuellen Lebensmittelbestand (Kühlschrank)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kuehlschrank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produkt_name TEXT UNIQUE NOT NULL,
            menge REAL NOT NULL,
            einheit TEXT NOT NULL
        )
    """)

    # Tabelle für die Einkaufsliste
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS einkaufsliste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produkt_name TEXT UNIQUE NOT NULL,
            menge REAL NOT NULL,
            einheit TEXT NOT NULL
        )
    """)

    verbindung.commit()
    verbindung.close()


def kuehlschrank_bestand_aktualisieren(
    produkt_name: str, menge_aenderung: float, einheit: str
) -> None:
    """
    Fügt ein Produkt zum Kühlschrank hinzu oder aktualisiert die vorhandene Menge.
    Wenn die Gesamtmenge auf oder unter 0 fällt, wird das Produkt gelöscht.

    Args:
        produkt_name (str): Der Name des Lebensmittels.
        menge_aenderung (float): Die hinzuzufügende oder abzuziehende Menge.
        einheit (str): Die Maßeinheit (z. B. 'g', 'Liter', 'Stück').
    """
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()

    cursor.execute(
        "SELECT menge FROM kuehlschrank WHERE produkt_name = ?", (produkt_name,)
    )
    ergebnis = cursor.fetchone()

    if ergebnis:
        neue_menge = ergebnis[0] + menge_aenderung
        if neue_menge <= 0:
            cursor.execute(
                "DELETE FROM kuehlschrank WHERE produkt_name = ?", (produkt_name,)
            )
        else:
            cursor.execute(
                "UPDATE kuehlschrank SET menge = ? WHERE produkt_name = ?",
                (neue_menge, produkt_name),
            )
    else:
        if menge_aenderung > 0:
            cursor.execute(
                "INSERT INTO kuehlschrank (produkt_name, menge, einheit) VALUES (?, ?, ?)",
                (produkt_name, menge_aenderung, einheit),
            )

    verbindung.commit()
    verbindung.close()


def hole_kuehlschrank_bestand() -> list:
    """
    Ruft den gesamten aktuellen Inhalt des Kühlschranks aus der Datenbank ab.

    Returns:
        list: Eine Liste von Tupeln (produkt_name, menge, einheit).
    """
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()

    cursor.execute("SELECT produkt_name, menge, einheit FROM kuehlschrank")
    aktueller_bestand = cursor.fetchall()

    verbindung.close()
    return aktueller_bestand


def einkaufsliste_aktualisieren(
    produkt_name: str, menge_aenderung: float, einheit: str
) -> None:
    """
    Fügt ein Produkt zur Einkaufsliste hinzu oder modifiziert dessen Menge.
    Fällt die Menge auf oder unter 0, wird der Eintrag entfernt.

    Args:
        produkt_name (str): Der Name des benötigten Produkts.
        menge_aenderung (float): Die Mengenänderung auf dem Einkaufszettel.
        einheit (str): Die Maßeinheit des Produkts.
    """
    verbindung = sqlite3.connect(DATENBANK_PFAD)
    cursor = verbindung.cursor()

    cursor.execute(
        "SELECT menge FROM einkaufsliste WHERE produkt_name = ?", (produkt_name,)
    )
    ergebnis = cursor.fetchone()

    if ergebnis:
        neue_menge = ergebnis[0] + menge_aenderung
        if neue_menge <= 0:
            cursor.execute(
                "DELETE FROM einkaufsliste WHERE produkt_name = ?", (produkt_name,)
            )
        else:
            cursor.execute(
                "UPDATE einkaufsliste SET menge = ? WHERE produkt_name = ?",
                (neue_menge, produkt_name),
            )
    else:
        if menge_aenderung > 0:
            cursor.execute(
                "INSERT INTO einkaufsliste (produkt_name, menge, einheit) VALUES (?, ?, ?)",
                (produkt_name, menge_aenderung, einheit),
            )

    verbindung.commit()
    verbindung.close()


# Der Main-Guard Block
if __name__ == "__main__":
    print("--- Isolierter Modultest für datenbank_modul.py ---")

    # 1. Datenbank initialisieren
    init_datenbank()
    print("Datenbank erfolgreich initialisiert.")

    # 2. Testdaten in den Kühlschrank legen
    kuehlschrank_bestand_aktualisieren("Milch", 2.0, "Liter")
    kuehlschrank_bestand_aktualisieren("Eier", 6.0, "Stück")
    kuehlschrank_bestand_aktualisieren("Butter", 250.0, "g")    

    # 3. Bestand auslesen
    print("Bestand nach dem Einkauf:", hole_kuehlschrank_bestand())

    # 4. Test: Etwas verbrauchen (z. B. nach dem Kochen)
    kuehlschrank_bestand_aktualisieren("Milch", -0.5, "Liter")
    kuehlschrank_bestand_aktualisieren("Eier", -6.0, "Stück")  # Eier müssten jetzt gelöscht sein

    print("Bestand nach dem Kochen:", hole_kuehlschrank_bestand())