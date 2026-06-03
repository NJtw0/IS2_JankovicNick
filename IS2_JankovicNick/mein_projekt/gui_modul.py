"""
Fachmodul für die grafische Benutzeroberfläche (GUI).
Beinhaltet Tabs für Bestandsmanagement, Einkaufszettel, Editoren und E-Mail-Export.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import urllib.parse
import webbrowser

# Relative Imports
from .datenbank_modul import (hole_kuehlschrank_bestand, kuehlschrank_bestand_aktualisieren, 
                              einkaufsliste_aktualisieren, hole_einkaufsliste, 
                              bearbeite_kuehlschrank_produkt)
from .visualisierung_modul import erstelle_bestand_balkendiagramm
from .ocr_modul import lese_text_aus_bild, parse_rezept_mit_ki
from .rezept_modul import speichere_neues_rezept, lade_rezepte_aus_datei, ermittle_kochbare_rezepte


# ==========================================
# GEMEINSAME LISTEN LOGIK
# ==========================================
def aktualisiere_listen(lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    lb_k.delete(0, tk.END)
    bestand = hole_kuehlschrank_bestand()
    for produkt, menge, einheit in bestand:
        lb_k.insert(tk.END, f"{produkt}: {menge} {einheit}")

    lb_e.delete(0, tk.END)
    for produkt, menge, einheit in hole_einkaufsliste():
        lb_e.insert(tk.END, f"{produkt}: {menge} {einheit}")

    lb_r.delete(0, tk.END)
    rezepte = lade_rezepte_aus_datei("daten/rezepte.json")
    kochbar = ermittle_kochbare_rezepte(rezepte, bestand)
    for r in rezepte:
        name = r.get("name")
        lb_r.insert(tk.END, f"✅ {name}" if name in kochbar else f"❌ {name}")


def einkauf_erledigen(lb_e: tk.Listbox, lb_k: tk.Listbox, lb_r: tk.Listbox) -> None:
    auswahl = lb_e.curselection()
    if not auswahl:
        messagebox.showwarning("Fehler", "Bitte wähle ein Produkt aus!")
        return

    produkt_name, rest = lb_e.get(auswahl[0]).split(":")
    menge_str, einheit = rest.strip().split(" ", 1)
    
    kuehlschrank_bestand_aktualisieren(produkt_name.strip(), float(menge_str), einheit)
    einkaufsliste_aktualisieren(produkt_name.strip(), -float(menge_str), einheit)
    
    aktualisiere_listen(lb_k, lb_e, lb_r)
    messagebox.showinfo("Gekauft!", f"{produkt_name} wurde eingeräumt.")


def alles_einkaufen(lb_e: tk.Listbox, lb_k: tk.Listbox, lb_r: tk.Listbox) -> None:
    """Räumt den kompletten Einkaufszettel mit einem Klick in den Kühlschrank."""
    liste = hole_einkaufsliste()
    if not liste:
        messagebox.showinfo("Leer", "Der Einkaufszettel ist bereits leer.")
        return

    for produkt, menge, einheit in liste:
        kuehlschrank_bestand_aktualisieren(produkt, menge, einheit)
        einkaufsliste_aktualisieren(produkt, -menge, einheit)
        
    aktualisiere_listen(lb_k, lb_e, lb_r)
    messagebox.showinfo("Super Einkauf!", "Alle Produkte wurden erfolgreich in den Kühlschrank geräumt!")


def einkauf_loeschen(lb_e: tk.Listbox, lb_k: tk.Listbox, lb_r: tk.Listbox) -> None:
    auswahl = lb_e.curselection()
    if not auswahl:
        messagebox.showwarning("Fehler", "Bitte wähle ein Produkt zum Löschen aus!")
        return

    produkt_name, rest = lb_e.get(auswahl[0]).split(":")
    menge_str, einheit = rest.strip().split(" ", 1)
    
    einkaufsliste_aktualisieren(produkt_name.strip(), -float(menge_str), einheit)
    
    aktualisiere_listen(lb_k, lb_e, lb_r)
    messagebox.showinfo("Gelöscht", f"{produkt_name} wurde vom Einkaufszettel entfernt.")


def sende_einkaufsliste_per_mail() -> None:
    liste = hole_einkaufsliste()
    if not liste:
        messagebox.showinfo("Leer", "Dein Einkaufszettel ist aktuell leer.")
        return

    body = "Hallo!\n\nHier ist mein aktueller Einkaufszettel:\n\n"
    for prod, menge, einh in liste:
        body += f"- [ ] {menge} {einh} {prod}\n"

    body_encoded = urllib.parse.quote(body)
    subject_encoded = urllib.parse.quote("Mein Einkaufszettel 🛒")
    
    try:
        webbrowser.open(f"mailto:?subject={subject_encoded}&body={body_encoded}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Mail-Programm konnte nicht geöffnet werden: {e}")


# ==========================================
# KÜHLSCHRANK HINZUFÜGEN & EDITOR LOGIK
# ==========================================
def speichere_kuehl_aenderung(fenster, alter_name, name_v, menge_v, einh_v, lb_k, lb_e, lb_r):
    try:
        n_menge = float(menge_v.get())
        n_name = name_v.get().strip()
        n_einh = einh_v.get().strip()
        
        if not n_name or not n_einh:
            messagebox.showerror("Fehler", "Bitte Name und Einheit ausfüllen.")
            return
            
        if alter_name == "":
            kuehlschrank_bestand_aktualisieren(n_name, n_menge, n_einh)
        else:
            bearbeite_kuehlschrank_produkt(alter_name, n_name, n_menge, n_einh)
            
        aktualisiere_listen(lb_k, lb_e, lb_r)
        fenster.destroy()
    except ValueError:
        messagebox.showerror("Fehler", "Menge muss eine Zahl sein (z.B. 2.5).")


def oeffne_kuehlschrank_bearbeiten(lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    auswahl = lb_k.curselection()
    if not auswahl:
        alter_name, menge_str, alte_einheit = "", "1.0", "Stück"
        titel = "Neues Produkt hinzufügen"
    else:
        alter_name, rest = lb_k.get(auswahl[0]).split(":")
        alter_name = alter_name.strip()
        menge_str, alte_einheit = rest.strip().split(" ", 1)
        titel = "Produkt bearbeiten"

    f = tk.Toplevel()
    f.title(titel)
    n_var = tk.StringVar(value=alter_name)
    m_var = tk.StringVar(value=menge_str)
    e_var = tk.StringVar(value=alte_einheit)
    
    tk.Label(f, text="Name:").grid(row=0, column=0, pady=5, padx=5)
    tk.Entry(f, textvariable=n_var).grid(row=0, column=1, padx=5)
    tk.Label(f, text="Menge (0=Löschen):").grid(row=1, column=0, pady=5, padx=5)
    tk.Entry(f, textvariable=m_var).grid(row=1, column=1, padx=5)
    tk.Label(f, text="Einheit:").grid(row=2, column=0, pady=5, padx=5)
    tk.Entry(f, textvariable=e_var).grid(row=2, column=1, padx=5)
    
    tk.Button(f, text="Speichern", bg="lightgreen", command=lambda: speichere_kuehl_aenderung(
        f, alter_name, n_var, m_var, e_var, lb_k, lb_e, lb_r)).grid(row=3, columnspan=2, pady=10)


# ==========================================
# REZEPT LOGIK (KOCHEN, KI-SCAN & EINKAUFEN)
# ==========================================
def zeige_rezept_details(lb_r: tk.Listbox) -> None:
    auswahl = lb_r.curselection()
    if not auswahl:
        return
    name = lb_r.get(auswahl[0])[2:].strip()
    
    for r in lade_rezepte_aus_datei("daten/rezepte.json"):
        if r.get("name") == name:
            text = f"ZUTATEN:\n"
            for z in r.get("zutaten", []): text += f"• {z.get('menge')} {z.get('einheit')} {z.get('name')}\n"
            text += "\nSCHRITTE:\n"
            for i, s in enumerate(r.get("schritte", []), 1): text += f"{i}. {s}\n"
            messagebox.showinfo(f"Rezept: {name}", text)
            break


def rezept_auf_einkaufsliste(lb_r: tk.Listbox, lb_k: tk.Listbox, lb_e: tk.Listbox) -> None:
    auswahl = lb_r.curselection()
    if not auswahl:
        messagebox.showwarning("Fehlt", "Bitte wähle zuerst ein Rezept aus!")
        return
        
    eintrag = lb_r.get(auswahl[0])
    name = eintrag[2:].strip()
    
    for r in lade_rezepte_aus_datei("daten/rezepte.json"):
        if r.get("name") == name:
            for z in r.get("zutaten", []):
                einkaufsliste_aktualisieren(z.get("name"), float(z.get("menge")), z.get("einheit"))
            break
            
    aktualisiere_listen(lb_k, lb_e, lb_r)
    messagebox.showinfo("Erfolg", f"Die Zutaten für '{name}' stehen jetzt auf dem Einkaufszettel!")


def rezept_kochen(lb_r: tk.Listbox, lb_k: tk.Listbox, lb_e: tk.Listbox) -> None:
    auswahl = lb_r.curselection()
    if not auswahl:
        messagebox.showwarning("Fehlt", "Bitte Rezept auswählen!")
        return
        
    eintrag = lb_r.get(auswahl[0])
    if eintrag.startswith("❌"):
        messagebox.showwarning("Fehler", "Zutaten fehlen! Geh erst einkaufen.")
        return
        
    name = eintrag[2:].strip()
    for r in lade_rezepte_aus_datei("daten/rezepte.json"):
        if r.get("name") == name:
            for z in r.get("zutaten", []):
                kuehlschrank_bestand_aktualisieren(z.get("name"), -float(z.get("menge")), z.get("einheit"))
            break
            
    aktualisiere_listen(lb_k, lb_e, lb_r)
    messagebox.showinfo("Guten Appetit!", f"'{name}' gekocht!\nZutaten wurden abgezogen.")


def speichere_bearbeitetes_rezept(fenster, name_var, text_z, text_s, lb_k, lb_e, lb_r):
    neue_zutaten = []
    for zeile in text_z.get("1.0", tk.END).strip().split("\n"):
        if not zeile.strip(): continue
        teile = zeile.strip().split(maxsplit=2)
        if len(teile) >= 3:
            try: neue_zutaten.append({"menge": float(teile[0]), "einheit": teile[1], "name": teile[2]})
            except ValueError: neue_zutaten.append({"menge": 1.0, "einheit": "Stück", "name": zeile})
        else:
            neue_zutaten.append({"menge": 1.0, "einheit": "Stück", "name": zeile})
            
    neue_schritte = [s.strip() for s in text_s.get("1.0", tk.END).strip().split("\n") if s.strip()]
    rezept = {"name": name_var.get().strip(), "zutaten": neue_zutaten, "schritte": neue_schritte}
    
    if speichere_neues_rezept(rezept):
        aktualisiere_listen(lb_k, lb_e, lb_r)
        messagebox.showinfo("Erfolg", "Rezept gespeichert!")
        fenster.destroy()


def oeffne_rezept_bearbeiten(r_daten: dict, lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    f = tk.Toplevel()
    f.title("KI-Ergebnis überprüfen")
    f.geometry("450x550")
    
    tk.Label(f, text="Name:").pack(anchor="w", padx=10)
    name_v = tk.StringVar(value=r_daten.get("name", ""))
    tk.Entry(f, textvariable=name_v, width=65).pack(padx=10)

    tk.Label(f, text="Zutaten (Menge Einheit Produkt):").pack(anchor="w", padx=10, pady=(10,0))
    tz = tk.Text(f, height=8, width=50)
    tz.pack(padx=10)
    for z in r_daten.get("zutaten", []): tz.insert(tk.END, f"{z.get('menge','')} {z.get('einheit','')} {z.get('name','')}\n")

    tk.Label(f, text="Schritte:").pack(anchor="w", padx=10, pady=(10,0))
    ts = tk.Text(f, height=10, width=50)
    ts.pack(padx=10)
    for s in r_daten.get("schritte", []): ts.insert(tk.END, f"{s}\n")
        
    tk.Button(f, text="💾 Speichern", command=lambda: speichere_bearbeitetes_rezept(f, name_v, tz, ts, lb_k, lb_e, lb_r)).pack(pady=10)


def starte_ocr_scan_ui(lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    bild = "bilder/test_rezept.jpg"
    if not os.path.exists(bild):
        messagebox.showwarning("Fehlt", f"Bitte '{bild}' ablegen.")
        return
        
    messagebox.showinfo("Scan", "Text wird von lokaler KI analysiert...\nKlicke auf OK.")
    rohtext = lese_text_aus_bild(bild)
    
    if not rohtext.strip():
        messagebox.showwarning("Fehler", "Kein Text gefunden.")
        return
        
    daten = parse_rezept_mit_ki(rohtext)
    
    if not daten:
        messagebox.showerror("Fehler", "KI konnte nicht strukturieren.")
        return
        
    oeffne_rezept_bearbeiten(daten, lb_k, lb_e, lb_r)


# ==========================================
# GUI AUFBAU (TABS)
# ==========================================
def baue_rezepte_tab(tab: ttk.Frame, lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    tk.Label(tab, text="Deine gespeicherten Rezepte:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    tk.Label(tab, text="✅ = Kochbar | ❌ = Zutaten fehlen").pack()
    
    lb_r.pack(fill="x", padx=20, pady=10)
    
    tk.Button(tab, text="📖 Rezept-Details ansehen", command=lambda: zeige_rezept_details(lb_r)).pack(pady=5)
    tk.Button(tab, text="🛒 Zutaten auf Einkaufszettel setzen", bg="lightblue", command=lambda: rezept_auf_einkaufsliste(lb_r, lb_k, lb_e)).pack(pady=5)
    tk.Button(tab, text="🍳 Rezept Kochen (Zutaten abziehen)", bg="orange", command=lambda: rezept_kochen(lb_r, lb_k, lb_e)).pack(pady=5)


def baue_einkaufs_tab(tab: ttk.Frame, lb_k: tk.Listbox, lb_e: tk.Listbox, lb_r: tk.Listbox) -> None:
    eingabe = tk.Frame(tab)
    eingabe.pack(pady=10)
    n_v, m_v, e_v = tk.StringVar(), tk.StringVar(), tk.StringVar()
    
    tk.Label(eingabe, text="Produkt:").grid(row=0, column=0)
    tk.Entry(eingabe, textvariable=n_v, width=12).grid(row=0, column=1, padx=2)
    tk.Label(eingabe, text="Menge:").grid(row=0, column=2)
    tk.Entry(eingabe, textvariable=m_v, width=5).grid(row=0, column=3, padx=2)
    tk.Label(eingabe, text="Einheit:").grid(row=0, column=4)
    tk.Entry(eingabe, textvariable=e_v, width=8).grid(row=0, column=5, padx=2)

    def add():
        try:
            einkaufsliste_aktualisieren(n_v.get().strip(), float(m_v.get()), e_v.get().strip())
            n_v.set(""); m_v.set(""); e_v.set("")
            aktualisiere_listen(lb_k, lb_e, lb_r)
        except ValueError:
            messagebox.showerror("Fehler", "Die Menge muss eine Zahl sein.")

    tk.Button(tab, text="➕ Auf den Einkaufszettel", command=add).pack(pady=5)
    lb_e.pack(fill="x", padx=20, pady=10)
    
    # Die Einkaufs-Buttons
    frame_btns = tk.Frame(tab)
    frame_btns.pack(pady=5)
    tk.Button(frame_btns, text="✅ Ausgewähltes einräumen", bg="lightblue", command=lambda: einkauf_erledigen(lb_e, lb_k, lb_r)).grid(row=0, column=0, padx=5)
    tk.Button(frame_btns, text="🗑️ Ausgewähltes löschen", bg="#ffcccc", command=lambda: einkauf_loeschen(lb_e, lb_k, lb_r)).grid(row=0, column=1, padx=5)
    
    # NEU: Der "Alles auf einmal einkaufen"-Button
    tk.Button(tab, text="🛒 Alles auf einmal einkaufen & einräumen", bg="#90ee90", command=lambda: alles_einkaufen(lb_e, lb_k, lb_r)).pack(pady=2)
    
    tk.Button(tab, text="📧 Liste als E-Mail ans Handy schicken", bg="lightyellow", command=sende_einkaufsliste_per_mail).pack(pady=5)


def starte_app() -> None:
    fenster = tk.Tk()
    fenster.title("Bestandsmanagement System mit lokaler KI")
    fenster.geometry("540x630")
    
    notebook = ttk.Notebook(fenster)
    tab_kuehl = ttk.Frame(notebook)
    tab_einkauf = ttk.Frame(notebook)
    tab_rezepte = ttk.Frame(notebook)
    notebook.add(tab_kuehl, text="❄️ Kühlschrank")
    notebook.add(tab_einkauf, text="🛒 Einkaufszettel")
    notebook.add(tab_rezepte, text="🍽️ Rezepte")
    notebook.pack(expand=1, fill="both")

    lb_k = tk.Listbox(tab_kuehl, height=12)
    lb_e = tk.Listbox(tab_einkauf, height=12)
    lb_r = tk.Listbox(tab_rezepte, height=12)

    # --- TAB 1: KÜHLSCHRANK ---
    tk.Label(tab_kuehl, text="Aktueller Kühlschrankbestand:").pack(pady=5)
    lb_k.pack(fill="x", padx=20, pady=5)
    
    tk.Button(tab_kuehl, text="➕ Neu / ✏️ Bearbeiten", command=lambda: oeffne_kuehlschrank_bearbeiten(lb_k, lb_e, lb_r)).pack(pady=2)
    tk.Button(tab_kuehl, text="📊 Bestands-Diagramm", command=lambda: erstelle_bestand_balkendiagramm(hole_kuehlschrank_bestand())).pack(pady=10)
    tk.Button(tab_kuehl, text="📸 Neues KI-Rezept scannen", bg="lightgreen", command=lambda: starte_ocr_scan_ui(lb_k, lb_e, lb_r)).pack(pady=5)
    
    # --- TAB 2 & 3: EINKAUF & REZEPTE ---
    baue_einkaufs_tab(tab_einkauf, lb_k, lb_e, lb_r)
    baue_rezepte_tab(tab_rezepte, lb_k, lb_e, lb_r)
    
    aktualisiere_listen(lb_k, lb_e, lb_r)
    fenster.mainloop()


if __name__ == "__main__":
    print("Bitte starte das Programm über die __main__.py")