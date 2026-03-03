# ============================================================
# DASHBOARD WINDOW
# ============================================================

import customtkinter as ctk
from settings import APP_NAME

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.attributes("-fullscreen", True)

        ctk.set_appearance_mode("light")

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#000000", height=100, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="INVENTORY MANAGEMENT SYSTEM",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20, pady=10)

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = ctk.CTkFrame(body, fg_color="#ffffff", width=500, corner_radius=0)
        sidebar.pack(fill="y", side="left", padx=20, pady=20)
        sidebar.pack_propagate(False)

        buttons = [
            ("INVENTORY",                    "#ffffff", "#000000", 50),
            ("SELL",                         "#90EE90", "#000000", 50),
            ("RECEIPTS",                     "#00BFFF", "#000000", 50),
            ("INVENTORY\nTRANSACTION ENTRY", "#FFD700", "#000000", 30),
            ("USER",                         "#d3d3d3", "#000000", 50),
            ("LOG OUT",                      "#FF4444", "#000000", 50),
        ]

        for text, bg, fg, fsize in buttons:
            ctk.CTkButton(
                sidebar,
                text=text,
                fg_color=bg,
                text_color=fg,
                hover_color=bg,
                border_color="#000000",
                border_width=2,
                font=ctk.CTkFont(size=fsize, weight="bold"),
                corner_radius=0,
                height=150,
            ).pack(fill="x", pady=6)

def open_window():
    app = Dashboard()
    app.mainloop()

def open_window():
    app = Dashboard()
    app.mainloop()