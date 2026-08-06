import tkinter as tk
from tkinter import ttk, messagebox
import config
import database
from register import RegisterCitizenWindow
from search import SearchCitizenWindow
from update import UpdateCitizenWindow
from delete import DeleteCitizenWindow
from recognize_face import RecognizeFaceWindow
from reports import ReportsWindow

class DashboardWindow:
    def __init__(self, root, username, on_logout):
        self.root = root
        self.username = username
        self.on_logout = on_logout

        self.root.title(f"{config.APP_TITLE} - Dashboard")
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(config.IS_RESIZABLE, config.IS_RESIZABLE)
        self.root.configure(bg=config.COLOR_BACKGROUND)

        self._create_widgets()
        self.refresh_dashboard_stats()

    def _create_widgets(self):
        # 1. Top Header Bar
        header = tk.Frame(self.root, bg=config.COLOR_SIDEBAR, height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        brand_lbl = tk.Label(
            header,
            text="🏛️  NATIONAL PEOPLE DATABASE SYSTEM",
            font=config.FONT_TITLE,
            bg=config.COLOR_SIDEBAR,
            fg="white"
        )
        brand_lbl.pack(side="left", padx=20)

        # Right User Info & Logout
        user_frame = tk.Frame(header, bg=config.COLOR_SIDEBAR)
        user_frame.pack(side="right", padx=20)

        user_badge = tk.Label(
            user_frame,
            text=f"👤 Logged in as: {self.username.upper()}",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_SIDEBAR,
            fg=config.COLOR_ACCENT
        )
        user_badge.pack(side="left", padx=(0, 15))

        btn_logout = tk.Button(
            user_frame,
            text="🚪 Logout",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_DANGER,
            fg="white",
            activebackground="#DC2626",
            activeforeground="white",
            padx=12,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=self.handle_logout
        )
        btn_logout.pack(side="left")

        # 2. Main Horizontal Container (Sidebar + Main Content Area)
        main_container = tk.Frame(self.root, bg=config.COLOR_BACKGROUND)
        main_container.pack(fill="both", expand=True)

        # Sidebar Panel
        sidebar = tk.Frame(main_container, bg=config.COLOR_SIDEBAR, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        nav_label = tk.Label(
            sidebar,
            text="MAIN NAVIGATION",
            font=config.FONT_SMALL,
            bg=config.COLOR_SIDEBAR,
            fg=config.COLOR_MUTED_TEXT,
            anchor="w"
        )
        nav_label.pack(fill="x", padx=20, pady=(20, 10))

        # Navigation Buttons List
        nav_items = [
            ("👤 Register Citizen", self.open_register),
            ("🔍 Search Records", self.open_search),
            ("📷 Face Recognition", self.open_face_recognition),
            ("✏️ Update Record", self.open_update),
            ("🗑️ Delete Record", self.open_delete),
            ("📊 Database Reports", self.open_reports),
            ("❌ Exit Application", self.handle_exit)
        ]

        for text, cmd in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=config.FONT_BODY_BOLD,
                bg=config.COLOR_SIDEBAR,
                fg=config.COLOR_SIDEBAR_TEXT,
                activebackground=config.COLOR_SIDEBAR_HOVER,
                activeforeground="white",
                anchor="w",
                padx=20,
                pady=12,
                relief="flat",
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x", pady=2)

        # 3. Main Dashboard Workspace Panel
        self.workspace = tk.Frame(main_container, bg=config.COLOR_BACKGROUND, padx=30, pady=25)
        self.workspace.pack(side="right", fill="both", expand=True)

        # Welcome Subheading
        welcome_lbl = tk.Label(
            self.workspace,
            text="Executive Dashboard & System Overview",
            font=config.FONT_TITLE,
            bg=config.COLOR_BACKGROUND,
            fg=config.COLOR_DARK_TEXT
        )
        welcome_lbl.pack(anchor="w", pady=(0, 5))

        sub_lbl = tk.Label(
            self.workspace,
            text="Manage citizen identity profiles, biometric facial recognition, and database records.",
            font=config.FONT_BODY,
            bg=config.COLOR_BACKGROUND,
            fg=config.COLOR_MUTED_TEXT
        )
        sub_lbl.pack(anchor="w", pady=(0, 20))

        # Stat Cards Container Grid
        self.cards_frame = tk.Frame(self.workspace, bg=config.COLOR_BACKGROUND)
        self.cards_frame.pack(fill="x", pady=(0, 25))

        self.stat_widgets = {}
        card_configs = [
            ("Total Citizens", "total_citizens", "👥", config.COLOR_PRIMARY),
            ("Male Citizens", "male_count", "👨", "#3B82F6"),
            ("Female Citizens", "female_count", "👩", "#EC4899"),
            ("Recognition Attempts", "total_attempts", "📷", config.COLOR_SUCCESS)
        ]

        for idx, (title, key, icon, color) in enumerate(card_configs):
            card = tk.Frame(
                self.cards_frame,
                bg=config.COLOR_CARD_BG,
                padx=20,
                pady=18,
                highlightbackground=config.COLOR_BORDER,
                highlightthickness=1
            )
            card.grid(row=0, column=idx, padx=10, sticky="nsew")
            self.cards_frame.grid_columnconfigure(idx, weight=1)

            top_row = tk.Frame(card, bg=config.COLOR_CARD_BG)
            top_row.pack(fill="x")

            icon_lbl = tk.Label(top_row, text=icon, font=(config.FONT_FAMILY, 22), bg=config.COLOR_CARD_BG)
            icon_lbl.pack(side="left")

            title_lbl = tk.Label(
                top_row,
                text=title,
                font=config.FONT_BODY_BOLD,
                bg=config.COLOR_CARD_BG,
                fg=config.COLOR_MUTED_TEXT
            )
            title_lbl.pack(side="right", anchor="e")

            val_lbl = tk.Label(
                card,
                text="0",
                font=(config.FONT_FAMILY, 24, "bold"),
                bg=config.COLOR_CARD_BG,
                fg=color
            )
            val_lbl.pack(anchor="w", pady=(10, 0))
            self.stat_widgets[key] = val_lbl

        # Quick Actions Grid Section
        qa_lbl = tk.Label(
            self.workspace,
            text="Quick Administrative Actions",
            font=config.FONT_HEADING,
            bg=config.COLOR_BACKGROUND,
            fg=config.COLOR_DARK_TEXT
        )
        qa_lbl.pack(anchor="w", pady=(10, 10))

        actions_frame = tk.Frame(self.workspace, bg=config.COLOR_BACKGROUND)
        actions_frame.pack(fill="x")

        quick_btns = [
            ("➕ Register New Citizen", config.COLOR_PRIMARY, self.open_register),
            ("📷 Start Face Recognition", config.COLOR_SUCCESS, self.open_face_recognition),
            ("🔍 Search Database", config.COLOR_DARK_TEXT, self.open_search),
            ("📊 View Reports & Logs", "#8B5CF6", self.open_reports)
        ]

        for idx, (b_text, b_color, b_cmd) in enumerate(quick_btns):
            qbtn = tk.Button(
                actions_frame,
                text=b_text,
                font=config.FONT_BODY_BOLD,
                bg=b_color,
                fg="white",
                activebackground=b_color,
                activeforeground="white",
                pady=15,
                relief="flat",
                cursor="hand2",
                command=b_cmd
            )
            row_idx = idx // 2
            col_idx = idx % 2
            qbtn.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            actions_frame.grid_columnconfigure(col_idx, weight=1)

        # Educational Project Notice Footer
        disclaimer = tk.Label(
            self.workspace,
            text="🔒 COLLEGE DEMONSTRATION SYSTEM: Educational use only with consented or sample test dataset.",
            font=config.FONT_SMALL,
            bg=config.COLOR_BACKGROUND,
            fg=config.COLOR_MUTED_TEXT
        )
        disclaimer.pack(side="bottom", pady=10)

    def refresh_dashboard_stats(self):
        stats = database.get_report_stats()
        for k, lbl in self.stat_widgets.items():
            if k in stats:
                lbl.config(text=str(stats[k]))

    def open_register(self):
        RegisterCitizenWindow(self.root, on_success=self.refresh_dashboard_stats)

    def open_search(self):
        SearchCitizenWindow(self.root)

    def open_face_recognition(self):
        RecognizeFaceWindow(self.root)

    def open_update(self):
        UpdateCitizenWindow(self.root, on_success=self.refresh_dashboard_stats)

    def open_delete(self):
        DeleteCitizenWindow(self.root, on_success=self.refresh_dashboard_stats)

    def open_reports(self):
        ReportsWindow(self.root)

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the system?"):
            self.on_logout()

    def handle_exit(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the application?"):
            self.root.destroy()
