import customtkinter as ctk
from controllers import controller
from controllers.dashboard_controller import (
    on_inventory_click, on_sell_click, on_receipts_click, on_exit_click
)


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#000000", height=100, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="INVENTORY MANAGEMENT SYSTEM",
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=20, pady=10)

        # ── Body ──────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        # ── LEFT: Sidebar ─────────────────────────────────────
        sidebar = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0, width=500)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        # ── Role badge ────────────────────────────────────────
        self.role_badge = ctk.CTkLabel(
            sidebar, text="🧑 Staff",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#555555",
            fg_color="#f0f0f0",
            corner_radius=6,
            height=40
        )
        self.role_badge.pack(fill="x", pady=(0, 8), padx=2)

        btn_configs = [
            ("INVENTORY",    "#ffffff", "#000000", "#e0e0e0", on_inventory_click),
            ("SELL",         "#90EE90", "#000000", "#7dd67d", on_sell_click),
            ("RECEIPTS",     "#00BFFF", "#000000", "#009fd4", on_receipts_click),
            ("USER",         "#d3d3d3", "#000000", "#c0c0c0", lambda: controller.navigate("user")),
            ("📊 TOP 10",    "#FFD700", "#000000", "#e6c200", lambda: self._show_top10_popup()),
            ("EXIT",         "#FF4444", "#000000", "#cc0000", on_exit_click),
        ]

        for text, bg, fg, hover, cmd in btn_configs:
            btn = ctk.CTkButton(
                sidebar, text=text,
                fg_color=bg, text_color=fg, hover_color=hover,
                border_color="#000000", border_width=2,
                font=ctk.CTkFont(size=50, weight="bold"),
                corner_radius=0, width=500, height=120,
                command=cmd
            )
            btn.pack(fill="x", pady=6)

        # ── MIDDLE: Stats + Pie chart ─────────────────────────
        middle = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        middle.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # ── Profit / Sales summary cards ──────────────────────
        summary_frame = ctk.CTkFrame(middle, fg_color="#ffffff", corner_radius=0)
        summary_frame.pack(fill="x", pady=(5, 8))

        for i in range(4):
            summary_frame.grid_columnconfigure(i, weight=1, uniform="sc")

        card_data = [
            ("TODAY",      "today"),
            ("THIS WEEK",  "this_week"),
            ("THIS MONTH", "this_month"),
            ("THIS YEAR",  "this_year"),
        ]
        self._summary_labels = {}
        for col, (label, key) in enumerate(card_data):
            card = ctk.CTkFrame(summary_frame, fg_color="#000000", corner_radius=8,
                                border_color="#000000", border_width=1)
            card.grid(row=0, column=col, padx=4, sticky="nsew", ipady=6)

            ctk.CTkLabel(card, text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#aaaaaa"
            ).pack(pady=(8, 2))

            sales_lbl = ctk.CTkLabel(card, text="Sales: —",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#00BFFF"
            )
            sales_lbl.pack()

            profit_lbl = ctk.CTkLabel(card, text="Profit: —",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#90EE90"
            )
            profit_lbl.pack(pady=(0, 8))

            self._summary_labels[key] = (sales_lbl, profit_lbl)

        # Stats card
        stats_card = ctk.CTkFrame(
            middle, fg_color="#00BFFF", corner_radius=8, border_color="#000000", border_width=1
        )
        stats_card.pack(fill="x", pady=(5, 10), ipady=8)

        self.lbl_total_items = self._stat_label(stats_card, "Total Items: —")
        self.lbl_total_value = self._stat_label(stats_card, "Total Inventory Value: —")
        self.lbl_below_rop   = self._stat_label(stats_card, "Items Below Reorder Point: —")
        self.lbl_stockout    = self._stat_label(stats_card, "Stockout Risk Items: —")

        # Chart label
        ctk.CTkLabel(
            middle,
            text="Total Items for Each Classification:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(anchor="w", padx=5, pady=(5, 2))

        # Pie chart frame
        self.chart_frame = ctk.CTkFrame(middle, fg_color="#f0f0f0", corner_radius=8,
                                        border_color="#cccccc", border_width=1)
        self.chart_frame.pack(fill="both", expand=True, pady=(0, 5))

        # ── RIGHT: Reorder Point Counter ──────────────────────
        right = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0, width=360)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        rop_card = ctk.CTkFrame(
            right, fg_color="#00BFFF", corner_radius=8, border_color="#000000", border_width=1
        )
        rop_card.pack(fill="x", pady=(5, 10), ipady=8)

        ctk.CTkLabel(
            rop_card,
            text="Reorder Point Counter",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#000000"
        ).pack(anchor="w", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            rop_card,
            text="Items Below ROP:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000"
        ).pack(anchor="w", padx=15, pady=(0, 6))

        self.rop_items_frame = ctk.CTkScrollableFrame(
            rop_card, fg_color="#00BFFF", corner_radius=0, height=220
        )
        self.rop_items_frame.pack(fill="x", padx=10, pady=(0, 10))

    def _stat_label(self, parent, text):
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000", anchor="w"
        )
        lbl.pack(anchor="w", padx=15, pady=4)
        return lbl

    # ── Load data (called on navigate) ───────────────────────
    def load_items(self):
        self._load_stats()
        self._load_summary()
        self._load_pie_chart()
        self._load_rop_items()
        self.refresh_role_ui()

    def _show_top10_popup(self):
        from database.database import get_top10_profit_products
        import tkinter as tk

        popup = ctk.CTkToplevel(self)
        popup.title("Top 10 Products by Profit")
        popup.geometry("900x600")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()

        ctk.CTkLabel(popup, text="📊  TOP 10 PRODUCTS BY PROFIT",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#000000"
        ).pack(pady=(20, 5))

        ctk.CTkFrame(popup, fg_color="#cccccc", height=1, corner_radius=0).pack(fill="x", padx=20)

        data = get_top10_profit_products()

        if not data:
            ctk.CTkLabel(popup,
                text="No sales data yet.\nComplete some transactions first.",
                font=ctk.CTkFont(size=15), text_color="#888888", justify="center"
            ).pack(expand=True)
            return

        # ── Bar chart using tkinter Canvas ────────────────────
        chart_frame = ctk.CTkFrame(popup, fg_color="#ffffff", corner_radius=0)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=15)

        canvas_w, canvas_h = 860, 440
        canvas = tk.Canvas(chart_frame, width=canvas_w, height=canvas_h,
                           bg="#ffffff", highlightthickness=0)
        canvas.pack()

        margin_left  = 180
        margin_right = 30
        margin_top   = 30
        margin_bottom= 60
        bar_area_w   = canvas_w - margin_left - margin_right
        bar_area_h   = canvas_h - margin_top  - margin_bottom

        max_profit = max(row[1] for row in data) or 1
        bar_count  = len(data)
        bar_gap    = 12
        bar_w      = (bar_area_w - bar_gap * (bar_count + 1)) // bar_count

        bar_colors = ["#4488FF","#90EE90","#FFD700","#FF6B6B","#00BFFF",
                      "#FFA500","#9B59B6","#2ECC71","#E74C3C","#1ABC9C"]

        for idx, (name, profit, sales) in enumerate(data):
            x1 = margin_left + bar_gap + idx * (bar_w + bar_gap)
            x2 = x1 + bar_w
            bar_h = int((profit / max_profit) * bar_area_h)
            y1 = margin_top + bar_area_h - bar_h
            y2 = margin_top + bar_area_h

            color = bar_colors[idx % len(bar_colors)]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

            # Profit label on top of bar
            canvas.create_text(
                (x1 + x2) // 2, y1 - 8,
                text=f"₱{profit:,.0f}",
                font=("Arial", 9, "bold"),
                fill="#000000"
            )

            # Item name below bar (rotated using angled placement)
            short_name = name[:14] + "…" if len(name) > 14 else name
            canvas.create_text(
                (x1 + x2) // 2, y2 + 10,
                text=short_name,
                font=("Arial", 9),
                fill="#000000",
                angle=35,
                anchor="nw"
            )

        # Y-axis line
        canvas.create_line(margin_left, margin_top,
                           margin_left, margin_top + bar_area_h,
                           fill="#cccccc", width=1)
        # X-axis line
        canvas.create_line(margin_left, margin_top + bar_area_h,
                           canvas_w - margin_right, margin_top + bar_area_h,
                           fill="#cccccc", width=1)

        # Y-axis labels
        for i in range(5):
            val = max_profit * i / 4
            y   = margin_top + bar_area_h - int((val / max_profit) * bar_area_h)
            canvas.create_text(margin_left - 8, y,
                text=f"₱{val:,.0f}", font=("Arial", 9),
                fill="#555555", anchor="e")
            canvas.create_line(margin_left - 4, y,
                               margin_left, y, fill="#aaaaaa")

        ctk.CTkButton(popup, text="CLOSE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", corner_radius=0,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120, height=38,
            command=popup.destroy
        ).pack(pady=(0, 15))

    def _load_summary(self):
        from database.database import get_sales_and_profit_summary
        data = get_sales_and_profit_summary()
        for key, (sales_lbl, profit_lbl) in self._summary_labels.items():
            sales, profit = data.get(key, (0, 0))
            sales_lbl.configure(text=f"Sales: ₱{sales:,.2f}")
            profit_lbl.configure(text=f"Profit: ₱{profit:,.2f}")

    def refresh_role_ui(self):
        from controllers.controller import is_admin

        if is_admin():
            self.role_badge.configure(text="👑 Admin", text_color="#2c7a2c")
        else:
            self.role_badge.configure(text="🧑 Staff", text_color="#555555")

        # INVENTORY button is always visible — staff can access it
        # but admin-only actions are hidden inside the inventory page itself

    def _load_stats(self):
        from database.database import get_all_items
        items = get_all_items()

        total_items  = len(items)
        total_value  = sum(float(i[3]) * int(i[5]) for i in items)   # unit_cost * stock
        below_rop    = 0
        stockout     = 0

        from database.database import get_connection
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT current_stock, rop, safety_stock FROM items")
        rows = cur.fetchall()
        conn.close()

        for stock, rop, ss in rows:
            stock = float(stock or 0)
            rop   = float(rop   or 0)
            ss    = float(ss    or 0)
            if stock <= rop:
                below_rop += 1
            if stock <= ss:
                stockout  += 1

        self.lbl_total_items.configure(text=f"Total Items: {total_items}")
        self.lbl_total_value.configure(text=f"Total Inventory Value: ₱{total_value:,.2f}")
        self.lbl_below_rop.configure(  text=f"Items Below Reorder Point: {below_rop}")
        self.lbl_stockout.configure(   text=f"Stockout Risk Items: {stockout}")

    def _load_pie_chart(self):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        from database.database import get_all_items
        items = get_all_items()

        count = {"A": 0, "B": 0, "C": 0}
        for item in items:
            cls = item[7]
            if cls in count:
                count[cls] += 1

        total = sum(count.values())

        if total == 0:
            ctk.CTkLabel(
                self.chart_frame,
                text="📊 No classification data yet.\nGo to Reorder Table → select an item\n→ Run Reorder Computation first.",
                font=ctk.CTkFont(size=14),
                text_color="#555555",
                justify="center"
            ).pack(expand=True, pady=40)
            return

        # ── Canvas pie chart (no matplotlib needed) ───────────
        import tkinter as tk
        import math

        canvas_size = 750
        canvas = tk.Canvas(
            self.chart_frame,
            width=canvas_size, height=canvas_size,
            bg="#f0f0f0", highlightthickness=0
        )
        canvas.pack(side="left", padx=(0, 0), pady=0)

        cx, cy, r = canvas_size // 2, canvas_size // 2, 340

        color_map = {"A": "#4488FF", "B": "#9B59B6", "C": "#A0522D"}
        label_map = {"A": "A Items", "B": "B Items", "C": "C Items"}

        start_angle = 90
        slices = [(cls, count[cls]) for cls in ["A", "B", "C"] if count[cls] > 0]

        for cls, val in slices:
            pct   = val / total
            sweep = pct * 360
            color = color_map[cls]

            canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=start_angle, extent=sweep,
                fill=color, outline="#ffffff", width=2
            )

            mid_deg   = start_angle + sweep / 2
            mid_rad   = math.radians(mid_deg)
            label_r   = r * 0.62
            lx = cx + label_r * math.cos(mid_rad)
            ly = cy - label_r * math.sin(mid_rad)

            canvas.create_text(
                lx, ly,
                text=f"{pct*100:.0f}%",
                fill="#ffffff",
                font=("Arial", 24, "bold")
            )
            start_angle += sweep

        # ── Legend ────────────────────────────────────────────
        legend = ctk.CTkFrame(self.chart_frame, fg_color="#f0f0f0", corner_radius=0)
        legend.pack(side="left", padx=20, pady=10, anchor="center")

        for cls in ["A", "B", "C"]:
            if count[cls] == 0:
                continue
            pct = count[cls] / total * 100
            row = ctk.CTkFrame(legend, fg_color="transparent")
            row.pack(anchor="w", pady=8)

            ctk.CTkFrame(row, fg_color=color_map[cls],
                width=22, height=22, corner_radius=4
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(row,
                text=f"{label_map[cls]}  {pct:.0f}%  ({count[cls]} items)",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#000000"
            ).pack(side="left")

    def _load_rop_items(self):
        for w in self.rop_items_frame.winfo_children():
            w.destroy()

        from database.database import get_connection
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT item_name, current_stock, rop, max_level
            FROM items
            WHERE rop > 0 AND current_stock <= rop
            ORDER BY current_stock ASC
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.rop_items_frame,
                text="✅ All items are above ROP!",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#006600"
            ).pack(pady=10)
            return

        for item_name, stock, rop, max_level in rows:
            stock     = float(stock     or 0)
            rop       = float(rop       or 0)
            max_level = float(max_level or 1)

            row = ctk.CTkFrame(self.rop_items_frame, fg_color="transparent", corner_radius=0)
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row,
                text=f"{item_name}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#000000", anchor="w", width=120, wraplength=115
            ).pack(side="left")

            bar_bg = ctk.CTkFrame(row, fg_color="#dddddd", corner_radius=4, height=18, width=120)
            bar_bg.pack(side="left", padx=(5, 0))
            bar_bg.pack_propagate(False)

            fill_pct = min(stock / max_level, 1.0) if max_level > 0 else 0
            fill_w   = max(int(fill_pct * 120), 4)

            from database.database import get_connection as gc
            cn = gc(); cr = cn.cursor()
            cr.execute("SELECT safety_stock FROM items WHERE item_name=?", (item_name,))
            ss_row = cr.fetchone(); cn.close()
            ss = float(ss_row[0]) if ss_row and ss_row[0] else 0

            bar_color = "#FF4444" if stock <= ss else "#FF8C00"

            ctk.CTkFrame(bar_bg, fg_color=bar_color, corner_radius=4, height=18,
                width=fill_w
            ).place(x=0, y=0)

            ctk.CTkLabel(row,
                text=f"{int(stock)}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#000000", width=35, anchor="w"
            ).pack(side="left", padx=(6, 0))