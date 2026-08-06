import tkinter as tk
from tkinter import ttk
import config
import database

class ReportsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Database & Biometric Recognition Analytics Reports")
        self.geometry("1050x650")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self.load_report_data()

    def _create_widgets(self):
        # Header Banner
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="System Analytics & Biometric Recognition Reports",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        ).pack(pady=10)

        body = tk.Frame(self, bg=config.COLOR_BACKGROUND, padx=25, pady=20)
        body.pack(fill="both", expand=True)

        # Executive Metrics Cards Row
        cards_row = tk.Frame(body, bg=config.COLOR_BACKGROUND)
        cards_row.pack(fill="x", pady=(0, 20))

        self.cards = {}
        metrics = [
            ("Total Registered", "total_citizens", "👥", config.COLOR_PRIMARY),
            ("Male Citizens", "male_count", "👨", "#3B82F6"),
            ("Female Citizens", "female_count", "👩", "#EC4899"),
            ("Total Attempts", "total_attempts", "📷", config.COLOR_DARK_TEXT),
            ("Successful Recognitions", "successful_recognitions", "✅", config.COLOR_SUCCESS)
        ]

        for idx, (title, key, icon, color) in enumerate(metrics):
            c = tk.Frame(cards_row, bg=config.COLOR_CARD_BG, padx=15, pady=15, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
            c.grid(row=0, column=idx, padx=5, sticky="nsew")
            cards_row.grid_columnconfigure(idx, weight=1)

            t = tk.Label(c, text=f"{icon} {title}", font=config.FONT_SMALL, bg=config.COLOR_CARD_BG, fg=config.COLOR_MUTED_TEXT)
            t.pack(anchor="w")

            v = tk.Label(c, text="0", font=(config.FONT_FAMILY, 20, "bold"), bg=config.COLOR_CARD_BG, fg=color)
            v.pack(anchor="w", pady=(5, 0))
            self.cards[key] = v

        # Analytics Accuracy Summary Banner
        self.banner = tk.Frame(body, bg=config.COLOR_CARD_BG, padx=20, pady=12, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        self.banner.pack(fill="x", pady=(0, 15))

        self.lbl_accuracy = tk.Label(
            self.banner,
            text="Biometric Accuracy Score: 100%",
            font=config.FONT_HEADING,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_SUCCESS
        )
        self.lbl_accuracy.pack(side="left")

        btn_refresh = tk.Button(
            self.banner,
            text="🔄 Refresh Data",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=12,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=self.load_report_data
        )
        btn_refresh.pack(side="right")

        # Audit Logs Section Label
        tk.Label(body, text="Biometric Recognition Audit Trail", font=config.FONT_HEADING, bg=config.COLOR_BACKGROUND, fg=config.COLOR_DARK_TEXT).pack(anchor="w", pady=(0, 8))

        # Logs Treeview Table Container
        logs_frame = tk.Frame(body, bg=config.COLOR_CARD_BG, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        logs_frame.pack(fill="both", expand=True)

        columns = ("id", "timestamp", "citizen_id", "name", "confidence", "status")
        self.tree = ttk.Treeview(logs_frame, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="Log ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("citizen_id", text="Citizen ID")
        self.tree.heading("name", text="Identified Name")
        self.tree.heading("confidence", text="Match Confidence")
        self.tree.heading("status", text="Verification Result")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("timestamp", width=160, anchor="center")
        self.tree.column("citizen_id", width=90, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("confidence", width=130, anchor="center")
        self.tree.column("status", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_report_data(self):
        stats = database.get_report_stats()

        # Update Stat Cards
        for k in self.cards:
            self.cards[k].config(text=str(stats.get(k, 0)))

        # Calculate Accuracy %
        attempts = stats.get('total_attempts', 0)
        successes = stats.get('successful_recognitions', 0)
        rate = (successes / attempts * 100) if attempts > 0 else 0.0

        self.lbl_accuracy.config(
            text=f"Biometric Identification Success Rate: {rate:.1f}% ({successes} / {attempts} recognitions)",
            fg=config.COLOR_SUCCESS if rate >= 50.0 else config.COLOR_WARNING
        )

        # Clear and Populate Audit Logs Table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for log in stats.get('recent_logs', []):
            c_id_str = str(log['citizen_id']) if log['citizen_id'] else "N/A"
            conf_str = f"{log['confidence']:.1f}%"
            self.tree.insert(
                "",
                "end",
                values=(
                    log['id'],
                    log['timestamp'],
                    c_id_str,
                    log['citizen_name'],
                    conf_str,
                    log['status']
                )
            )
