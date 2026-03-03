def on_back_click(dashboard):
    for widget in dashboard.content_area.winfo_children():
        widget.destroy()