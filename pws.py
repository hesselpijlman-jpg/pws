import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from openai import OpenAI
from PIL import Image, ImageTk  # voor nep-FaceTime foto's

# === AI Instellen ===
client = OpenAI(api_key="--JOUW_KEY--")  # vervang door jouw key als je AI wilt gebruiken

# === Data Opslaan ===
DATA_FILE = "gebruikers_data.json"

# Startbestand maken als het nog niet bestaat
if not os.path.exists(DATA_FILE):
    startdata = {
        "nieuws": {
            "Buurtnieuws": [],
            "Activiteiten": [],
            "Gezondheidstips": [],
            "Wereldnieuws": []
        },
        "piet": {
            "wachtwoord": "1234",
            "rol": "beheerder",
            "antwoorden": [],
            "chat": {}
        }
    }
    with open(DATA_FILE, "w") as f:
        json.dump(startdata, f, indent=4)

def laad_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def opslaan_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Zorg dat Piet altijd beheerder is
data = laad_data()
if "piet" in data:
    if not isinstance(data["piet"], dict):
        data["piet"] = {"wachtwoord": "1234", "rol": "beheerder", "antwoorden": [], "chat": {}}
    else:
        data["piet"]["rol"] = "beheerder"
        data["piet"].setdefault("wachtwoord", "1234")
        data["piet"].setdefault("antwoorden", [])
        data["piet"].setdefault("chat", {})
else:
    data["piet"] = {"wachtwoord": "1234", "rol": "beheerder", "antwoorden": [], "chat": {}}
data.setdefault("nieuws", {"Buurtnieuws": [], "Activiteiten": [], "Gezondheidstips": [], "Wereldnieuws": []})
opslaan_data(data)

# === Hoofdvenster ===
root = tk.Tk()
root.title("Alles voor Ouderen")
root.geometry("950x700")

gebruiker = ""
antwoorden = []

def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# === Startscherm ===
def start_scherm():
    clear_frame()
    tk.Label(root, text="Welkom bij Alles voor Ouderen", font=("Arial", 24, "bold")).pack(pady=30)
    tk.Button(root, text="Inloggen", font=("Arial", 16), width=30, command=login_scherm).pack(pady=8)
    tk.Button(root, text="Account aanmaken", font=("Arial", 16), width=30, command=aanmeld_scherm).pack(pady=8)
    tk.Button(root, text="Afsluiten", font=("Arial", 14), width=20, command=root.destroy).pack(pady=20)

# === Inloggen ===
def login_scherm():
    clear_frame()
    tk.Label(root, text="Inloggen", font=("Arial", 22, "bold")).pack(pady=15)

    tk.Label(root, text="Gebruikersnaam:", font=("Arial", 14)).pack()
    naam_entry = tk.Entry(root, font=("Arial", 14))
    naam_entry.pack(pady=5)

    tk.Label(root, text="Wachtwoord:", font=("Arial", 14)).pack()
    ww_entry = tk.Entry(root, show="*", font=("Arial", 14))
    ww_entry.pack(pady=5)

    melding = tk.Label(root, text="", font=("Arial", 12), fg="red")
    melding.pack(pady=5)

    def inloggen():
        global gebruiker, antwoorden
        naam = naam_entry.get().strip()
        ww = ww_entry.get().strip()
        if not naam or not ww:
            melding.config(text="Vul alle velden in.")
            return
        data = laad_data()
        if naam not in data or not isinstance(data.get(naam), dict):
            melding.config(text="Gebruiker niet gevonden.")
            return
        if data[naam].get("wachtwoord") != ww:
            melding.config(text="Verkeerd wachtwoord.")
            return
        gebruiker = naam
        antwoorden = data[gebruiker].get("antwoorden", [])
        welkom_scherm()

    tk.Button(root, text="Inloggen", font=("Arial", 14), command=inloggen).pack(pady=8)
    tk.Button(root, text="Terug", font=("Arial", 14), command=start_scherm).pack(pady=6)

