#!/usr/bin/env python3

# Current GUI issues:
#
# - Settings:
#   - Broken toggle(Does not update variable)
#   - Missing toggles(OpenCore, Kext, Metal, Wifi, SMBIOS)
# - Install OpenCore:
#   - Outright non-functional
#     - Pottential implementations would be to copy TUI's UI

from tkinter import *
import subprocess, sys, time
import tkinter as tk
from Resources import build, ModelArray, Constants, utilities


# Build main menu
class GUI_MENU():
    def __init__(self):
        self.constants = Constants.Constants()
        self.current_model: str = None
        self.constants.gui_mode = True
        opencore_model: str = subprocess.run("nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:oem-product".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
        if not opencore_model.startswith("nvram: Error getting variable"):
            opencore_model = [line.strip().split(":oem-product	", 1)[1] for line in opencore_model.split("\n") if line.strip().startswith("4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:")][0]
            self.current_model = opencore_model
        else:
            self.current_model = subprocess.run("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.current_model = [line.strip().split(": ", 1)[1] for line in self.current_model.stdout.decode().split("\n") if line.strip().startswith("Model Identifier")][0]

    # Update SMBIOS
    def update_model_clicked(self):
        current_model = self.entry_smbios.get()
        self.current_model = current_model.strip()
        if self.current_model in ModelArray.SupportedSMBIOS11:
            self.support = True
            self.support_string = "Model is supported"
        else:
            self.support = False
            self.support_string = "Model is unsupported"
        # Update Labels
        self.label_smbios.configure(text=f"        Configured model: {self.current_model}        ", font=(".AppleSystemUIFont", 15))
        self.label_support.configure(text=self.support_string, font=(".AppleSystemUIFont", 15))

    def build_clicked(self):
        build_window = tk.Tk()
        build_window.title("Build Menu")
        build_window.minsize(250, 30)
        build_window.eval('tk::PlaceWindow %s center' % build_window.winfo_pathname(build_window.winfo_id()))
        support_build_2 = """Model is unsupported
Please enter a supported model in the main menu.
        """

        build_label = tk.Label(build_window, text=support_build_2)
        if self.current_model in ModelArray.SupportedSMBIOS11:
            support_build_2 = """
            Model is supported, building EFI..
 If you see this text for more than 15 seconds, try restarting the build

If repeated, please open an issue on Github
            """

            build_label.configure(text=support_build_2)
            build_label.pack()
            build.BuildOpenCore(self.current_model, self.constants).build_opencore()
            support_build_2 = f"""Finished building OpenCore for model {self.current_model}!
   Built at:
{self.constants.opencore_release_folder}

   Close this window and select Install OpenCore 🔧
"""
            build_label.configure(text=support_build_2)
            build_label.pack()
        else:
            support_build_2 = "Model is unsupported"
            build_label.pack()
        build_window.eval('tk::PlaceWindow %s center' % build_window.winfo_pathname(build_window.winfo_id()))

    def settings_menu(self):

        #def v_func(self, v_var):



        settings_window = tk.Tk()
        settings_window.title("Settings Menu")
        settings_window.minsize(250, 20)

        label_settings = tk.Label(settings_window, text="Patcher Settings")
        label_settings.place(relx=0.1, rely=0.1, anchor=SW)

        local_verbose_debug = tk.BooleanVar()
        verbose_box = tk.Checkbutton(settings_window, text='Enable Verbose Booting', variable=local_verbose_debug)
        verbose_box.pack()
        local_verbose_debug.set(True)
        print(local_verbose_debug.get())
        verbose_box.local_verbose_debug = local_verbose_debug


        #local_verbose_debug..set(self.constants.verbose_debug)

        settings_window.eval('tk::PlaceWindow %s center' % settings_window.winfo_pathname(settings_window.winfo_id()))



    def main_menu(self):
        #self.identify_model()
        main_window = tk.Tk()
        main_window.title("Main Menu")
        window_height = 350
        window_width = 400
        main_window.resizable(False, False)
        screen_width = main_window.winfo_screenwidth()
        screen_height = main_window.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        main_window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))


        # Check if supported
        if self.current_model in ModelArray.SupportedSMBIOS11:
            self.support = True
            self.support_string = "Model is supported"
        else:
            self.support = False
            self.support_string = "Model is unsupported"

        # Setup Labels
        self.label_header = tk.Label(text=f"OpenCore Legacy Patcher v{self.constants.patcher_version}", font=(".AppleSystemUIFont", 20))
        self.label_smbios = tk.Label(text=f"Detected model: {self.current_model}", font=(".AppleSystemUIFont", 15))
        self.label_support = tk.Label(text=self.support_string, font=(".AppleSystemUIFont", 15))
        self.label_build = tk.Label(text="🔨",font=(".AppleSystemUIFont", 50))
        self.label_install = tk.Label(text="🔧",font=(".AppleSystemUIFont", 50))

        # Setup Text Entry
        self.entry_smbios = tk.Entry(width=12, justify='center')

        # Setup Buttons
        self.button_update = tk.Button(text="Update SMBIOS", command=self.update_model_clicked)
        self.button_build = tk.Button(text="Build OpenCore", command=self.build_clicked)
        self.button_install = tk.Button(text="Install OpenCore")
        self.button_settings = tk.Button(text="⚙️", command=self.settings_menu)

        # Place Labels
        self.label_header.place(relx=0.5, rely=0.0, anchor=N)
        self.label_smbios.place(relx=0.5, rely=0.1, anchor=N)
        self.label_support.place(relx=0.5, rely=0.2, anchor=N)
        self.entry_smbios.place(relx=0.5, rely=0.3, anchor=N)
        self.button_update.place(relx=0.5, rely=0.4, anchor=N)
        self.label_build.place(relx=0.25, rely=0.75, anchor=S)
        self.button_build.place(relx=0.25, rely=0.85, anchor=S)
        self.label_install.place(relx=0.75, rely=0.75, anchor=S)
        self.button_install.place(relx=0.75, rely=0.85, anchor=S)
        self.button_settings.place(relx=0.9, rely=0.175, anchor=S)

        main_window.mainloop()



GUI_MENU().main_menu()