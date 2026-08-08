import tkinter as tk
from tkinter import ttk, messagebox
import config
import database
from utils.face_utils import load_and_resize_image

class SearchCitizenWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search Citizen Database - National People Database")
        self.geometry("1100x650")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.citizens_data = []

        self._create_widgets()
        self.perform_search()

    def _create_widgets(self):
        # Header Banner
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Citizen Database Directory & Profile Search",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        ).pack(pady=10)

        # Top Search Control Bar
        search_bar = tk.Frame(self, bg=config.COLOR_CARD_BG, padx=20, pady=12, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        search_bar.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            search_bar,
            text="🔍 Search Query:",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_DARK_TEXT
        ).pack(side="left", padx=(0, 10))

        self.entry_search = tk.Entry(
            search_bar,
            font=(config.FONT_FAMILY, 11),
            bg=config.COLOR_SECONDARY,
            fg=config.COLOR_DARK_TEXT,
            relief="flat",
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1,
            width=40
        )
        self.entry_search.pack(side="left", ipady=5, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda e: self.perform_search())

        btn_search = tk.Button(
            search_bar,
            text="Search",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=15,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=self.perform_search
        )
        btn_search.pack(side="left", padx=(0, 5))

        btn_reset = tk.Button(
            search_bar,
            text="Clear",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_MUTED_TEXT,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            padx=15,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=self.reset_search
        )
        btn_reset.pack(side="left")

        # Main Workspace Split (Left: Treeview Table, Right: Profile Details Card)
        workspace = tk.Frame(self, bg=config.COLOR_BACKGROUND, padx=20, pady=5)
        workspace.pack(fill="both", expand=True)

        # Left Column: Treeview
        table_frame = tk.Frame(workspace, bg=config.COLOR_CARD_BG, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        columns = ("id", "name", "age", "gender", "phone", "national_id")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        self.tree.heading("id", text="Citizen ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("national_id", text="National ID")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("age", width=50, anchor="center")
        self.tree.column("gender", width=70, anchor="center")
        self.tree.column("phone", width=120, anchor="w")
        self.tree.column("national_id", width=130, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_record_selected)

        # Right Column: Full Citizen Profile Details Card
        self.profile_card = tk.Frame(workspace, bg=config.COLOR_CARD_BG, width=360, padx=20, pady=15, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        self.profile_card.pack(side="right", fill="both", expand=False)
        self.profile_card.pack_propagate(False)

        tk.Label(self.profile_card, text="Citizen Identity Profile", font=config.FONT_HEADING, bg=config.COLOR_CARD_BG, fg=config.COLOR_PRIMARY).pack(anchor="w", pady=(0, 10))

        self.photo_label = tk.Label(
            self.profile_card,
            text="Select citizen from table\nto view full profile",
            font=config.FONT_BODY,
            bg="#E2E8F0",
            fg=config.COLOR_MUTED_TEXT,
            width=20,
            height=8
        )
        self.photo_label.pack(pady=5)

        self.details_grid = tk.Frame(self.profile_card, bg=config.COLOR_CARD_BG)
        self.details_grid.pack(fill="both", expand=True, pady=10)

        self.info_labels = {}
        info_fields = [
            ("Citizen ID:", "citizen_id"),
            ("Full Name:", "name"),
            ("National ID:", "national_id"),
            ("Age / DOB:", "age_dob"),
            ("Gender:", "gender"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address"),
            ("Criminal Record:", "criminal_record"),
            ("Document:", "document_info"),
            ("Registered:", "created_at")
        ]

        for idx, (lbl_txt, k) in enumerate(info_fields):
            l = tk.Label(self.details_grid, text=lbl_txt, font=config.FONT_BODY_BOLD, bg=config.COLOR_CARD_BG, fg=config.COLOR_MUTED_TEXT, anchor="w")
            l.grid(row=idx, column=0, sticky="w", pady=2)

            v = tk.Label(self.details_grid, text="--", font=config.FONT_BODY, bg=config.COLOR_CARD_BG, fg=config.COLOR_DARK_TEXT, anchor="w", wraplength=200)
            v.grid(row=idx, column=1, sticky="w", padx=(10, 0), pady=2)
            self.info_labels[k] = v

    def perform_search(self):
        query = self.entry_search.get().strip()
        self.citizens_data = database.search_citizen(query)

        # Clear existing Treeview rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new rows
        for c in self.citizens_data:
            self.tree.insert(
                "",
                "end",
                values=(
                    c['citizen_id'],
                    c['name'],
                    c['age'],
                    c['gender'],
                    c['phone'],
                    c['national_id']
                )
            )

        if len(self.citizens_data) > 0:
            # Select first item by default
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)

    def reset_search(self):
        self.entry_search.delete(0, tk.END)
        self.perform_search()

    def on_record_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0])['values']
        if not item_vals:
            return

        c_id = item_vals[0]
        citizen = database.get_citizen_by_id(c_id)
        if not citizen:
            return

        # Update profile card fields
        self.info_labels["citizen_id"].config(text=str(citizen['citizen_id']))
        self.info_labels["name"].config(text=citizen['name'])
        self.info_labels["national_id"].config(text=citizen['national_id'])
        self.info_labels["age_dob"].config(text=f"{citizen['age']} yrs ({citizen['dob']})")
        self.info_labels["gender"].config(text=citizen['gender'])
        self.info_labels["phone"].config(text=citizen['phone'])
        self.info_labels["email"].config(text=citizen['email'])
        self.info_labels["address"].config(text=citizen['address'])
        crim = citizen.get('criminal_record') or "Clean / None"
        self.info_labels["criminal_record"].config(text=crim)
        doc_path = citizen.get('document_path') or ""
        doc_desc = citizen.get('document_description') or ""
        doc_str = doc_desc if doc_desc else (doc_path if doc_path else "None")
        self.info_labels["document_info"].config(text=doc_str)
        self.info_labels["created_at"].config(text=citizen['created_at'])

        # Load Facial Photo
        photo_tk = load_and_resize_image(citizen.get('photo_path', ''), 140, 140)
        if photo_tk:
            self.photo_label.img_tk = photo_tk
            self.photo_label.config(image=photo_tk, text="")
        else:
            self.photo_label.config(image="", text="Photo Not Available")
