import customtkinter as ctk
from controllers import controller
from settings import APP_NAME
from database.database import initialize_db

# ── Force-load libusb DLL for PyInstaller bundled exe ────────
import os, sys, ctypes
def _load_libusb():
    try:
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            dll_path = os.path.join(base, 'libusb-1.0.dll')
            if os.path.exists(dll_path):
                ctypes.CDLL(dll_path)
                return
        ctypes.CDLL('libusb-1.0.dll')
    except Exception:
        pass
_load_libusb()
# ─────────────────────────────────────────────────────────────

initialize_db()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.attributes("-fullscreen", True)
        ctk.set_appearance_mode("light")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        controller.init(self)

        # Set role based on whoever is marked is_current in the DB
        from database.database import get_all_accounts
        for _, _, role, is_current in get_all_accounts():
            if is_current:
                controller.set_role(role)
                break

        from views.dashboard import DashboardPage
        from views.user import UserPage
        from views.inventory import InventoryPage
        from views.sell import SellPage
        from views.receipts import ReceiptsPage
        from views.reorder_table import ReorderTablePage
        from views.reorder_computation import ReorderComputationPage
        from views.receipt import ReceiptPage

        self.dashboard_page = DashboardPage(self.container)
        self.user_page = UserPage(self.container)
        self.inventory_page = InventoryPage(self.container)
        self.sell_page = SellPage(self.container)
        self.receipts_page = ReceiptsPage(self.container)
        self.reorder_table_page = ReorderTablePage(self.container)
        self.reorder_computation_page = ReorderComputationPage(self.container)
        self.receipt_page = ReceiptPage(self.container)

        self.dashboard_page.grid(row=0, column=0, sticky="nsew")
        self.user_page.grid(row=0, column=0, sticky="nsew")
        self.inventory_page.grid(row=0, column=0, sticky="nsew")
        self.sell_page.grid(row=0, column=0, sticky="nsew")
        self.receipts_page.grid(row=0, column=0, sticky="nsew")
        self.reorder_table_page.grid(row=0, column=0, sticky="nsew")
        self.reorder_computation_page.grid(row=0, column=0, sticky="nsew")
        self.receipt_page.grid(row=0, column=0, sticky="nsew")

        self.show_page("user")

        # ── Global barcode scanner listener ───────────────────
        self._scan_buffer = ""
        self._scan_timer  = None
        self.bind_all("<Key>", self._on_global_key)

    def _on_global_key(self, event):
        char = event.char
        if self._scan_timer:
            self.after_cancel(self._scan_timer)
            self._scan_timer = None
        if event.keysym == "Return":
            barcode = self._scan_buffer.strip()
            self._scan_buffer = ""
            if barcode:
                self._handle_scanned_barcode(barcode)
        elif char and char.isprintable():
            self._scan_buffer += char
            self._scan_timer = self.after(300, self._clear_scan_buffer)

    def _clear_scan_buffer(self):
        self._scan_buffer = ""
        self._scan_timer  = None

    def _handle_scanned_barcode(self, barcode):
        # If inventory page is currently visible, ignore global scan
        # Inventory handles its own item selection — scanning there
        # was causing quantity and price to double
        if self.inventory_page.winfo_ismapped():
            return
        self.show_page("sell")
        err = self.sell_page.ctrl.add_by_barcode(barcode)
        if err:
            self.sell_page._warning(err)
        else:
            self.sell_page._refresh_cart()

    def show_page(self, page_name):
        pages = {
            "dashboard": self.dashboard_page,
            "user": self.user_page,
            "inventory": self.inventory_page,
            "sell": self.sell_page,
            "receipts": self.receipts_page,
            "reorder_table": self.reorder_table_page,
            "reorder_computation": self.reorder_computation_page,
            "receipt": self.receipt_page,
        }
        if page_name in pages:
            pages[page_name].tkraise()
            if hasattr(pages[page_name], 'load_items'):
                pages[page_name].load_items()

if __name__ == "__main__":
    app = App()
    app.mainloop()