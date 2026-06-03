"""
Fachmodul für die grafische Benutzeroberfläche (GUI).
Beinhaltet Tabs für Bestandsmanagement, den Einkaufszettel und den Rezept-Scanner.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os

# Relative Imports
from .datenbank_modul import (hole_kuehlschrank_bestand, kuehlschrank_bestand_aktualisieren, 
                              einkaufsliste_aktualisieren, hole_einkaufsliste)
from .visualisierung_modul import erstelle_bestand_balkendiagramm
from .ocr_modul import lese_text_aus_bild, bereinige_erkannten_text, extrahiere_zutaten_liste


def aktualisiere_listen(listbox_kuehlschrank: tk.Listbox, listbox_einkauf: tk.Listbox) -> None:
    """Aktualisiert beide GUI-Listen mit den neuesten Daten aus der Datenbank."""
    listbox_kuehlschrank.delete(0, tk.END)
    for produkt, menge, einheit in hole_kuehlschrank_bestand():
        listbox_kuehlschrank.insert(tk.END, f"{produkt}: {menge} {einheit}")

    listbox_einkauf.delete(0, tk.END)
    for produkt, menge, einheit in hole_einkaufsliste():
        listbox_einkauf.insert(tk.END, f"{produkt}: {menge} {einheit}")


def einkauf_erledigen(listbox_einkauf: tk.Listbox, listbox_kuehlschrank: tk.Listbox) -> None:
    """Nimmt das ausgewählte Produkt vom Einkaufszettel und legt es in den Kühlschrank."""
    auswahl = listbox_einkauf.curselection()
    if not auswahl:
        messagebox.showwarning("Fehler", "Bitte wähle ein Produkt vom Einkaufszettel aus!")
        return

    # Text auslesen (Format: "Milch: 2.0 Liter")
    eintrag_text = listbox_einkauf.get(auswahl[0])
    produkt_name, rest = eintrag_text.split(":")
    menge_str, einheit = rest.strip().split(" ", 1)
    menge = float(menge_str)

    # 1. Im Kühlschrank den Bestand erhöhen
    kuehlschrank_bestand_aktualisieren(produkt_name.strip(), menge, einheit)
    # 2. Von der Einkaufsliste abziehen (löschen)
    einkaufsliste_aktualisieren(produkt_name.strip(), -menge, einheit)
    
    aktualisiere_listen(listbox_kuehlschrank, listbox_einkauf)
    messagebox.showinfo("Gekauft!", f"{produkt_name} wurde in den Kühlschrank gelegt.")


def produkt_zur_liste_hinzufuegen(
    name_var: tk.StringVar, menge_var: tk.StringVar, einheit_var: tk.StringVar, 
    listbox_einkauf: tk.Listbox, listbox_kuehlschrank: tk.Listbox
) -> None:
    """Liest die Felder aus und setzt das Produkt auf den Einkaufszettel."""
    produkt = name_var.get().strip()
    einheit = einheit_var.get().strip()
    try:
        menge = float(menge_var.get().strip())
    except ValueError:
        messagebox.showerror("Fehler", "Menge muss eine Zahl sein (z.B. 2.0).")
        return

    if not produkt or not einheit:
        return

    einkaufsliste_aktualisieren(produkt, menge, einheit)
    name_var.set("")
    menge_var.set("")
    einheit_var.set("")
    aktualisiere_listen(listbox_kuehlschrank, listbox_einkauf)


def starte_ocr_scan_ui() -> None:
    """Führt den OCR-Scan aus und zeigt das Ergebnis in der GUI."""
    bild_pfad = "bilder/test_rezept.jpg"
    if not os.path.exists(bild_pfad):
        messagebox.showwarning("Fehlt", f"Bitte lege ein Bild '{bild_pfad}' ab.")
        return
        
    rohtext = lese_text_aus_bild(bild_pfad)
    zeilen = bereinige_erkannten_text(rohtext)
    zutaten = extrahiere_zutaten_liste(zeilen)
    
    ergebnis = "\n".join(zutaten) if zutaten else "Keine Zutaten erkannt."
    messagebox.showinfo("Gefundene Zutaten", f"Aus dem Bild extrahiert:\n\n{ergebnis}")


def baue_einkaufs_tab(tab: ttk.Frame, listbox_kuehlschrank: tk.Listbox, 
                      listbox_einkauf: tk.Listbox) -> None:
    """Erstellt alle UI-Elemente für den Einkaufszettel-Tab."""
    name_var, menge_var, einheit_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
    
    eingabe_frame = tk.Frame(tab)
    eingabe_frame.pack(pady=10)
    tk.Label(eingabe_frame, text="Produkt:").grid(row=0, column=0)
    tk.Entry(eingabe_frame, textvariable=name_var, width=10).grid(row=0, column=1)
    tk.Label(eingabe_frame, text="Menge:").grid(row=0, column=2)
    tk.Entry(eingabe_frame, textvariable=menge_var, width=5).grid(row=0, column=3)
    tk.Label(eingabe_frame, text="Einheit:").grid(row=0, column=4)
    tk.Entry(eingabe_frame, textvariable=einheit_var, width=8).grid(row=0, column=5)

    tk.Button(tab, text="Auf den Einkaufszettel setzen", 
              command=lambda: produkt_zur_liste_hinzufuegen(
                  name_var, menge_var, einheit_var, listbox_einkauf, listbox_kuehlschrank
              )).pack(pady=5)
    
    listbox_einkauf.pack(pady=10, fill="x", padx=20)
    tk.Button(tab, text="✅ Ausgewähltes kaufen & einräumen", bg="lightblue",
              command=lambda: einkauf_erledigen(listbox_einkauf, listbox_kuehlschrank)).pack(pady=5)


def starte_app() -> None:
    """Initialisiert das Hauptfenster und die Tabs."""
    fenster = tk.Tk()
    fenster.title("Bestandsmanagement System")
    fenster.geometry("520x480")
    
    notebook = ttk.Notebook(fenster)
    tab_kuehl = ttk.Frame(notebook)
    tab_einkauf = ttk.Frame(notebook)
    notebook.add(tab_kuehl, text="❄️ Kühlschrank")
    notebook.add(tab_einkauf, text="🛒 Einkaufszettel")
    notebook.pack(expand=1, fill="both")

    listbox_kuehl = tk.Listbox(tab_kuehl, height=12)
    listbox_einkauf = tk.Listbox(tab_einkauf, height=12)

    # --- TAB 1: KÜHLSCHRANK ---
    tk.Label(tab_kuehl, text="Aktueller Kühlschrankbestand:").pack(pady=5)
    listbox_kuehl.pack(fill="x", padx=20, pady=5)
    
    tk.Button(tab_kuehl, text="📊 Bestands-Diagramm", 
              command=lambda: erstelle_bestand_balkendiagramm(hole_kuehlschrank_bestand())).pack(pady=5)
              
    tk.Button(tab_kuehl, text="📸 Rezept-Bild scannen", 
              command=starte_ocr_scan_ui).pack(pady=5)
    
    # --- TAB 2: EINKAUF ---
    baue_einkaufs_tab(tab_einkauf, listbox_kuehl, listbox_einkauf)
    
    aktualisiere_listen(listbox_kuehl, listbox_einkauf)
    fenster.mainloop()


if __name__ == "__main__":
    print("Bitte starte das Programm über die __main__.py")