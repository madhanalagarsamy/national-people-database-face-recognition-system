import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

import config
import database
from login import LoginWindow
from dashboard import DashboardWindow

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(config.IS_RESIZABLE, config.IS_RESIZABLE)

        # Initialize Database Tables
        database.init_db()

        # Apply Global TTK Modern Styles
        self._setup_styles()

        # Current View Reference
        self.current_user = None
        self.show_login()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Global fonts and colors
        style.configure(".", font=(config.FONT_FAMILY, 10), background=config.COLOR_BACKGROUND)

        # Treeview styling
        style.configure(
            "Treeview",
            background=config.COLOR_CARD_BG,
            fieldbackground=config.COLOR_CARD_BG,
            foreground=config.COLOR_DARK_TEXT,
            font=(config.FONT_FAMILY, 10),
            rowheight=28
        )
        style.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground=config.COLOR_DARK_TEXT,
            font=(config.FONT_FAMILY, 10, "bold"),
            padding=6
        )
        style.map("Treeview", background=[("selected", config.COLOR_PRIMARY)], foreground=[("selected", "white")])

        # Combobox styling
        style.configure(
            "TCombobox",
            fieldbackground=config.COLOR_SECONDARY,
            background=config.COLOR_SECONDARY,
            foreground=config.COLOR_DARK_TEXT,
            padding=5
        )

    def show_login(self):
        self._clear_window()
        LoginWindow(self.root, on_login_success=self.on_login_success)

    def on_login_success(self, username):
        self.current_user = username
        self.show_dashboard()

    def show_dashboard(self):
        self._clear_window()
        DashboardWindow(self.root, username=self.current_user, on_logout=self.show_login)

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
