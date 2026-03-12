from datetime import datetime
import io
import os
import sys

STORE_NAME    = "LANZ N LINDLY"
STORE_ADDRESS = "San Pablo City, Laguna"
STORE_TEL     = "TEL. NO. : ____________"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def generate_barcode_image(receipt_no):
    try:
        import barcode
        from barcode.writer import ImageWriter
        buf = io.BytesIO()
        code = barcode.get("code128", receipt_no, writer=ImageWriter())
        code.write(buf, options={
            "module_width": 0.8,
            "module_height": 8.0,
            "font_size": 6,
            "text_distance": 2,
            "quiet_zone": 2,
            "write_text": False
        })
        buf.seek(0)
        return buf
    except:
        return None

def print_pdf(cart, receipt_no):
    try:
        from reportlab.lib.pagesizes import A6
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from PIL import Image

        receipts_dir = os.path.join(get_base_path(), "receipts")
        os.makedirs(receipts_dir, exist_ok=True)
        filename = os.path.join(receipts_dir, f"receipt_{receipt_no}.pdf")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c = canvas.Canvas(filename, pagesize=A6)
        w, h = A6
        y = h - 15

        def center_text(text, size=10, bold=False):
            nonlocal y
            font = "Helvetica-Bold" if bold else "Helvetica"
            c.setFont(font, size)
            c.drawCentredString(w / 2, y, text)
            y -= size + 5

        def left_right(left, right, size=10, bold=False):
            nonlocal y
            font = "Helvetica-Bold" if bold else "Helvetica"
            c.setFont(font, size)
            c.drawString(15, y, left)
            c.drawRightString(w - 15, y, right)
            y -= size + 5

        def solid_line():
            nonlocal y
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.setDash()
            c.line(10, y, w - 10, y)
            y -= 8

        def dashed_line():
            nonlocal y
            c.setDash(3, 3)
            c.line(10, y, w - 10, y)
            c.setDash()
            y -= 8

        def four_col(desc, qty, unit, amount, size=9, bold=False):
            nonlocal y
            font = "Helvetica-Bold" if bold else "Helvetica"
            c.setFont(font, size)
            c.drawString(15, y, desc[:25])
            c.drawCentredString(w * 0.52, y, str(qty))
            c.drawCentredString(w * 0.68, y, unit)
            c.drawRightString(w - 15, y, amount)
            y -= size + 5

        # ── Store Header Block ────────────────────────────────
        c.setFillColor(colors.black)
        c.rect(10, y - 2, w - 20, 16, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(w / 2, y + 1, f"*  {STORE_NAME}  *")
        c.setFillColor(colors.black)
        y -= 20

        center_text(STORE_ADDRESS, size=9)
        center_text(STORE_TEL, size=9)
        y -= 2
        center_text(f"DATE: {now}", size=8)
        y -= 1
        center_text(f"RECEIPT NO: {receipt_no}", size=10, bold=True)
        y -= 3
        solid_line()

        # Official Receipt title with shaded bg
        c.setFillColor(colors.HexColor("#eeeeee"))
        c.rect(10, y - 12, w - 20, 18, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(w / 2, y - 6, "--- OFFICIAL RECEIPT ---")
        y -= 22
        solid_line()

        # Column headers with dark background
        c.setFillColor(colors.HexColor("#222222"))
        c.rect(10, y - 13, w - 20, 17, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(16, y - 8, "DESCRIPTION")
        c.drawCentredString(w * 0.52, y - 8, "QTY")
        c.drawCentredString(w * 0.68, y - 8, "UNIT PRICE")
        c.drawRightString(w - 15, y - 8, "AMOUNT")
        c.setFillColor(colors.black)
        y -= 20
        dashed_line()

        # Items with alternating rows
        total = 0
        for idx, item in enumerate(cart):
            amount = item["selling_price"] * item["quantity"]
            total += amount
            if idx % 2 == 0:
                c.setFillColor(colors.HexColor("#f9f9f9"))
                c.rect(10, y - 3, w - 20, 14, fill=1, stroke=0)
                c.setFillColor(colors.black)
            four_col(
                item["item_name"],
                str(item["quantity"]),
                f"P{item['selling_price']:.2f}",
                f"P{amount:.2f}"
            )

        dashed_line()

        # Total row with shaded background
        c.setFillColor(colors.HexColor("#eeeeee"))
        c.rect(10, y - 5, w - 20, 18, fill=1, stroke=0)
        c.setFillColor(colors.black)
        left_right("TOTAL", f"P{total:.2f}", size=11, bold=True)
        solid_line()

        # Barcode
        y -= 8
        barcode_buf = generate_barcode_image(receipt_no)
        if barcode_buf:
            img = Image.open(barcode_buf)
            barcode_path = os.path.join(get_base_path(), "_temp_barcode.png")
            img.save(barcode_path)
            barcode_w = w - 40
            barcode_h = 45
            c.drawImage(barcode_path, 20, y - barcode_h,
                        width=barcode_w, height=barcode_h)
            y -= barcode_h + 8
            c.setFont("Helvetica", 8)
            c.drawCentredString(w / 2, y, receipt_no)
            y -= 14
            try:
                os.remove(barcode_path)
            except:
                pass
        else:
            center_text("| || ||| || | ||| || |", size=14)
            center_text(receipt_no, size=9)

        solid_line()

        # Thank you footer with black banner
        c.setFillColor(colors.black)
        c.rect(10, y - 16, w - 20, 20, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(w / 2, y - 9, "*  THANK YOU FOR SHOPPING!  *")
        c.setFillColor(colors.black)
        y -= 24
        center_text("Please come again!", size=9)

        c.save()
        os.startfile(filename)
        return f"PDF saved!\n{filename}"

    except ImportError:
        return "Please install:\npip install reportlab pillow python-barcode"
    except Exception as e:
        return f"PDF Error: {str(e)}"

def print_usb(cart, receipt_no):
    try:
        from escpos.printer import Usb
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        printer = Usb(0x0FE6, 0x811E)  # OC-58H / POS58 Printer

        printer.set(align="center", bold=True)
        printer.text(f"* {STORE_NAME} *\n")
        printer.set(align="center", bold=False)
        printer.text(f"{STORE_ADDRESS}\n{STORE_TEL}\n")
        printer.text(f"DATE: {now}\n")
        printer.set(bold=True)
        printer.text(f"RECEIPT NO: {receipt_no}\n")
        printer.text("=" * 32 + "\n")
        printer.set(align="center", bold=True)
        printer.text("OFFICIAL RECEIPT\n")
        printer.text("=" * 32 + "\n")

        printer.set(align="left", bold=True)
        printer.text(f"{'QTY':<4}{'DESCRIPTION':<20}{'AMOUNT':>8}\n")
        printer.text("-" * 32 + "\n")

        total = 0
        printer.set(bold=False)
        for item in cart:
            amount = item["selling_price"] * item["quantity"]
            total += amount
            qty        = item["quantity"]
            name       = item["item_name"]
            unit       = item["selling_price"]
            qty_str    = str(qty)
            amount_str = f"P{amount:.2f}"

            if qty > 1:
                tag  = f"@{unit:.2f}"
                desc = f"{name[:13]} {tag}"
            else:
                desc = name[:20]

            printer.text(f"{qty_str:<4}{desc:<20}{amount_str:>8}\n")

        printer.text("-" * 32 + "\n")
        printer.set(bold=True)
        printer.text(f"{'TOTAL':<20}P{total:.2f}\n")
        printer.text("=" * 32 + "\n")

        # Barcode — CODE39 with numeric part only (REC prefix removed)
        printer.set(align="center")
        try:
            barcode_num = receipt_no.replace("REC", "").strip()
            printer.barcode(barcode_num, "CODE39", width=2, height=80, pos="BELOW", font="A")
        except Exception:
            printer.text(f"\n{receipt_no}\n")
        printer.set(align="center")
        printer.set(align="center", bold=True)
        printer.text("\n* THANK YOU FOR SHOPPING! *\n")
        printer.text("Please come again!\n\n\n")
        printer.cut()

        return "Printed successfully!"

    except ImportError:
        return "Please install:\npip install python-escpos"
    except Exception:
        return "No printer detected!\nMake sure USB thermal\nprinter is connected."