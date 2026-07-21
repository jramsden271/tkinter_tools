import tkinter as tk
from typing import List, Optional
from styles import apply_style, get_button_style, get_label_style, SPACING
from core.method_info import HelpRow


class HelpWindow:
    """A styled tkinter window that displays a method's parameters as a table."""

    _COLUMN_HEADERS = ("Parameter", "Type", "Required / Default", "Description")

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        rows: List[HelpRow],
        style: str = "light",
        summary: str = "",
        notes: Optional[List[str]] = None,
    ):
        self.root = tk.Toplevel(parent)
        self.root.title(title)

        apply_style(self.root, style=style)
        label_style = get_label_style(style)
        bg = self.root.cget("bg")
        border = label_style.get("fg", "#757575")

        title_label = tk.Label(
            self.root,
            text=title,
            font=("Segoe UI", 16, "bold"),
        )
        title_label.pack(pady=SPACING["padding"])

        if summary:
            summary_label = tk.Label(
                self.root,
                text=summary,
                wraplength=500,
                justify="left",
                anchor="w",
            )
            summary_label.pack(padx=SPACING["padding"], pady=(0, SPACING["padding"]), fill="x")

        table_frame = tk.Frame(self.root, bg=bg, highlightbackground=border, highlightthickness=1)
        table_frame.pack(padx=SPACING["padding"], pady=(0, SPACING["padding"]), fill="both", expand=True)

        for col, header in enumerate(self._COLUMN_HEADERS):
            tk.Label(
                table_frame,
                text=header,
                font=("Segoe UI", 10, "bold"),
                bg=bg,
                fg=label_style.get("fg"),
                anchor="w",
                padx=8,
                pady=4,
            ).grid(row=0, column=col, sticky="nsew")
            table_frame.grid_columnconfigure(col, weight=1 if col == len(self._COLUMN_HEADERS) - 1 else 0)

        if not rows:
            tk.Label(
                table_frame,
                text="This method takes no parameters.",
                bg=bg,
                fg=label_style.get("fg"),
                anchor="w",
                padx=8,
                pady=4,
            ).grid(row=1, column=0, columnspan=len(self._COLUMN_HEADERS), sticky="nsew")
        else:
            for r, row in enumerate(rows, start=1):
                cells = (row.name, row.type_text, row.default_text, row.description or "—")
                for col, value in enumerate(cells):
                    tk.Label(
                        table_frame,
                        text=value,
                        bg=bg,
                        fg=label_style.get("fg"),
                        anchor="w",
                        wraplength=200 if col == len(cells) - 1 else 0,
                        justify="left",
                        padx=8,
                        pady=4,
                    ).grid(row=r, column=col, sticky="nsew")

        if notes:
            for note in notes:
                tk.Label(
                    self.root,
                    text=note,
                    wraplength=500,
                    justify="left",
                    anchor="w",
                ).pack(padx=SPACING["padding"], pady=(0, 4), fill="x")

        close_button = tk.Button(
            self.root,
            text="Close",
            command=self.root.destroy,
            **get_button_style(style)
        )
        close_button.pack(pady=SPACING["button_pady"])
