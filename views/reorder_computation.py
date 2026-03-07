import customtkinter as ctk
import math
from controllers import controller
from database.database import get_all_items, update_reorder_info, update_all_classifications, get_item_by_barcode

class ReorderComputationPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)

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
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Select Item ──────────────────────────────────────
        select_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=5,
                                    border_color="#000000", border_width=1)
        select_frame.pack(pady=20, ipadx=10, ipady=5)

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
        )
        self.item_dropdown.pack(padx=1, pady=1)

        # ── Two Panels ───────────────────────────────────────
        panels_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        panels_frame.pack(fill="x", pady=20)

        # Left panel
        left_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                   corner_radius=5, border_color="#000000", border_width=1)
        left_panel.pack(side="left", expand=True, fill="both", padx=(0, 10))

        ctk.CTkLabel(left_panel, text="Demand Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000").pack(pady=10)

        demand_fields = ["Avg Demand", "Std.Dev", "Lead Time", "Service Lvl"]
        self.demand_entries = {}

        for field in demand_fields:
            row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"{field}  :",
                font=ctk.CTkFont(size=16), text_color="#000000",
                width=120, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, width=200, height=30,
                                  fg_color="#ffffff", border_color="#000000")
            entry.pack(side="left", padx=5)
            self.demand_entries[field] = entry

        # Right panel
        right_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                    corner_radius=5, border_color="#000000", border_width=1)
        right_panel.pack(side="left", expand=True, fill="both", padx=(10, 0))

        ctk.CTkLabel(right_panel, text="Reorder Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000").pack(pady=10)

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

        # ── Buttons ──────────────────────────────────────────
        btn_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        btn_frame.pack(pady=20)

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

    def load_items(self):
        items = get_all_items()
        item_names = [f"{item[0]} - {item[1]}" for item in items]
        self.item_dropdown.configure(values=item_names)
        if item_names:
            self.item_var.set(item_names[0])

    def set_entry(self, entry, value):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(value))
        entry.configure(state="disabled")

    def calculate(self):
        try:
            avg_demand  = float(self.demand_entries["Avg Demand"].get())
            std_dev     = float(self.demand_entries["Std.Dev"].get())
            lead_time   = float(self.demand_entries["Lead Time"].get())
            service_lvl = float(self.demand_entries["Service Lvl"].get())

            # Formulas
            safety_stock = round(service_lvl * std_dev * math.sqrt(lead_time), 2)
            rop          = round((avg_demand * lead_time) + safety_stock, 2)
            min_level    = rop
            max_level    = round(safety_stock + (avg_demand * lead_time), 2)

            self.set_entry(self.reorder_entries["Safety Stock"], safety_stock)
            self.set_entry(self.reorder_entries["Reorder Point"], rop)
            self.set_entry(self.reorder_entries["Min Level"], min_level)
            self.set_entry(self.reorder_entries["Max Level"], max_level)

        except ValueError:
            popup = ctk.CTkToplevel(self)
            popup.title("Error")
            popup.geometry("300x150")
            popup.resizable(False, False)
            popup.grab_set()
            ctk.CTkLabel(popup, text="Please fill all fields\nwith valid numbers!",
                font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
            ctk.CTkButton(popup, text="OK", command=popup.destroy,
                fg_color="#d3d3d3", text_color="#000000",
                corner_radius=0, width=100).pack(pady=10)

    def apply_to_table(self):
        try:
            selected = self.item_var.get()
            if not selected:
                return
            barcode = selected.split(" - ")[0]

            safety_stock = float(self.reorder_entries["Safety Stock"].get())
            rop          = float(self.reorder_entries["Reorder Point"].get())
            min_level    = float(self.reorder_entries["Min Level"].get())
            max_level    = float(self.reorder_entries["Max Level"].get())
            avg_demand   = float(self.demand_entries["Avg Demand"].get())

            # Get current stock for status
            item = get_item_by_barcode(barcode)
            current_stock = item[6]

            # Status logic
            if current_stock <= safety_stock:
                status = "CRITICAL"
            elif current_stock <= rop:
                status = "REORDER"
            else:
                status = "OK"

            # Save reorder info for this item only
            update_reorder_info(barcode, safety_stock, rop, min_level, max_level, status, avg_demand)

            # Recompute ABC classification only among computed items
            update_all_classifications()

            # Show success popup then navigate
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
            popup = ctk.CTkToplevel(self)
            popup.title("Error")
            popup.geometry("300x150")
            popup.resizable(False, False)
            popup.grab_set()
            ctk.CTkLabel(popup, text="Please calculate first!",
                font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
            ctk.CTkButton(popup, text="OK", command=popup.destroy,
                fg_color="#d3d3d3", text_color="#000000",
                corner_radius=0, width=100).pack(pady=10)