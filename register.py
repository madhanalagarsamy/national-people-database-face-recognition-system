import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import config
import database
from capture_face import FaceCaptureWindow
from utils.face_utils import load_and_resize_image

class RegisterCitizenWindow(tk.Toplevel):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.title("Register New Citizen - National People Database")
        self.geometry("900x650")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.on_success = on_success
        self.captured_photo_path = None

        self._create_widgets()

    def _create_widgets(self):
        # Header Banner
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Citizen Registration Form",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        ).pack(pady=10)

        # Content Layout Frame
        body = tk.Frame(self, bg=config.COLOR_BACKGROUND, padx=25, pady=15)
        body.pack(fill="both", expand=True)

        # Left Column: Form Fields Grid
        left_frame = tk.Frame(body, bg=config.COLOR_CARD_BG, padx=20, pady=20, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        tk.Label(left_frame, text="Personal Details", font=config.FONT_HEADING, bg=config.COLOR_CARD_BG, fg=config.COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        fields = [
            ("Citizen ID *", "entry_id"),
            ("Full Name *", "entry_name"),
            ("Age *", "entry_age"),
            ("Gender *", "entry_gender"),
            ("Date of Birth (YYYY-MM-DD) *", "entry_dob"),
            ("National ID Card No *", "entry_national_id"),
            ("Phone Number *", "entry_phone"),
            ("Email Address *", "entry_email"),
            ("Residential Address *", "entry_address"),
            ("Criminal Record", "entry_criminal"),
            ("Document Path", "entry_document"),
            ("Document Description", "entry_doc_desc")
        ]

        self.inputs = {}

        for idx, (label_txt, key) in enumerate(fields, start=1):
            lbl = tk.Label(
                left_frame,
                text=label_txt,
                font=config.FONT_BODY_BOLD,
                bg=config.COLOR_CARD_BG,
                fg=config.COLOR_DARK_TEXT,
                anchor="w"
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=4)

            if key == "entry_gender":
                widget = ttk.Combobox(
                    left_frame,
                    values=["Male", "Female", "Other"],
                    state="readonly",
                    font=(config.FONT_FAMILY, 10),
                    width=28
                )
                widget.set("Male")
            else:
                widget = tk.Entry(
                    left_frame,
                    font=(config.FONT_FAMILY, 10),
                    bg=config.COLOR_SECONDARY,
                    fg=config.COLOR_DARK_TEXT,
                    relief="flat",
                    highlightbackground=config.COLOR_BORDER,
                    highlightthickness=1,
                    width=30
                )

            widget.grid(row=idx, column=1, sticky="w", padx=(10, 0), pady=4, ipady=3 if key != "entry_gender" else 1)
            self.inputs[key] = widget
            if key == "entry_document":
                browse_btn = tk.Button(left_frame, text="Browse...", command=self.browse_document)
                browse_btn.grid(row=idx, column=2, padx=5)

        # Auto-suggest Next Citizen ID
        existing = database.get_all_citizens()
        next_id = max([c['citizen_id'] for c in existing], default=1000) + 1
        self.inputs['entry_id'].insert(0, str(next_id))

        # Right Column: Photo Capture & Preview Panel
        right_frame = tk.Frame(body, bg=config.COLOR_CARD_BG, width=280, padx=20, pady=20, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        right_frame.pack(side="right", fill="both", expand=False)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Biometric Facial Photo", font=config.FONT_HEADING, bg=config.COLOR_CARD_BG, fg=config.COLOR_PRIMARY).pack(anchor="w", pady=(0, 15))

        self.photo_preview = tk.Label(
            right_frame,
            text="No Photo Captured\n\nClick 'Capture Face'\nbelow to take a photo",
            font=config.FONT_BODY,
            bg="#E2E8F0",
            fg=config.COLOR_MUTED_TEXT,
            width=22,
            height=10
        )
        self.photo_preview.pack(pady=10)

        btn_capture = tk.Button(
            right_frame,
            text="📷 Capture / Upload Face",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.open_capture_window
        )
        btn_capture.pack(fill="x", pady=(10, 20))

        # Form Action Buttons (Save, Reset, Back)
        actions_frame = tk.Frame(right_frame, bg=config.COLOR_CARD_BG)
        actions_frame.pack(fill="x", side="bottom")

        btn_save = tk.Button(
            actions_frame,
            text="💾 Save Record",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.save_citizen
        )
        btn_save.pack(fill="x", pady=3)

        btn_reset = tk.Button(
            actions_frame,
            text="🔄 Reset Form",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_MUTED_TEXT,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.reset_form
        )
        btn_reset.pack(fill="x", pady=3)

        btn_back = tk.Button(
            actions_frame,
            text="⬅️ Back",
            font=config.FONT_BODY_BOLD,
            bg="#94A3B8",
            fg="white",
            activebackground="#64748B",
            activeforeground="white",
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        )
        btn_back.pack(fill="x", pady=3)

    def open_capture_window(self):
        c_id = self.inputs['entry_id'].get().strip() or "temp"
        FaceCaptureWindow(self, citizen_id=c_id, on_captured_callback=self.on_face_captured)

    def on_face_captured(self, photo_path):
        self.captured_photo_path = photo_path
        photo_tk = load_and_resize_image(photo_path, 160, 160)
        if photo_tk:
            self.photo_preview.img_tk = photo_tk
            self.photo_preview.config(image=photo_tk, text="")

    def save_citizen(self):
        # Extract inputs
        c_id = self.inputs['entry_id'].get().strip()
        name = self.inputs['entry_name'].get().strip()
        age = self.inputs['entry_age'].get().strip()
        gender = self.inputs['entry_gender'].get().strip()
        dob = self.inputs['entry_dob'].get().strip()
        nat_id = self.inputs['entry_national_id'].get().strip()
        phone = self.inputs['entry_phone'].get().strip()
        email = self.inputs['entry_email'].get().strip()
        address = self.inputs['entry_address'].get().strip()

        # Input Validation Rules
        if not all([c_id, name, age, gender, dob, nat_id, phone, email, address]):
            messagebox.showwarning("Validation Error", "All registration fields are required! Please fill out all inputs.")
            return

        if not c_id.isdigit():
            messagebox.showwarning("Validation Error", "Citizen ID must be a numeric integer value.")
            return

        if not age.isdigit():
            messagebox.showwarning("Validation Error", "Age must be a numeric integer value.")
            return

        if not self.captured_photo_path or not os.path.exists(self.captured_photo_path):
            messagebox.showwarning("Validation Error", "Facial photo is required. Click 'Capture / Upload Face' before saving.")
            return

        # Attempt Database Insertion
        # Gather optional admin fields
        criminal_record = self.inputs.get('entry_criminal').get().strip() if self.inputs.get('entry_criminal') else None
        document_path = self.inputs.get('entry_document').get().strip() if self.inputs.get('entry_document') else None
        document_description = self.inputs.get('entry_doc_desc').get().strip() if self.inputs.get('entry_doc_desc') else None
        success, msg = database.add_citizen(
            citizen_id=int(c_id),
            name=name,
            age=int(age),
            gender=gender,
            dob=dob,
            address=address,
            phone=phone,
            national_id=nat_id,
            email=email,
            photo_path=self.captured_photo_path,
            criminal_record=criminal_record if criminal_record else None,
            document_path=document_path if document_path else None,
            document_description=document_description if document_description else None
        )

        if success:
            messagebox.showinfo("Registration Successful", f"Citizen '{name}' registered successfully under ID #{c_id}!")
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Registration Error", msg)

    def reset_form(self):
        for k, widget in self.inputs.items():
            if k == "entry_gender":
                widget.set("Male")
            else:
                widget.delete(0, tk.END)

        self.captured_photo_path = None
        self.photo_preview.config(image="", text="No Photo Captured\n\nClick 'Capture Face'\nbelow to take a photo")
    def browse_document(self):
        file_path = filedialog.askopenfilename(title="Select Document", filetypes=[("All Files", "*.*")])
        if file_path:
            self.inputs['entry_document'].delete(0, tk.END)
            self.inputs['entry_document'].insert(0, file_path)

