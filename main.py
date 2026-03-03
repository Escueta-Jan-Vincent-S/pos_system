import customtkinter as ctk
import time
from controllers import controller
from settings import APP_NAME


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.attributes("-fullscreen", True)
        ctk.set_appearance_mode("light")

        # Container to hold all pages in the same spot
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        controller.init(self)

        from views.dashboard import DashboardPage
        from views.user import UserPage

        self.dashboard_page = DashboardPage(self.container)
        self.user_page = UserPage(self.container)

        # Place them both in the same grid cell
        self.dashboard_page.grid(row=0, column=0, sticky="nsew")
        self.user_page.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    def show_page(self, page_name):
        if page_name == "dashboard":
            self.dashboard_page.tkraise()
        elif page_name == "user":
            self.user_page.tkraise()

    def smooth_switch(self, page_name):
        # Fade out
        for i in range(10, 6, -1):
            self.attributes("-alpha", i / 10)
            self.update()
            time.sleep(0.01)

        self.show_page(page_name)

        for i in range(7, 11):
            self.attributes("-alpha", i / 10)
            self.update()
            time.sleep(0.01)

if __name__ == "__main__":
    app = App()
    app.mainloop()