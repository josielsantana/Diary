import json
from datetime import datetime
import customtkinter as ctkr
from tkcalendar import DateEntry
from tkinter import messagebox
from cryptography.fernet import Fernet
import os

def file_exists(user, data):
    if os.path.exists(data) and os.path.exists(user) and os.path.getsize(user) != 0:
        return True
    else:
        return False

def generate_key():
    if load_user("hasKey") == "False":
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    else:
        return None

def load_user(option):
    with open(userfile, "r") as f:
        temp = json.load(f)
    return temp[0].get(option, "")

def create_user(userfile):
    item_data = {
        "name": "Josin",
        "birth": "2004-08-30",
        "lang": "en-US",
        "hasKey": "False"
    }
    with open(userfile, "w") as f:
        json.dump([item_data], f, indent=4)

def create_anotation(datafile):
    with open(datafile, "w") as f:
        json.dump([], f, indent=4)

def welcome(user, data):
    if file_exists(user, data):
        "File already exists"
    else:
        create_user(user)
        create_anotation(data)
        generate_key()

datafile = "data.json" #verify
userfile = "user.json" #verify
welcome(userfile, datafile)

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())
def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

selected_language = load_user("lang")
language = {
    "pt-BR": {
        "cumpliment": ["Boa noite", "Bom dia", "Boa tarde"],
        "date_format": "dd-mm-yyyy",
        "windows": ["Inicio", "Escrever", "Consultar"],
        "labels": ["Selecione um dia", "Digite um título", "Anotação", "Seu humor"],
        "humor": ["Maravilhoso", "Bom", "Normal", "Ruim", "Péssimo"],
        "buttons": ["Salvar", "Limpar"]
    },
    "en-US": {
        "cumpliment": ["Good Evening", "Good Morning", "Good Afternoon"],
        "date_format": "yyyy-mm-dd",
        "windows": ["Home", "Write", "Search"],
        "labels": ["Select a day", "Enter a title", "Enter annotation", "Enter humor"],
        "humor": ["Wonderful", "Good", "Normal", "Bad", "Worst"],
        "buttons": ["Save entry", "Clear"]
    }
}

def cumpliment():
    hour = datetime.now().hour
    if hour > 18 or hour < 6:
        return language[selected_language]["cumpliment"][0]
    elif hour <= 12:
        return language[selected_language]["cumpliment"][1]
    else:
        return language[selected_language]["cumpliment"][2]

#db related
def list_dates():
    dates = []
    with open(datafile, "r") as f:
        temp = json.load(f)
        for entry in temp:
            dates.append(entry["date_reference"])
    return dates

def new_id():
    #id = []
    #out = 1
    #with open(datafile, "r") as f:
    #    temp = json.load(f)
    #    for entry in temp:
    #        id.append(int(decrypt_data(entry["id"])))
    #
    #if len(id) != 0:
    #    out = max(id) + 1
    return 10 #out

def add_data(date_reference, title, anotation, humor, selected_language):
    item_data = {
        "id": encrypt_data(str(new_id())), #converted to string
        "date_reference": encrypt_data(date_reference),
        "year": encrypt_data(date_reference[0:4]),
        "month": encrypt_data(date_reference[5:7]),
        "title": encrypt_data(title),
        "humor": encrypt_data(humor),
        "days_birth": encrypt_data(str((datetime.strptime(date_reference, "%Y-%m-%d") - datetime.strptime(load_user("birth"), "%Y-%m-%d")).days)),#converted to string
        "days_ytd": encrypt_data(str((datetime.strptime(date_reference, "%Y-%m-%d") - datetime.strptime(f"{date_reference[0:4]}-01-01", "%Y-%m-%d")).days + 1)),#converted to string
        "anotation": encrypt_data(anotation),
        "lang_registered": encrypt_data(selected_language)
    }
    with open(datafile, "r") as f:
        temp = json.load(f)
    temp.append(item_data)
    with open(datafile, "w") as f:
        json.dump(temp, f, indent=4)

