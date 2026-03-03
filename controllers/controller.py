# ============================================================
# CONTROLLER - Central navigation router
# ============================================================

_app = None

def init(app):
    global _app
    _app = app

def navigate(page_name):
    _app.show_page(page_name)