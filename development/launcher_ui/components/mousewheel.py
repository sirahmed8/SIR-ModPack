def attach_mousewheel(widget, canvas):
    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass
    widget.bind("<MouseWheel>", _on_mousewheel, add="+")
    for child in widget.winfo_children():
        attach_mousewheel(child, canvas)
