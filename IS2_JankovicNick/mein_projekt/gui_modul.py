"""
Fachmodul für die grafische Benutzeroberfläche (GUI).
Architektur: View-Layer gemäß MVC-Prinzip.
"""
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

import sv_ttk

from .datenbank_modul import (
    hole_lagerbestand, 
    lagerbestand_aktualisieren, 
    einkaufsliste_aktualisieren, 
    hole_einkaufsliste, 
    bearbeite_bestand_produkt
)
from .visualisierung_modul import erstelle_bestand_balkendiagramm
from .ocr_modul import lese_text_aus_bild, parse_rezept_mit_ki
from .rezept_modul import (
    speichere_neues_rezept,
    lade_rezepte_aus_datei,
    ermittle_kochbare_rezepte,
    loesche_rezept,
    baue_rezept_aus_text,
    ermittle_fehlende_zutaten,
    skaliere_zutaten
)
from .export_modul import sende_einkaufsliste_per_mail, exportiere_bestand_als_csv

GLOBAL_PORTIONEN = 1

# --- HILFSFUNKTIONEN FÜR DIE GUI ---
def formatiere_listen_eintrag(produkt_name: str, menge: float, einheit: str) -> str:
    """Formatiert Produktdaten zentral für die Anzeige in GUI-Listen."""
    return f"{produkt_name}: {menge} {einheit}"


def parse_listen_eintrag(eintrag: str) -> tuple:
    """Zerschneidet einen String aus der GUI-Liste wieder in seine Bestandteile."""
    try:
        produkt_name, rest = eintrag.split(":")
        menge_str, einheit = rest.strip().split(" ", 1)
        return produkt_name.strip(), float(menge_str), einheit.strip()
    except ValueError:
        return "", 0.0, ""

# --- GUI FUNKTIONEN (VIEW-LOGIK) ---

