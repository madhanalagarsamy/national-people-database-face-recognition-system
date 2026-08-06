import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import os
import numpy as np
from PIL import Image, ImageTk
import config
import database
from utils.face_utils import (
    detect_faces,
    get_face_encoding,
    compare_encodings,
    cv2_to_photoimage,
    load_and_resize_image
)

class RecognizeFaceWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Live Face Recognition & Identity Verification")
        self.geometry("1100x650")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.cap = None
        self.is_running = False
        self.known_encodings = []  # List of tuples: (citizen_dict, encoding_tuple)
        self.current_match = None
        self.last_logged_person = None

        self._load_known_faces()
        self._create_widgets()
        self._start_camera()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _load_known_faces(self):
        """Pre-loads face encodings for all citizens in the database."""
        citizens = database.get_all_citizens()
        self.known_encodings = []

        for citizen in citizens:
            photo_path = citizen.get('photo_path', '')
            if photo_path and os.path.exists(photo_path):
                img = cv2.imread(photo_path)
                if img is not None:
                    enc = get_face_encoding(img)
                    if enc is not None:
                        self.known_encodings.append((citizen, enc))

    def _create_widgets(self):
        # Header Bar
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Biometric Face Recognition Engine",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        ).pack(pady=10)

        # Main Layout (Left: Camera Feed, Right: Citizen Identity Card & Match Results)
        body_frame = tk.Frame(self, bg=config.COLOR_BACKGROUND)
        body_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Left Column: Video Feed Container
        left_col = tk.Frame(body_frame, bg=config.COLOR_BACKGROUND)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.video_container = tk.Frame(
            left_col,
            bg="black",
            width=600,
            height=440,
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=2
        )
        self.video_container.pack()
        self.video_container.pack_propagate(False)

        self.video_label = tk.Label(self.video_container, bg="black")
        self.video_label.pack(fill="both", expand=True)

        # Camera Controls
        ctrl_frame = tk.Frame(left_col, bg=config.COLOR_BACKGROUND)
        ctrl_frame.pack(pady=10)

        self.btn_upload = tk.Button(
            ctrl_frame,
            text="📁 Test Image File",
            font=config.FONT_BODY_BOLD,
            bg="#475569",
            fg="white",
            activebackground="#334155",
            activeforeground="white",
            padx=12,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=self.recognize_from_file
        )
        self.btn_upload.pack(side="left", padx=5)

        self.btn_resume = tk.Button(
            ctrl_frame,
            text="📹 Resume Live Camera",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=12,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=self.resume_live_camera
        )
        self.btn_resume.pack(side="left", padx=5)

        # Right Column: Identity Match Card
        right_col = tk.Frame(body_frame, bg=config.COLOR_CARD_BG, width=420, highlightbackground=config.COLOR_BORDER, highlightthickness=1)
        right_col.pack(side="right", fill="both", expand=False)
        right_col.pack_propagate(False)

        card_title = tk.Label(
            right_col,
            text="Identity Verification Results",
            font=config.FONT_HEADING,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_DARK_TEXT
        )
        card_title.pack(anchor="w", padx=15, pady=(15, 5))

        tk.Frame(right_col, bg=config.COLOR_BORDER, height=1).pack(fill="x", padx=15, pady=5)

        # Matched Photo Preview
        self.photo_preview_label = tk.Label(
            right_col,
            bg="#E2E8F0",
            text="No Identity Matched",
            font=config.FONT_BODY,
            fg=config.COLOR_MUTED_TEXT,
            width=18,
            height=8
        )
        self.photo_preview_label.pack(pady=10)

        # Status & Confidence Badge
        self.badge_label = tk.Label(
            right_col,
            text="STATUS: SCANNING...",
            font=config.FONT_BODY_BOLD,
            bg="#E2E8F0",
            fg=config.COLOR_DARK_TEXT,
            padx=15,
            pady=6
        )
        self.badge_label.pack(fill="x", padx=20, pady=5)

        # Details Grid
        self.details_frame = tk.Frame(right_col, bg=config.COLOR_CARD_BG)
        self.details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.fields = [
            ("Citizen ID:", "citizen_id"),
            ("Full Name:", "name"),
            ("National ID:", "national_id"),
            ("Phone:", "phone"),
            ("Gender / Age:", "gender_age"),
            ("Match Confidence:", "confidence")
        ]

        self.val_labels = {}
        for idx, (label_text, key) in enumerate(self.fields):
            lbl = tk.Label(
                self.details_frame,
                text=label_text,
                font=config.FONT_BODY_BOLD,
                bg=config.COLOR_CARD_BG,
                fg=config.COLOR_MUTED_TEXT,
                anchor="w"
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=4)

            val = tk.Label(
                self.details_frame,
                text="--",
                font=config.FONT_BODY,
                bg=config.COLOR_CARD_BG,
                fg=config.COLOR_DARK_TEXT,
                anchor="w"
            )
            val.grid(row=idx, column=1, sticky="w", padx=(10, 0), pady=4)
            self.val_labels[key] = val

    def _start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Webcam device non-responsive.")
            self.is_running = True
            self.update_recognition_feed()
        except Exception as e:
            self.video_label.config(
                text=f"⚠️ Camera Device Unavailable\n\n({str(e)})\n\nClick 'Test Image File' above to verify facial recognition.",
                fg="white",
                font=config.FONT_BODY_BOLD
            )

    def update_recognition_feed(self):
        if not self.is_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            processed_frame = self._process_frame_and_match(frame)
            img_tk = cv2_to_photoimage(processed_frame, 600, 440)
            self.video_label.img_tk = img_tk
            self.video_label.config(image=img_tk, text="")

        self.after(50, self.update_recognition_feed)

    def _process_frame_and_match(self, frame):
        faces = detect_faces(frame)
        best_citizen = None
        best_confidence = 0.0

        if len(faces) > 0:
            # Pick largest detected face
            faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
            x, y, w, h = faces[0]

            face_enc = get_face_encoding(frame, bbox=(x, y, w, h))

            if face_enc is not None and len(self.known_encodings) > 0:
                best_dist = 999.0
                for citizen, known_enc in self.known_encodings:
                    dist, conf = compare_encodings(face_enc, known_enc)
                    if conf > best_confidence:
                        best_confidence = conf
                        best_dist = dist
                        best_citizen = citizen

            # Determine Match Decision
            if best_citizen and best_confidence >= config.CONFIDENCE_PASS_PERCENT:
                color = (0, 255, 0) # Green
                label_txt = f"{best_citizen['name']} ({best_confidence:.1f}%)"
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                cv2.putText(frame, label_txt, (x, max(25, y - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                self._update_identity_card(best_citizen, best_confidence, is_match=True)

                # Log to DB if changed or newly detected
                if self.last_logged_person != best_citizen['citizen_id']:
                    database.log_recognition(
                        best_citizen['citizen_id'],
                        best_citizen['name'],
                        best_confidence,
                        "SUCCESS"
                    )
                    self.last_logged_person = best_citizen['citizen_id']
            else:
                color = (0, 0, 255) # Red
                label_txt = f"Unknown Person ({best_confidence:.1f}%)"
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                cv2.putText(frame, label_txt, (x, max(25, y - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                self._update_identity_card(None, best_confidence, is_match=False)

                if self.last_logged_person != "UNKNOWN":
                    database.log_recognition(
                        None,
                        "Unknown Person",
                        best_confidence,
                        "UNKNOWN"
                    )
                    self.last_logged_person = "UNKNOWN"
        else:
            self._update_identity_card(None, 0.0, is_match=False, scanning=True)

        return frame

    def _update_identity_card(self, citizen, confidence, is_match=False, scanning=False):
        if scanning:
            self.badge_label.config(text="🔍 SCANNING FOR FACES...", bg="#E2E8F0", fg=config.COLOR_DARK_TEXT)
            self.photo_preview_label.config(image="", text="No Face Detected", bg="#E2E8F0")
            for k in self.val_labels:
                self.val_labels[k].config(text="--")
            return

        if is_match and citizen:
            self.badge_label.config(
                text=f"MATCH VERIFIED - {confidence:.1f}%",
                bg=config.COLOR_SUCCESS,
                fg="white"
            )
            self.val_labels["citizen_id"].config(text=str(citizen['citizen_id']))
            self.val_labels["name"].config(text=citizen['name'])
            self.val_labels["national_id"].config(text=citizen['national_id'])
            self.val_labels["phone"].config(text=citizen['phone'])
            self.val_labels["gender_age"].config(text=f"{citizen['gender']} / {citizen['age']} yrs")
            self.val_labels["confidence"].config(text=f"{confidence:.1f}% Match", fg=config.COLOR_SUCCESS)

            # Load Photo
            photo_tk = load_and_resize_image(citizen.get('photo_path', ''), 140, 140)
            if photo_tk:
                self.photo_preview_label.img_tk = photo_tk
                self.photo_preview_label.config(image=photo_tk, text="")
            else:
                self.photo_preview_label.config(image="", text="Photo\nNot Found")
        else:
            self.badge_label.config(
                text="UNKNOWN PERSON",
                bg=config.COLOR_DANGER,
                fg="white"
            )
            self.photo_preview_label.config(image="", text="❌ Unknown", bg="#FEE2E2", fg=config.COLOR_DANGER)
            self.val_labels["citizen_id"].config(text="N/A")
            self.val_labels["name"].config(text="Unknown Person", fg=config.COLOR_DANGER)
            self.val_labels["national_id"].config(text="N/A")
            self.val_labels["phone"].config(text="N/A")
            self.val_labels["gender_age"].config(text="N/A")
            self.val_labels["confidence"].config(text=f"{confidence:.1f}% (Below Threshold)", fg=config.COLOR_DANGER)

    def recognize_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Test Face Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        frame = cv2.imread(file_path)
        if frame is None:
            messagebox.showerror("Error", "Could not load test image file.")
            return

        self.is_running = False
        processed_frame = self._process_frame_and_match(frame)
        img_tk = cv2_to_photoimage(processed_frame, 600, 440)
        self.video_label.img_tk = img_tk
        self.video_label.config(image=img_tk, text="")

    def resume_live_camera(self):
        if self.cap and self.cap.isOpened():
            self.is_running = True
            self.update_recognition_feed()
        else:
            self._start_camera()

    def on_close(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.destroy()
