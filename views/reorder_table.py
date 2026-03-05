import customtkinter as ctk
from controllers import controller
from database.database import get_all_items

class ReorderTablePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#f0f0f0",
            font=ctk.CTkFont(size=40, weight="bold"),
            corner_radius=0, width=60, height=60,
            command=lambda: controller.navigate("inventory")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text="REORDER TABLE",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Table ────────────────────────────────────────────
        table_frame = ctk.CTkFrame(body, fg_color="#000000", corner_radius=0)
        table_frame.pack(fill="both", expand=True)

        columns = ["Item Code", "Item Name", "Category", "MIN", "MAX", "Status"]

        header_row = ctk.CTkFrame(table_frame, fg_color="#000000", corner_radius=0)
        header_row.pack(fill="x")

        for i, col in enumerate(columns):
            header_row.grid_columnconfigure(i, weight=1, uniform="col")
            ctk.CTkLabel(
                header_row, text=col,
                font=ctk.CTkFont(size=25, weight="bold"),
                text_color="white", justify="center"
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=12)

        self.rows_frame = ctk.CTkScrollableFrame(
            table_frame, fg_color="#ffffff", corner_radius=0)
        self.rows_frame.pack(fill="both", expand=True)

        for i in range(len(columns)):
            self.rows_frame.grid_columnconfigure(i, weight=1, uniform="col")

        self.load_items()

        # ── Bottom Button ────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        btn_frame.pack(fill="x", padx=10, pady=10)
        btn_frame.pack_propagate(False)

        ctk.CTkButton(
            btn_frame, text="GENERATE REORDER POINT",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=30, weight="bold"),
            corner_radius=0, width=400, height=60,
            command=lambda: controller.navigate("reorder_computation")
        ).pack(side="left", padx=5)

    def load_items(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        items = get_all_items()

        for i, item in enumerate(items):
            bg = "#f0f0f0" if i % 2 == 0 else "#d3d3d3"
            barcode, item_name, category, unit_cost, selling_price, current_stock = item
            row_data = [barcode, item_name, category, "", "", ""]

            for j, val in enumerate(row_data):
                ctk.CTkLabel(
                    self.rows_frame,
                    text=str(val),
                    font=ctk.CTkFont(size=18),
                    text_color="#000000",
                    justify="center",
                    fg_color=bg
                ).grid(row=i, column=j, sticky="nsew", padx=1, pady=10)