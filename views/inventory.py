import customtkinter as ctk
from datetime import datetime, timedelta, date
from controllers import controller
from controllers.inventory_controller import on_add_item, on_delete_item, on_edit_item
import controllers.controller as c


class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        self.selected_barcode = None
        self.selected_row_labels = []
        self.cart = []

        # Date filter state — None means "All Time"
        self._filter_start = None
        self._filter_end = None
        self._filter_label_text = "ALL TIME"

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

        # ── Date of Records Banner ────────────────────────────
        self.date_banner = ctk.CTkFrame(self, fg_color="#f0f0f0", height=36, corner_radius=0)
        self.date_banner.pack(fill="x")
        self.date_banner.pack_propagate(False)

        self.date_record_label = ctk.CTkLabel(
            self.date_banner,
            text="DATE OF RECORDS:  ALL TIME",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        )
        self.date_record_label.pack(side="left", padx=20, pady=6)

        ctk.CTkFrame(self, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x")

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

        # ── Bottom Button Bar ─────────────────────────────────
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

        # DAILY ▼ → replaced with calendar date filter button
        ctk.CTkButton(
            btn_frame, text="📅 FILTER DATE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=22, weight="bold"),
            corner_radius=0, height=60, width=220,
            command=self._open_date_filter
        ).pack(side="left", padx=5)

    # ─────────────────────────────────────────────────────────
    # Date Filter Popup
    # ─────────────────────────────────────────────────────────
    def _open_date_filter(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Filter by Date")
        popup.geometry("420x520")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="📅  FILTER BY DATE",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=(15, 5))

        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=20)

        # ── Quick select buttons ──────────────────────────────
        quick_frame = ctk.CTkFrame(popup, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=12)

        today = date.today()

        def q(label, start, end):
            def _set():
                start_e.delete(0, "end"); start_e.insert(0, start.strftime("%Y-%m-%d"))
                end_e.delete(0, "end");   end_e.insert(0, end.strftime("%Y-%m-%d"))
            return ctk.CTkButton(quick_frame, text=label,
                fg_color="#e0e0e0", text_color="#000000",
                hover_color="#c8c8c8", corner_radius=4,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=36, command=_set)

        yesterday   = today - timedelta(days=1)
        week_start  = today - timedelta(days=today.weekday())
        lweek_start = week_start - timedelta(days=7)
        lweek_end   = week_start - timedelta(days=1)
        month_start = today.replace(day=1)
        lmonth_end  = month_start - timedelta(days=1)
        lmonth_start= lmonth_end.replace(day=1)
        year_start  = today.replace(month=1, day=1)
        lyear_start = year_start.replace(year=today.year - 1)
        lyear_end   = year_start - timedelta(days=1)

        buttons = [
            ("Today",       today,        today),
            ("Yesterday",   yesterday,    yesterday),
            ("This Week",   week_start,   today),
            ("Last Week",   lweek_start,  lweek_end),
            ("This Month",  month_start,  today),
            ("Last Month",  lmonth_start, lmonth_end),
            ("This Year",   year_start,   today),
            ("Last Year",   lyear_start,  lyear_end),
        ]

        for col, (label, s, e) in enumerate(buttons):
            btn = q(label, s, e)
            btn.grid(row=col // 2, column=col % 2, padx=4, pady=3, sticky="ew")
            quick_frame.grid_columnconfigure(col % 2, weight=1)

        # ── All Time button ───────────────────────────────────
        def set_all_time():
            start_e.delete(0, "end")
            end_e.delete(0, "end")

        ctk.CTkButton(quick_frame, text="ALL TIME",
            fg_color="#555555", text_color="#ffffff",
            hover_color="#333333", corner_radius=4,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36, command=set_all_time
        ).grid(row=4, column=0, columnspan=2, padx=4, pady=(6, 0), sticky="ew")

        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=20, pady=10)

        # ── Manual date entry ─────────────────────────────────
        ctk.CTkLabel(popup, text="Select Date Range",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000"
        ).pack()

        date_frame = ctk.CTkFrame(popup, fg_color="transparent")
        date_frame.pack(padx=20, pady=8)

        ctk.CTkLabel(date_frame, text="Start Date (YYYY-MM-DD):",
            font=ctk.CTkFont(size=13), text_color="#000000"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=4)
        start_e = ctk.CTkEntry(date_frame, width=180, height=34, font=ctk.CTkFont(size=13))
        start_e.grid(row=0, column=1, padx=5, pady=4)

        ctk.CTkLabel(date_frame, text="End Date (YYYY-MM-DD):",
            font=ctk.CTkFont(size=13), text_color="#000000"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=4)
        end_e = ctk.CTkEntry(date_frame, width=180, height=34, font=ctk.CTkFont(size=13))
        end_e.grid(row=1, column=1, padx=5, pady=4)

        # Pre-fill with current filter
        if self._filter_start:
            start_e.insert(0, self._filter_start)
        if self._filter_end:
            end_e.insert(0, self._filter_end)

        # ── Apply button ──────────────────────────────────────
        def apply():
            s = start_e.get().strip()
            e = end_e.get().strip()

            if not s and not e:
                # All Time
                self._filter_start = None
                self._filter_end = None
                self._filter_label_text = "ALL TIME"
            else:
                # Validate format
                try:
                    datetime.strptime(s, "%Y-%m-%d")
                    datetime.strptime(e, "%Y-%m-%d")
                except ValueError:
                    self._warning("Invalid date format!\nUse YYYY-MM-DD")
                    return
                self._filter_start = s
                self._filter_end = e
                if s == e:
                    self._filter_label_text = datetime.strptime(s, "%Y-%m-%d").strftime("%B %d, %Y").upper()
                else:
                    ds = datetime.strptime(s, "%Y-%m-%d").strftime("%b %d, %Y").upper()
                    de = datetime.strptime(e, "%Y-%m-%d").strftime("%b %d, %Y").upper()
                    self._filter_label_text = f"{ds}  →  {de}"

            self.date_record_label.configure(
                text=f"DATE OF RECORDS:  {self._filter_label_text}"
            )
            self.load_items()
            popup.destroy()

        ctk.CTkButton(popup, text="SHOW RECORDS",
            fg_color="#1a73e8", text_color="#ffffff",
            hover_color="#1558b0", corner_radius=4,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42, width=200,
            command=apply
        ).pack(pady=10)

        ctk.CTkButton(popup, text="Cancel",
            fg_color="transparent", text_color="#555555",
            hover_color="#f0f0f0", corner_radius=4,
            font=ctk.CTkFont(size=13),
            height=32, command=popup.destroy
        ).pack()

    # ─────────────────────────────────────────────────────────
    # Load Items — uses demand_log for the Demand column
    # ─────────────────────────────────────────────────────────
    def load_items(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.selected_barcode = None
        self.selected_row_labels = []

        from database.database import get_items_with_demand
        items = get_items_with_demand(self._filter_start, self._filter_end)

        # Filter by search query
        query = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        if query:
            items = [i for i in items if
                     query in str(i[0]).lower() or  # barcode
                     query in str(i[1]).lower() or  # item_name
                     query in str(i[2]).lower()]     # category

        for i, item in enumerate(items):
            bg = "#f0f0f0" if i % 2 == 0 else "#d3d3d3"
            barcode, item_name, category, unit_cost, selling_price, \
                current_stock, demand, classification, status = item

            cls_colors = {"A": "#90EE90", "B": "#00BFFF", "C": "#FFD700"}
            cls_bg = cls_colors.get(classification, bg)

            row_data = [barcode, item_name, category, unit_cost, selling_price,
                        demand, current_stock, classification]
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

    # ─────────────────────────────────────────────────────────
    # Cart
    # ─────────────────────────────────────────────────────────
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

    # ─────────────────────────────────────────────────────────
    # Warning popup
    # ─────────────────────────────────────────────────────────
    def _warning(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("Warning")
        popup.geometry("320x160")
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=message,
            font=ctk.CTkFont(size=14)).pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)

    # ─────────────────────────────────────────────────────────
    # Add / Edit / Delete Item dialogs
    # ─────────────────────────────────────────────────────────
    def open_add_item(self):
        from database.database import get_next_barcode, get_all_items
        popup = ctk.CTkToplevel(self)
        popup.title("Add Item")
        popup.geometry("500x550")
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup, text="ADD ITEM",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        ctk.CTkLabel(popup, text=f"Barcode: {get_next_barcode()}",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30)

        # Get existing categories for dropdown
        all_items = get_all_items()
        categories = sorted(set(i[2] for i in all_items if i[2]))

        entries = {}

        # Item Name
        ctk.CTkLabel(popup, text="Item Name",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
        entries["Item Name"] = ctk.CTkEntry(popup, width=440, height=35)
        entries["Item Name"].pack(padx=30)

        # Category — dropdown if existing categories, else text entry
        ctk.CTkLabel(popup, text="Category",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))

        cat_var = ctk.StringVar(value=categories[0] if categories else "")
        if categories:
            cat_combo = ctk.CTkComboBox(popup, width=440, height=35,
                values=categories, variable=cat_var,
                font=ctk.CTkFont(size=14))
            cat_combo.pack(padx=30)
            entries["Category"] = cat_combo
        else:
            entries["Category"] = ctk.CTkEntry(popup, width=440, height=35)
            entries["Category"].pack(padx=30)

        # Other fields
        for field in ["Unit Cost", "Selling Price", "Current Stock"]:
            ctk.CTkLabel(popup, text=field,
                font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
            entry = ctk.CTkEntry(popup, width=440, height=35)
            entry.pack(padx=30)
            entries[field] = entry

        def save():
            cat_val = cat_var.get() if categories else entries["Category"].get()
            on_add_item(
                entries["Item Name"].get(),
                cat_val,
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

        from database.database import get_item_by_barcode, get_all_items
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

        all_items = get_all_items()
        categories = sorted(set(i[2] for i in all_items if i[2]))
        current_cat = item[3] or ""

        entries = {}

        # Item Name
        ctk.CTkLabel(popup, text="Item Name",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
        entries["Item Name"] = ctk.CTkEntry(popup, width=440, height=35)
        entries["Item Name"].insert(0, str(item[2]) if item[2] else "")
        entries["Item Name"].pack(padx=30)

        # Category dropdown
        ctk.CTkLabel(popup, text="Category",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
        cat_var = ctk.StringVar(value=current_cat)
        if categories:
            cat_combo = ctk.CTkComboBox(popup, width=440, height=35,
                values=categories, variable=cat_var,
                font=ctk.CTkFont(size=14))
            cat_combo.pack(padx=30)
            entries["Category"] = cat_combo
        else:
            entries["Category"] = ctk.CTkEntry(popup, width=440, height=35)
            entries["Category"].insert(0, current_cat)
            entries["Category"].pack(padx=30)

        # Other fields
        prefill = {"Unit Cost": item[4], "Selling Price": item[5], "Current Stock": item[6]}
        for field, value in prefill.items():
            ctk.CTkLabel(popup, text=field,
                font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
            entry = ctk.CTkEntry(popup, width=440, height=35)
            entry.insert(0, str(value) if value is not None else "")
            entry.pack(padx=30)
            entries[field] = entry

        def save():
            cat_val = cat_var.get() if categories else entries["Category"].get()
            on_edit_item(
                self.selected_barcode,
                entries["Item Name"].get(),
                cat_val,
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