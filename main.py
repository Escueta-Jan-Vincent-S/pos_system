import customtkinter as ctk
from controllers import controller
from settings import APP_NAME
from database.database import initialize_db
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

        from views.dashboard import DashboardPage
        from views.user import UserPage
        from views.inventory import InventoryPage
        from views.sell import SellPage
        from views.receipts import ReceiptsPage
        from views.inventory_transaction import InventoryTransactionPage
        from views.reorder_table import ReorderTablePage
        from views.reorder_computation import ReorderComputationPage

        self.dashboard_page = DashboardPage(self.container)
        self.user_page = UserPage(self.container)
        self.inventory_page = InventoryPage(self.container)
        self.sell_page = SellPage(self.container)
        self.receipts_page = ReceiptsPage(self.container)
        self.inventory_transaction_page = InventoryTransactionPage(self.container)
        self.reorder_table_page = ReorderTablePage(self.container)
        self.reorder_computation_page = ReorderComputationPage(self.container)

        self.dashboard_page.grid(row=0, column=0, sticky="nsew")
        self.user_page.grid(row=0, column=0, sticky="nsew")
        self.inventory_page.grid(row=0, column=0, sticky="nsew")
        self.sell_page.grid(row=0, column=0, sticky="nsew")
        self.receipts_page.grid(row=0, column=0, sticky="nsew")
        self.inventory_transaction_page.grid(row=0, column=0, sticky="nsew")
        self.reorder_table_page.grid(row=0, column=0, sticky="nsew")
        self.reorder_computation_page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    def show_page(self, page_name):
        pages = {
            "dashboard": self.dashboard_page,
            "user": self.user_page,
            "inventory": self.inventory_page,
            "sell": self.sell_page,
            "receipts": self.receipts_page,
            "inventory_transaction": self.inventory_transaction_page,
            "reorder_table": self.reorder_table_page,
            "reorder_computation": self.reorder_computation_page,
        }
        if page_name in pages:
            pages[page_name].tkraise()
            if hasattr(pages[page_name], 'load_items'):
                pages[page_name].load_items()

if __name__ == "__main__":
    app = App()
    app.mainloop()