def read_data():
    with open(datafile, "r") as f:
        temp = json.load(f)
    entries = []
    for entry in temp:
        entries.append({
            "id": decrypt_data(entry["id"]),
            "date_reference": decrypt_data(entry["date_reference"]),
            "title": decrypt_data(entry["title"]),
            "humor": decrypt_data(entry["humor"]),
            "diff_birth": decrypt_data(entry["diff_birth"]),
            "diff_ytd": decrypt_data(entry["diff_ytd"]),
            "anotation": decrypt_data(entry["anotation"]),
            "lang_registered": decrypt_data(entry["lang_registered"])
        })
    return entries


ctkr.set_appearance_mode("dark")
ctkr.set_default_color_theme("dark-blue")


root = ctkr.CTk()
root.geometry("500x550")

title = ctkr.CTkLabel(master=root, text=f"{cumpliment()}, {load_user('name')}.", font=ctkr.CTkFont(size=23, weight="bold"))
title.pack(pady=20, padx=60, fill="both", expand=True)

tabview = ctkr.CTkTabview(master=root)
tabview.pack(pady=20, padx=20)

tabview.add(language[selected_language]["windows"][0])
tabview.add(language[selected_language]["windows"][1])
tabview.add(language[selected_language]["windows"][2])

label_ref = ctkr.CTkLabel(master=tabview.tab(language[selected_language]["windows"][1]), text=language[selected_language]["labels"][0])
label_ref.pack()
frame_ref = ctkr.CTkFrame(master=tabview.tab(language[selected_language]["windows"][1]))
frame_ref.pack(pady=5)
calendar = DateEntry(master=frame_ref, date_pattern=language[selected_language]["date_format"], text_color="#FFCC70")
calendar.pack()

entry_title = ctkr.CTkEntry(master=tabview.tab(language[selected_language]["windows"][1]), border_color="#FFCC70", placeholder_text = language[selected_language]["labels"][1], width=300, text_color="#FFCC70")
entry_title.pack(pady=10)

label_anotation = ctkr.CTkLabel(master=tabview.tab(language[selected_language]["windows"][1]), text=language[selected_language]["labels"][2])
label_anotation.pack()
entry_note = ctkr.CTkTextbox(master=tabview.tab(language[selected_language]["windows"][1]), width=400, height=150, corner_radius=16, border_color="#FFCC70", scrollbar_button_color="#FFCC70", border_width=2)
entry_note.pack(pady=10)

label_humor = ctkr.CTkLabel(master=tabview.tab(language[selected_language]["windows"][1]), text=language[selected_language]["labels"][3])
label_humor.pack()
entry_humor = ctkr.CTkComboBox(master=tabview.tab(language[selected_language]["windows"][1]), values=language[selected_language]["humor"], border_color="#FFCC70")
entry_humor.pack(pady=10)

def save_anotation():
    data = calendar.get()
    anotation = entry_note.get("0.0", "end").strip()
    title_text = entry_title.get().strip()
    humor = entry_humor.get().strip()

    if not (data and title_text and anotation and humor):
        messagebox.showerror("Error", "Preencha todos os campos!")
        return

    confirmed = True
    if data in list_dates():
        confirmed = messagebox.askyesno("Aviso", "Essa data já existe. Deseja sobrescrever?")

    if confirmed:
        add_data(data, title_text, anotation, humor, selected_language)
        messagebox.showinfo("Success", "Entrada salva com sucesso!")
        clear_fields()

def clear_fields():
    entry_title.delete(0, "end")
    entry_note.delete("0.0", "end")
    entry_humor.set("")

submit = ctkr.CTkButton(master=tabview.tab(language[selected_language]["windows"][1]), text=language[selected_language]["buttons"][0], command=save_anotation, corner_radius=40, fg_color="#4158D0", hover_color= "#4D68EF")
submit.pack(side=ctkr.LEFT, padx=10, pady=10, fill="both", expand=True)

clear = ctkr.CTkButton(master=tabview.tab(language[selected_language]["windows"][1]), text=language[selected_language]["buttons"][1], command=clear_fields, corner_radius=40, fg_color="transparent", border_width=2)
clear.pack(side=ctkr.LEFT, padx=10, pady=10, fill="both", expand=True)

root.mainloop()

#search
#consulta
