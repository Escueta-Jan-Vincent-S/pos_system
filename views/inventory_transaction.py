import customtkinter as ctk
from controllers import controller

class InventoryTransactionPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        header = ctk.CTkFrame(self, fg_color="#FFD700", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#e6c200",
            font=ctk.CTkFont(size=70, weight="bold"),
            corner_radius=0, width=50, height=50,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="INVENTORY TRANSACTION ENTRY",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)