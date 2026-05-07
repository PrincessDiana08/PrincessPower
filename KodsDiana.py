import tkinter as tk
from tkinter import ttk, messagebox
import csv
import webbrowser
import os
import random
import re

# ========== COACH/CONTACT FORMATTING ==========
def format_contact_with_coaches(kontaktinformācija):
    """Formats contact info with Bratz doll coach icons."""
    # Bratz coach emojis for different contact types
    bratz_coaches = ["👠", "💅", "💄", "👗", "💁‍♀️", "🎀", "✨"]
    coach_icon = random.choice(bratz_coaches)
    
    # Detect phone numbers (Latvian format: typically 8 digits starting with 2-3)
    phone_pattern = r'\b\d{8}\b'
    if re.search(phone_pattern, kontaktinformācija):
        return f"📱 {coach_icon} {kontaktinformācija}"
    # Detect Instagram
    elif "instagram" in kontaktinformācija.lower() or "@" in kontaktinformācija:
        return f"📸 {coach_icon} {kontaktinformācija}"
    # Detect URLs
    elif "http" in kontaktinformācija.lower():
        return f"🔗 {coach_icon} {kontaktinformācija}"
    else:
        return f"💬 {coach_icon} {kontaktinformācija}"

# ========== SPARKLE ANIMATION ==========
def create_sparkle_animation(widget, x=None, y=None):
    """Creates animated sparkles that pop up on button clicks."""
    parent = widget.winfo_toplevel()
    
    # Get widget position
    if x is None or y is None:
        x = widget.winfo_x() + widget.winfo_width() // 2
        y = widget.winfo_y() + widget.winfo_height() // 2
    
    # Create sparkles at multiple positions
    sparkle_emojis = ["✨", "💫", "⭐", "🌟", "💥"]
    
    for _ in range(3):
        sparkle = tk.Label(parent, text=random.choice(sparkle_emojis), 
                          fg="#FFD700", font=("Segoe UI", 16, "bold"), 
                          bg=parent.cget("bg"))
        
        # Random offset from click position
        offset_x = random.randint(-40, 40)
        offset_y = random.randint(-40, 40)
        
        sparkle.place(x=x + offset_x, y=y + offset_y)
        
        # Animate sparkle (float up and fade by deleting)
        def animate_sparkle(sp=sparkle, steps=[0]):
            steps[0] += 1
            if steps[0] < 15:
                current_y = sp.winfo_y() - 3
                sp.place(x=sp.winfo_x(), y=current_y)
                parent.after(30, lambda sp=sp, steps=steps: animate_sparkle(sp, steps))
            else:
                sp.destroy()
        
        parent.after(50, animate_sparkle)

