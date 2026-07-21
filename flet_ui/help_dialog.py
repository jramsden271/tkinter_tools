"""Help dialog: a Flet AlertDialog table view of a method's parameters."""
import flet as ft

from core.method_info import MethodInfo

_COLUMN_HEADERS = ("Parameter", "Type", "Required / Default", "Description")


def build_help_dialog(method: MethodInfo, on_close) -> ft.AlertDialog:
    """Build an AlertDialog showing method.summary, a parameter table, and help_notes()."""
    rows = method.help_rows()
    notes = method.help_notes()

    content_items = []

    if method.summary:
        content_items.append(ft.Text(method.summary))

    if not rows:
        content_items.append(ft.Text("This method takes no parameters."))
    else:
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(header, weight=ft.FontWeight.BOLD)) for header in _COLUMN_HEADERS],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row.name)),
                        ft.DataCell(ft.Text(row.type_text)),
                        ft.DataCell(ft.Text(row.default_text)),
                        ft.DataCell(ft.Text(row.description or "—")),
                    ]
                )
                for row in rows
            ],
        )
        content_items.append(table)

    for note in notes:
        content_items.append(ft.Text(note))

    return ft.AlertDialog(
        title=ft.Text(f"Help: {method.formatted_title}"),
        content=ft.Column(content_items, width=650, height=450, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("Close", on_click=on_close)],
    )
