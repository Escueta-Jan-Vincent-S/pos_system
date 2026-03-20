import customtkinter as ctk
from controllers import controller
from controllers.sell_controller import SellController


class SellPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)
        self.ctrl = SellController(self)
        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#90EE90", height=100, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#7dd67d",
            font=ctk.CTkFont(size=60, weight="bold"),
            corner_radius=0, width=80, height=80,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="SELL",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # Body
        body = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── LEFT: Order list ──────────────────────────────────
        left = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0,
                            border_color="#000000", border_width=2)
        left.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)

        # Mode label + barcode entry
        top_bar = ctk.CTkFrame(left, fg_color="#e8e8e8", corner_radius=0, height=55)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        self.mode_label = ctk.CTkLabel(
            top_bar, text="📷 SCAN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff", fg_color="#228B22",
            corner_radius=6, width=110
        )
        self.mode_label.pack(side="left", padx=10, pady=10)

        self.barcode_entry = ctk.CTkEntry(
            top_bar, placeholder_text="Type barcode or REC##### here...",
            height=38, font=ctk.CTkFont(size=14)
        )
        self.barcode_entry.pack(side="left", padx=(5, 5), pady=8, fill="x", expand=True)
        self.barcode_entry.bind("<Return>", lambda e: self._on_add_barcode())

        ctk.CTkButton(
            top_bar, text="ADD",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=1,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=0, width=60, height=38,
            command=self._on_add_barcode
        ).pack(side="left", padx=(0, 10))

        ctk.CTkFrame(left, fg_color="#000000", height=1, corner_radius=0).pack(fill="x")

        # Column headers
        col_header = ctk.CTkFrame(left, fg_color="#000000", corner_radius=0, height=40)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)
        col_header.grid_columnconfigure(0, weight=46)
        col_header.grid_columnconfigure(1, weight=14)
        col_header.grid_columnconfigure(2, weight=18)
        col_header.grid_columnconfigure(3, weight=14)
        col_header.grid_columnconfigure(4, weight=8)

        for i, (txt, anchor) in enumerate([
            ("DESCRIPTION", "w"),
            ("UNIT PRICE",  "w"),
            ("QTY",         "center"),
            ("AMOUNT",      "e"),
            ("",            "e"),
        ]):
            ctk.CTkLabel(col_header, text=txt,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff", anchor=anchor
            ).grid(row=0, column=i, padx=8, pady=8, sticky="ew")

        # Scrollable cart rows
        self.cart_frame = ctk.CTkScrollableFrame(
            left, fg_color="#ffffff", corner_radius=0)
        self.cart_frame.pack(fill="both", expand=True)
        self.cart_frame.grid_columnconfigure(0, weight=3)
        self.cart_frame.grid_columnconfigure(1, weight=1)
        self.cart_frame.grid_columnconfigure(2, weight=1)
        self.cart_frame.grid_columnconfigure(3, weight=1)
        self.cart_frame.grid_columnconfigure(4, weight=0)

        # Total bar
        ctk.CTkFrame(left, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        total_bar = ctk.CTkFrame(left, fg_color="#f9f9f9", corner_radius=0, height=50)
        total_bar.pack(fill="x")
        total_bar.pack_propagate(False)

        ctk.CTkLabel(total_bar, text="TOTAL",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#000000"
        ).pack(side="left", padx=15)

        self.total_label = ctk.CTkLabel(
            total_bar, text="₱0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#000000"
        )
        self.total_label.pack(side="right", padx=15)

        # ── RIGHT: Numpad ─────────────────────────────────────
        right = ctk.CTkFrame(body, fg_color="#f5f5f5", corner_radius=0, width=430)
        right.pack(side="right", fill="y", padx=(10, 20), pady=20)
        right.pack_propagate(False)

        # Cash display
        cash_box = ctk.CTkFrame(right, fg_color="#ffffff",
                                border_color="#000000", border_width=2,
                                corner_radius=0, height=65)
        cash_box.pack(fill="x", pady=(0, 6))
        cash_box.pack_propagate(False)

        ctk.CTkLabel(cash_box, text="CASH:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#555555"
        ).pack(side="left", padx=12)

        self.cash_display = ctk.CTkLabel(
            cash_box, text="₱0",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#000000"
        )
        self.cash_display.pack(side="right", padx=15)

        # Change display
        change_box = ctk.CTkFrame(right, fg_color="#e8ffe8",
                                  border_color="#228B22", border_width=2,
                                  corner_radius=0, height=50)
        change_box.pack(fill="x", pady=(0, 10))
        change_box.pack_propagate(False)

        ctk.CTkLabel(change_box, text="CHANGE:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#228B22"
        ).pack(side="left", padx=12)

        self.change_display = ctk.CTkLabel(
            change_box, text="₱0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#228B22"
        )
        self.change_display.pack(side="right", padx=15)

        # Numpad
        pad = ctk.CTkFrame(right, fg_color="#f5f5f5", corner_radius=0)
        pad.pack(fill="both", expand=True)

        for r in range(4):
            pad.grid_rowconfigure(r, weight=1)
        for c in range(4):
            pad.grid_columnconfigure(c, weight=1)

        g = dict(fg_color="#90EE90", text_color="#000000", hover_color="#7dd67d",
                 border_color="#888888", border_width=1,
                 font=ctk.CTkFont(size=28, weight="bold"),
                 corner_radius=8, width=95, height=78)

        # Row 0
        ctk.CTkButton(pad, text="1", **g, command=lambda: self._num("1")).grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="2", **g, command=lambda: self._num("2")).grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="3", **g, command=lambda: self._num("3")).grid(row=0, column=2, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="ENTER",
            fg_color="#90EE90", text_color="#000000", hover_color="#7dd67d",
            border_color="#888888", border_width=1,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=8, width=95, height=78,
            command=self._refresh_displays
        ).grid(row=0, column=3, padx=4, pady=4, sticky="nsew")

        # Row 1
        ctk.CTkButton(pad, text="4", **g, command=lambda: self._num("4")).grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="5", **g, command=lambda: self._num("5")).grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="6", **g, command=lambda: self._num("6")).grid(row=1, column=2, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="PAY",
            fg_color="#228B22", text_color="#ffffff", hover_color="#1a6b1a",
            border_color="#888888", border_width=1,
            font=ctk.CTkFont(size=24, weight="bold"),
            corner_radius=8, width=95, height=78,
            command=self._on_pay
        ).grid(row=1, column=3, padx=4, pady=4, sticky="nsew")

        # Row 2
        ctk.CTkButton(pad, text="7", **g, command=lambda: self._num("7")).grid(row=2, column=0, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="8", **g, command=lambda: self._num("8")).grid(row=2, column=1, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="9", **g, command=lambda: self._num("9")).grid(row=2, column=2, padx=4, pady=4, sticky="nsew")

        # Row 3
        ctk.CTkButton(pad, text="0", **g, command=lambda: self._num("0")).grid(row=3, column=0, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="00", **g, command=lambda: self._num("00")).grid(row=3, column=1, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="←",
            fg_color="#90EE90", text_color="#000000", hover_color="#7dd67d",
            border_color="#888888", border_width=1,
            font=ctk.CTkFont(size=26, weight="bold"),
            corner_radius=8, width=95, height=78,
            command=self._backspace
        ).grid(row=3, column=2, padx=4, pady=4, sticky="nsew")
        ctk.CTkButton(pad, text="DELETE",
            fg_color="#FF4444", text_color="#ffffff", hover_color="#cc0000",
            border_color="#888888", border_width=1,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=8, width=95, height=78,
            command=self._clear_cash
        ).grid(row=3, column=3, padx=4, pady=4, sticky="nsew")

    # ── Cart rendering ────────────────────────────────────────
    def _refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()

        for i, item in enumerate(self.ctrl.cart):
            amount = item["selling_price"] * item["quantity"]
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"

            row = ctk.CTkFrame(self.cart_frame, fg_color=bg, corner_radius=0, height=46)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            # Description (0% - 46%)
            ctk.CTkLabel(row, text=item["item_name"],
                font=ctk.CTkFont(size=15), text_color="#000000",
                anchor="w", fg_color=bg
            ).place(relx=0.01, rely=0.5, anchor="w", relwidth=0.44)

            # Unit Price — aligned under UNIT PRICE header
            ctk.CTkLabel(row, text=f"₱{item['selling_price']:.2f}",
                font=ctk.CTkFont(size=14), text_color="#555555",
                anchor="w", fg_color=bg
            ).place(relx=0.45, rely=0.5, anchor="w", relwidth=0.14)

            # +/- QTY (60% - 78%) — centered under QTY header
            btn_frame = ctk.CTkFrame(row, fg_color=bg, corner_radius=0)
            btn_frame.place(relx=0.69, rely=0.5, anchor="center")

            ctk.CTkButton(btn_frame, text="-",
                fg_color="#d3d3d3", text_color="#000000", hover_color="#c0c0c0",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=4, width=28, height=28,
                command=lambda b=item["barcode"]: self._on_decrement(b)
            ).pack(side="left", padx=1)

            ctk.CTkLabel(btn_frame, text=str(item["quantity"]),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#000000", width=28
            ).pack(side="left")

            ctk.CTkButton(btn_frame, text="+",
                fg_color="#d3d3d3", text_color="#000000", hover_color="#c0c0c0",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=4, width=28, height=28,
                command=lambda b=item["barcode"]: self._on_increment(b)
            ).pack(side="left", padx=1)

            # Amount (78% - 93%) — right-aligned under AMOUNT header
            ctk.CTkLabel(row, text=f"₱{amount:.2f}",
                font=ctk.CTkFont(size=15, weight="bold"), text_color="#000000",
                anchor="e", fg_color=bg
            ).place(relx=0.79, rely=0.5, anchor="w", relwidth=0.14)

            # Remove button
            ctk.CTkButton(row, text="✕",
                fg_color=bg, text_color="#FF4444", hover_color="#ffe0e0",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=4, width=32, height=32,
                command=lambda b=item["barcode"]: self._on_remove(b)
            ).place(relx=0.97, rely=0.5, anchor="e")

        self._refresh_displays()

    def _refresh_displays(self):
        total  = self.ctrl.get_total()
        cash   = self.ctrl.get_cash()
        change = self.ctrl.get_change()
        self.total_label.configure(text=f"₱{total:.2f}")
        self.cash_display.configure(text=f"₱{cash:,.0f}")
        self.change_display.configure(text=f"₱{change:.2f}")

    # ── Event handlers ────────────────────────────────────────
    def _on_add_barcode(self):
        barcode = self.barcode_entry.get().strip()
        err = self.ctrl.add_by_barcode(barcode)
        self.barcode_entry.delete(0, "end")
        if err:
            self._warning(err)
        else:
            self._refresh_cart()

    def _on_increment(self, barcode):
        self.ctrl.increment(barcode)
        self._refresh_cart()

    def _on_decrement(self, barcode):
        self.ctrl.decrement(barcode)
        self._refresh_cart()

    def _on_remove(self, barcode):
        self.ctrl.remove_item(barcode)
        self._refresh_cart()

    def _num(self, digit):
        self.ctrl.numpad_press(digit)
        self._refresh_displays()

    def _backspace(self):
        self.ctrl.numpad_backspace()
        self._refresh_displays()

    def _clear_cash(self):
        self.ctrl.numpad_clear()
        self._refresh_displays()

    def _on_pay(self):
        receipt_no, err = self.ctrl.process_payment()
        if err:
            self._warning(err)
            return
        self._show_success(receipt_no)

    def _show_success(self, receipt_no):
        total  = self.ctrl.get_total()
        cash   = self.ctrl.get_cash()
        change = self.ctrl.get_change()
        cart   = list(self.ctrl.cart)

        popup = ctk.CTkToplevel(self)
        popup.title("Payment Successful")
        popup.geometry("420x320")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="✅ PAYMENT SUCCESSFUL",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#228B22").pack(pady=18)

        for label, val in [("TOTAL", total), ("CASH", cash), ("CHANGE", change)]:
            row = ctk.CTkFrame(popup, fg_color="transparent")
            row.pack(fill="x", padx=50, pady=3)
            ctk.CTkLabel(row, text=label,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#000000").pack(side="left")
            ctk.CTkLabel(row, text=f"₱{val:.2f}",
                font=ctk.CTkFont(size=15),
                text_color="#000000").pack(side="right")

        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=30, pady=10)

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=8)

        import controllers.controller as c

        def go_receipt():
            popup.destroy()
            c._app.receipt_page.load_receipt(
                cart, receipt_no=receipt_no, back_to="sell",
                cash=cash, change=change
            )
            controller.navigate("receipt")
            self.ctrl.clear_cart()
            self._refresh_cart()

        def new_sale():
            popup.destroy()
            self.ctrl.clear_cart()
            self._refresh_cart()

        ctk.CTkButton(btn_row, text="🖨 PRINT RECEIPT",
            fg_color="#FFD700", text_color="#000000",
            hover_color="#e6c200", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=0, width=160, height=48,
            command=go_receipt
        ).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="🛒 NEW SALE",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=0, width=160, height=48,
            command=new_sale
        ).pack(side="left", padx=8)

    # ── Page entry ────────────────────────────────────────────
    def load_items(self):
        """Called by show_page — just focus barcode entry, scanner is always ready."""
        self.after(150, self.barcode_entry.focus_set)

    # ── Helpers ───────────────────────────────────────────────
    def _warning(self, msg):
        p = ctk.CTkToplevel(self)
        p.title("Warning")
        p.geometry("320x160")
        p.resizable(False, False)
        p.grab_set()
        ctk.CTkLabel(p, text=msg, font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
        ctk.CTkButton(p, text="OK", command=p.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)

    def _info(self, msg):
        p = ctk.CTkToplevel(self)
        p.title("Info")
        p.geometry("320x150")
        p.resizable(False, False)
        p.grab_set()
        ctk.CTkLabel(p, text=msg, font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
        ctk.CTkButton(p, text="OK", command=p.destroy,
            fg_color="#90EE90", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)