# === Account maken ===
def aanmeld_scherm():
    clear_frame()
    tk.Label(root, text="Account aanmaken", font=("Arial", 22, "bold")).pack(pady=15)

    tk.Label(root, text="Kies een naam:", font=("Arial", 14)).pack()
    naam_entry = tk.Entry(root, font=("Arial", 14))
    naam_entry.pack(pady=5)

    tk.Label(root, text="Kies een wachtwoord:", font=("Arial", 14)).pack()
    ww_entry = tk.Entry(root, show="*", font=("Arial", 14))
    ww_entry.pack(pady=5)

    melding = tk.Label(root, text="", font=("Arial", 12), fg="red")
    melding.pack(pady=5)

    def aanmaken():
        global gebruiker
        naam = naam_entry.get().strip()
        ww = ww_entry.get().strip()
        if not naam or not ww:
            melding.config(text="Vul alles in.")
            return
        data = laad_data()
        if naam in data:
            melding.config(text="Naam bestaat al.")
            return
        data[naam] = {"wachtwoord": ww, "rol": "gebruiker", "antwoorden": [], "chat": {}}
        opslaan_data(data)
        gebruiker = naam
        antwoorden[:] = []
        welkom_scherm()

    tk.Button(root, text="Aanmaken", font=("Arial", 14), command=aanmaken).pack(pady=8)
    tk.Button(root, text="Terug", font=("Arial", 14), command=start_scherm).pack(pady=6)

# === Vragenlijst ===
vragen = [
    {"vraag": "Wat doet u in uw vrije tijd?", "antwoorden": ["Lezen", "Sporten", "Reizen", "Tuinieren"]},
    {"vraag": "Wat drinkt u het liefst?", "antwoorden": ["Thee", "Koffie", "Fris", "Water"]},
    {"vraag": "Heeft u huisdieren?", "antwoorden": ["Hond", "Kat", "Ander dier", "Geen"]},
    {"vraag": "Hoe vaak bezoekt u familie of vrienden?", "antwoorden": ["Vaak", "Soms", "Zelden", "Nooit"]},
    {"vraag": "Wat vindt u leuk om te doen in een groep?", "antwoorden": ["Koffie drinken", "Spelletjes", "Samen eten", "Niks"]}
]

def toon_vraag(i):
    clear_frame()
    if i < len(vragen):
        v = vragen[i]
        tk.Label(root, text=f"Vraag {i+1} van {len(vragen)}", font=("Arial", 14)).pack(pady=5)
        tk.Label(root, text=v["vraag"], font=("Arial", 16, "bold")).pack(pady=10)
        for antw in v["antwoorden"]:
            tk.Button(root, text=antw, font=("Arial", 14),
                      command=lambda a=antw: beantwoord(i, a)).pack(pady=5)
    else:
        data = laad_data()
        if gebruiker and isinstance(data.get(gebruiker), dict):
            data[gebruiker]["antwoorden"] = antwoorden
            opslaan_data(data)
        toon_match()

def beantwoord(i, antwoord):
    if len(antwoorden) > i:
        antwoorden[i] = antwoord
    else:
        antwoorden.append(antwoord)
    toon_vraag(i + 1)

# === Matching ===
def toon_match():
    clear_frame()
    data = laad_data()
    tk.Label(root, text="🔍 Jouw Matches", font=("Arial", 20, "bold")).pack(pady=15)
    gevonden = False
    for naam, info in data.items():
        if naam in ["nieuws", gebruiker] or not isinstance(info, dict):
            continue
        if not info.get("antwoorden"):
            continue
        score = sum(a == b for a, b in zip(antwoorden, info["antwoorden"]))
        if score > 0:
            gevonden = True
            rij = tk.Frame(root)
            rij.pack(pady=4, fill="x", padx=40)
            tk.Label(rij, text=f"{naam} — {score} overeenkomsten", font=("Arial", 14)).pack(side="left")
            tk.Button(rij, text="💬 Chat", command=lambda n=naam: open_chat(n)).pack(side="right")
    if not gevonden:
        tk.Label(root, text="Geen matches gevonden.", font=("Arial", 14)).pack(pady=10)
    tk.Button(root, text="Terug", command=welkom_scherm).pack(pady=20)

