import customtkinter as ctk
from controllers import controller
from controllers.user_controller import get_accounts, on_switch_account
import os, sys

def _get_config_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "config.ini")

def _load_password():
    path = _get_config_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if line.startswith("admin_password="):
                    return line.strip().split("=", 1)[1]
    return "pogiako123"

def _save_password(new_pw):
    path = _get_config_path()
    with open(path, "w") as f:
        f.write(f"admin_password={new_pw}\n")

ADMIN_PASSWORD = _load_password()


class UserPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#808080", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        self.back_btn = ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#707070",
            font=ctk.CTkFont(size=70, weight="bold"),
            corner_radius=0, width=50, height=50,
            command=lambda: controller.navigate("dashboard")
        )
        self.back_btn.pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="USER",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── Body ─────────────────────────────────────────────
        self.body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.body.pack(fill="both", expand=True)

        # ── Change User Card ─────────────────────────────────
        card = ctk.CTkFrame(self.body, fg_color="#ffffff", corner_radius=0,
                            border_color="#000000", border_width=1, width=1280, height=720)
        card.place(relx=0.5, rely=0.4, anchor="center")
        card.pack_propagate(False)

        # Card header
        card_header = ctk.CTkFrame(card, fg_color="#d3d3d3", height=50, corner_radius=0)
        card_header.pack(fill="x")
        card_header.pack_propagate(False)
        ctk.CTkLabel(
            card_header, text="CHANGE USER",
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color="#000000"
        ).pack(expand=True)

        # Account list
        self.account_list = ctk.CTkFrame(card, fg_color="#ffffff", corner_radius=0)
        self.account_list.pack(fill="x", padx=20, pady=10)

        # Change password button
        ctk.CTkFrame(card, fg_color="#e0e0e0", height=1, corner_radius=0).pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkButton(
            card, text="🔑  Change Admin Password",
            fg_color="transparent", text_color="#555555",
            hover_color="#f0f0f0",
            font=ctk.CTkFont(size=18),
            corner_radius=0, height=45,
            command=self._show_change_password
        ).pack(fill="x", padx=20, pady=5)

        self.load_accounts()

    def load_accounts(self):
        # Alias for show_page compatibility
        for widget in self.account_list.winfo_children():
            widget.destroy()

        accounts = get_accounts()
        for account_id, email, role, is_current in accounts:
            row = ctk.CTkFrame(self.account_list, fg_color="#ffffff", corner_radius=0)
            row.pack(fill="x", pady=5)

            # Email
            ctk.CTkLabel(
                row, text=email,
                font=ctk.CTkFont(size=30),
                text_color="#000000"
            ).pack(side="left")

            # Role label
            if role == "admin":
                ctk.CTkLabel(
                    row, text="ADMIN",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color="#90EE90"
                ).pack(side="right", padx=10)
            else:
                ctk.CTkLabel(
                    row, text="STAFF",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color="#808080"
                ).pack(side="right", padx=10)

            # Current label or Login button
            if is_current:
                ctk.CTkLabel(
                    row, text="Current",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color="#FF4444"
                ).pack(side="right", padx=120)
            else:
                ctk.CTkButton(
                    row, text="Log in",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    fg_color="transparent",
                    text_color="#000000",
                    hover_color="#f0f0f0",
                    width=60,
                    command=lambda aid=account_id, r=role: self._handle_login(aid, r)
                ).pack(side="right", padx=120)

    # Alias so show_page() triggers a refresh
    def load_items(self):
        self.load_accounts()

    # ── Login logic ──────────────────────────────────────────
    def _handle_login(self, account_id, role):
        if role == "admin":
            self._show_password_popup(account_id)
        else:
            # Staff — direct login, no password
            self._complete_login(account_id, "staff")

    def _show_password_popup(self, account_id):
        popup = ctk.CTkToplevel(self)
        popup.title("Admin Login")
        popup.geometry("420x280")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(
            popup, text="👑  ADMIN LOGIN",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#000000"
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            popup, text="Enter password to continue:",
            font=ctk.CTkFont(size=15),
            text_color="#555555"
        ).pack()

        pw_entry = ctk.CTkEntry(
            popup, width=300, height=45,
            font=ctk.CTkFont(size=18),
            show="●", placeholder_text="Password"
        )
        pw_entry.pack(pady=15)
        pw_entry.focus()

        error_label = ctk.CTkLabel(
            popup, text="",
            font=ctk.CTkFont(size=13),
            text_color="#FF4444"
        )
        error_label.pack()

        def attempt_login(event=None):
            entered = pw_entry.get()
            if entered == ADMIN_PASSWORD:
                popup.destroy()
                self._complete_login(account_id, "admin")
            else:
                error_label.configure(text="❌  Incorrect password. Try again.")
                pw_entry.delete(0, "end")
                pw_entry.focus()

        pw_entry.bind("<Return>", attempt_login)

        ctk.CTkButton(
            popup, text="LOGIN",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=300, height=45,
            command=attempt_login
        ).pack(pady=(5, 0))

    def _complete_login(self, account_id, role):
        # Update DB current account
        on_switch_account(account_id, self.load_accounts)

        # Set role in controller
        controller.set_role(role)

        # Navigate to dashboard and refresh its role UI
        controller.navigate("dashboard")

    # ── Change Password ──────────────────────────────────────
    def _show_change_password(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Change Admin Password")
        popup.geometry("420x420")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="🔑  CHANGE ADMIN PASSWORD",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=(25, 5))

        ctk.CTkLabel(popup, text="Enter current password first to confirm.",
            font=ctk.CTkFont(size=13), text_color="#555555"
        ).pack(pady=(0, 15))

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(padx=30, fill="x")

        ctk.CTkLabel(form, text="Current Password",
            font=ctk.CTkFont(size=13), text_color="#000000", anchor="w"
        ).pack(fill="x", pady=(0, 2))
        current_entry = ctk.CTkEntry(form, width=360, height=38,
            font=ctk.CTkFont(size=15), show="●")
        current_entry.pack(fill="x")

        ctk.CTkLabel(form, text="New Password",
            font=ctk.CTkFont(size=13), text_color="#000000", anchor="w"
        ).pack(fill="x", pady=(12, 2))
        new_entry = ctk.CTkEntry(form, width=360, height=38,
            font=ctk.CTkFont(size=15), show="●")
        new_entry.pack(fill="x")

        ctk.CTkLabel(form, text="Confirm New Password",
            font=ctk.CTkFont(size=13), text_color="#000000", anchor="w"
        ).pack(fill="x", pady=(12, 2))
        confirm_entry = ctk.CTkEntry(form, width=360, height=38,
            font=ctk.CTkFont(size=15), show="●")
        confirm_entry.pack(fill="x")

        error_label = ctk.CTkLabel(popup, text="",
            font=ctk.CTkFont(size=13), text_color="#FF4444"
        )
        error_label.pack(pady=(8, 0))

        def save():
            global ADMIN_PASSWORD
            current = current_entry.get()
            new_pw  = new_entry.get()
            confirm = confirm_entry.get()

            if current != ADMIN_PASSWORD:
                error_label.configure(text="❌ Current password is incorrect.")
                return
            if not new_pw:
                error_label.configure(text="❌ New password cannot be empty.")
                return
            if new_pw != confirm:
                error_label.configure(text="❌ New passwords do not match.")
                return

            ADMIN_PASSWORD = new_pw
            _save_password(new_pw)
            popup.destroy()

            done = ctk.CTkToplevel(self)
            done.title("Success")
            done.geometry("320x140")
            done.resizable(False, False)
            done.grab_set()
            done.lift()
            ctk.CTkLabel(done, text="✅ Password changed successfully!",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#000000"
            ).pack(expand=True)
            ctk.CTkButton(done, text="OK", command=done.destroy,
                fg_color="#90EE90", text_color="#000000",
                corner_radius=0, width=100
            ).pack(pady=10)

        ctk.CTkButton(popup, text="SAVE NEW PASSWORD",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=0, width=360, height=42,
            command=save
        ).pack(padx=30, pady=(5, 0))