def aktualisiere_listen(lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Aktualisiert Bestand, Einkaufsliste und Rezeptliste."""
    lb_b.delete(0, tk.END)
    bestand = hole_lagerbestand()

    for p, m, e in bestand:
        lb_b.insert(tk.END, formatiere_listen_eintrag(p, m, e))

    lb_e.delete(0, tk.END)
    for p, m, e in hole_einkaufsliste():
        lb_e.insert(tk.END, formatiere_listen_eintrag(p, m, e))

    lb_r.delete(0, tk.END)
    rezepte = lade_rezepte_aus_datei()

    # Fachmodul mit der Logik beauftragen (keine Doppelprogrammierung mehr)
    portions_vorgaben = {r["name"]: GLOBAL_PORTIONEN for r in rezepte}
    kochbar = ermittle_kochbare_rezepte(rezepte, bestand, portions_vorgaben)

    for r in rezepte:
        name = r.get("name")
        lb_r.insert(tk.END, f"✅ {name}" if name in kochbar else f"❌ {name}")


def einkauf_erledigen(lb_e: tk.Listbox, lb_b: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Räumt das aktuell in der Liste ausgewählte Produkt in den Bestand ein."""
    auswahl = lb_e.curselection()
    if not auswahl: 
        messagebox.showwarning("Fehler", "Bitte wähle ein Produkt aus!")
        return
        
    p_name, p_menge, p_einheit = parse_listen_eintrag(lb_e.get(auswahl[0]))
    lagerbestand_aktualisieren(p_name, p_menge, p_einheit)
    einkaufsliste_aktualisieren(p_name, -p_menge, p_einheit)
    aktualisiere_listen(lb_b, lb_e, lb_r)
    messagebox.showinfo("Erfolg", f"{p_name} wurde in den Bestand verschoben.")


def alles_einkaufen(lb_e: tk.Listbox, lb_b: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Räumt alle vorhandenen Produkte der Einkaufsliste in den Bestand."""
    liste = hole_einkaufsliste()
    if not liste: 
        messagebox.showinfo("Info", "Einkaufsliste ist leer.")
        return
        
    for p, m, e in liste:
        lagerbestand_aktualisieren(p, m, e)
        einkaufsliste_aktualisieren(p, -m, e)
        
    aktualisiere_listen(lb_b, lb_e, lb_r)
    messagebox.showinfo("Erfolg", "Alles in den Bestand übernommen!")


def einkauf_loeschen(lb_e: tk.Listbox, lb_b: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Löscht ein ausgewähltes Produkt restlos von der Einkaufsliste."""
    auswahl = lb_e.curselection()
    if not auswahl: 
        messagebox.showwarning("Fehler", "Bitte Produkt auswählen!")
        return
        
    p_name, p_menge, p_einheit = parse_listen_eintrag(lb_e.get(auswahl[0]))
    einkaufsliste_aktualisieren(p_name, -p_menge, p_einheit)
    aktualisiere_listen(lb_b, lb_e, lb_r)
    messagebox.showinfo("Gelöscht", f"{p_name} entfernt.")


def gui_mail_versenden() -> None:
    """Ruft das Export-Modul auf, um die Einkaufsliste per E-Mail zu versenden."""
    liste = hole_einkaufsliste()
    if not liste: 
        messagebox.showinfo("Info", "Zettel ist leer.")
        return
        
    if not sende_einkaufsliste_per_mail(liste): 
        messagebox.showerror("Fehler", "Mail-App konnte nicht gestartet werden.")


def csv_export_aktion() -> None:
    """Führt den CSV-Export aus und gibt Status-Feedback an den Nutzer."""
    pfad = os.path.join(os.path.dirname(__file__), "daten", "bestand_export.csv")
    if exportiere_bestand_als_csv(hole_lagerbestand(), pfad):
        messagebox.showinfo("Erfolg", f"Bestand wurde als CSV exportiert.")
    else: 
        messagebox.showerror("Fehler", "Export fehlgeschlagen.")


def speichere_bestand_aenderung(fenster, alter_name, name_v, menge_v, einh_v, lb_b, lb_e, lb_r):
    """Speichert GUI-Änderungen oder Neuanlagen in der Datenbank."""
    try:
        n_menge = float(menge_v.get())
        n_name = name_v.get().strip()
        n_einh = einh_v.get().strip()
        
        if not n_name or not n_einh: 
            messagebox.showerror("Fehler", "Bitte Felder ausfüllen.")
            return
            
        if alter_name == "": 
            lagerbestand_aktualisieren(n_name, n_menge, n_einh)
        else:
            bearbeite_bestand_produkt(alter_name, n_name, n_menge, n_einh)
            
        aktualisiere_listen(lb_b, lb_e, lb_r)
        fenster.destroy()
    except ValueError: 
        messagebox.showerror("Fehler", "Menge muss eine Zahl sein.")


def oeffne_bestand_bearbeiten(lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox, erzwinge_neu: bool = False) -> None:
    """Öffnet ein Fenster zum Hinzufügen (neu) oder Bearbeiten eines Produkts."""
    if erzwinge_neu: 
        lb_b.selection_clear(0, tk.END)
        
    auswahl = lb_b.curselection()
    a_name = ""
    m_str = "1.0"
    a_einh = "Stück"
    titel = "Neues Produkt"
    
    if not erzwinge_neu and auswahl:
        a_name, p_menge, a_einh = parse_listen_eintrag(lb_b.get(auswahl[0]))
        m_str = str(p_menge)
        titel = "Produkt bearbeiten"
        
    f = tk.Toplevel()
    f.title(titel)
    n_v = tk.StringVar(value=a_name)
    m_v = tk.StringVar(value=m_str)
    e_v = tk.StringVar(value=a_einh)
    
    ttk.Label(f, text="Name:").grid(row=0, column=0, pady=8, padx=10, sticky="w")
    ttk.Entry(f, textvariable=n_v, width=20).grid(row=0, column=1, padx=10)
    
    ttk.Label(f, text="Menge:").grid(row=1, column=0, pady=8, padx=10, sticky="w")
    ttk.Entry(f, textvariable=m_v, width=20).grid(row=1, column=1, padx=10)
    
    ttk.Label(f, text="Einheit:").grid(row=2, column=0, pady=8, padx=10, sticky="w")
    ttk.Entry(f, textvariable=e_v, width=20).grid(row=2, column=1, padx=10)
    
    ttk.Button(f, text="Speichern", style="Accent.TButton", 
               command=lambda: speichere_bestand_aenderung(f, a_name, n_v, m_v, e_v, lb_b, lb_e, lb_r)).grid(row=3, columnspan=2, pady=15)


def zeige_rezept_details(lb_r: tk.Listbox) -> None:
    """Zeigt Rezeptdetails mit globalen Portionen."""
    auswahl = lb_r.curselection()
    if not auswahl:
        return

    name = lb_r.get(auswahl[0])[2:].strip()
    bestand = hole_lagerbestand()

    for r in lade_rezepte_aus_datei():
        if r.get("name") != name:
            continue

        fenster = tk.Toplevel()
        fenster.title(f"Rezept: {name}")
        fenster.geometry("550x600")

        text_widget = tk.Text(fenster, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Fachmodul nutzen für skalierte Zutaten
        skalierte_zutaten = skaliere_zutaten(r, GLOBAL_PORTIONEN)
        # 2. Fachmodul nutzen für fehlende Zutaten
        fehlend = ermittle_fehlende_zutaten(r, bestand, GLOBAL_PORTIONEN)

        text = f"PORTIONEN: {GLOBAL_PORTIONEN}\n\nZUTATEN:\n"
        for z in skalierte_zutaten:
            text += f"• {z['menge']} {z['einheit']} {z['name']}\n"

        text += "\n"
        text += "⚠️ Zutaten fehlen!\n" if fehlend else "✅ Alle Zutaten vorhanden!\n"
        text += "\nSCHRITTE:\n"

        for i, s in enumerate(r.get("schritte", []), 1):
            s_sauber = re.sub(r'^\d+[\.)]\s*', '', s.strip())
            text += f"{i}. {s_sauber}\n"

        text_widget.insert("1.0", text)
        break

    
def rezept_loeschen_aktion(lb_r: tk.Listbox, lb_b: tk.Listbox, lb_e: tk.Listbox) -> None:
    """Führt nach Bestätigung die Löschung eines Rezepts aus."""
    auswahl = lb_r.curselection()
    if not auswahl: 
        messagebox.showwarning("Fehlt", "Bitte Rezept auswählen!")
        return
        
    name = lb_r.get(auswahl[0])[2:].strip()
    if messagebox.askyesno("Löschen", f"'{name}' wirklich löschen?"):
        if loesche_rezept(name):
            aktualisiere_listen(lb_b, lb_e, lb_r)
            messagebox.showinfo("Erfolg", "Gelöscht.")


def rezept_auf_einkaufsliste(lb_r: tk.Listbox, lb_b: tk.Listbox, lb_e: tk.Listbox) -> None:
    """Setzt fehlende Zutaten des Rezepts skaliert auf die Einkaufsliste."""
    auswahl = lb_r.curselection()
    if not auswahl:
        messagebox.showwarning("Fehlt", "Bitte Rezept auswählen!")
        return

    name = lb_r.get(auswahl[0])[2:].strip()

    for r in lade_rezepte_aus_datei():
        if r.get("name") == name:
            fehlende = ermittle_fehlende_zutaten(r, hole_lagerbestand(), GLOBAL_PORTIONEN)

            if not fehlende:
                messagebox.showinfo("Info", "Alles vorhanden!")
                return

            for z in fehlende:
                einkaufsliste_aktualisieren(z["name"], z["menge"], z["einheit"])
                
            break

    aktualisiere_listen(lb_b, lb_e, lb_r)
    messagebox.showinfo("Erfolg", "Fehlende Zutaten wurden hinzugefügt!")


def rezept_kochen(lb_r: tk.Listbox, lb_b: tk.Listbox, lb_e: tk.Listbox) -> None:
    """Zieht Zutaten eines gekochten Rezepts skaliert vom Bestand ab."""
    auswahl = lb_r.curselection()

    if not auswahl:
        messagebox.showwarning("Fehlt", "Bitte Rezept auswählen!")
        return

    eintrag = lb_r.get(auswahl[0])

    if eintrag.startswith("❌"):
        messagebox.showwarning("Fehler", "Zutaten fehlen!")
        return

    name = eintrag[2:].strip()

    for r in lade_rezepte_aus_datei():
        if r.get("name") == name:
            for z in skaliere_zutaten(r, GLOBAL_PORTIONEN):
                lagerbestand_aktualisieren(z["name"], -z["menge"], z["einheit"])
            break

    aktualisiere_listen(lb_b, lb_e, lb_r)
    messagebox.showinfo("Guten Appetit!", "Zutaten abgezogen.")


def speichere_bearbeitetes_rezept(fenster, name_var, portionen_var, text_z, text_s, lb_b, lb_e, lb_r):
    """Leitet GUI-Eingaben an das Rezept-Modul zur Datenerstellung weiter."""
    rezept = baue_rezept_aus_text(
        name_var.get(),
        text_z.get("1.0", tk.END),
        text_s.get("1.0", tk.END),
        int(portionen_var.get())
    )

    if speichere_neues_rezept(rezept):
        aktualisiere_listen(lb_b, lb_e, lb_r)
        messagebox.showinfo("Erfolg", "Gespeichert!")
        fenster.destroy()


def oeffne_rezept_bearbeiten(r_daten: dict, lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Öffnet den Rezept-Editor zur manuellen Korrektur der KI-Ergebnisse."""
    f = tk.Toplevel()
    f.title("Überprüfung")
    f.geometry("450x600")

    ttk.Label(f, text="Name:").pack(anchor="w", padx=15, pady=(10, 0))
    name_v = tk.StringVar(value=r_daten.get("name", ""))
    ttk.Entry(f, textvariable=name_v, width=50).pack(padx=15, pady=5)

    ttk.Label(f, text="Portionen:").pack(anchor="w", padx=15, pady=(10, 0))
    portionen_v = tk.IntVar(value=r_daten.get("portionen", 1))
    ttk.Entry(f, textvariable=portionen_v, width=10).pack(padx=15, pady=5)

    ttk.Label(f, text="Zutaten:").pack(anchor="w", padx=15, pady=(10, 0))
    tz = tk.Text(f, height=8, width=50)
    tz.pack(padx=15, pady=5)

    for z in r_daten.get("zutaten", []):
        tz.insert(tk.END, f"{z.get('menge','')} {z.get('einheit','')} {z.get('name','')}\n")

    ttk.Label(f, text="Schritte:").pack(anchor="w", padx=15, pady=(10, 0))
    ts = tk.Text(f, height=10, width=50)
    ts.pack(padx=15, pady=5)

    for s in r_daten.get("schritte", []):
        ts.insert(tk.END, f"{s}\n")

    ttk.Button(
        f,
        text="💾 Speichern",
        style="Accent.TButton",
        command=lambda: speichere_bearbeitetes_rezept(
            f, name_v, portionen_v, tz, ts, lb_b, lb_e, lb_r
        )
    ).pack(pady=15)


def starte_ocr_scan_ui(lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Startet den Workflow zum Scannen eines Rezepts per OCR und lokaler KI."""
    bild = os.path.join(os.path.dirname(__file__), "bilder", "test_rezept.jpg")
    if not os.path.exists(bild):
        messagebox.showwarning("Fehler", "Bild fehlt.")
        return
        
    rohtext = lese_text_aus_bild(bild)
    if not rohtext.strip(): 
        messagebox.showwarning("Fehler", "Kein Text gefunden.")
        return
        
    daten = parse_rezept_mit_ki(rohtext)
    if not daten:
        messagebox.showerror("Fehler", "KI-Strukturierung fehlgeschlagen.")
        return
        
    oeffne_rezept_bearbeiten(daten, lb_b, lb_e, lb_r)


def baue_rezepte_tab(tab: ttk.Frame, lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Erzeugt die UI-Elemente für den Rezept-Tab."""
    global GLOBAL_PORTIONEN
    ttk.Label(tab, text="Rezepte:", font=("Arial", 11, "bold")).pack(pady=(15, 2))
    regler = ttk.Frame(tab)
    regler.pack(pady=5)
    portionen_var = tk.IntVar(value=GLOBAL_PORTIONEN)

    def minus():
        """Verringert die berechnete Portionenzahl."""
        global GLOBAL_PORTIONEN
        if portionen_var.get() > 1:
            portionen_var.set(portionen_var.get() - 1)
            GLOBAL_PORTIONEN = portionen_var.get()
            aktualisiere_listen(lb_b, lb_e, lb_r)
    def plus():
        """Erhöht die berechnete Portionenzahl."""
        global GLOBAL_PORTIONEN
        portionen_var.set(portionen_var.get() + 1)
        GLOBAL_PORTIONEN = portionen_var.get()
        aktualisiere_listen(lb_b, lb_e, lb_r)

    ttk.Label(regler, text="Portionen").grid(row=0, column=0, padx=5)
    ttk.Button(regler, text="-", width=3, command=minus).grid(row=0, column=1)
    
    zahl_label = ttk.Label(regler, textvariable=portionen_var, width=4, anchor="center")
    zahl_label.grid(row=0, column=2, padx=15)

    ttk.Button(regler, text="+", width=3, command=plus).grid(row=0, column=3)

    lb_r.pack(fill="x", padx=20, pady=5)

    ttk.Button(tab, text="📸 Scan & Hinzufügen", style="Accent.TButton", width=35, command=lambda: starte_ocr_scan_ui(lb_b, lb_e, lb_r)).pack(pady=6)
    ttk.Button(tab, text="📖 Rezept-Details", width=35, command=lambda: zeige_rezept_details(lb_r)).pack(pady=4)
    ttk.Button(tab, text="🗑️ Löschen", width=35, command=lambda: rezept_loeschen_aktion(lb_r, lb_b, lb_e)).pack(pady=4)
    ttk.Button(tab, text="🛒 Fehlendes zur Einkaufsliste", width=35, command=lambda: rezept_auf_einkaufsliste(lb_r, lb_b, lb_e)).pack(pady=4)
    ttk.Button(tab, text="🍳 Kochen", width=35, command=lambda: rezept_kochen(lb_r, lb_b, lb_e)).pack(pady=8)


def baue_einkaufs_tab(tab: ttk.Frame, lb_b: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Erzeugt die UI-Elemente für den Einkaufszettel-Tab."""
    eingabe = ttk.Frame(tab)
    eingabe.pack(pady=15)
    
    n_v = tk.StringVar()
    m_v = tk.StringVar()
    e_v = tk.StringVar()
    
    ttk.Label(eingabe, text="Produkt:").grid(row=0, column=0, padx=2)
    ttk.Entry(eingabe, textvariable=n_v, width=12).grid(row=0, column=1, padx=4)
    ttk.Label(eingabe, text="Menge:").grid(row=0, column=2, padx=2)
    ttk.Entry(eingabe, textvariable=m_v, width=5).grid(row=0, column=3, padx=4)
    ttk.Label(eingabe, text="Einheit:").grid(row=0, column=4, padx=2)
    ttk.Entry(eingabe, textvariable=e_v, width=8).grid(row=0, column=5, padx=4)
    
    def eintrag_hinzufuegen():
            """Fügt der Einkaufsliste einen neuen Artikel hinzu."""
            try:
                einkaufsliste_aktualisieren(n_v.get().strip(), float(m_v.get()), e_v.get().strip())
                n_v.set("")
                m_v.set("")
                e_v.set("")
                aktualisiere_listen(lb_b, lb_e, lb_r)
            except ValueError: 
                messagebox.showerror("Fehler", "Bitte eine gültige Zahl bei der Menge eingeben!")

    ttk.Button(tab, text="➕ Hinzufügen", width=35, command=eintrag_hinzufuegen).pack(pady=5)
    lb_e.pack(fill="x", padx=20, pady=5)
    
    f = ttk.Frame(tab)
    f.pack(pady=6)
    
    ttk.Button(f, text="✅ Einräumen", width=22, command=lambda: einkauf_erledigen(lb_e, lb_b, lb_r)).grid(row=0, column=0, padx=4)
    ttk.Button(f, text="🗑️ Löschen", width=22, command=lambda: einkauf_loeschen(lb_e, lb_b, lb_r)).grid(row=0, column=4, padx=4)
    ttk.Button(tab, text="🛒 Alles Einräumen", style="Accent.TButton", width=46, command=lambda: alles_einkaufen(lb_e, lb_b, lb_r)).pack(pady=6)
    ttk.Button(tab, text="📧 Einkaufsliste per Mail", width=46, command=gui_mail_versenden).pack(pady=4)


def toggle_theme():
    """Wechselt zwischen Light- und Dark-Mode."""
    sv_ttk.toggle_theme()


def starte_app() -> None:
    """Initialisiert und startet das Hauptfenster der GUI."""
    fenster = tk.Tk()
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        sv_ttk.set_theme("light" if val == 1 else "dark")
    except Exception: 
        sv_ttk.set_theme("dark") 

    fenster.title("Bestandsmanagement System")
    fenster.geometry("540x650")
    notebook = ttk.Notebook(fenster)
    t1 = ttk.Frame(notebook)
    t2 = ttk.Frame(notebook)
    t3 = ttk.Frame(notebook)
    notebook.add(t1, text="📦 Bestand")
    notebook.add(t2, text="🛒 Einkaufen")
    notebook.add(t3, text="🍽️ Rezepte")
    notebook.pack(expand=1, fill="both")  
    lb_b = tk.Listbox(t1, height=12)
    lb_e = tk.Listbox(t2, height=12)
    lb_r = tk.Listbox(t3, height=12)   
    ttk.Label(t1, text="Lagerbestand:", font=("Arial", 11, "bold")).pack(pady=5)
    lb_b.pack(fill="x", padx=20, pady=5) 
    f = ttk.Frame(t1)
    f.pack(pady=4)
    ttk.Button(f, text="➕ Neu", width=16, command=lambda: oeffne_bestand_bearbeiten(lb_b, lb_e, lb_r, erzwinge_neu=True)).grid(row=0, column=0, padx=4)
    ttk.Button(f, text="✏️ Bearbeiten", width=16, command=lambda: oeffne_bestand_bearbeiten(lb_b, lb_e, lb_r, erzwinge_neu=False)).grid(row=0, column=1, padx=4)
    ttk.Button(t1, text="📊 Diagramm", width=35, command=lambda: erstelle_bestand_balkendiagramm(hole_lagerbestand())).pack(pady=4)
    ttk.Button(t1, text="💾 CSV Export", width=35, command=csv_export_aktion).pack(pady=4)
    ttk.Button(t1, text="🌓 Helle/Dunkle Ansicht", width=35, command=toggle_theme).pack(pady=4)
    baue_einkaufs_tab(t2, lb_b, lb_e, lb_r)
    baue_rezepte_tab(t3, lb_b, lb_e, lb_r)  
    aktualisiere_listen(lb_b, lb_e, lb_r)
    fenster.mainloop()


if __name__ == "__main__":
    print("Starte GUI-Testlauf...")
    print("Fülle Datenbank mit initialen Demo-Daten für die Ansicht...")
    
    # Wir nutzen die bereits im Modul importierten Funktionen
    lagerbestand_aktualisieren("Demo-Tomaten", 5.0, "Stück")
    lagerbestand_aktualisieren("Demo-Pasta", 500.0, "g")
    einkaufsliste_aktualisieren("Demo-Basilikum", 1.0, "Bund")
    
    print("Starte Benutzeroberfläche...")
    starte_app()