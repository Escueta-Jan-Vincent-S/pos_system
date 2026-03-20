import customtkinter as ctk
from controllers import controller
from controllers.receipt_controller import print_pdf, print_usb
from database.database import save_receipt as db_save_receipt
from datetime import datetime
import random
import io

class ReceiptPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#ffffff", corner_radius=0)
        self.cart = []
        self.receipt_no = ""
        self.cash = 0
        self.change = 0

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#000000", height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        self._back_target = "inventory"  # default, overridable

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#ffffff", hover_color="#222222",
            font=ctk.CTkFont(size=40, weight="bold"),
            corner_radius=0, width=60, height=60,
            command=lambda: controller.navigate(self._back_target)
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="OFFICIAL RECEIPT",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── Receipt Card ──────────────────────────────────────
        card_border = ctk.CTkFrame(
            body, fg_color="#ffffff", corner_radius=0,
            border_color="#000000", border_width=2,
            width=566, height=756
        )
        card_border.place(relx=0.5, rely=0.5, anchor="center")
        card_border.pack_propagate(False)

        self.card = ctk.CTkScrollableFrame(
            card_border, fg_color="#ffffff", corner_radius=0,
            border_width=0,
            width=560, height=750
        )
        self.card.pack(fill="both", expand=True)

        # ── Bottom Bar ────────────────────────────────────────
        bottom_bar = ctk.CTkFrame(self, fg_color="#1a1a1a", height=70, corner_radius=0)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        ctk.CTkButton(
            bottom_bar, text="🖨️  USB Thermal",
            fg_color="#3a3a3a", text_color="#ffffff",
            hover_color="#555555", border_color="#666666", border_width=1,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=0, width=220, height=46,
            command=self.do_usb_print
        ).pack(side="left", padx=(20, 8), pady=12)

        ctk.CTkButton(
            bottom_bar, text="📄  Save as PDF",
            fg_color="#2e7d32", text_color="#ffffff",
            hover_color="#1b5e20", border_color="#388e3c", border_width=1,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=0, width=220, height=46,
            command=self.do_pdf_print
        ).pack(side="left", padx=8, pady=12)

    def load_receipt(self, cart, receipt_no=None, back_to="inventory", cash=0, change=0):
        self._back_target = back_to
        self.cart = cart
        self.cash = cash
        self.change = change
        # Use provided receipt_no (from sell page) or generate new one
        if receipt_no:
            self.receipt_no = receipt_no
            # Already saved as PAID by sell_controller — don't overwrite
        else:
            self.receipt_no = f"REC{random.randint(10000, 99999)}"
            # Coming from inventory — save as UNPAID
            total = sum(i["selling_price"] * i["quantity"] for i in cart)
            db_save_receipt(cart, total, cash, change, is_paid=0, receipt_no=self.receipt_no)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for widget in self.card.winfo_children():
            widget.destroy()

        def divider(style="solid"):
            if style == "dashed":
                ctk.CTkLabel(self.card,
                    text="- " * 30,
                    font=ctk.CTkFont(size=8),
                    text_color="#aaaaaa").pack(fill="x", padx=10)
            else:
                ctk.CTkFrame(self.card, fg_color="#000000",
                    height=1, corner_radius=0).pack(fill="x", padx=10, pady=3)

        def center_label(text, size=12, bold=False, color="#000000"):
            ctk.CTkLabel(self.card, text=text,
                font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
                text_color=color).pack()

        # ── Store Header Banner ───────────────────────────────
        banner = ctk.CTkFrame(self.card, fg_color="#000000", corner_radius=0, height=36)
        banner.pack(fill="x", padx=10, pady=(8, 0))
        banner.pack_propagate(False)
        ctk.CTkLabel(banner, text="★  LANZ N LINDLY  ★",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.card, text="", height=4).pack()
        center_label("San Pablo City, Laguna", size=11)
        center_label("TEL. NO. : ____________", size=11)
        ctk.CTkLabel(self.card, text="", height=2).pack()
        center_label(f"DATE: {now}", size=10)
        center_label(f"RECEIPT NO: {self.receipt_no}", size=11, bold=True)
        ctk.CTkLabel(self.card, text="", height=4).pack()
        divider()

        # ── Official Receipt Title ────────────────────────────
        title_bg = ctk.CTkFrame(self.card, fg_color="#eeeeee", corner_radius=0, height=32)
        title_bg.pack(fill="x", padx=10, pady=2)
        title_bg.pack_propagate(False)
        ctk.CTkLabel(title_bg, text="─── OFFICIAL RECEIPT ───",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#000000").place(relx=0.5, rely=0.5, anchor="center")

        divider()

        # ── Column Headers ────────────────────────────────────
        col = ctk.CTkFrame(self.card, fg_color="#222222", corner_radius=0, height=30)
        col.pack(fill="x", padx=10, pady=2)
        col.pack_propagate(False)
        ctk.CTkLabel(col, text="QTY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=35, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(col, text="DESCRIPTION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", anchor="w").pack(side="left", padx=2, fill="x", expand=True)
        ctk.CTkLabel(col, text="AMOUNT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=80, anchor="e").pack(side="right", padx=5)

        # ── Items ─────────────────────────────────────────────
        total = 0
        for idx, item in enumerate(cart):
            amount = item["selling_price"] * item["quantity"]
            total += amount
            qty = item["quantity"]
            unit = item["selling_price"]
            desc = item["item_name"]
            if qty > 1:
                desc = f"{item['item_name']} @₱{unit:.2f}"
            row_bg = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            row = ctk.CTkFrame(self.card, fg_color=row_bg, corner_radius=0)
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=str(qty),
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=35, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=desc,
                font=ctk.CTkFont(size=11),
                text_color="#000000", anchor="w").pack(side="left", padx=2, fill="x", expand=True)
            ctk.CTkLabel(row, text=f"₱{amount:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=80, anchor="e").pack(side="right", padx=5)

        # ── Total ─────────────────────────────────────────────
        total_bg = ctk.CTkFrame(self.card, fg_color="#eeeeee", corner_radius=0, height=34)
        total_bg.pack(fill="x", padx=10, pady=2)
        total_bg.pack_propagate(False)
        ctk.CTkLabel(total_bg, text="TOTAL",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#000000").pack(side="left", padx=8)
        ctk.CTkLabel(total_bg, text=f"₱{total:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#000000").pack(side="right", padx=8)

        # ── Cash and Change ───────────────────────────────────
        if self.cash > 0:
            cash_row = ctk.CTkFrame(self.card, fg_color="#ffffff", corner_radius=0, height=28)
            cash_row.pack(fill="x", padx=10, pady=1)
            cash_row.pack_propagate(False)
            ctk.CTkLabel(cash_row, text="CASH",
                font=ctk.CTkFont(size=12),
                text_color="#555555").pack(side="left", padx=8)
            ctk.CTkLabel(cash_row, text=f"₱{self.cash:.2f}",
                font=ctk.CTkFont(size=12),
                text_color="#555555").pack(side="right", padx=8)

            change_row = ctk.CTkFrame(self.card, fg_color="#f0fff0", corner_radius=0, height=28)
            change_row.pack(fill="x", padx=10, pady=1)
            change_row.pack_propagate(False)
            ctk.CTkLabel(change_row, text="CHANGE",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#228B22").pack(side="left", padx=8)
            ctk.CTkLabel(change_row, text=f"₱{self.change:.2f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#228B22").pack(side="right", padx=8)

        divider()

        # ── Barcode Image ─────────────────────────────────────
        try:
            import barcode
            from barcode.writer import ImageWriter
            from PIL import Image

            buf = io.BytesIO()
            code = barcode.get("code128", self.receipt_no, writer=ImageWriter())
            code.write(buf, options={
                "module_width": 0.8,
                "module_height": 8.0,
                "font_size": 6,
                "text_distance": 2,
                "quiet_zone": 2,
                "write_text": False
            })
            buf.seek(0)
            pil_img = Image.open(buf).convert("RGB")
            pil_img = pil_img.resize((360, 70), Image.LANCZOS)

            self._barcode_img = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=(360, 70)
            )

            ctk.CTkLabel(self.card, text="", height=10).pack()
            ctk.CTkLabel(self.card, image=self._barcode_img, text="").pack(pady=5)
            ctk.CTkLabel(self.card,
                text=self.receipt_no,
                font=ctk.CTkFont(size=10),
                text_color="#000000").pack(pady=(0, 5))

        except ImportError:
            ctk.CTkLabel(self.card, text="", height=10).pack()
            center_label("| || ||| || | ||| || |", size=16)
            center_label(self.receipt_no, size=10)

        divider()

        # ── Thank You Footer Banner ───────────────────────────
        footer = ctk.CTkFrame(self.card, fg_color="#000000", corner_radius=0, height=36)
        footer.pack(fill="x", padx=10, pady=(2, 4))
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="★  THANK YOU FOR SHOPPING!  ★",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        center_label("Please come again!", size=11)
        ctk.CTkLabel(self.card, text="", height=10).pack()

    def do_usb_print(self):
        result = print_usb(self.cart, self.receipt_no, self.cash, self.change)
        self._show_result(result)

    def do_pdf_print(self):
        result = print_pdf(self.cart, self.receipt_no, self.cash, self.change)
        self._show_result(result)

    def _show_result(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("Print")
        popup.geometry("350x150")
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=message,
            font=ctk.CTkFont(size=14), justify="center").pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy,
            fg_color="#d3d3d3", text_color="#000000",
            corner_radius=0, width=100).pack(pady=10)