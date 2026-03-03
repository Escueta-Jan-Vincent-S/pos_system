import customtkinter as ctk
from controllers import controller

class SellPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        header = ctk.CTkFrame(self, fg_color="#90EE90", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#7dd67d",
            font=ctk.CTkFont(size=70, weight="bold"),
            corner_radius=0, width=50, height=50,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="SELL",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)