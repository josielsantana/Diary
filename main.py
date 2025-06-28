import json
from datetime import datetime
import customtkinter as ctkr
from tkcalendar import DateEntry
from tkinter import messagebox
from cryptography.fernet import Fernet
import os

datafile = "data.json"
userfile = "user.json"

def file_exists(user, data):
    if os.path.exists(data) and os.path.exists(user) and os.path.getsize(user) != 0:
        return True
    else:
        return False

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def create_files(userfile, datafile):
    with open(userfile, "w") as f:
        json.dump([], f, indent=4)
    with open(datafile, "w") as f:
        json.dump([], f, indent=4)

def register_window():
    reg_root = ctkr.CTk()
    reg_root.title("Registro de Usuário")
    reg_root.geometry("400x400")

    title = ctkr.CTkLabel(master=reg_root, text="Registre-se", font=ctkr.CTkFont(size=20, weight="bold"))
    title.pack(pady=20)

    name_label = ctkr.CTkLabel(master=reg_root, text="Nome:")
    name_label.pack()
    name_entry = ctkr.CTkEntry(master=reg_root)
    name_entry.pack(pady=5)

    birth_label = ctkr.CTkLabel(master=reg_root, text="Data de Nascimento:")
    birth_label.pack()
    birth_entry = DateEntry(master=reg_root, date_pattern="yyyy-mm-dd", text_color="#FFCC70")
    birth_entry.pack(pady=5)

    lang_label = ctkr.CTkLabel(master=reg_root, text="Idioma:")
    lang_label.pack()
    lang_combo = ctkr.CTkComboBox(master=reg_root, values=["en-US", "pt-BR"])
    lang_combo.pack(pady=5)

    def on_register():
        name = name_entry.get().strip()
        birth = birth_entry.get().strip()
        lang = lang_combo.get().strip()

        if not name or not birth or not lang:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        user_data = {
            "name": name,
            "birth": birth,
            "lang": lang,
            "hasKey": "True"
        }

        with open(userfile, "w") as f:
            json.dump([user_data], f, indent=4)


        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
        reg_root.destroy()
        root.deiconify()

    submit_btn = ctkr.CTkButton(master=reg_root, text="Registrar", command=on_register)
    submit_btn.pack(pady=20)

    reg_root.mainloop()

def welcome(user, data):
    if file_exists(user, data):
        "File already exists"
    else:
        create_files(user, data)
        register_window()
        generate_key()

def create_temp_user(userfile):
    if not os.path.exists(userfile) or os.path.getsize(userfile) == 0:
        temp_user = {
            "name": "TempUser",
            "birth": "2000-01-01",
            "lang": "en-US",
            "hasKey": "False"
        }
        with open(userfile, "w") as f:
            json.dump([temp_user], f, indent=4)
        generate_key()
        
create_temp_user(userfile)
welcome(userfile, datafile)

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())
def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

def load_user(option):
    with open(userfile, "r") as f:
        temp = json.load(f)
    return temp[0].get(option, "")

def find_language(user, data):
    if file_exists(user, data):
        return "en-US" #return load_user("lang")
    else: 
        return "en-US"
    
