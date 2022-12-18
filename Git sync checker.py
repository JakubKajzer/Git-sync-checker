import tkinter as tk
import os
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from tkinter import ttk
import subprocess

class App:
    def __init__(self, master):
        self.master = master
        self.notebook = ttk.Notebook(master)
        self.master.title("Git sync checker")
        self.master.geometry("273x358")
        self.master.resizable(False, False)
        self.notebook.pack()
        self.tabs = {}

        # Create the menu and set the disableddash option to False
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        # Add a File menu with a Quit option
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Add folder with repos", command=self.add_tab)
        self.file_menu.add_command(label="Save tabs", command=self.save_tabs)
        self.file_menu.add_command(label="Load tabs", command=self.load_tabs)
        self.file_menu.activate(False)

        self.tab_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Tab", menu=self.tab_menu)
        self.tab_menu.add_command(label="Change tab name", command=self.change_tab_name)
        self.tab_menu.add_command(label="Delete tab", command=self.delete_tab)

        # Add a Help menu with a About option
        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Color explanation", command=self.show_color_explanation)
        self.help_menu.add_command(label="About", command=self.show_about)


        self.load_tabs()

    def show_about(self):
        messagebox.showinfo("About", "Git sync checker\nby Jakub Kajzer")
    def show_color_explanation(self):
        messagebox.showinfo("Color explanation", "Green - up to date\nOrange - differences between local and remote\nRed - repo doesn't exist or error")

    def load_tabs(self):
        # Delete all tabs
        for tab_id in self.tabs:
            self.notebook.forget(tab_id)
        self.tabs = {}

        if not os.path.exists("tabs.txt"):
            return
        try:
            with open("tabs.txt", "r") as f:
                for line in f:
                    name, path = line.strip().split("\t")
                    self.add_tab(name=name, path=path)
        except FileNotFoundError:
            pass


    def save_tabs(self):
        if not os.path.exists("tabs.txt"):
            open("tabs.txt", "w").close()
        with open("tabs.txt", "w", encoding="utf-8") as f:
            for tab_id in self.tabs:
                name = self.notebook.tab(tab_id, "text")
                path = self.tabs[tab_id]["path"]
                f.write(f"{name}\t{path}\n")
        messagebox.showinfo("Save tabs","Tabs saved succesfully!")


    def add_tab(self, name=None, path=None):
        if name is None:
            name = "New tab"
        if path is None:
            path = filedialog.askdirectory()
            if not path:
                return

        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=name)
        self.tabs[tab] = {"path": path, "folders": []}

        listbox = tk.Listbox(tab, width=50, height=100,selectmode="none")
        listbox.pack()
        self.tabs[tab]["listbox"] = listbox

        button_frame = tk.Frame(tab)
        button_frame.pack(side="right")

        self.update_tab(tab)
          
        
    def delete_tab(self):
            if messagebox.askokcancel("Delete tab", "Are you sure to delete this tab?"):
                index = self.notebook.index(self.notebook.select())
                if index is not None and index in self.tabs:
                    self.notebook.forget(index)
                    del self.tabs[index]   
                    
    def change_tab_name(self):
            new_name = simpledialog.askstring("Change tab name", "New tab name:")
            index = self.notebook.index(self.notebook.select())
            if new_name and index is not None and index in self.tabs:
                self.notebook.tab(index, text=new_name) 

    def update_tab(self, tab):
        self.tabs[tab]["folders"] = []
        self.tabs[tab]["listbox"].delete(0, "end")
        path = self.tabs[tab]["path"]
        for name in os.listdir(path):
            folder_path = os.path.join(path, name)
            if os.path.isdir(folder_path):
                # Sprawdź, czy folder jest repozytorium Git
                if os.path.exists(os.path.join(folder_path, ".git")):
                    status, color = self.check_repo_status(folder_path)
                else:
                    status = "nie jest repozytorium"
                    color = "gray"
                self.tabs[tab]["folders"].append((name, folder_path, color))
                self.tabs[tab]["listbox"].insert("end", name)
                self.tabs[tab]["listbox"].itemconfig("end", fg=color)

    def check_repo_status(self, folder_path):
        try:
            # Pobierz nowe dane zdalne
            subprocess.run(["git", "fetch"], cwd=folder_path, check=True)

            # Sprawdź, czy są niezatwierdzone zmiany w lokalnym repozytorium
            diff_output = subprocess.run(
                ["git", "diff"], cwd=folder_path, capture_output=True, check=True
            ).stdout.decode()
            if diff_output:
                return "niezatwierdzone zmiany", "orange"

            # Sprawdź, czy lokalne repozytorium jest aktualne w stosunku do zdalnego
            status_output = subprocess.run(
                ["git", "status"], cwd=folder_path, capture_output=True, check=True
            ).stdout.decode()
            if "Your branch is up to date" in status_output:
                return "aktualne", "green"
            elif "Your branch has diverged" in status_output:
                return "rozgałęzione", "orange"
            elif "Your branch is ahead of" in status_output:
                return "do przodu", "orange"
            else:
                return "nieaktualne", "red"
        except subprocess.CalledProcessError:
            return "błąd", "red"

root = tk.Tk()
app = App(root)
root.mainloop()
            