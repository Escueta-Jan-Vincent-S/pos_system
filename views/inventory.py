import customtkinter as ctk
from controllers import controller
from controllers.inventory_controller import on_add_item, on_delete_item

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        self.selected_barcode = None
        self.selected_row_labels = []

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#f0f0f0",
            font=ctk.CTkFont(size=40, weight="bold"),
            corner_radius=0, width=60, height=60,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text="INVENTORY / ITEM MASTERLIST (THE DATA BASE)",
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

        columns = ["Barcode", "Item Name", "Category", "Unit\nCost",
                   "Selling\nPrice", "Demand", "Current\nStock", "Classification"]

        header_row = ctk.CTkFrame(table_frame, fg_color="#000000", corner_radius=0)
        header_row.pack(fill="x")

        for i, col in enumerate(columns):
            header_row.grid_columnconfigure(i, weight=1, uniform="col")
            ctk.CTkLabel(
                header_row, text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white", justify="center"
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=12)

        self.rows_frame = ctk.CTkScrollableFrame(
            table_frame, fg_color="#ffffff", corner_radius=0)
        self.rows_frame.pack(fill="both", expand=True)

        for i in range(len(columns)):
            self.rows_frame.grid_columnconfigure(i, weight=1, uniform="col")

        self.load_items()

        # ── Bottom Buttons ────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        btn_frame.pack(fill="x", padx=10, pady=10)
        btn_frame.pack_propagate(False)

        left_btns = ctk.CTkFrame(btn_frame, fg_color="#ffffff", corner_radius=0)
        left_btns.pack(side="left")

        btn_configs = [
            ("ADD ITEM",      "#90EE90", "#000000", lambda: self.open_add_item()),
            ("REORDER TABLE", "#90EE90", "#000000", lambda: print("REORDER clicked")),
            ("EDIT ITEM",     "#d3d3d3", "#000000", lambda: print("EDIT clicked")),
            ("DELETE ITEM",   "#FF4444", "#ffffff", lambda: self.open_delete_confirm()),
        ]

        for text, bg, fg, cmd in btn_configs:
            ctk.CTkButton(
                left_btns, text=text, fg_color=bg, text_color=fg,
                hover_color=bg, border_color="#000000", border_width=2,
                font=ctk.CTkFont(size=16, weight="bold"),
                corner_radius=0, width=200, height=60, command=cmd
            ).pack(side="left", padx=5)

        right_btns = ctk.CTkFrame(btn_frame, fg_color="#ffffff", corner_radius=0)
        right_btns.pack(side="right")

        ctk.CTkButton(
            right_btns, text="DAILY  ▼",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=150, height=40,
            command=lambda: print("DAILY clicked")
        ).pack(pady=2)

        ctk.CTkButton(
            right_btns, text="PRINT",
            fg_color="#FFD700", text_color="#000000",
            hover_color="#e6c200", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=150, height=40,
            command=lambda: print("PRINT clicked")
        ).pack(pady=2)

    def load_items(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.selected_barcode = None
        self.selected_row_labels = []

        from database.database import get_all_items
        items = get_all_items()

        for i, item in enumerate(items):
            bg = "#f0f0f0" if i % 2 == 0 else "#d3d3d3"
            barcode, item_name, category, unit_cost, selling_price, current_stock = item
            row_data = [barcode, item_name, category, unit_cost, selling_price, "", current_stock, ""]

            row_labels = []
            for j, val in enumerate(row_data):
                lbl = ctk.CTkLabel(
                    self.rows_frame,
                    text=str(val),
                    font=ctk.CTkFont(size=12),
                    text_color="#000000",
                    justify="center",
                    fg_color=bg,
                    cursor="hand2"
                )
                lbl.grid(row=i, column=j, sticky="nsew", padx=1, pady=10)
                lbl.bind("<Button-1>", lambda e, b=barcode, rl=row_labels: self.select_row(b, rl))
                row_labels.append(lbl)

            self.selected_row_labels.append((barcode, row_labels, bg))

    def select_row(self, barcode, row_labels):
        # Reset all rows
        for b, labels, orig_bg in self.selected_row_labels:
            for lbl in labels:
                lbl.configure(fg_color=orig_bg)

        # Highlight selected row
        for lbl in row_labels:
            lbl.configure(fg_color="#00BFFF")

        self.selected_barcode = barcode

    def open_add_item(self):
        from database.database import get_next_barcode
        popup = ctk.CTkToplevel(self)
        popup.title("Add Item")
        popup.geometry("500x550")
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup, text="ADD ITEM",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        ctk.CTkLabel(popup, text=f"Barcode: {get_next_barcode()}",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30)

        fields = ["Item Name", "Category", "Unit Cost", "Selling Price", "Current Stock"]
        entries = {}

        for field in fields:
            ctk.CTkLabel(popup, text=field,
                font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
            entry = ctk.CTkEntry(popup, width=440, height=35)
            entry.pack(padx=30)
            entries[field] = entry

        def save():
            on_add_item(
                entries["Item Name"].get(),
                entries["Category"].get(),
                entries["Unit Cost"].get(),
                entries["Selling Price"].get(),
                entries["Current Stock"].get(),
            )
            popup.destroy()
            self.load_items()

        ctk.CTkButton(popup, text="SAVE",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=440, height=45,
            command=save
        ).pack(padx=30, pady=20)

    def open_delete_confirm(self):
        if not self.selected_barcode:
            popup = ctk.CTkToplevel(self)
            popup.title("Warning")
            popup.geometry("300x150")
            popup.resizable(False, False)
            popup.grab_set()

            ctk.CTkLabel(popup, text="Please select an item first!",
                font=ctk.CTkFont(size=14)).pack(expand=True)
            ctk.CTkButton(popup, text="OK", command=popup.destroy,
                fg_color="#d3d3d3", text_color="#000000",
                corner_radius=0, width=100).pack(pady=10)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Delete Item")
        popup.geometry("350x180")
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup,
            text=f"Are you sure you want to\ndelete barcode {self.selected_barcode}?",
            font=ctk.CTkFont(size=14), justify="center").pack(expand=True, pady=20)

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=10)

        def confirm_delete():
            on_delete_item(self.selected_barcode)
            popup.destroy()
            self.load_items()

        ctk.CTkButton(btn_row, text="YES",
            fg_color="#FF4444", text_color="#ffffff",
            hover_color="#cc0000", corner_radius=0,
            width=120, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=confirm_delete
        ).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="NO",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", corner_radius=0,
            width=120, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=popup.destroy
        ).pack(side="left", padx=10)