# ========== DATU IELĀDE ==========
def ieladet_grupas(fails="grupas.csv"):
    """Nolasa CSV failu un atgriež sarakstu ar vārdnīcām."""
    grupas = []
    try:
        with open(fails, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Pārbaudām, vai ir visas svarīgākās kolonnas
                if all(col in row for col in ["pilseta", "tips", "nosaukums", "vieta_laiks",
                                               "kontaktinformācija", "tiessaiste"]):
                    # Pievienojam noklusētās vērtības, ja trūkst jaunās kolonnas
                    if "apraksts" not in row:
                        row["apraksts"] = "Apraksts vēl nav pievienots."
                    if "lidzi" not in row:
                        row["lidzi"] = "Nav norādīts"
                    grupas.append(row)
    except FileNotFoundError:
        messagebox.showerror("Kļūda", f"Datnes '{fails}' nav. Lūdzu, izveido to ar nepieciešamajām kolonnām.")
    return grupas

# ========== DALĪBNIEČU PĀRVALDĪBA ==========
def lasit_dalibnieces(grupas_nosaukums):
    """Atgriež sarakstu ar pieteikušos dalībnieču vārdiem konkrētai grupai."""
    if not os.path.exists("pieteikumi.csv"):
        return []
    dalibnieces = []
    with open("pieteikumi.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['grupa'] == grupas_nosaukums:
                dalibnieces.append(row['vards'])
    return dalibnieces

def pievienot_dalibnieci(grupas_nosaukums, vards):
    """Pievieno jaunu dalībnieču ierakstu."""
    eksiste = os.path.exists("pieteikumi.csv")
    with open("pieteikumi.csv", "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        if not eksiste:
            writer.writerow(["grupa", "vards"])
        writer.writerow([grupas_nosaukums, vards])

# ========== GRUPAS DETAĻU LOGS ==========
def atvert_detalas(grupa):
    """Atver jaunu logu ar pilnu informāciju par izvēlēto grupu."""
    logs = tk.Toplevel()
    logs.title(grupa['nosaukums'])
    logs.geometry("500x480")
    logs.configure(bg="#fff0f7")
    logs.resizable(False, False)

    # Virsraksts ar sparkles
    tk.Label(logs, text="✨ " + grupa['nosaukums'] + " ✨", bg="#fff0f7", fg="#ff1493",
             font=("Segoe UI", 14, "bold")).pack(pady=10)

    # Pamatinformācija
    info = f"📍 {grupa['vieta_laiks']}\n"
    info += f"{format_contact_with_coaches(grupa['kontaktinformācija'])}\n"
    info += f"📝 {grupa.get('apraksts', 'Nav apraksta')}\n"
    info += f"🎒 Līdzi jāņem: {grupa.get('lidzi', 'Nav norādīts')}"

    tk.Label(logs, text=info, bg="#fffafc", fg="#c2185b", font=("Segoe UI", 10),
             justify="left", wraplength=450, relief="ridge", bd=2, padx=10, pady=10).pack(pady=10, padx=15)

    # Dalībnieču saraksts
    dalibnieces = lasit_dalibnieces(grupa['nosaukums'])
    if dalibnieces:
        dalib_teksts = "✨ 👯‍♀️ Jau pieteikušās: " + ", ".join(dalibnieces) + " ✨"
    else:
        dalib_teksts = "✨ 👯‍♀️ Pagaidām neviens nav pieteicies. Esi pirmā! ✨"

    tk.Label(logs, text=dalib_teksts, bg="#fff0f7", fg="#ff1493",
             font=("Segoe UI", 10, "italic"), wraplength=450).pack(pady=5)

    # Pieteikšanās zona
    vards_sv = tk.StringVar()
    tk.Label(logs, text="💫 Tavs vārds:", bg="#fff0f7", fg="#c2185b", font=("Segoe UI", 10, "bold")).pack()
    ievade = tk.Entry(logs, textvariable=vards_sv, font=("Segoe UI", 10), width=25, bg="#fffafc", fg="#c2185b", relief="solid", bd=2)
    ievade.pack(pady=5)

    def pieteikties():
        vards = vards_sv.get().strip()
        if vards:
            pievienot_dalibnieci(grupa['nosaukums'], vards)
            messagebox.showinfo("Pieteikums pieņemts",
                                f"Brīnišķīgi, {vards}! Tiekamies {grupa['vieta_laiks']} 💖")
            logs.destroy()  # aizveram logu
        else:
            messagebox.showwarning("Uzmanību", "Lūdzu, ieraksti savu vārdu.")

    pieteikties_btn = tk.Button(logs, text="✨ ✅ Pieteikties ✨", 
              command=lambda: (create_sparkle_animation(pieteikties_btn), pieteikties()),
              bg="#ff1493", fg="white", font=("Segoe UI", 10, "bold"),
              relief="flat", bd=0, padx=20, pady=5, activebackground="#ff69b4")
    pieteikties_btn.pack(pady=10)

    # Aizvērt pogu
    aizvert_btn = tk.Button(logs, text="Aizvērt ✨", 
              command=lambda: (create_sparkle_animation(aizvert_btn), logs.destroy()),
              bg="#ffb6d9", fg="#fff", font=("Segoe UI", 10),
              relief="flat", bd=0)
    aizvert_btn.pack(pady=5)

# ========== SKAISTUMA PADOMI ==========
def paradit_padomus():
    """Atver logu ar rotējošiem skaistumkopšanas padomiem."""
    logs = tk.Toplevel()
    logs.title("PrincessPower padomi 💄✨")
    logs.geometry("480x320")
    logs.configure(bg="#fff0f7")
    logs.resizable(False, False)

    try:
        with open("padomi.txt", "r", encoding="utf-8") as f:
            padomi = [rinda.strip() for rinda in f.readlines() if rinda.strip()]
    except FileNotFoundError:
        padomi = ["Padomi vēl nav pievienoti. Izveido 'padomi.txt' ar ieteikumiem katra rindā."]

    if not padomi:
        padomi = ["Dzer daudz ūdens un smaidi! 🌸"]

    idx = [0]  # izmantojam sarakstu, lai varētu mainīt iekšējā funkcijā
    padoma_teksts = tk.StringVar()
    padoma_teksts.set(padomi[0])

    tk.Label(logs, text="✨ 🌸 Skaistuma un labsajūtas padomi 🌸 ✨", bg="#fff0f7",
             fg="#ff1493", font=("Segoe UI", 14, "bold")).pack(pady=10)

    padoma_ramis = tk.Frame(logs, bg="#ffffff", relief="groove", bd=2)
    padoma_ramis.pack(pady=10, padx=20, fill="both", expand=True)

    label = tk.Label(padoma_ramis, textvariable=padoma_teksts, bg="#fffafc", fg="#c2185b",
                     font=("Segoe UI", 11), wraplength=380, justify="center",
                     padx=15, pady=15)
    label.pack(expand=True)

    def nakamais():
        idx[0] = (idx[0] + 1) % len(padomi)
        padoma_teksts.set(padomi[idx[0]])

    nakamais_btn = tk.Button(logs, text="✨ Nākamais padoms ➡️", 
              command=lambda: (create_sparkle_animation(nakamais_btn), nakamais()),
              bg="#ff69b4", fg="white", font=("Segoe UI", 10, "bold"),
              relief="flat", bd=0, padx=10, pady=5, activebackground="#ff1493")
    nakamais_btn.pack(pady=5)

    aizvert_padomu_btn = tk.Button(logs, text="Aizvērt ✨", 
              command=lambda: (create_sparkle_animation(aizvert_padomu_btn), logs.destroy()),
              bg="#ffb6d9", fg="white", font=("Segoe UI", 10),
              relief="flat", bd=0)
    aizvert_padomu_btn.pack(pady=5)

# ========== MEKLĒŠANA UN REZULTĀTU ATTAISĪŠANA ==========
def meklet():
    """Filtrē grupas un parāda tās kā klikšķināmas pogas."""
    pilseta = pilsetas_izvele.get()
    tips = tipa_izvele.get()

    if not pilseta or not tips:
        messagebox.showwarning("Uzmanību", "Lūdzu, izvēlies gan pilsētu, gan aktivitātes veidu!")
        return

    # Notīrām iepriekšējos rezultātus (izņemot info_label, ja tas vairs netiek izmantots)
    for widget in rezultatu_ramis.winfo_children():
        widget.destroy()

    rezultati = []
    for g in dati:
        atbilst_pilseta = (g["pilseta"].strip().lower() == pilseta.strip().lower() or g["pilseta"].strip().lower() == "visi")
        atbilst_tips = (tips == "Viss" or g["tips"].strip().lower() == tips.strip().lower())
        if atbilst_pilseta and atbilst_tips:
            rezultati.append(g)

    if not rezultati:
        # Ja nav rezultātu, parādām paziņojumu
        nav_rez = tk.Label(rezultatu_ramis, text="✨ Šajā kategorijā pagaidām nav ierakstu. 😔 ✨\nPamēģini citu pilsētu vai veidu!",
                           bg="#fff0f7", fg="#ff1493", font=("Segoe UI", 10, "italic"))
        nav_rez.pack(pady=20)
        return

    # Izveidojam kartiņveida pogas katrai grupai
    for g in rezultati:
        # Kartiņas rāmis
        karte = tk.Frame(rezultatu_ramis, bg="#fffafc", relief="ridge", bd=2)
        karte.pack(fill="x", pady=4, padx=10)

        # Informācija kartiņā
        nosaukums = g['nosaukums']
        vieta = g['vieta_laiks']
        teksts = f"✨ 🌸 {nosaukums} ✨\n📍 {vieta}"

        # Poga, kas atver detaļas
        poga = tk.Button(karte, text=teksts, bg="#fffafc", fg="#ff1493",
                         font=("Segoe UI", 10, "bold"), justify="left",
                         relief="flat", bd=0, padx=10, pady=8,
                         command=lambda grupa=g, p=karte: (create_sparkle_animation(p), atvert_detalas(grupa)), activebackground="#ffb6d9")
        poga.pack(fill="both", expand=True)

def atvert_saiti():
    """Atver pirmo tiešsaistes saiti no visiem datiem."""
    for g in dati:
        kontaktinformācija = g["kontaktinformācija"].strip()
        if kontaktinformācija.startswith("http://") or kontaktinformācija.startswith("https://"):
            webbrowser.open(kontaktinformācija)
            return
    messagebox.showinfo("Nav saites", "Neviena tiešsaistes saite netika atrasta.")

# ========== GALVENĀ LOGU VEIDOŠANA ==========
logs = tk.Tk()
logs.title("PrincessPower ✨ 🌸 ✨")
logs.geometry("600x600")
logs.minsize(550, 500)
logs.configure(bg="#fff0f7")

# Virsraksts ar sparkles
tk.Label(logs, text="✨ PrincessPower ✨", bg="#fff0f7", fg="#ff1493",
         font=("Segoe UI", 22, "bold")).pack(pady=(15, 0))
tk.Label(logs, text="💫 Atrodi meitenes, ar kurām kustēties! 💪 💫",
         bg="#fff0f7", fg="#ff1493", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))

# Pilsētas izvēlne
tk.Label(logs, text="🌟 Izvēlies pilsētu:", bg="#fff0f7", fg="#ff1493",
         font=("Segoe UI", 10, "bold")).pack()
pilsetas_izvele = ttk.Combobox(logs, state="readonly",
                               values=["Rīga", "Daugavpils", "Liepāja", "Jelgava",
                                       "Jūrmala", "Ventspils", "Rēzekne", "Cita"],
                               font=("Segoe UI", 10))
pilsetas_izvele.pack(pady=5)

# Aktivitātes veids
tk.Label(logs, text="⭐ Ko vēlies darīt?", bg="#fff0f7", fg="#ff1493",
         font=("Segoe UI", 10, "bold")).pack()
tipa_izvele = ttk.Combobox(logs, state="readonly",
                           values=["Skriešana", "Pilates / Joga", "Mājas treniņi", "Viss"],
                           font=("Segoe UI", 10))
tipa_izvele.pack(pady=5)

# Meklēšanas poga
meklet_btn = tk.Button(logs, text="✨ ❤️ Parādi draudzīgās grupas ❤️ ✨", 
          command=lambda: (create_sparkle_animation(meklet_btn), meklet()),
          bg="#ff1493", fg="white", font=("Segoe UI", 11, "bold"),
          relief="flat", bd=0, padx=20, pady=8, activebackground="#ff69b4")
meklet_btn.pack(pady=15)

# Rāmis rezultātiem (scrollable var pievienot, bet pagaidām vienkārši)
rezultatu_ramis = tk.Frame(logs, bg="#fff0f7")
rezultatu_ramis.pack(fill="both", expand=True, padx=10, pady=5)

# Pogas apakšā
pogu_ramis = tk.Frame(logs, bg="#fff0f7")
pogu_ramis.pack(fill="x", pady=10)

tiessaiste_btn = tk.Button(pogu_ramis, text="✨ 💻 Tiešsaistes treniņš ✨", 
          command=lambda: (create_sparkle_animation(tiessaiste_btn), atvert_saiti()),
          bg="#ff69b4", fg="white", font=("Segoe UI", 10, "bold"),
          relief="flat", bd=0, padx=15, pady=5, activebackground="#ff1493")
tiessaiste_btn.pack(side="left", padx=5)

skaistuma_btn = tk.Button(pogu_ramis, text="✨ 💄 Skaistuma padomi ✨", 
          command=lambda: (create_sparkle_animation(skaistuma_btn), paradit_padomus()),
          bg="#ff69b4", fg="white", font=("Segoe UI", 10, "bold"),
          relief="flat", bd=0, padx=15, pady=5, activebackground="#ff1493")
skaistuma_btn.pack(side="right", padx=5)

# Datu ielāde
dati = ieladet_grupas()
if not dati:
    messagebox.showwarning("Uzmanību", "Dati nav ielādēti. Pārbaudi 'grupas.csv' failu.")

logs.mainloop()