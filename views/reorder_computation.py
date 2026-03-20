import customtkinter as ctk
import math
import statistics
from controllers import controller
from database.database import (
    get_all_items, update_reorder_info, update_classification_for_item,
    get_item_by_barcode
)

# Service level table
SERVICE_LEVELS = {
    "90%  (Z = 1.28)":  (1.28, "10% risk of stockout\n(Lower inventory cost,\nhigher stockout risk)"),
    "95%  (Z = 1.65)":  (1.65, "5% risk of stockout\n(Balanced approach)"),
    "97.5%  (Z = 1.96)": (1.96, "2.5% chance of stockout\n(High safety stock and cost)"),
    "99%  (Z = 2.33)":  (2.33, "1% chance of stockout\n(Very high safety\nstock and cost)"),
}

AVG_DEMAND_BASIS = ["Weekly (÷7)", "Monthly (÷30)", "Annually (÷365)"]


class ReorderComputationPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#ffffff", height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#f0f0f0",
            font=ctk.CTkFont(size=40, weight="bold"),
            corner_radius=0, width=60, height=60,
            command=lambda: controller.navigate("reorder_table")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text="GENERATE REORDER POINT / REORDER COMPUTATION PANEL",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Select Item ──────────────────────────────────────
        select_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=5,
                                    border_color="#000000", border_width=1)
        select_frame.pack(pady=(10, 15), ipadx=10, ipady=5)

        ctk.CTkLabel(
            select_frame, text="Select Item:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(side="left", padx=10)

        dropdown_wrapper = ctk.CTkFrame(select_frame, fg_color="#000000",
                                        corner_radius=5, border_color="#000000", border_width=1)
        dropdown_wrapper.pack(side="left", padx=10)

        self.item_var = ctk.StringVar(value="")
        self.item_dropdown = ctk.CTkOptionMenu(
            dropdown_wrapper,
            variable=self.item_var,
            values=[],
            font=ctk.CTkFont(size=16),
            width=300, height=40,
            fg_color="#ffffff", text_color="#000000",
            button_color="#d3d3d3", button_hover_color="#c0c0c0",
            dropdown_fg_color="#ffffff", dropdown_text_color="#000000",
            command=self._on_item_selected
        )
        self.item_dropdown.pack(padx=1, pady=1)

        # ── Two Panels ───────────────────────────────────────
        panels_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        panels_frame.pack(fill="x", pady=5)

        # ════════════════════════════════════════════════════
        # LEFT PANEL — Demand Information
        # ════════════════════════════════════════════════════
        left_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                   corner_radius=5, border_color="#000000", border_width=1)
        left_panel.pack(side="left", expand=True, fill="both", padx=(0, 10))

        ctk.CTkLabel(left_panel, text="Demand Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000").pack(pady=8)

        # — Demand (raw total from demand_log) ————————————
        demand_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        demand_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(demand_row, text="Demand  :",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#cc0000",
            width=120, anchor="w").pack(side="left")
        self.demand_display = ctk.CTkEntry(demand_row, width=200, height=30,
            fg_color="#fffbe6", border_color="#cc0000", border_width=2,
            font=ctk.CTkFont(size=15, weight="bold"),
            state="disabled")
        self.demand_display.pack(side="left", padx=5)

        # — Avg Demand basis dropdown + display ————————————
        avg_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        avg_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(avg_row, text="Avg Demand  :",
            font=ctk.CTkFont(size=16), text_color="#000000",
            width=120, anchor="w").pack(side="left")
        self.avg_demand_display = ctk.CTkEntry(avg_row, width=130, height=30,
            fg_color="#e8f5e9", border_color="#000000",
            font=ctk.CTkFont(size=15),
            state="disabled")
        self.avg_demand_display.pack(side="left", padx=5)

        self.avg_basis_var = ctk.StringVar(value=AVG_DEMAND_BASIS[0])
        ctk.CTkOptionMenu(
            avg_row,
            variable=self.avg_basis_var,
            values=AVG_DEMAND_BASIS,
            font=ctk.CTkFont(size=13),
            width=140, height=30,
            fg_color="#ffffff", text_color="#000000",
            button_color="#aaaaaa", button_hover_color="#888888",
            dropdown_fg_color="#ffffff", dropdown_text_color="#000000",
            command=lambda _: self._recalc_avg_demand()
        ).pack(side="left", padx=4)

        # — Std Dev (auto or manual) ————————————————————————
        std_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        std_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(std_row, text="Std.Dev  :",
            font=ctk.CTkFont(size=16), text_color="#000000",
            width=120, anchor="w").pack(side="left")
        self.std_dev_entry = ctk.CTkEntry(std_row, width=200, height=30,
            fg_color="#ffffff", border_color="#000000")
        self.std_dev_entry.pack(side="left", padx=5)
        self.std_auto_label = ctk.CTkLabel(std_row, text="",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#555555")
        self.std_auto_label.pack(side="left", padx=4)

        # — Lead Time ——————————————————————————————————————
        lt_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        lt_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(lt_row, text="Lead Time  :",
            font=ctk.CTkFont(size=16), text_color="#000000",
            width=120, anchor="w").pack(side="left")
        self.lead_time_entry = ctk.CTkEntry(lt_row, width=200, height=30,
            fg_color="#ffffff", border_color="#000000")
        self.lead_time_entry.pack(side="left", padx=5)

        # — Service Level (dropdown + z-value + interpretation) ——————
        svc_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        svc_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(svc_row, text="Service Lvl  :",
            font=ctk.CTkFont(size=16), text_color="#000000",
            width=120, anchor="w").pack(side="left")

        self.svc_var = ctk.StringVar(value=list(SERVICE_LEVELS.keys())[1])  # default 95%
        ctk.CTkOptionMenu(
            svc_row,
            variable=self.svc_var,
            values=list(SERVICE_LEVELS.keys()),
            font=ctk.CTkFont(size=13),
            width=220, height=30,
            fg_color="#ffffff", text_color="#000000",
            button_color="#aaaaaa", button_hover_color="#888888",
            dropdown_fg_color="#ffffff", dropdown_text_color="#000000",
            command=self._on_service_level_change
        ).pack(side="left", padx=5)

        # Service level interpretation label
        svc_info_row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
        svc_info_row.pack(fill="x", padx=10, pady=(0, 6))
        self.svc_info_label = ctk.CTkLabel(
            svc_info_row, text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#1a5276", justify="left", anchor="w"
        )
        self.svc_info_label.pack(side="left", padx=(130, 0))
        self._on_service_level_change(self.svc_var.get())  # init label

        # ════════════════════════════════════════════════════
        # RIGHT PANEL — Reorder Information
        # ════════════════════════════════════════════════════
        right_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                    corner_radius=5, border_color="#000000", border_width=1)
        right_panel.pack(side="left", expand=True, fill="both", padx=(10, 0))

        ctk.CTkLabel(right_panel, text="Reorder Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000").pack(pady=8)

        reorder_fields = ["Safety Stock", "Reorder Point", "Min Level", "Max Level"]
        self.reorder_entries = {}

        for field in reorder_fields:
            row = ctk.CTkFrame(right_panel, fg_color="#d3d3d3", corner_radius=0)
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"{field}  :",
                font=ctk.CTkFont(size=16), text_color="#000000",
                width=130, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, width=200, height=30,
                                  fg_color="#ffffff", border_color="#000000",
                                  state="disabled")
            entry.pack(side="left", padx=5)
            self.reorder_entries[field] = entry

        # Note about Min Level = Reorder Point
        ctk.CTkLabel(right_panel,
            text="ℹ  Reorder Point = Min Level",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#555555"
        ).pack(padx=10, anchor="w", pady=(0, 4))

        # Max Level formula note
        ctk.CTkLabel(right_panel,
            text="ℹ  Max Level = ROP + (Avg Demand × Lead Time)",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#555555"
        ).pack(padx=10, anchor="w", pady=(0, 8))

        # ── Buttons ──────────────────────────────────────────
        btn_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="CALCULATE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=20, width=200, height=45,
            command=self.calculate
        ).pack(side="left", padx=20)

        ctk.CTkButton(btn_frame, text="APPLY TO TABLE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=20, width=200, height=45,
            command=self.apply_to_table
        ).pack(side="left", padx=20)

        # internal state
        self._current_demand_qty = 0

    # ─────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────
    def _set_entry(self, entry, value):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(value))
        entry.configure(state="disabled")

    def _on_service_level_change(self, choice):
        _, interp = SERVICE_LEVELS.get(choice, (1.65, ""))
        self.svc_info_label.configure(text=interp)

    def _on_item_selected(self, choice):
        """Auto-populate Demand and Avg Demand when item is selected."""
        self._populate_demand(choice)

    def _get_selected_barcode(self):
        selected = self.item_var.get()
        if not selected:
            return None
        return selected.split(" - ")[0]

    def _populate_demand(self, choice=None):
        """Load total demand and auto-fill Avg Demand + Std Dev for selected item."""
        from database.database import get_items_with_demand
        barcode = self._get_selected_barcode()
        if not barcode:
            return

        # Get all-time cumulative demand for this item
        all_items = get_items_with_demand()
        demand_qty = 0
        for row in all_items:
            if str(row[0]) == str(barcode):
                demand_qty = int(row[6])
                break

        self._current_demand_qty = demand_qty

        # Show raw demand
        self._set_entry(self.demand_display, demand_qty)

        # Auto-compute avg demand
        self._recalc_avg_demand()

        # Auto-compute Std Dev from demand_log daily records
        self._recalc_std_dev(barcode)

    def _recalc_avg_demand(self):
        """Recompute avg demand based on selected basis."""
        basis = self.avg_basis_var.get()
        demand = self._current_demand_qty

        if "Weekly" in basis:
            avg = round(demand / 7, 2) if demand else 0
        elif "Monthly" in basis:
            avg = round(demand / 30, 2) if demand else 0
        else:  # Annually
            avg = round(demand / 365, 2) if demand else 0

        self._set_entry(self.avg_demand_display, avg)

    def _recalc_std_dev(self, barcode):
        """Auto-compute std dev from daily demand_log records if >= 5 days."""
        from database.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT qty FROM demand_log
            WHERE barcode = ?
            ORDER BY log_date
        """, (barcode,))
        rows = cursor.fetchall()
        conn.close()

        daily_qtys = [r[0] for r in rows]

        if len(daily_qtys) >= 5:
            std = round(statistics.stdev(daily_qtys), 2)
            self.std_dev_entry.configure(state="normal")
            self.std_dev_entry.delete(0, "end")
            self.std_dev_entry.insert(0, str(std))
            self.std_dev_entry.configure(state="normal")  # keep editable
            self.std_auto_label.configure(
                text=f"Auto ({len(daily_qtys)} days)",
                text_color="#1a7a1a"
            )
        else:
            self.std_dev_entry.configure(state="normal")
            self.std_dev_entry.delete(0, "end")
            self.std_auto_label.configure(
                text=f"Manual input ({len(daily_qtys)} day(s) recorded, need 5+)",
                text_color="#cc5500"
            )

    # ─────────────────────────────────────────────────────────
    # Load Items
    # ─────────────────────────────────────────────────────────
    def load_items(self):
        items = get_all_items()
        item_names = [f"{item[0]} - {item[1]}" for item in items]
        self.item_dropdown.configure(values=item_names)
        if item_names:
            self.item_var.set(item_names[0])
            self._populate_demand()

    # ─────────────────────────────────────────────────────────
    # Calculate
    # ─────────────────────────────────────────────────────────
    def calculate(self):
        try:
            avg_demand_raw = self.avg_demand_display.get()
            avg_demand = float(avg_demand_raw) if avg_demand_raw else 0.0

            std_dev   = float(self.std_dev_entry.get())
            lead_time = float(self.lead_time_entry.get())

            svc_key = self.svc_var.get()
            z_value, _ = SERVICE_LEVELS.get(svc_key, (1.65, ""))

            # Formulas — results in whole numbers
            safety_stock  = math.ceil(z_value * std_dev * math.sqrt(lead_time))
            rop           = math.ceil((avg_demand * lead_time) + safety_stock)
            min_level     = rop  # same as ROP
            max_level     = math.ceil(rop + (avg_demand * lead_time))

            self._set_entry(self.reorder_entries["Safety Stock"], safety_stock)
            self._set_entry(self.reorder_entries["Reorder Point"], rop)
            self._set_entry(self.reorder_entries["Min Level"], min_level)
            self._set_entry(self.reorder_entries["Max Level"], max_level)

        except ValueError:
            self._error("Please fill all fields\nwith valid numbers!")

    # ─────────────────────────────────────────────────────────
    # Apply to Table
    # ─────────────────────────────────────────────────────────
    def apply_to_table(self):
        try:
            selected = self.item_var.get()
            if not selected:
                return
            barcode = selected.split(" - ")[0]

            safety_stock = int(self.reorder_entries["Safety Stock"].get())
            rop          = int(self.reorder_entries["Reorder Point"].get())
            min_level    = int(self.reorder_entries["Min Level"].get())
            max_level    = int(self.reorder_entries["Max Level"].get())

            avg_demand_raw = self.avg_demand_display.get()
            avg_demand = float(avg_demand_raw) if avg_demand_raw else 0.0

            item = get_item_by_barcode(barcode)
            current_stock = item[6]

            # Status based on min/max ranges
            if current_stock <= safety_stock:
                status = "CRITICAL"
            elif current_stock <= rop:
                status = "REORDER"
            else:
                status = "OK"

            update_reorder_info(barcode, safety_stock, rop, min_level, max_level, status, avg_demand)
            update_classification_for_item(barcode)

            popup = ctk.CTkToplevel(self)
            popup.title("Applied")
            popup.geometry("350x150")
            popup.resizable(False, False)
            popup.grab_set()
            popup.lift()
            ctk.CTkLabel(popup,
                text=f"✅ Applied to {item[2]}!\nStatus: {status}",
                font=ctk.CTkFont(size=15, weight="bold"),
                justify="center", text_color="#000000"
            ).pack(expand=True)
            ctk.CTkButton(popup, text="OK",
                command=lambda: [popup.destroy(), controller.navigate("reorder_table")],
                fg_color="#90EE90", text_color="#000000",
                corner_radius=0, width=100
            ).pack(pady=10)

        except ValueError:
            self._error("Please calculate first!")

    # ─────────────────────────────────────────────────────────
    # Error popup
    # ─────────────────────────────────────────────────────────
    def _error(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("Error")
        popup.geometry("320x160")
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=message,
            font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)