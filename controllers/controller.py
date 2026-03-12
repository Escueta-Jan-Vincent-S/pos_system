_app = None
_role = "staff"  # default role before login

def init(app):
    global _app
    _app = app


def navigate(page_name):
    _app.show_page(page_name)


def set_role(role):
    global _role
    _role = role


def get_role():
    return _role


def is_admin():
    return _role == "admin"