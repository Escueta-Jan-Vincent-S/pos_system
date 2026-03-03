import customtkinter as ctk
from controllers.user_controller import on_back_click

class UserPage(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#808080", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header,
            text="<",
            fg_color="transparent",
            text_color="#000000",
            hover_color="#707070",
            font=ctk.CTkFont(size=70, weight="bold"),
            corner_radius=0,
            width=50,
            height=50,
            command=lambda: on_back_click(dashboard)
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text="USER",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)