# === Chatfunctie ===
def open_chat_selectie():
    clear_frame()
    data = laad_data()
    tk.Label(root, text="Kies met wie u wilt chatten:", font=("Arial", 18, "bold")).pack(pady=20)
    for naam, info in data.items():
        if naam == "nieuws" or naam == gebruiker:
            continue
        if isinstance(info, dict):
            tk.Button(root, text=naam, font=("Arial", 14), command=lambda n=naam: open_chat(n)).pack(pady=5)
    tk.Button(root, text="Terug", font=("Arial", 14), command=welkom_scherm).pack(pady=20)

def open_chat(ander):
    clear_frame()
    data = laad_data()
    geschiedenis = data.get(gebruiker, {}).get("chat", {}).get(ander, [])

    tk.Label(root, text=f"Chat met {ander}", font=("Arial", 18, "bold")).pack(pady=10)
    chatbox = tk.Text(root, height=15, font=("Arial", 12), state="normal")
    chatbox.pack(padx=10, pady=10, fill="both", expand=True)
    for msg in geschiedenis:
        chatbox.insert(tk.END, msg + "\n")
    chatbox.config(state="disabled")

    invoer = tk.Entry(root, font=("Arial", 14))
    invoer.pack(fill="x", padx=10, pady=5)

    def stuur():
        bericht = invoer.get().strip()
        if not bericht:
            return
        invoer.delete(0, tk.END)
        tijd = datetime.now().strftime("%H:%M")
        tekst = f"{gebruiker} ({tijd}): {bericht}"
        chatbox.config(state="normal")
        chatbox.insert(tk.END, tekst + "\n")
        chatbox.config(state="disabled")
        data = laad_data()
        data.setdefault(gebruiker, {}).setdefault("chat", {}).setdefault(ander, []).append(tekst)
        data.setdefault(ander, {}).setdefault("chat", {}).setdefault(gebruiker, []).append(tekst)
        opslaan_data(data)

    tk.Button(root, text="Stuur", font=("Arial", 14), command=stuur).pack(pady=5)
    tk.Button(root, text="Terug", font=("Arial", 14), command=open_chat_selectie).pack(pady=10)

# === AI Chat ===
def ai_chat_scherm():
    clear_frame()
    tk.Label(root, text="AI Meeluister Chat", font=("Arial", 18, "bold")).pack(pady=10)

    ai_box = tk.Text(root, height=20, width=45, font=("Arial", 12), bg="#f0f0f0")
    ai_box.pack(side="left", padx=5, pady=5)
    ai_box.insert(tk.END, "🤖 AI: Hallo! Ik luister mee.\n")
    ai_box.config(state="disabled")

    user_box = tk.Text(root, height=20, width=45, font=("Arial", 12))
    user_box.pack(side="right", padx=5, pady=5)

    invoer = tk.Entry(root, font=("Arial", 14))
    invoer.pack(pady=5, fill="x")

    def stuur_ai():
        msg = invoer.get().strip()
        if not msg:
            return
        invoer.delete(0, tk.END)
        user_box.insert(tk.END, f"Jij: {msg}\n")

        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=f"De gebruiker zegt: '{msg}'. Stel 3 korte vervolgvraagjes."
            )
            antwoord = getattr(response, "output_text", None) or str(response)
        except Exception as e:
            antwoord = f"[AI-fout: {e}]"

        ai_box.config(state="normal")
        ai_box.insert(tk.END, f"🤖 AI: {antwoord}\n")
        ai_box.config(state="disabled")

    tk.Button(root, text="Stuur", font=("Arial", 14), command=stuur_ai).pack(pady=5)
    tk.Button(root, text="Terug", font=("Arial", 14), command=welkom_scherm).pack(pady=5)

