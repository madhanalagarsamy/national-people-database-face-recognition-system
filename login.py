import tkinter as tk
from tkinter import messagebox
import config
import database

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success

        self.root.title(config.APP_TITLE + " - Authentication")
        self.root.geometry(config.WINDOW_SIZE)
        self.root.resizable(config.IS_RESIZABLE, config.IS_RESIZABLE)
        self.root.configure(bg=config.COLOR_BACKGROUND)

        self._center_window()
        self._create_widgets()

    def _center_window(self):
        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        # Outer Layout Container
        main_container = tk.Frame(self.root, bg=config.COLOR_BACKGROUND)
        main_container.pack(expand=True)

        # Login Card Panel
        card = tk.Frame(
            main_container,
            bg=config.COLOR_CARD_BG,
            padx=45,
            pady=40,
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1
        )
        card.pack()

        # Application Header Banner
        header = tk.Label(
            card,
            text="🏛️ National People Database",
            font=(config.FONT_FAMILY, 20, "bold"),
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_PRIMARY
        )
        header.pack(pady=(0, 4))

        sub_header = tk.Label(
            card,
            text="Biometric Identity Verification System",
            font=config.FONT_BODY,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_MUTED_TEXT
        )
        sub_header.pack(pady=(0, 25))

        # Divider
        tk.Frame(card, bg=config.COLOR_BORDER, height=1).pack(fill="x", pady=(0, 25))

        # Form Inputs Container
        form_frame = tk.Frame(card, bg=config.COLOR_CARD_BG)
        form_frame.pack()

        # Username Input
        lbl_user = tk.Label(
            form_frame,
            text="Username",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_DARK_TEXT,
            anchor="w"
        )
        lbl_user.pack(fill="x", pady=(0, 5))

        self.entry_user = tk.Entry(
            form_frame,
            font=(config.FONT_FAMILY, 11),
            bg=config.COLOR_SECONDARY,
            fg=config.COLOR_DARK_TEXT,
            relief="flat",
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1,
            width=32
        )
        self.entry_user.pack(ipady=8, pady=(0, 15))
        self.entry_user.insert(0, "admin")  # Pre-fill default

        # Password Input
        lbl_pass = tk.Label(
            form_frame,
            text="Password",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_DARK_TEXT,
            anchor="w"
        )
        lbl_pass.pack(fill="x", pady=(0, 5))

        pass_row = tk.Frame(form_frame, bg=config.COLOR_CARD_BG)
        pass_row.pack(fill="x", pady=(0, 20))

        self.entry_pass = tk.Entry(
            pass_row,
            font=(config.FONT_FAMILY, 11),
            bg=config.COLOR_SECONDARY,
            fg=config.COLOR_DARK_TEXT,
            show="•",
            relief="flat",
            highlightbackground=config.COLOR_BORDER,
            highlightthickness=1,
            width=26
        )
        self.entry_pass.pack(side="left", ipady=8)
        self.entry_pass.insert(0, "admin123")  # Pre-fill default

        self.show_pass_var = tk.BooleanVar(value=False)
        btn_show = tk.Checkbutton(
            pass_row,
            text="Show",
            variable=self.show_pass_var,
            command=self._toggle_password,
            bg=config.COLOR_CARD_BG,
            font=config.FONT_SMALL,
            activebackground=config.COLOR_CARD_BG,
            cursor="hand2"
        )
        btn_show.pack(side="right", padx=(8, 0))

        # Login Action Button
        btn_login = tk.Button(
            form_frame,
            text="Sign In to System",
            font=config.FONT_BODY_BOLD,
            bg=config.COLOR_PRIMARY,
            fg="white",
            activebackground=config.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=10,
            command=self.handle_login
        )
        btn_login.pack(fill="x", pady=(10, 15))

        # Bind Return key to login action
        self.root.bind('<Return>', lambda event: self.handle_login())

        # Demo Credentials Hint Footer
        hint_box = tk.Label(
            card,
            text="💡 Default Admin Login:\nUsername: admin  |  Password: admin123",
            font=config.FONT_SMALL,
            bg="#EFF6FF",
            fg=config.COLOR_PRIMARY,
            padx=15,
            pady=8,
            justify="center"
        )
        hint_box.pack(fill="x", pady=(10, 0))

    def _toggle_password(self):
        if self.show_pass_var.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="•")

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Authentication Warning", "Please enter both username and password.")
            return

        if database.login(username, password):
            messagebox.showinfo("Login Success", f"Welcome back, {username}!")
            self.on_login_success(username)
        else:
            messagebox.showerror("Authentication Failed", "Invalid username or password. Please try again.")
