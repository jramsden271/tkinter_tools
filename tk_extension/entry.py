import tkinter as tk

class Entry(tk.Entry):
    """A custom Entry widget that supports validation and context menu."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._context_menu = self._create_context_menu()
        self.bind("<Button-3>", self._show_context_menu)

    def _create_context_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Cut", command=self._cut)
        menu.add_command(label="Copy", command=self._copy)
        menu.add_command(label="Paste", command=self._paste)
        menu.add_separator()
        menu.add_command(label="Clear", command=self._clear)
        menu.add_command(label="Clear & Paste", command=self._clear_and_paste)
        return menu

    def _show_context_menu(self, event: tk.Event):
        if self._context_menu:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def _cut(self):
        self.event_generate("<<Cut>>")

    def _copy(self):
        self.event_generate("<<Copy>>")

    def _paste(self):
        self.event_generate("<<Paste>>")

    def _clear(self):
        self.delete(0, tk.END)

    def _clear_and_paste(self):
        self._clear()
        self._paste()