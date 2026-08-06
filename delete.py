import tkinter as tk
from tkinter import messagebox
import os
import config
import database
from utils.face_utils import load_and_resize_image

class DeleteCitizenWindow(tk.Toplevel):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.title("Delete Citizen Record - National People Database")
        self.geometry("750x550")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.on_success = on_success
        self.selected_citizen = None

        self._create_widgets()

    def _create_widgets(self):
        # Header Banner
        header = tk.Frame(self, bg=config.COLOR_DANGER, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="⚠️ Delete Citizen Record",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_DANGER,
            fg="white"
        ).pack(pady=10)

        body = tk.Frame(self, bg=config.COLOR_BACKGROUND, padx=25, pady=20)
        body.pack(fill="both", expand=True)

        # Lookup Bar
        lookup_frame = tk.Frame(body, bg=config.COLOR_CARD_BG, padx=15, pady=12, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        lookup_frame.pack(fill="x", pady=(0, 20))

        tk.Label(lookup_frame, text="Enter Citizen ID:", font=config.FONT_BODY_BOLD, bg=config.COLOR_CARD_BG).pack(side="left", padx=(0, 10))

        self.entry_id = tk.Entry(
            lookup_frame,
            font=(config.FONT_FAMILY, 10),
            bg=config.COLOR_SECONDARY,
            relief="flat",
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1,
            width=20
        )
        self.entry_id.pack(side="left", ipady=4, padx=(0, 10))

        btn_fetch = tk.Button(
            lookup_frame,
            text="🔍 Find Record",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=12,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=self.fetch_record
        )
        btn_fetch.pack(side="left")

        # Record Details Card Container
        self.card = tk.Frame(body, bg=config.COLOR_CARD_BG, padx=25, pady=20, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        self.card.pack(fill="both", expand=True)

        self.card_content = tk.Frame(self.card, bg=config.COLOR_CARD_BG)
        self.card_content.pack(fill="both", expand=True)

        self.placeholder_lbl = tk.Label(
            self.card_content,
            text="Enter a Citizen ID above and click 'Find Record' to inspect before deletion.",
            font=config.FONT_BODY,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_MUTED_TEXT
        )
        self.placeholder_lbl.pack(expand=True)

    def fetch_record(self):
        c_id = self.entry_id.get().strip()
        if not c_id:
            messagebox.showwarning("Warning", "Please enter a Citizen ID.")
            return

        if not c_id.isdigit():
            messagebox.showwarning("Warning", "Citizen ID must be a numeric integer.")
            return

        citizen = database.get_citizen_by_id(c_id)
        if not citizen:
            messagebox.showerror("Error", f"No citizen record found with ID #{c_id}.")
            return

        self.selected_citizen = citizen

        # Clear placeholder
        for w in self.card_content.winfo_children():
            w.destroy()

        # Render Citizen Summary Card for Deletion Confirmation
        left = tk.Frame(self.card_content, bg=config.COLOR_CARD_BG)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(self.card_content, bg=config.COLOR_CARD_BG)
        right.pack(side="right", padx=(20, 0))

        fields = [
            ("Citizen ID:", str(citizen['citizen_id'])),
            ("Full Name:", citizen['name']),
            ("National ID:", citizen['national_id']),
            ("Gender / Age:", f"{citizen['gender']} ({citizen['age']} yrs)"),
            ("Phone:", citizen['phone']),
            ("Registered:", citizen['created_at'])
        ]

        for idx, (k, v) in enumerate(fields):
            tk.Label(left, text=k, font=config.FONT_BODY_BOLD, bg=config.COLOR_CARD_BG, fg=config.COLOR_MUTED_TEXT).grid(row=idx, column=0, sticky="w", pady=4)
            tk.Label(left, text=v, font=config.FONT_BODY, bg=config.COLOR_CARD_BG, fg=config.COLOR_DARK_TEXT).grid(row=idx, column=1, sticky="w", padx=(10, 0), pady=4)

        # Photo
        photo_tk = load_and_resize_image(citizen.get('photo_path', ''), 120, 120)
        if photo_tk:
            lbl_p = tk.Label(right, image=photo_tk, bg=config.COLOR_CARD_BG)
            lbl_p.img_tk = photo_tk
            lbl_p.pack()

        # Delete Action Controls
        actions = tk.Frame(self.card, bg=config.COLOR_CARD_BG)
        actions.pack(fill="x", side="bottom", pady=(15, 0))

        btn_delete = tk.Button(
            actions,
            text="🗑️ Permanently Delete Record",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_DANGER,
            fg="white",
            activebackground="#DC2626",
            activeforeground="white",
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.confirm_delete
        )
        btn_delete.pack(side="right", padx=5)

        btn_cancel = tk.Button(
            actions,
            text="Cancel",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_MUTED_TEXT,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            pady=8,
            padx=15,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=5)

    def confirm_delete(self):
        if not self.selected_citizen:
            return

        c_id = self.selected_citizen['citizen_id']
        name = self.selected_citizen['name']

        if messagebox.askyesno(
            "Confirm Permanent Deletion",
            f"Are you sure you want to permanently delete record for '{name}' (ID #{c_id})?\n\nThis will remove the database record and facial image permanently!"
        ):
            success, msg, photo_path = database.delete_citizen(c_id)
            if success:
                # Delete image file from disk if present
                if photo_path and os.path.exists(photo_path):
                    try:
                        os.remove(photo_path)
                    except Exception as e:
                        print(f"Warning: Failed to delete image file {photo_path}: {e}")

                messagebox.showinfo("Deleted", f"Citizen record #{c_id} deleted successfully.")
                if self.on_success:
                    self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Delete Error", msg)
