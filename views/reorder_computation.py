import customtkinter as ctk
from controllers import controller
from database.database import get_all_items

class ReorderComputationPage(ctk.CTkFrame):
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
            command=lambda: controller.navigate("reorder_table")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header,
            text="GENERATE REORDER POINT / REORDER COMPUTATION PANEL",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Select Item Dropdown ──────────────────────────────
        select_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=5,
                                    border_color="#000000", border_width=1)
        select_frame.pack(pady=20, ipadx=10, ipady=5)

        ctk.CTkLabel(
            select_frame, text="Select Item:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(side="left", padx=10)

        # Dropdown wrapper for border
        dropdown_wrapper = ctk.CTkFrame(select_frame, fg_color="#000000",
                                        corner_radius=5, border_color="#000000", border_width=1)
        dropdown_wrapper.pack(side="left", padx=10)

        self.item_var = ctk.StringVar(value="")
        self.item_dropdown = ctk.CTkOptionMenu(
            dropdown_wrapper,
            variable=self.item_var,
            values=[],
            font=ctk.CTkFont(size=16),
            width=300,
            height=40,
            fg_color="#ffffff",
            text_color="#000000",
            button_color="#d3d3d3",
            button_hover_color="#c0c0c0",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
        )
        self.item_dropdown.pack(padx=1, pady=1)

        # ── Two Panels ───────────────────────────────────────
        panels_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        panels_frame.pack(fill="x", pady=20)

        # Left panel - Demand Information
        left_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                   corner_radius=5, border_color="#000000", border_width=1)
        left_panel.pack(side="left", expand=True, fill="both", padx=(0, 10))

        ctk.CTkLabel(
            left_panel, text="Demand Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=10)

        demand_fields = ["Avg Demand", "Std.Dev", "Lead Time", "Service Lvl"]
        self.demand_entries = {}

        for field in demand_fields:
            row = ctk.CTkFrame(left_panel, fg_color="#d3d3d3", corner_radius=0)
            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                row, text=f"{field}  :",
                font=ctk.CTkFont(size=16),
                text_color="#000000",
                width=120, anchor="w"
            ).pack(side="left")

            entry = ctk.CTkEntry(row, width=200, height=30,
                                  fg_color="#ffffff", border_color="#000000")
            entry.pack(side="left", padx=5)
            self.demand_entries[field] = entry

        # Right panel - Reorder Information
        right_panel = ctk.CTkFrame(panels_frame, fg_color="#d3d3d3",
                                    corner_radius=5, border_color="#000000", border_width=1)
        right_panel.pack(side="left", expand=True, fill="both", padx=(10, 0))

        ctk.CTkLabel(
            right_panel, text="Reorder Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=10)

        reorder_fields = ["Safety Stock", "Reorder Point", "Min Level", "Max Level"]
        self.reorder_entries = {}

        for field in reorder_fields:
            row = ctk.CTkFrame(right_panel, fg_color="#d3d3d3", corner_radius=0)
            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                row, text=f"{field}  :",
                font=ctk.CTkFont(size=16),
                text_color="#000000",
                width=130, anchor="w"
            ).pack(side="left")

            entry = ctk.CTkEntry(row, width=200, height=30,
                                  fg_color="#ffffff", border_color="#000000",
                                  state="disabled")
            entry.pack(side="left", padx=5)
            self.reorder_entries[field] = entry

        # ── Buttons ───────────────────────────────────────────
        btn_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame, text="CALCULATE",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=20, width=200, height=45,
            command=self.calculate
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            btn_frame, text="APPLY TO TABLE",
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

    def calculate(self):
        print("CALCULATE clicked")

    def apply_to_table(self):
        print("APPLY TO TABLE clicked")