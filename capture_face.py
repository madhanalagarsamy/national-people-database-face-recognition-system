import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import os
import shutil
from PIL import Image, ImageTk
import config
from utils.face_utils import detect_faces, cv2_to_photoimage

class FaceCaptureWindow(tk.Toplevel):
    def __init__(self, parent, citizen_id=None, on_captured_callback=None):
        super().__init__(parent)
        self.title("Face Capture - National People Database")
        self.geometry("700x580")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BACKGROUND)
        self.transient(parent)
        self.grab_set()

        self.citizen_id = citizen_id or "preview"
        self.on_captured_callback = on_captured_callback

        self.cap = None
        self.is_running = False
        self.captured_frame = None
        self.saved_photo_path = None

        self._create_widgets()
        self._start_camera()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, height=50)
        header_frame.pack(fill="x")
        header_label = tk.Label(
            header_frame,
            text="Facial Image Capture",
            font=config.FONT_SUBTITLE,
            bg=config.COLOR_PRIMARY,
            fg="white"
        )
        header_label.pack(pady=10)

        # Video Display Container
        self.video_container = tk.Frame(
            self,
            bg="black",
            width=640,
            height=400,
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=2
        )
        self.video_container.pack(pady=15)
        self.video_container.pack_propagate(False)

        self.video_label = tk.Label(self.video_container, bg="black")
        self.video_label.pack(fill="both", expand=True)

        # Instruction & Status Label
        self.status_label = tk.Label(
            self,
            text="Position your face inside the camera frame...",
            font=config.FONT_BODY,
            bg=config.COLOR_BACKGROUND,
            fg=config.COLOR_DARK_TEXT
        )
        self.status_label.pack(pady=2)

        # Action Control Panel
        control_frame = tk.Frame(self, bg=config.COLOR_BACKGROUND)
        control_frame.pack(pady=10)

        self.btn_capture = tk.Button(
            control_frame,
            text="📷 Capture Photo",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.capture_photo
        )
        self.btn_capture.grid(row=0, column=0, padx=10)

        self.btn_recapture = tk.Button(
            control_frame,
            text="🔄 Recapture",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_MUTED_TEXT,
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.recapture_photo,
            state="disabled"
        )
        self.btn_recapture.grid(row=0, column=1, padx=10)

        self.btn_upload = tk.Button(
            control_frame,
            text="📁 Upload Image File",
            font=config.FONT_BODY_BOLD,
            bg="#475569",
            fg="white",
            activebackground="#334155",
            activeforeground="white",
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.upload_file
        )
        self.btn_upload.grid(row=0, column=2, padx=10)

        self.btn_save = tk.Button(
            control_frame,
            text="✅ Confirm & Save",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            padx=15,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.confirm_save,
            state="disabled"
        )
        self.btn_save.grid(row=0, column=3, padx=10)

    def _start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Unable to access webcam device.")
            self.is_running = True
            self.update_video_feed()
        except Exception as e:
            self.video_label.config(
                text=f"⚠️ Camera Unavailable\n\n({str(e)})\n\nPlease click 'Upload Image File' below to load a photo.",
                fg="white",
                font=config.FONT_BODY_BOLD
            )

    def update_video_feed(self):
        if not self.is_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # Flip horizontally for mirrored preview
            frame = cv2.flip(frame, 1)
            self.current_raw_frame = frame.copy()

            display_frame = frame.copy()
            faces = detect_faces(display_frame)

            # Draw bounding box for detected faces
            if len(faces) == 1:
                x, y, w, h = faces[0]
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face Detected", (x, max(20, y - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                self.status_label.config(text="✅ Ready! Face detected. Click 'Capture Photo'.", fg=config.COLOR_SUCCESS)
            elif len(faces) > 1:
                for (x, y, w, h) in faces:
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                self.status_label.config(text="⚠️ Multiple faces detected. Ensure only one person is in frame.", fg=config.COLOR_WARNING)
            else:
                self.status_label.config(text="👤 Position face in the center of camera...", fg=config.COLOR_MUTED_TEXT)

            img_tk = cv2_to_photoimage(display_frame, 640, 400)
            self.video_label.img_tk = img_tk
            self.video_label.config(image=img_tk, text="")

        self.after(30, self.update_video_feed)

    def capture_photo(self):
        if hasattr(self, 'current_raw_frame') and self.current_raw_frame is not None:
            faces = detect_faces(self.current_raw_frame)
            if len(faces) == 0:
                messagebox.showwarning("Face Detection Warning", "No face detected in the current frame! Please center your face before capturing.")
            elif len(faces) > 1:
                messagebox.showwarning("Face Detection Warning", "Multiple faces detected! Please ensure only one person is visible.")

            self.captured_frame = self.current_raw_frame.copy()
            self.is_running = False

            # Freeze preview frame with green overlay box
            preview_frame = self.captured_frame.copy()
            if len(faces) == 1:
                x, y, w, h = faces[0]
                cv2.rectangle(preview_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            img_tk = cv2_to_photoimage(preview_frame, 640, 400)
            self.video_label.img_tk = img_tk
            self.video_label.config(image=img_tk)

            self.btn_capture.config(state="disabled")
            self.btn_recapture.config(state="normal")
            self.btn_save.config(state="normal")
            self.status_label.config(text="📸 Photo Captured! Click 'Confirm & Save' or 'Recapture'.", fg=config.COLOR_PRIMARY)
        else:
            messagebox.showerror("Error", "No camera frame available to capture.")

    def recapture_photo(self):
        self.captured_frame = None
        self.btn_capture.config(state="normal")
        self.btn_recapture.config(state="disabled")
        self.btn_save.config(state="disabled")

        if self.cap and self.cap.isOpened():
            self.is_running = True
            self.update_video_feed()
        else:
            self._start_camera()

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Face Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        cv_img = cv2.imread(file_path)
        if cv_img is None:
            messagebox.showerror("File Error", "Failed to load selected image file.")
            return

        self.captured_frame = cv_img.copy()
        self.is_running = False

        faces = detect_faces(cv_img)
        preview_frame = cv_img.copy()
        if len(faces) >= 1:
            x, y, w, h = faces[0]
            cv2.rectangle(preview_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        img_tk = cv2_to_photoimage(preview_frame, 640, 400)
        self.video_label.img_tk = img_tk
        self.video_label.config(image=img_tk, text="")

        self.btn_capture.config(state="disabled")
        self.btn_recapture.config(state="normal")
        self.btn_save.config(state="normal")
        self.status_label.config(text=f"📁 Loaded image from: {os.path.basename(file_path)}", fg=config.COLOR_PRIMARY)

    def confirm_save(self):
        if self.captured_frame is None:
            messagebox.showerror("Save Error", "No photo captured or selected.")
            return

        # Save photo into images/citizen_photos/<citizen_id>.jpg
        filename = f"{self.citizen_id}.jpg"
        save_path = os.path.join(config.IMAGES_DIR, filename)

        cv2.imwrite(save_path, self.captured_frame)
        self.saved_photo_path = save_path

        if self.on_captured_callback:
            self.on_captured_callback(save_path)

        messagebox.showinfo("Success", f"Facial image saved successfully:\n{filename}")
        self.on_close()

    def on_close(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.destroy()