# === Nieuws ===
def nieuws_scherm():
    clear_frame()
    tk.Label(root, text="📢 Nieuws & Updates", font=("Arial", 18, "bold")).pack(pady=10)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    for categorie in ["Buurtnieuws", "Activiteiten", "Gezondheidstips", "Wereldnieuws"]:
        frame = tk.Frame(notebook)
        notebook.add(frame, text=categorie)
        toon_nieuws_in_tab(frame, categorie)

    tk.Button(root, text="Terug naar menu", font=("Arial", 14), command=welkom_scherm).pack(pady=10)

def toon_nieuws_in_tab(frame, categorie):
    data = laad_data()
    nieuws_list = data.get("nieuws", {}).get(categorie, [])
    tekstvak = tk.Text(frame, font=("Arial", 12), wrap="word", height=15)
    tekstvak.pack(fill="both", expand=True, padx=10, pady=10)
    tekstvak.insert(tk.END, "\n".join([f"- {item}" for item in nieuws_list]) if nieuws_list else "Geen items.")
    tekstvak.config(state="disabled")

    rol = data.get(gebruiker, {}).get("rol")
    if rol == "beheerder":
        invoer = tk.Entry(frame, font=("Arial", 12))
        invoer.pack(fill="x", padx=10, pady=5)

        def toevoegen():
            item = invoer.get().strip()
            if not item:
                messagebox.showinfo("Leeg", "Vul eerst tekst in.")
                return
            d = laad_data()
            d.setdefault("nieuws", {}).setdefault(categorie, []).append(item)
            opslaan_data(d)
            nieuws_scherm()

        tk.Button(frame, text="➕ Voeg nieuws toe", command=toevoegen).pack(pady=5)

        if categorie == "Wereldnieuws":
            def ai_genereren():
                try:
                    response = client.responses.create(
                        model="gpt-4o-mini",
                        input="Genereer 4 korte, begrijpelijke wereldnieuwsberichten voor ouderen."
                    )
                    tekst = getattr(response, "output_text", None) or str(response)
                    items = [s.strip("- ").strip() for s in tekst.split("\n") if len(s.strip()) > 5]
                    d = laad_data()
                    d.setdefault("nieuws", {}).setdefault("Wereldnieuws", []).extend(items)
                    opslaan_data(d)
                    nieuws_scherm()
                except Exception as e:
                    messagebox.showerror("AI fout", str(e))

            tk.Button(frame, text="🔄 AI nieuws genereren", command=ai_genereren).pack(pady=5)

# === FaceTime ===
def facetime_menu():
    clear_frame()
    data = laad_data()
    tk.Label(root, text="📞 FaceTime", font=("Arial", 22, "bold")).pack(pady=15)
    tk.Label(root, text="Kies een contact om te bellen:", font=("Arial", 14)).pack(pady=10)

    lijst_frame = tk.Frame(root)
    lijst_frame.pack(pady=10)

    for naam in data:
        if naam not in ["nieuws", gebruiker] and isinstance(data.get(naam), dict):
            tk.Button(lijst_frame, text=f"{naam}", font=("Arial", 14), width=25,
                      command=lambda n=naam: facetime_belscherm(n)).pack(pady=4)

    tk.Button(root, text="Terug", font=("Arial", 14), command=welkom_scherm).pack(pady=20)

