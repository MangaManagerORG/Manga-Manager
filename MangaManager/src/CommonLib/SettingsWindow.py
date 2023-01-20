import json
import tkinter as tk
from tkinter.filedialog import askdirectory


class App(tk.Toplevel):
    def __init__(self, master: tk.Tk, settings, settings_path):
        super().__init__(master=master)
        self.settings_json = settings
        self.setting_path = settings_path

    def start_ui(self):
        self.title = "Test_title"
        # self.configure(width=80,height=90)
        latest_row = 0
        self.frame_1 = tk.Frame(self)
        self.settings_list = {}
        for i, setting in enumerate(self.settings_json):
            self.settings_list[str(setting)] = {}
            self.settings_list[str(setting)]["var"] = tk.StringVar(master=self.frame_1, name=setting,
                                                                   value=self.settings_json.get(setting))
            self.settings_list[str(setting)]["label"] = tk.Label(master=self.frame_1,
                                                                 text=setting.replace("_", " ").title())
            self.settings_list[str(setting)]["entry"] = tk.Entry(master=self.frame_1,
                                                                 textvariable=self.settings_list[str(setting)]["var"],
                                                                 width=90)
            self.settings_list[str(setting)]["button"] = tk.Button(master=self.frame_1, text="Browse",
                                                                   command=lambda m=setting: self.set_field(m))

            self.settings_list[str(setting)]["label"].grid(row=i, column=0)
            self.settings_list[str(setting)]["entry"].grid(row=i, column=1)
            self.settings_list[str(setting)]["button"].grid(row=i, column=2)
            latest_row += 1
        self.save_btn = tk.Button(master=self.frame_1, text="Save", command=self.save)
        self.save_btn.grid(row=latest_row, column=0, columnspan=2)

        self.frame_1.pack(anchor="center", padx=60, pady=60)

    def save(self):
        for setting in self.settings_json:
            self.settings_json[setting] = self.settings_list[setting]["var"].get()
        with open(self.setting_path, 'w') as settings_json:
            json.dump(self.settings_json, settings_json, indent=4)

    def set_field(self, e):
        self.settings_list[e]["var"].set(askdirectory(parent=self.frame_1))
