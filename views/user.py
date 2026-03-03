import customtkinter as ctk
from controllers.user_controller import on_back_click

class UserPage(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # Header
        header = ctk.CTkFrame(self, fg_color="#808080", height=150, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="USER",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="white"
        ).pack(expand=True)

        ctk.CTkButton(
            header,
            text="BACK",
            fg_color="#ffffff",
            text_color="#000000",
            hover_color="#d3d3d3",
            border_color="#000000",
            border_width=2,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=0,
            width=100,
            height=50,
            command=lambda: on_back_click(dashboard)
        ).place(relx=1.0, rely=0.5, anchor="e", x=-20)

        # Body
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)