import customtkinter as ctk
from controllers import controller
from controllers.user_controller import get_accounts, on_switch_account

class UserPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#808080", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#707070",
            font=ctk.CTkFont(size=70, weight="bold"),
            corner_radius=0, width=50, height=50,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

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

        self.load_accounts()

    def load_accounts(self):
        # Clear list
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

            # Admin label
            # Role label
            if role == "admin":
                ctk.CTkLabel(
                    row, text="ADMIN",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color="#90EE90"
                ).pack(side="right", padx=10)
            else:
                ctk.CTkLabel(
                    row, text="GUEST",
                    font=ctk.CTkFont(size=30, weight="bold"),
                    text_color="#808080"
                ).pack(side="right", padx=10)

            # Current or Switch button
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
                    command=lambda aid=account_id: on_switch_account(aid, self.load_accounts)
                ).pack(side="right", padx=120)