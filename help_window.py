import tkinter as tk
from styles import apply_style, get_button_style, SPACING


class HelpWindow:
    """A styled tkinter window for displaying help text."""

    def __init__(self, parent:tk.Tk, title: str, body: str, style: str = "light"):
        self.root = tk.Toplevel(parent)
        self.root.title(title)

        # Apply the same styling as the main window
        apply_style(self.root, style=style)

        # Title label
        title_label = tk.Label(
            self.root,
            text=title,
            font=("Segoe UI", 16, "bold"),
            #bg=self.root.cget("bg"),
            #fg=self.root.cget("fg")
        )
        title_label.pack(pady=SPACING["padding"])

        # Body label with word wrapping
        body_label = tk.Label(
            self.root,
            text=body,
            wraplength=500,
            justify="left",
            #bg=self.root.cget("bg"),
            #fg=self.root.cget("fg")
        )
        body_label.pack(pady=SPACING["padding"], padx=SPACING["padding"])

        # Close button
        close_button = tk.Button(
            self.root,
            text="Close",
            command=self.root.destroy,
            **get_button_style(style)
        )
        close_button.pack(pady=SPACING["button_pady"])

        # Center the window
        #self.root.eval('tk::PlaceWindow . center')

        #self.root.mainloop()