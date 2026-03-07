import customtkinter as ctk
from controllers import controller
from controllers.inventory_controller import on_add_item, on_delete_item, on_edit_item
import controllers.controller as c

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        self.selected_barcode = None
        self.selected_row_labels = []
        self.cart = []

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
            text="INVENTORY / ITEM",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Search bar on the right of header
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right", padx=15)

        ctk.CTkLabel(search_frame, text="🔍",
            font=ctk.CTkFont(size=18),
            text_color="#000000"
        ).pack(side="left", padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Search name, category, barcode...",
            width=280, height=38, font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_items())

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Main area (table + cart side by side) ────────────
        main = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Table (left) ─────────────────────────────────────
        table_frame = ctk.CTkFrame(main, fg_color="#000000", corner_radius=0)
        table_frame.pack(fill="both", expand=True, side="left")

        columns = ["Barcode", "Item Name", "Category", "Unit Cost",
                   "Selling Price", "Demand", "Current Stock", "Classification"]

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

        # ── Cart Panel (right) ────────────────────────────────
        cart_panel = ctk.CTkFrame(main, fg_color="#f9f9f9", corner_radius=0,
                                   border_color="#000000", border_width=1, width=400)
        cart_panel.pack(fill="y", side="right", padx=(10, 0))
        cart_panel.pack_propagate(False)

        ctk.CTkLabel(cart_panel, text="CART",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#000000"
        ).pack(pady=10)

        ctk.CTkFrame(cart_panel, fg_color="#000000", height=1, corner_radius=0).pack(fill="x")

        # Quantity input
        qty_frame = ctk.CTkFrame(cart_panel, fg_color="#f9f9f9", corner_radius=0)
        qty_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(qty_frame, text="Quantity:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#000000"
        ).pack(side="left")

        self.qty_entry = ctk.CTkEntry(qty_frame, width=100, height=35,
                                       font=ctk.CTkFont(size=16))
        self.qty_entry.pack(side="left", padx=10)
        self.qty_entry.insert(0, "1")

        ctk.CTkButton(
            cart_panel, text="ADD TO CART",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, height=40,
            command=self.add_to_cart
        ).pack(fill="x", padx=10, pady=5)

        # Cart items list
        self.cart_frame = ctk.CTkScrollableFrame(
            cart_panel, fg_color="#ffffff", corner_radius=0)
        self.cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Total
        ctk.CTkFrame(cart_panel, fg_color="#000000", height=1, corner_radius=0).pack(fill="x")
        self.total_label = ctk.CTkLabel(cart_panel, text="TOTAL: ₱0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        )
        self.total_label.pack(pady=5)

        # Clear + Print buttons
        ctk.CTkButton(
            cart_panel, text="CLEAR CART",
            fg_color="#FF4444", text_color="#ffffff",
            hover_color="#cc0000", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, height=40,
            command=self.clear_cart
        ).pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(
            cart_panel, text="PRINT RECEIPT",
            fg_color="#FFD700", text_color="#000000",
            hover_color="#e6c200", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, height=45,
            command=self.go_to_receipt
        ).pack(fill="x", padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        btn_frame.pack(fill="x", padx=10, pady=10)
        btn_frame.pack_propagate(False)

        btn_configs = [
            ("ADD ITEM",      "#90EE90", "#000000", "#7dd67d", lambda: self.open_add_item()),
            ("REORDER TABLE", "#90EE90", "#000000", "#7dd67d", lambda: controller.navigate("reorder_table")),
            ("EDIT ITEM",     "#d3d3d3", "#000000", "#c0c0c0", lambda: self.open_edit_item()),
            ("DELETE ITEM",   "#FF4444", "#ffffff", "#cc0000", lambda: self.open_delete_confirm()),
        ]

        for text, bg, fg, hover, cmd in btn_configs:
            ctk.CTkButton(
                btn_frame, text=text, fg_color=bg, text_color=fg,
                hover_color=hover, border_color="#000000", border_width=2,
                font=ctk.CTkFont(size=26, weight="bold"),
                corner_radius=0, height=60, command=cmd
            ).pack(side="left", padx=5, expand=True, fill="x")

        # DAILY dropdown — right side
        self.daily_var = ctk.StringVar(value="DAILY  ▼")
        ctk.CTkOptionMenu(
            btn_frame,
            variable=self.daily_var,
            values=["Daily", "Weekly", "Monthly", "Annually"],
            command=self._on_daily_select,
            fg_color="#d3d3d3", text_color="#000000",
            button_color="#c0c0c0", button_hover_color="#aaaaaa",
            dropdown_fg_color="#ffffff", dropdown_text_color="#000000",
            font=ctk.CTkFont(size=22, weight="bold"),
            width=200, height=60
        ).pack(side="left", padx=5)

    def load_items(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.selected_barcode = None
        self.selected_row_labels = []

        from database.database import get_all_items
        items = get_all_items()

        # Filter by search query
        query = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        if query:
            items = [i for i in items if
                     query in str(i[0]).lower() or  # barcode
                     query in str(i[1]).lower() or  # item_name
                     query in str(i[2]).lower()]     # category

        for i, item in enumerate(items):
            bg = "#f0f0f0" if i % 2 == 0 else "#d3d3d3"
            barcode, item_name, category, unit_cost, selling_price, current_stock, weekly_demand, classification, status = item

            cls_colors = {"A": "#90EE90", "B": "#00BFFF", "C": "#FFD700"}
            cls_bg = cls_colors.get(classification, bg)

            row_data = [barcode, item_name, category, unit_cost, selling_price, weekly_demand, current_stock, classification]
            row_colors = [bg, bg, bg, bg, bg, bg, bg, cls_bg]

            row_labels = []
            for j, (val, cell_bg) in enumerate(zip(row_data, row_colors)):
                lbl = ctk.CTkLabel(
                    self.rows_frame,
                    text=str(val),
                    font=ctk.CTkFont(size=18),
                    text_color="#000000",
                    justify="center",
                    fg_color=cell_bg,
                    cursor="hand2"
                )
                lbl.grid(row=i, column=j, sticky="nsew", padx=1, pady=10)
                lbl.bind("<Button-1>", lambda e, b=barcode, rl=row_labels: self.select_row(b, rl))
                row_labels.append(lbl)

            self.selected_row_labels.append((barcode, row_labels, bg))

    def select_row(self, barcode, row_labels):
        for b, labels, orig_bg in self.selected_row_labels:
            for lbl in labels:
                lbl.configure(fg_color=orig_bg)
        for lbl in row_labels:
            lbl.configure(fg_color="#00BFFF")
        self.selected_barcode = barcode

    def add_to_cart(self):
        if not self.selected_barcode:
            self._warning("Please select an item first!")
            return

        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            self._warning("Please enter a valid quantity!")
            return

        from database.database import get_item_by_barcode
        item = get_item_by_barcode(self.selected_barcode)
        barcode       = item[1]
        item_name     = item[2]
        selling_price = float(item[5])

        # If already in cart, add quantity
        for cart_item in self.cart:
            if cart_item["barcode"] == barcode:
                cart_item["quantity"] += qty
                self.refresh_cart()
                return

        self.cart.append({
            "barcode": barcode,
            "item_name": item_name,
            "selling_price": selling_price,
            "quantity": qty
        })
        self.refresh_cart()

    def refresh_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        total = 0
        for idx, item in enumerate(self.cart):
            amount = item["selling_price"] * item["quantity"]
            total += amount

            row = ctk.CTkFrame(self.cart_frame, fg_color="#f0f0f0", corner_radius=0,
                                border_color="#d3d3d3", border_width=1)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row,
                text=f"{item['item_name']}\nx{item['quantity']} @ ₱{item['selling_price']:.2f}",
                font=ctk.CTkFont(size=12),
                text_color="#000000", justify="left"
            ).pack(side="left", padx=5)

            ctk.CTkLabel(row,
                text=f"₱{amount:.2f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#000000"
            ).pack(side="right", padx=5)

            ctk.CTkButton(row, text="✕",
                fg_color="transparent", text_color="#FF4444",
                hover_color="#f0f0f0", width=20,
                font=ctk.CTkFont(size=12),
                command=lambda i=idx: self.remove_from_cart(i)
            ).pack(side="right")

        self.total_label.configure(text=f"TOTAL: ₱{total:.2f}")

    def remove_from_cart(self, idx):
        self.cart.pop(idx)
        self.refresh_cart()

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()

    def go_to_receipt(self):
        if not self.cart:
            self._warning("Cart is empty!")
            return
        c._app.receipt_page.load_receipt(self.cart)
        controller.navigate("receipt")

    def _on_daily_select(self, timeframe):
        from database.database import update_weekly_demand_from_timeframe, update_all_classifications
        updated = update_weekly_demand_from_timeframe(timeframe)
        self.daily_var.set("DAILY  ▼")

        if updated == 0:
            self._warning(f"No sales data found for '{timeframe}'.\nMake sales first to track demand.")
            return

        # Re-run ABC classification based on new weekly_demand values
        update_all_classifications()

        # Refresh table
        self.load_items()

        # Show confirmation
        popup = ctk.CTkToplevel(self)
        popup.title("Demand Updated")
        popup.geometry("380x160")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()
        ctk.CTkLabel(popup,
            text=f"✅ {timeframe} demand updated!\n{updated} item(s) weekly demand refreshed.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000", justify="center"
        ).pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy,
            fg_color="#90EE90", text_color="#000000",
            corner_radius=0, width=100
        ).pack(pady=10)

    def _warning(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("Warning")
        popup.geometry("300x150")
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=message,
            font=ctk.CTkFont(size=14)).pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)

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

    def open_edit_item(self):
        if not self.selected_barcode:
            self._warning("Please select an item first!")
            return

        from database.database import get_item_by_barcode
        item = get_item_by_barcode(self.selected_barcode)

        popup = ctk.CTkToplevel(self)
        popup.title("Edit Item")
        popup.geometry("500x550")
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup, text="EDIT ITEM",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        ctk.CTkLabel(popup, text=f"Barcode: {item[1]}",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30)

        fields = ["Item Name", "Category", "Unit Cost", "Selling Price", "Current Stock"]
        prefill = [item[2], item[3], item[4], item[5], item[6]]
        entries = {}

        for field, value in zip(fields, prefill):
            ctk.CTkLabel(popup, text=field,
                font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
            entry = ctk.CTkEntry(popup, width=440, height=35)
            entry.insert(0, str(value) if value else "")
            entry.pack(padx=30)
            entries[field] = entry

        def save():
            on_edit_item(
                self.selected_barcode,
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
            self._warning("Please select an item first!")
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