selected_language = find_language(userfile, datafile)
language = {
    "pt-BR": {
        "cumpliment": ["Boa noite", "Bom dia", "Boa tarde"],
        "date_format": "dd-mm-yyyy",
        "windows": ["Inicio", "Escrever", "Consultar"],
        "labels": ["Selecione um dia", "Digite um título", "Anotação", "Seu humor"],
        "humor": ["Maravilhoso", "Bom", "Normal", "Ruim", "Péssimo"],
        "buttons": ["Salvar", "Limpar"],
        "months_map": {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "Dezember"}
    },
    "en-US": {
        "cumpliment": ["Good Evening", "Good Morning", "Good Afternoon"],
        "date_format": "yyyy-mm-dd",
        "windows": ["Home", "Write", "Search"],
        "labels": ["Select a day", "Enter a title", "Enter annotation", "Enter humor"],
        "humor": ["Wonderful", "Good", "Normal", "Bad", "Worst"],
        "buttons": ["Save entry", "Clear"],
        "months_map": {"01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril", "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto", "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"}
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

def list_dates():
    dates = []
    with open(datafile, "r") as f:
        temp = json.load(f)
        for entry in temp:
            dates.append(entry["date_reference"])
    return dates

def new_id():
    id = []
    out = 1
    with open(datafile, "r") as f:
        temp = json.load(f)
        for entry in temp:
            id.append(int(decrypt_data(entry["id"])))
    
    if len(id) != 0:
        out = max(id) + 1
    return out

def add_data(date_reference, title, anotation, humor, selected_language):
    item_data = {
        "id": encrypt_data(str(new_id())),
        "date_reference": encrypt_data(date_reference),
        "year": encrypt_data(date_reference[0:4]),
        "month": encrypt_data(date_reference[5:7]),
        "title": encrypt_data(title),
        "humor": encrypt_data(humor),
        "days_birth": encrypt_data(str((datetime.strptime(date_reference, "%Y-%m-%d") - datetime.strptime(load_user("birth"), "%Y-%m-%d")).days)),#converted to string
        "days_ytd": encrypt_data(str((datetime.strptime(date_reference, "%Y-%m-%d") - datetime.strptime(f"{date_reference[0:4]}-01-01", "%Y-%m-%d")).days + 1)),#converted to string
        "anotation": encrypt_data(anotation),
        "time_registered": encrypt_data(str(datetime.now())),
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
            "id": int(decrypt_data(entry["id"])),
            "date_reference": decrypt_data(entry["date_reference"]),
            "title": decrypt_data(entry["title"]),
            "humor": decrypt_data(entry["humor"]),
            "days_birth": int(decrypt_data(entry["days_birth"])),
            "days_ytd": int(decrypt_data(entry["days_ytd"])),
            "anotation": decrypt_data(entry["anotation"]),
            "lang_registered": decrypt_data(entry["lang_registered"])
        })
    return entries

ctkr.set_appearance_mode("dark")
ctkr.set_default_color_theme("dark-blue")

root = ctkr.CTk()
root.geometry("500x600")
root.iconbitmap('icon.ico') 
root.title("Diary")

title = ctkr.CTkLabel(master=root, text=f"{cumpliment()}, {load_user('name')}.", font=ctkr.CTkFont(size=23, weight="bold"))
title.pack(pady=20, padx=60, fill="both")

tabview = ctkr.CTkTabview(master=root)
tabview.pack(pady=20, padx=20)

tabview.add(language[selected_language]["windows"][0])
tabview.add(language[selected_language]["windows"][1])
#tabview.add(language[selected_language]["windows"][2])

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




def show_month_entries(selected_month):
    window = ctkr.CTkToplevel()
    notes = read_data()
    month_notes = [n for n in notes if n["date_reference"][5:7] == selected_month]

    if not month_notes:
        messagebox.showinfo("Info", "Nenhuma anotação encontrada para este mês.")
        return

    window = ctkr.CTkToplevel()
    window.title("Anotações do Mês")
    window.geometry("500x600")

    title = ctkr.CTkLabel(master=window, text=f"Anotações de {language[selected_language]['months_map'][selected_month]}", font=ctkr.CTkFont(size=20, weight="bold"))
    title.pack(pady=10)

    scroll_frame = ctkr.CTkScrollableFrame(master=window, width=480, height=500)
    scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

    for note in month_notes:
        frame = ctkr.CTkFrame(master=scroll_frame, border_width=2, border_color="#FFCC70")
        frame.pack(pady=5, fill="x", padx=5)

        label = ctkr.CTkLabel(
            master=frame,
            text=f"Data: {note['date_reference']}\nTítulo: {note['title']}\nHumor: {note['humor']}\n\n{note['anotation']}",
            anchor="w",
            justify="left",
            wraplength=460
        )
        label.pack(padx=5, pady=5, fill="x", expand=True)



month_selector = ctkr.CTkComboBox(
    master=tabview.tab(language[selected_language]["windows"][0]),
    values=[f"{num} - {name}" for num, name in language[selected_language]["months_map"].items()],
    border_color="#FFCC70"
)
month_selector.pack(pady=10)

view_btn = ctkr.CTkButton(
    master=tabview.tab(language[selected_language]["windows"][0]),
    text="Ver Anotações",
    command=lambda: show_month_entries(month_selector.get().split(" - ")[0]),
    corner_radius=40,
    fg_color="#4158D0",
    hover_color="#4D68EF"
)
view_btn.pack(pady=10)




root.mainloop()