def facetime_belscherm(contact):
    clear_frame()
    tk.Label(root, text=f"📞 FaceTime met {contact}", font=("Arial", 22, "bold")).pack(pady=10)

    try:
        img = Image.open("facetime.jpg")
    except:
        img = Image.new("RGB", (400, 300), "gray")
    img = img.resize((400, 300))
    img_tk = ImageTk.PhotoImage(img)
    panel = tk.Label(root, image=img_tk)
    panel.image = img_tk
    panel.pack(pady=20)

    tk.Button(root, text="📞 BEL NU", font=("Arial", 18, "bold"), bg="green", fg="white",
              width=15, height=2, command=lambda: facetime_in_gesprek(contact)).pack(pady=10)

    tk.Label(root, text="🤖 AI luistert mee…", font=("Arial", 12, "italic"), fg="#666").pack(pady=4)
    tk.Button(root, text="Terug", font=("Arial", 14), command=facetime_menu).pack(pady=20)

def facetime_in_gesprek(contact):
    clear_frame()
    tk.Label(root, text=f"📞 In gesprek met {contact}", font=("Arial", 22, "bold")).pack(pady=15)
    try:
        img = Image.open("facetime.jpg")
    except:
        img = Image.new("RGB", (400, 300), "gray")
    img = img.resize((400, 300))
    img_tk = ImageTk.PhotoImage(img)
    panel = tk.Label(root, image=img_tk)
    panel.image = img_tk
    panel.pack(pady=10)

    ai_box = tk.Text(root, height=10, width=60, bg="#e8e8e8", font=("Arial", 12))
    ai_box.pack(pady=10)
    ai_box.insert(tk.END, "🤖 AI: Ik luister mee tijdens het gesprek.\n")
    ai_box.config(state="disabled")

    invoer = tk.Entry(root, font=("Arial", 14))
    invoer.pack(fill="x", padx=20, pady=10)

    def stuur_ai():
        tekst = invoer.get().strip()
        if not tekst:
            return
        invoer.delete(0, tk.END)
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=f"Tijdens bellen zegt gebruiker: '{tekst}'. Reageer kort alsof je meeluistert."
            )
            antwoord = getattr(response, "output_text", None) or str(response)
        except Exception as e:
            antwoord = f"[AI fout: {e}]"
        ai_box.config(state="normal")
        ai_box.insert(tk.END, f"Gebruiker: {tekst}\n")
        ai_box.insert(tk.END, f"AI: {antwoord}\n\n")
        ai_box.config(state="disabled")

    tk.Button(root, text="Stuur naar AI", font=("Arial", 14), command=stuur_ai).pack(pady=5)
    tk.Button(root, text="📴 Ophangen", font=("Arial", 14), bg="red", fg="white",
              command=facetime_menu).pack(pady=20)

# === Menu na inloggen ===
def welkom_scherm():
    clear_frame()
    tk.Label(root, text=f"Welkom, {gebruiker}!", font=("Arial", 20, "bold")).pack(pady=20)
    tk.Button(root, text="📝 Vragenlijst", font=("Arial", 16), width=30, command=lambda: toon_vraag(0)).pack(pady=6)
    tk.Button(root, text="💬 Chat", font=("Arial", 16), width=30, command=open_chat_selectie).pack(pady=6)
    tk.Button(root, text="📞 FaceTime", font=("Arial", 16), width=30, command=facetime_menu).pack(pady=6)
    tk.Button(root, text="🤖 AI Chat", font=("Arial", 16), width=30, command=ai_chat_scherm).pack(pady=6)
    tk.Button(root, text="🔍 Matches", font=("Arial", 16), width=30, command=toon_match).pack(pady=6)
    tk.Button(root, text="📰 Nieuws", font=("Arial", 16), width=30, command=nieuws_scherm).pack(pady=6)
    tk.Button(root, text="🚪 Uitloggen", font=("Arial", 14),
              command=lambda: (setattr_globals_logout(), start_scherm())).pack(pady=12)

def setattr_globals_logout():
    global gebruiker, antwoorden
    gebruiker = ""
    antwoorden = []

# === Start app ===
start_scherm()
root.mainloop()
