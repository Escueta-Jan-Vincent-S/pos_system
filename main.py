import customtkinter as ctk
from controllers import controller
from settings import APP_NAME

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.attributes("-fullscreen", True)
        ctk.set_appearance_mode("light")
        self.configure(fg_color="#000000")

        controller.init(self)

        from views.dashboard import DashboardPage
        from views.user import UserPage
        self.dashboard_page = DashboardPage(self)
        self.user_page = UserPage(self)

        self.dashboard_page.pack(fill="both", expand=True)

    def show_page(self, page_name):
        self.dashboard_page.pack_forget()
        self.user_page.pack_forget()

        if page_name == "dashboard":
            self.dashboard_page.pack(fill="both", expand=True)
        elif page_name == "user":
            self.user_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()