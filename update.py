import tkinter as tk
from tkinter import ttk, messagebox
import os
import config
import database
from capture_face import FaceCaptureWindow
from utils.face_utils import load_and_resize_image

class UpdateCitizenWindow(tk.Toplevel):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.title("Update Citizen Record - National People Database")
        self.geometry("900x620")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.on_success = on_success
        self.selected_citizen = None
        self.new_photo_path = None

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Update Citizen Profile Details",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        ).pack(pady=10)

        body = tk.Frame(self, bg=config.COLOR_BACKGROUND, padx=25, pady=15)
        body.pack(fill="both", expand=True)

        # Top Lookup Section
        lookup_frame = tk.Frame(body, bg=config.COLOR_CARD_BG, padx=15, pady=10, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        lookup_frame.pack(fill="x", pady=(0, 15))

        tk.Label(lookup_frame, text="Enter Citizen ID to Update:", font=config.FONT_BODY_BOLD, bg=config.COLOR_CARD_BG).pack(side="left", padx=(0, 10))

        self.entry_search_id = tk.Entry(
            lookup_frame,
            font=(config.FONT_FAMILY, 10),
            bg=config.COLOR_SECONDARY,
            relief="flat",
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1,
            width=20
        )
        self.entry_search_id.pack(side="left", ipady=4, padx=(0, 10))

        btn_fetch = tk.Button(
            lookup_frame,
            text="🔍 Fetch Record",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=12,
            pady=3,
            relief="flat",
            cursor="hand2",
            command=self.fetch_record
        )
        btn_fetch.pack(side="left")

        # Form & Photo Section Split
        content_frame = tk.Frame(body, bg=config.COLOR_BACKGROUND)
        content_frame.pack(fill="both", expand=True)

        # Left Column: Editable Form Fields
        self.form_frame = tk.Frame(content_frame, bg=config.COLOR_CARD_BG, padx=20, pady=15, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        self.form_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        tk.Label(self.form_frame, text="Editable Information", font=config.FONT_HEADING, bg=config.COLOR_CARD_BG, fg=config.COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Read-only Info Header
        self.lbl_readonly = tk.Label(self.form_frame, text="Select a record above to edit details.", font=config.FONT_BODY, bg=config.COLOR_CARD_BG, fg=config.COLOR_MUTED_TEXT)
        self.lbl_readonly.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Editable inputs
        self.entries = {}
        editable_fields = [
            ("Full Name *", "name"),
            ("Residential Address *", "address"),
            ("Phone Number *", "phone"),
            ("Email Address *", "email")
        ]

        for idx, (lbl_txt, key) in enumerate(editable_fields, start=2):
            lbl = tk.Label(self.form_frame, text=lbl_txt, font=config.FONT_BODY_BOLD, bg=config.COLOR_CARD_BG, fg=config.COLOR_DARK_TEXT, anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=6)

            ent = tk.Entry(
                self.form_frame,
                font=(config.FONT_FAMILY, 10),
                bg=config.COLOR_SECONDARY,
                fg=config.COLOR_DARK_TEXT,
                relief="flat",
                highlightbackground=config.COLOR_BORDER,
                highlightthickness=1,
                width=32,
                state="disabled"
            )
            ent.grid(row=idx, column=1, sticky="w", padx=(10, 0), pady=6, ipady=4)
            self.entries[key] = ent

        # Right Column: Photo Update Panel
        photo_frame = tk.Frame(content_frame, bg=config.COLOR_CARD_BG, width=280, padx=20, pady=15, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        photo_frame.pack(side="right", fill="both", expand=False)
        photo_frame.pack_propagate(False)

        tk.Label(photo_frame, text="Facial Photo Management", font=config.FONT_HEADING, bg=config.COLOR_CARD_BG, fg=config.COLOR_PRIMARY).pack(anchor="w", pady=(0, 10))

        self.photo_preview = tk.Label(
            photo_frame,
            text="No Record Loaded",
            font=config.FONT_BODY,
            bg="#E2E8F0",
            fg=config.COLOR_MUTED_TEXT,
            width=20,
            height=8
        )
        self.photo_preview.pack(pady=5)

        self.btn_change_photo = tk.Button(
            photo_frame,
            text="📷 Retake / Replace Photo",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            pady=6,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=self.open_retake_camera
        )
        self.btn_change_photo.pack(fill="x", pady=10)

        # Action Buttons
        actions_frame = tk.Frame(photo_frame, bg=config.COLOR_CARD_BG)
        actions_frame.pack(fill="x", side="bottom")

        self.btn_save = tk.Button(
            actions_frame,
            text="💾 Save Changes",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            pady=8,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=self.save_updates
        )
        self.btn_save.pack(fill="x", pady=3)

        btn_close = tk.Button(
            actions_frame,
            text="⬅️ Cancel",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_MUTED_TEXT,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        )
        btn_close.pack(fill="x", pady=3)

    def fetch_record(self):
        c_id = self.entry_search_id.get().strip()
        if not c_id:
            messagebox.showwarning("Warning", "Please enter a Citizen ID to search.")
            return

        if not c_id.isdigit():
            messagebox.showwarning("Warning", "Citizen ID must be a numeric integer.")
            return

        citizen = database.get_citizen_by_id(c_id)
        if not citizen:
            messagebox.showerror("Error", f"No citizen found with ID #{c_id}.")
            return

        self.selected_citizen = citizen
        self.new_photo_path = None

        # Display Readonly Metadata
        self.lbl_readonly.config(
            text=f"Citizen ID: {citizen['citizen_id']}  |  National ID: {citizen['national_id']}  |  Gender: {citizen['gender']}",
            fg=config.COLOR_PRIMARY
        )

        # Fill Entries
        for k in self.entries:
            self.entries[k].config(state="normal")
            self.entries[k].delete(0, tk.END)
            self.entries[k].insert(0, citizen[k])

        # Load Photo
        photo_tk = load_and_resize_image(citizen.get('photo_path', ''), 140, 140)
        if photo_tk:
            self.photo_preview.img_tk = photo_tk
            self.photo_preview.config(image=photo_tk, text="")
        else:
            self.photo_preview.config(image="", text="Photo Missing")

        self.btn_change_photo.config(state="normal")
        self.btn_save.config(state="normal")

    def open_retake_camera(self):
        if not self.selected_citizen:
            return
        FaceCaptureWindow(self, citizen_id=self.selected_citizen['citizen_id'], on_captured_callback=self.on_new_photo_captured)

    def on_new_photo_captured(self, photo_path):
        self.new_photo_path = photo_path
        photo_tk = load_and_resize_image(photo_path, 140, 140)
        if photo_tk:
            self.photo_preview.img_tk = photo_tk
            self.photo_preview.config(image=photo_tk, text="")

    def save_updates(self):
        if not self.selected_citizen:
            return

        c_id = self.selected_citizen['citizen_id']
        name = self.entries['name'].get().strip()
        address = self.entries['address'].get().strip()
        phone = self.entries['phone'].get().strip()
        email = self.entries['email'].get().strip()

        if not all([name, address, phone, email]):
            messagebox.showwarning("Validation Error", "Please fill in all editable fields before saving.")
            return

        success, msg = database.update_citizen(
            citizen_id=c_id,
            name=name,
            address=address,
            phone=phone,
            email=email,
            photo_path=self.new_photo_path
        )

        if success:
            messagebox.showinfo("Success", f"Citizen record #{c_id} updated successfully!")
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Update Error", msg)
