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

        # col weights: Barcode=1, Item Name=3, Category=1, Unit Cost=1, Selling Price=1,
        #              Demand=1, Current Stock=1, Classification=1
        self._col_weights = [1, 3, 1, 1, 1, 1, 1, 1]
        # anchor per column
        self._col_anchors = ["center", "w", "center", "center", "center", "center", "center", "center"]

        # Single scrollable frame — header at row 0, data from row 1 onward
        self.rows_frame = ctk.CTkScrollableFrame(
            table_frame, fg_color="#bbbbbb", corner_radius=0)
        self.rows_frame.pack(fill="both", expand=True)

        for i, w in enumerate(self._col_weights):
            self.rows_frame.grid_columnconfigure(i, weight=w)

        # ── Header row inside the scroll frame ───────────────
        for i, col in enumerate(columns):
            anchor = self._col_anchors[i]
            padx_left = 10 if anchor == "w" else 2
            ctk.CTkLabel(
                self.rows_frame, text=col,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white",
                fg_color="#000000",
                anchor=anchor,
                justify="left" if anchor == "w" else "right" if anchor == "e" else "center",
                padx=12 if anchor == "w" else 4
            ).grid(row=0, column=i, sticky="nsew", padx=(0, 1), pady=(0, 1), ipady=10)

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

        # Admin-only buttons wrapped in a frame so they can be hidden for staff
        self.admin_btn_frame = ctk.CTkFrame(btn_frame, fg_color="transparent", corner_radius=0)
        self.admin_btn_frame.pack(side="left", fill="x", expand=True)

        btn_configs = [
            ("ADD ITEM",      "#90EE90", "#000000", "#7dd67d", lambda: self.open_add_item()),
            ("IMPORT EXCEL",  "#4488FF", "#ffffff", "#2266cc", lambda: self.open_import_excel()),
            ("REORDER TABLE", "#90EE90", "#000000", "#7dd67d", lambda: controller.navigate("reorder_table")),
            ("EDIT ITEM",     "#d3d3d3", "#000000", "#c0c0c0", lambda: self.open_edit_item()),
            ("DELETE ITEM",   "#FF4444", "#ffffff", "#cc0000", lambda: self.open_delete_confirm()),
        ]

        for text, bg, fg, hover, cmd in btn_configs:
            ctk.CTkButton(
                self.admin_btn_frame, text=text, fg_color=bg, text_color=fg,
                hover_color=hover, border_color="#000000", border_width=2,
                font=ctk.CTkFont(size=26, weight="bold"),
                corner_radius=0, height=60, command=cmd
            ).pack(side="left", padx=5, expand=True, fill="x")

        # 📅 FILTER DATE — always visible for both Admin and Staff
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
    # ─────────────────────────────────────────────────────────
    # Role UI — show/hide admin-only buttons
    # ─────────────────────────────────────────────────────────
    def refresh_role_ui(self):
        if not hasattr(self, "admin_btn_frame"):
            return
        from controllers.controller import is_admin
        if is_admin():
            self.admin_btn_frame.pack(side="left", fill="x", expand=True)
        else:
            self.admin_btn_frame.pack_forget()

    def load_items(self):
        self.refresh_role_ui()

        # Remove only data rows — keep header labels at grid row 0
        for widget in self.rows_frame.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) > 0:
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
            row_num = i + 1  # row 0 is the sticky header
            bg = "#f0f0f0" if i % 2 == 0 else "#d3d3d3"
            barcode, item_name, category, unit_cost, selling_price, \
                current_stock, demand, classification, status = item

            cls_colors = {"A": "#90EE90", "B": "#00BFFF", "C": "#FFD700"}
            cls_bg = cls_colors.get(classification, bg)

            # Format values for display
            def fmt_price(v):
                try:
                    return f"₱{float(v):,.2f}"
                except (TypeError, ValueError):
                    return "₱0.00"

            display_data = [
                barcode,
                item_name,
                category,
                fmt_price(unit_cost),
                fmt_price(selling_price),
                demand if demand not in (None, "") else 0,
                current_stock if current_stock not in (None, "") else 0,
                classification if classification else "—",
            ]
            row_colors = [bg, bg, bg, bg, bg, bg, bg, cls_bg]

            row_labels = []
            for j, (val, cell_bg) in enumerate(zip(display_data, row_colors)):
                anchor = self._col_anchors[j]
                # For left-anchored (Item Name), add inner text padding so text
                # doesn't sit right against the black divider
                lbl_padx = (12, 4) if anchor == "w" else (4, 4)
                lbl = ctk.CTkLabel(
                    self.rows_frame,
                    text=str(val),
                    font=ctk.CTkFont(size=14),
                    text_color="#000000",
                    justify="left" if anchor == "w" else "right" if anchor == "e" else "center",
                    anchor=anchor,
                    fg_color=cell_bg,
                    cursor="hand2",
                    padx=lbl_padx[0]
                )
                lbl.grid(row=row_num, column=j, sticky="nsew", padx=(0, 1), pady=(0, 1), ipady=8)
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
    # Import from Excel / CSV
    # ─────────────────────────────────────────────────────────
    def open_import_excel(self):
        from tkinter import filedialog
        import os

        filepath = filedialog.askopenfilename(
            title="Import Items from File",
            filetypes=[
                ("Excel / CSV files", "*.xlsx *.xls *.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ]
        )
        if not filepath:
            return

        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext in (".xlsx", ".xls"):
                try:
                    import openpyxl
                except ImportError:
                    self._warning("openpyxl is not installed.\nRun: pip install openpyxl")
                    return

                wb = openpyxl.load_workbook(filepath, data_only=True)
                ws = wb.active

                # Read all rows into a list
                all_rows = list(ws.iter_rows(values_only=True))
                if not all_rows:
                    self._warning("The file appears to be empty.")
                    return

                # ── Auto-detect format ──────────────────────────────────────
                # Horizontal pivot format: Row 0 has item names in many columns,
                # Row 1 has prices, Row 2 has total demand.
                # Simple vertical format: Row 0 is a header, data starts Row 1.

                row0 = all_rows[0]
                non_none_r0 = [c for c in row0 if c not in (None, "", " ")]

                # Heuristic: if row 0 has more than 10 non-empty cells AND
                # the first non-empty cell looks like a label (not a number),
                # treat as horizontal pivot.
                def _is_horizontal_pivot(r0):
                    if len(non_none_r0) < 8:
                        return False
                    # If most non-None values in row0 are strings → pivot
                    str_count = sum(1 for v in non_none_r0 if isinstance(v, str))
                    return str_count >= len(non_none_r0) * 0.5

                if _is_horizontal_pivot(row0):
                    parsed_rows = self._parse_horizontal_excel(all_rows)
                else:
                    # Simple vertical format (original logic)
                    parsed_rows = []
                    for i, row in enumerate(all_rows):
                        if i == 0:
                            continue  # skip header
                        parsed_rows.append(list(row))

                self._show_import_preview(parsed_rows, filepath)

            elif ext == ".csv":
                import csv
                parsed_rows = []
                with open(filepath, newline="", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # skip header
                    for row in reader:
                        parsed_rows.append(row)
                self._show_import_preview(parsed_rows, filepath)

        except Exception as e:
            self._warning(f"Failed to read file:\n{str(e)}")

    def _parse_horizontal_excel(self, all_rows):
        """
        Parse the horizontal pivot demand sheet used by this store.

        Layout (0-indexed rows):
          Row 0  → item names (category names appear as section separators, None = separator col)
          Row 1  → selling prices  e.g. '₱ 9.00'
          Row 2  → 2025 total demand values (floats)

        Returns list of [item_name, category, unit_cost, selling_price, current_stock]
        where unit_cost = 0 (not in file), current_stock = 0 (not in file).
        """
        import re

        if len(all_rows) < 3:
            return []

        row_names   = all_rows[0]   # item names / category labels
        row_prices  = all_rows[1]   # selling prices
        row_demand  = all_rows[2]   # total demand (we use as a reference only, not stock)

        parsed = []
        current_category = ""

        # Known category-header keywords (Row 0 cells that are category names, not items)
        # We detect them by the fact that Row 1 (price) for that column is None.
        for col_idx in range(len(row_names)):
            cell_name   = row_names[col_idx]
            cell_price  = row_prices[col_idx]  if col_idx < len(row_prices)  else None

            # Skip completely empty columns
            if cell_name is None or str(cell_name).strip() == "":
                continue

            name_str = str(cell_name).strip()

            # If price cell is None/empty → this column is a category header
            price_is_empty = (cell_price is None or str(cell_price).strip() == "")
            if price_is_empty:
                # Could be a category label like "Cigarettes", "Nestle", etc.
                # Only treat as category if the name looks like a label (not a data keyword)
                data_keywords = {
                    "price", "2025 total demand", "total profit", "year 2025",
                    "for standard dev.", "average daily demand", "total monthlly demand",
                    "mean", "stanadard deviation", "demand tally sheet",
                    "jan", "feb", "mar", "apr", "may", "jun",
                    "jul", "aug", "sep", "oct", "nov", "dec",
                    "january", "february", "march", "april", "june",
                    "july", "august", "september", "october", "november", "december",
                    "1st week", "2nd week", "3rd week", "4th week", "5th week",
                    "total demand (2025)", "total demand checker (2025)",
                }
                if name_str.lower() not in data_keywords and not name_str.startswith("If "):
                    current_category = name_str
                continue

            # Parse selling price — strip ₱ and spaces
            selling_price = 0.0
            if cell_price not in (None, ""):
                price_str = re.sub(r"[₱,\s]", "", str(cell_price))
                try:
                    selling_price = float(price_str)
                except ValueError:
                    selling_price = 0.0

            # Stock = 0 (not available in this file)
            # Unit cost = 0 (not available in this file)
            parsed.append([
                name_str,           # item_name
                current_category,   # category
                0.0,                # unit_cost  (unknown)
                selling_price,      # selling_price
                0,                  # current_stock (unknown)
            ])

        return parsed

    def _show_import_preview(self, rows, filepath):
        import os
        from database.database import add_item

        popup = ctk.CTkToplevel(self)
        popup.title("Import Preview")
        popup.geometry("860x560")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="📂  IMPORT FROM FILE",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=(12, 2))

        ctk.CTkLabel(popup,
            text=f"File: {os.path.basename(filepath)}   |   {len(rows)} row(s) found",
            font=ctk.CTkFont(size=12), text_color="#555555"
        ).pack()

        ctk.CTkLabel(popup,
            text="Supports standard column format OR horizontal demand sheet (auto-detected)",
            font=ctk.CTkFont(size=12, slant="italic"), text_color="#1a5276"
        ).pack(pady=(2, 6))

        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=20)

        # Preview table
        cols = ["Item Name", "Category", "Unit Cost", "Selling Price", "Current Stock"]
        tbl = ctk.CTkFrame(popup, fg_color="#000000", corner_radius=0)
        tbl.pack(fill="both", expand=True, padx=20, pady=8)

        hdr = ctk.CTkFrame(tbl, fg_color="#222222", corner_radius=0)
        hdr.pack(fill="x")
        for i, col in enumerate(cols):
            hdr.grid_columnconfigure(i, weight=1, uniform="pcol")
            ctk.CTkLabel(hdr, text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff", justify="center"
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=6)

        scroll = ctk.CTkScrollableFrame(tbl, fg_color="#ffffff", corner_radius=0)
        scroll.pack(fill="both", expand=True)
        for i in range(5):
            scroll.grid_columnconfigure(i, weight=1, uniform="pcol")

        valid_rows = []
        error_rows = []

        for idx, row in enumerate(rows):
            row = list(row) + [None] * 5
            item_name     = str(row[0]).strip() if row[0] not in (None, "") else ""
            category      = str(row[1]).strip() if row[1] not in (None, "") else ""
            unit_cost_raw = row[2]
            sell_raw      = row[3]
            stock_raw     = row[4]

            ok = True
            try:
                unit_cost     = float(unit_cost_raw)  if unit_cost_raw not in (None, "") else 0.0
                selling_price = float(sell_raw)        if sell_raw      not in (None, "") else 0.0
                current_stock = int(float(stock_raw))  if stock_raw     not in (None, "") else 0
            except (ValueError, TypeError):
                ok = False

            if not item_name:
                ok = False

            bg     = "#f0f0f0" if idx % 2 == 0 else "#e8e8e8"
            err_bg = "#ffe0e0"

            display = [item_name or "⚠ EMPTY", category,
                       str(unit_cost_raw), str(sell_raw), str(stock_raw)]

            for j, val in enumerate(display):
                ctk.CTkLabel(scroll, text=str(val),
                    font=ctk.CTkFont(size=12),
                    text_color="#000000" if ok else "#cc0000",
                    fg_color=bg if ok else err_bg,
                    justify="center"
                ).grid(row=idx, column=j, sticky="nsew", padx=1, pady=4)

            if ok:
                valid_rows.append((item_name, category, unit_cost, selling_price, current_stock))
            else:
                error_rows.append(idx + 2)

        summary = f"✅ {len(valid_rows)} valid row(s) ready to import"
        if error_rows:
            summary += f"   ⚠ {len(error_rows)} row(s) skipped (invalid data)"

        ctk.CTkLabel(popup, text=summary,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1a7a1a" if not error_rows else "#cc5500"
        ).pack(pady=4)

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=8)

        def do_import():
            imported = 0
            for item_name, category, unit_cost, selling_price, current_stock in valid_rows:
                try:
                    add_item(item_name, category, unit_cost, selling_price, current_stock)
                    imported += 1
                except Exception:
                    pass
            popup.destroy()
            self.load_items()

            done = ctk.CTkToplevel(self)
            done.title("Import Complete")
            done.geometry("340x140")
            done.resizable(False, False)
            done.grab_set()
            done.lift()
            ctk.CTkLabel(done,
                text=f"✅ Successfully imported {imported} item(s)!",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#000000", justify="center"
            ).pack(expand=True)
            ctk.CTkButton(done, text="OK", command=done.destroy,
                fg_color="#90EE90", text_color="#000000",
                corner_radius=0, width=100
            ).pack(pady=10)

        ctk.CTkButton(btn_row, text="IMPORT",
            fg_color="#4488FF", text_color="#ffffff",
            hover_color="#2266cc", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=0, width=160, height=42,
            state="normal" if valid_rows else "disabled",
            command=do_import
        ).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="CANCEL",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=0, width=160, height=42,
            command=popup.destroy
        ).pack(side="left", padx=10)

    # ─────────────────────────────────────────────────────────
    # Add / Edit / Delete Item dialogs
    # ─────────────────────────────────────────────────────────
    def open_add_item(self):
        from database.database import get_next_barcode, get_all_items
        popup = ctk.CTkToplevel(self)
        popup.title("Add Item")
        popup.geometry("500x620")
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

        # Product Barcode (optional)
        ctk.CTkLabel(popup, text="Product Barcode (optional — scan or type real barcode)",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
        entries["Product Barcode"] = ctk.CTkEntry(popup, width=440, height=35,
            placeholder_text="Scan the product or type barcode here...")
        entries["Product Barcode"].pack(padx=30)

        # Auto-fill product barcode when scanner fires while popup is open
        _scan_buf = []
        _scan_timer = [None]
        def _on_key(event):
            if _scan_timer[0]:
                popup.after_cancel(_scan_timer[0])
                _scan_timer[0] = None
            if event.keysym == "Return":
                scanned = "".join(_scan_buf).strip()
                _scan_buf.clear()
                if scanned:
                    entries["Product Barcode"].delete(0, "end")
                    entries["Product Barcode"].insert(0, scanned)
            elif event.char and event.char.isprintable():
                _scan_buf.append(event.char)
                _scan_timer[0] = popup.after(300, _scan_buf.clear)
        popup.bind("<Key>", _on_key)

        def save():
            cat_val = cat_var.get() if categories else entries["Category"].get()
            on_add_item(
                entries["Item Name"].get(),
                cat_val,
                entries["Unit Cost"].get(),
                entries["Selling Price"].get(),
                entries["Current Stock"].get(),
                entries["Product Barcode"].get().strip(),
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
        popup.geometry("500x620")
        popup.resizable(False, False)
        popup.grab_set()

        # Tell main app that edit item is open — blocks global scanner
        import controllers.controller as ctrl
        if ctrl._app:
            ctrl._app._edit_item_open = True
        def _on_close():
            if ctrl._app:
                ctrl._app._edit_item_open = False
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", _on_close)

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

        # Product Barcode (optional)
        ctk.CTkLabel(popup, text="Product Barcode (optional — scan or type real barcode)",
            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=30, pady=(10, 0))
        entries["Product Barcode"] = ctk.CTkEntry(popup, width=440, height=35,
            placeholder_text="Scan the product or type barcode here...")
        # Pre-fill existing product barcode if available (index 14)
        existing_pb = item[14] if len(item) > 14 and item[14] else ""
        entries["Product Barcode"].insert(0, existing_pb)
        entries["Product Barcode"].pack(padx=30)

        # Auto-fill product barcode when scanner fires while popup is open
        _scan_buf = []
        _scan_timer = [None]
        def _on_key(event):
            if _scan_timer[0]:
                popup.after_cancel(_scan_timer[0])
                _scan_timer[0] = None
            if event.keysym == "Return":
                scanned = "".join(_scan_buf).strip()
                _scan_buf.clear()
                if scanned:
                    entries["Product Barcode"].delete(0, "end")
                    entries["Product Barcode"].insert(0, scanned)
            elif event.char and event.char.isprintable():
                _scan_buf.append(event.char)
                _scan_timer[0] = popup.after(300, _scan_buf.clear)
        popup.bind("<Key>", _on_key)

        def save():
            cat_val = cat_var.get() if categories else entries["Category"].get()
            on_edit_item(
                self.selected_barcode,
                entries["Item Name"].get(),
                cat_val,
                entries["Unit Cost"].get(),
                entries["Selling Price"].get(),
                entries["Current Stock"].get(),
                entries["Product Barcode"].get().strip(),
            )
            import controllers.controller as ctrl
            if ctrl._app:
                ctrl._app._edit_item_open = False
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