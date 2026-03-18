import customtkinter as ctk
from controllers import controller
from controllers.receipts_controller import ReceiptsController


class ReceiptsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)
        self.ctrl = ReceiptsController(self)
        self._filter_start = None
        self._filter_end = None
        self._filter_label_text = "ALL TIME"
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#00BFFF", height=90, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#009fd4",
            font=ctk.CTkFont(size=50, weight="bold"),
            corner_radius=0, width=70, height=70,
            command=lambda: controller.navigate("dashboard")
        ).pack(side="left", padx=10)

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(search_frame, text="🔍",
            font=ctk.CTkFont(size=20),
            text_color="#000000"
        ).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(search_frame,
            textvariable=self.search_var,
            placeholder_text="Search receipt no / date...",
            font=ctk.CTkFont(size=14),
            width=220, height=40
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="LIST OF RECORD OF RECEIPTS",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # PRINT button
        ctk.CTkButton(
            header, text="PRINT / VIEW",
            fg_color="#ffffff", text_color="#000000",
            hover_color="#e0e0e0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=22, weight="bold"),
            corner_radius=0, width=180, height=55,
            command=self._on_print
        ).pack(side="right", padx=20)

        ctk.CTkButton(
            header, text="📅 FILTER DATE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=170, height=55,
            command=self._open_date_filter
        ).pack(side="right", padx=(0, 5))

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Date filter banner ────────────────────────────────
        self.date_banner = ctk.CTkFrame(self, fg_color="#f0f0f0", height=34, corner_radius=0)
        self.date_banner.pack(fill="x")
        self.date_banner.pack_propagate(False)
        self.date_record_label = ctk.CTkLabel(
            self.date_banner, text="DATE FILTER:  ALL TIME",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        )
        self.date_record_label.pack(side="left", padx=20, pady=6)

        # ── Table header ──────────────────────────────────────
        col_header = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0, height=45)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        for i in range(5):
            col_header.grid_columnconfigure(i, weight=1, uniform="col")

        for i, txt in enumerate(["DATE", "TIME", "RECEIPT NO.", "TOTAL", "STATUS"]):
            ctk.CTkLabel(col_header, text=txt,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff", anchor="center",
                fg_color="#000000"
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Scrollable rows ───────────────────────────────────
        self.rows_frame = ctk.CTkScrollableFrame(
            self, fg_color="#ffffff", corner_radius=0)
        self.rows_frame.pack(fill="both", expand=True)

        for i in range(5):
            self.rows_frame.grid_columnconfigure(i, weight=1, uniform="col")

        # ── Bottom bar ────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        bottom = ctk.CTkFrame(self, fg_color="#00BFFF", height=65, corner_radius=0)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            bottom, text="Select a receipt to manage.",
            font=ctk.CTkFont(size=14),
            text_color="#000000"
        )
        self.status_label.pack(side="left", padx=20, pady=10)

        ctk.CTkButton(
            bottom, text="🗑 DELETE",
            fg_color="#FF4444", text_color="#ffffff",
            hover_color="#cc0000", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, width=130, height=45,
            command=self._on_delete
        ).pack(side="right", padx=(5, 20))

        ctk.CTkButton(
            bottom, text="💰 TOGGLE PAID",
            fg_color="#FFD700", text_color="#000000",
            hover_color="#e6c200", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, width=160, height=45,
            command=self._on_toggle_paid
        ).pack(side="right", padx=5)

        self.selected_label = ctk.CTkLabel(
            bottom, text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000"
        )
        self.selected_label.pack(side="right", padx=10)

    # ── Load / Refresh ────────────────────────────────────────
    def load_items(self):
        self.ctrl.selected_receipt_no = None
        self.selected_label.configure(text="")
        self.status_label.configure(text="Select a receipt to print.")
        self.search_var.set("")
        self._filter_start = None
        self._filter_end = None
        self._filter_label_text = "ALL TIME"
        self.date_record_label.configure(text="DATE FILTER:  ALL TIME")
        self._render_rows()

    def _on_search(self):
        self._render_rows(query=self.search_var.get().strip().lower())

    def _render_rows(self, query=""):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        records = self.ctrl.load_all(self._filter_start, self._filter_end)

        if query:
            records = [r for r in records if query in r[2].lower()]

        if not records:
            ctk.CTkLabel(self.rows_frame,
                text="No receipts found.",
                font=ctk.CTkFont(size=16),
                text_color="#888888"
            ).grid(row=0, column=0, columnspan=5, pady=40)
            return

        self._row_frames = []

        for i, (date, time, receipt_no, total, is_paid) in enumerate(records):
            bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
            badge_color = "#228B22" if is_paid else "#FF4444"
            badge_text  = "✔ PAID" if is_paid else "✘ UNPAID"

            row_widgets = []
            for j, val in enumerate([date, time, receipt_no, f"₱{total:.2f}"]):
                lbl = ctk.CTkLabel(self.rows_frame, text=val,
                    font=ctk.CTkFont(size=15), text_color="#000000",
                    anchor="center", justify="center", fg_color=bg
                )
                lbl.grid(row=i*2, column=j, sticky="nsew", ipady=12)
                lbl.bind("<Button-1>", lambda e, rno=receipt_no: self._select_row(rno))
                row_widgets.append(lbl)

            # Badge cell
            badge_lbl = ctk.CTkLabel(self.rows_frame, text=badge_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff", fg_color=badge_color,
                corner_radius=8, width=90, anchor="center"
            )
            badge_lbl.grid(row=i*2, column=4, pady=8, sticky="")
            self.rows_frame.columnconfigure(4, weight=1, uniform="col")
            badge_lbl.bind("<Button-1>", lambda e, rno=receipt_no: self._select_row(rno))
            row_widgets.append(badge_lbl)

            # Separator row
            for j in range(5):
                sep = ctk.CTkFrame(self.rows_frame, fg_color="#dddddd", height=1, corner_radius=0)
                sep.grid(row=i*2+1, column=j, sticky="ew")

            self._row_frames.append((receipt_no, row_widgets, bg))

    def _select_row(self, receipt_no):
        for rno, widgets, bg in self._row_frames:
            for w in widgets:
                if w.cget("text") not in ["✔ PAID", "✘ UNPAID"]:
                    w.configure(fg_color=bg)

        for rno, widgets, bg in self._row_frames:
            if rno == receipt_no:
                for w in widgets:
                    if w.cget("text") not in ["✔ PAID", "✘ UNPAID"]:
                        w.configure(fg_color="#00BFFF")

        self.ctrl.select(receipt_no)
        self.selected_label.configure(text=f"Selected: {receipt_no}")
        self.status_label.configure(text="Ready — Print, Toggle Paid, or Delete.")

    # ── Toggle Paid ───────────────────────────────────────────
    def _on_toggle_paid(self):
        if not self.ctrl.selected_receipt_no:
            self._show_msg("Please select a receipt first!", error=True)
            return
        err = self.ctrl.toggle_paid()
        if err:
            self._show_msg(err, error=True)
        else:
            self._render_rows()
            self.selected_label.configure(text="")
            self.status_label.configure(text="Payment status updated.")

    # ── Delete ────────────────────────────────────────────────
    def _on_delete(self):
        if not self.ctrl.selected_receipt_no:
            self._show_msg("Please select a receipt first!", error=True)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Confirm Delete")
        popup.geometry("380x180")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup,
            text=f"Delete receipt {self.ctrl.selected_receipt_no}?\nThis cannot be undone.",
            font=ctk.CTkFont(size=14), text_color="#000000", justify="center"
        ).pack(pady=25)

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack()

        def confirm():
            popup.destroy()
            self.ctrl.delete_selected()
            self.selected_label.configure(text="")
            self.status_label.configure(text="Receipt deleted.")
            self._render_rows()

        ctk.CTkButton(btn_row, text="YES, DELETE",
            fg_color="#FF4444", text_color="#ffffff",
            hover_color="#cc0000", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=0, width=140, height=45,
            command=confirm
        ).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="CANCEL",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=0, width=140, height=45,
            command=popup.destroy
        ).pack(side="left", padx=10)

    # ── Print / View ──────────────────────────────────────────
    def _on_print(self):
        if not self.ctrl.selected_receipt_no:
            self._show_msg("Please select a receipt first!", error=True)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Receipt Options")
        popup.geometry("380x230")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup,
            text=f"Receipt: {self.ctrl.selected_receipt_no}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#000000"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(popup,
            text="What would you like to do?",
            font=ctk.CTkFont(size=13),
            text_color="#555555"
        ).pack(pady=(0, 15))

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=5)

        def do_view():
            popup.destroy()
            cart, err = self.ctrl.get_selected_cart()
            if err:
                self._show_msg(err, error=True)
                return
            import controllers.controller as c
            c._app.receipt_page.load_receipt(cart, self.ctrl.selected_receipt_no, back_to="receipts")
            controller.navigate("receipt")

        def do_pdf():
            popup.destroy()
            result = self.ctrl.print_selected_pdf()
            self._show_msg(result)

        def do_usb():
            popup.destroy()
            result = self.ctrl.print_selected_usb()
            self._show_msg(result)

        ctk.CTkButton(btn_row, text="👁 VIEW",
            fg_color="#00BFFF", text_color="#000000",
            hover_color="#009fd4", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, width=100, height=50,
            command=do_view
        ).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="📄 PDF",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, width=100, height=50,
            command=do_pdf
        ).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="🖨 USB",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0, width=100, height=50,
            command=do_usb
        ).pack(side="left", padx=8)

    # ── Date Filter ───────────────────────────────────────────
    def _open_date_filter(self):
        from datetime import date, timedelta, datetime
        popup = ctk.CTkToplevel(self)
        popup.title("Filter by Date")
        popup.geometry("420x520")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="📅  FILTER BY DATE",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#000000"
        ).pack(pady=(15, 5))
        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=20)

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

        yesterday    = today - timedelta(days=1)
        week_start   = today - timedelta(days=today.weekday())
        lweek_start  = week_start - timedelta(days=7)
        lweek_end    = week_start - timedelta(days=1)
        month_start  = today.replace(day=1)
        lmonth_end   = month_start - timedelta(days=1)
        lmonth_start = lmonth_end.replace(day=1)
        year_start   = today.replace(month=1, day=1)
        lyear_start  = year_start.replace(year=today.year - 1)
        lyear_end    = year_start - timedelta(days=1)

        buttons = [
            ("Today",      today,        today),
            ("Yesterday",  yesterday,    yesterday),
            ("This Week",  week_start,   today),
            ("Last Week",  lweek_start,  lweek_end),
            ("This Month", month_start,  today),
            ("Last Month", lmonth_start, lmonth_end),
            ("This Year",  year_start,   today),
            ("Last Year",  lyear_start,  lyear_end),
        ]
        for col, (label, s, e) in enumerate(buttons):
            btn = q(label, s, e)
            btn.grid(row=col // 2, column=col % 2, padx=4, pady=3, sticky="ew")
            quick_frame.grid_columnconfigure(col % 2, weight=1)

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
        ctk.CTkLabel(popup, text="Or enter a custom date range:",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#000000"
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

        if self._filter_start:
            start_e.insert(0, self._filter_start)
        if self._filter_end:
            end_e.insert(0, self._filter_end)

        def apply():
            s = start_e.get().strip()
            e = end_e.get().strip()
            if not s and not e:
                self._filter_start = None
                self._filter_end = None
                self._filter_label_text = "ALL TIME"
            else:
                try:
                    datetime.strptime(s, "%Y-%m-%d")
                    datetime.strptime(e, "%Y-%m-%d")
                except ValueError:
                    self._show_msg("Invalid date format!\nUse YYYY-MM-DD", error=True)
                    return
                self._filter_start = s
                self._filter_end = e
                if s == e:
                    self._filter_label_text = datetime.strptime(s, "%Y-%m-%d").strftime("%B %d, %Y").upper()
                else:
                    ds = datetime.strptime(s, "%Y-%m-%d").strftime("%b %d, %Y").upper()
                    de = datetime.strptime(e, "%Y-%m-%d").strftime("%b %d, %Y").upper()
                    self._filter_label_text = f"{ds}  →  {de}"
            self.date_record_label.configure(text=f"DATE FILTER:  {self._filter_label_text}")
            self.ctrl.selected_receipt_no = None
            self.selected_label.configure(text="")
            self._render_rows()
            popup.destroy()

        ctk.CTkButton(popup, text="SHOW RECORDS",
            fg_color="#1a73e8", text_color="#ffffff",
            hover_color="#1558b0", corner_radius=4,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42, width=200, command=apply
        ).pack(pady=10)
        ctk.CTkButton(popup, text="Cancel",
            fg_color="transparent", text_color="#555555",
            hover_color="#f0f0f0", corner_radius=4,
            font=ctk.CTkFont(size=13),
            height=32, command=popup.destroy
        ).pack()

    def _show_msg(self, msg, error=False):
        p = ctk.CTkToplevel(self)
        p.title("Info")
        p.geometry("340x160")
        p.resizable(False, False)
        p.grab_set()
        ctk.CTkLabel(p, text=msg,
            font=ctk.CTkFont(size=14), justify="center",
            text_color="#FF4444" if error else "#000000"
        ).pack(expand=True)
        ctk.CTkButton(p, text="OK", command=p.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)