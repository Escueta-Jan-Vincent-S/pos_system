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

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#90EE90", height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        self._back_target = "inventory"  # default, overridable

        ctk.CTkButton(
            header, text="<", fg_color="transparent",
            text_color="#000000", hover_color="#7dd67d",
            font=ctk.CTkFont(size=40, weight="bold"),
            corner_radius=0, width=60, height=60,
            command=lambda: controller.navigate(self._back_target)
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="OFFICIAL RECEIPT",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#000000"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkFrame(self, fg_color="#000000", height=2, corner_radius=0).pack(fill="x")

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── Receipt Card ──────────────────────────────────────
        card_border = ctk.CTkFrame(
            body, fg_color="#ffffff", corner_radius=0,
            border_color="#000000", border_width=2,
            width=566, height=756
        )
        card_border.place(relx=0.4, rely=0.5, anchor="center")
        card_border.pack_propagate(False)

        self.card = ctk.CTkScrollableFrame(
            card_border, fg_color="#ffffff", corner_radius=0,
            border_width=0,
            width=560, height=750
        )
        self.card.pack(fill="both", expand=True)

        # ── Right Buttons ─────────────────────────────────────
        right = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=0)
        right.place(relx=0.82, rely=0.5, anchor="center")

        ctk.CTkButton(
            right, text="🖨️  USB Thermal",
            fg_color="#d3d3d3", text_color="#000000",
            hover_color="#c0c0c0", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=200, height=50,
            command=self.do_usb_print
        ).pack(pady=5)

        ctk.CTkButton(
            right, text="📄  Save as PDF",
            fg_color="#90EE90", text_color="#000000",
            hover_color="#7dd67d", border_color="#000000", border_width=2,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=0, width=200, height=50,
            command=self.do_pdf_print
        ).pack(pady=5)

    def load_receipt(self, cart, receipt_no=None, back_to="inventory"):
        self._back_target = back_to
        self.cart = cart
        # Use provided receipt_no (from sell page) or generate new one
        if receipt_no:
            self.receipt_no = receipt_no
        else:
            self.receipt_no = f"REC{random.randint(10000, 99999)}"

        # Save to DB as UNPAID so it appears in receipts list
        total = sum(i["selling_price"] * i["quantity"] for i in cart)
        db_save_receipt(cart, total, 0, 0, is_paid=0, receipt_no=self.receipt_no)

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
        ctk.CTkLabel(banner, text="★  MINIMART  ★",
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
        ctk.CTkLabel(col, text="DESCRIPTION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=170, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(col, text="QTY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=40, anchor="center").pack(side="left")
        ctk.CTkLabel(col, text="UNIT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=65, anchor="center").pack(side="left")
        ctk.CTkLabel(col, text="AMOUNT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff", width=75, anchor="e").pack(side="right", padx=5)

        # ── Items ─────────────────────────────────────────────
        total = 0
        for idx, item in enumerate(cart):
            amount = item["selling_price"] * item["quantity"]
            total += amount
            row_bg = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            row = ctk.CTkFrame(self.card, fg_color=row_bg, corner_radius=0)
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=item["item_name"],
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=170, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(item["quantity"]),
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=40, anchor="center").pack(side="left")
            ctk.CTkLabel(row, text=f"₱{item['selling_price']:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=65, anchor="center").pack(side="left")
            ctk.CTkLabel(row, text=f"₱{amount:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#000000", width=75, anchor="e").pack(side="right", padx=5)

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
        result = print_usb(self.cart, self.receipt_no)
        self._show_result(result)

    def do_pdf_print(self):
        result = print_pdf(self.cart, self.receipt_no)
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