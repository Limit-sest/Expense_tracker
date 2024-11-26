import json
import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Button
from textual.screen import Screen
from textual import on

expense_file = 'expenses.json'

def read_expenses():
    if not os.path.isfile(expense_file):
        return []

    with open(expense_file, 'r') as f:
        return json.load(f)

def write_expenses(expenses):
    with open(expense_file, 'w') as f:
        json.dump(expenses, f)

class Add(Screen): #TODO: Auto refresh the table, see https://textual.textualize.io/guide/screens/#returning-data-from-screens
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Short description of the expense", type="text", id="name_input")
        yield Input(placeholder="Cost of the expense", type="number", id="cost_input")
        yield Button(label="Add expense", id="submit_button")
        yield Button(label="Cancel", id="cancel_button")

    @on(Button.Pressed, "#submit_button")
    async def handle_submit(self) -> None:
        name = self.query_one("#name_input", Input).value
        cost = self.query_one("#cost_input", Input).value

        cost = float(cost)

        if cost <= 0:
            self.notify("Please enter a positive number!", severity='error')
            return

        if not name:
            self.notify("Please enter a name of the expense.", severity='error')
            return

        expenses = read_expenses()

        ids = []
        for exp in expenses:
            exp_id = exp[0]
            ids.append(exp_id)

        new_expense = [
            max(ids) + 1 if ids else 0,
            datetime.today().strftime("%m-%d-%Y"),
            name,
            cost
        ]
        expenses.append(new_expense)
        write_expenses(expenses)

        table = self.app.query_one("#expense_table", DataTable)
        table.add_row(new_expense[1], new_expense[2], str(new_expense[3]), key=str(new_expense[0]))

        await self.app.pop_screen()

    @on(Button.Pressed, "#cancel_button")
    async def handle_cancel(self) -> None:
        await self.app.pop_screen()

class ExpenseTracker(App):
    """A Textual app to for managing expenses."""

    BINDINGS = [("d", "delete", "Delete selected"), ("a", "push_screen('add')", "Add new")]
    SCREENS = {"add": Add}

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable(id="expense_table")
        yield Footer()

    def action_delete(self):
        """Delete the currently selected row."""
        table = self.query_one("#expense_table", DataTable)

        if not table.is_valid_coordinate(table.cursor_coordinate):
            self.notify("No expense to delete.", severity='warning')
            return

        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        table.remove_row(row_key)

        expenses = read_expenses()
        for exp in expenses:
            if str(exp[0]) == row_key:
                expenses.remove(exp)
                write_expenses(expenses)


    def on_mount(self) -> None:
        table = self.query_one("#expense_table", DataTable)
        table.cursor_type = 'row'
        #rows = read_expenses()
        rows = read_expenses()

        rows.insert(0, ('Date', 'Expense', 'Amount'))
        table.add_columns(*rows[0])
        for exp in rows[1:]:
            table.add_row(exp[1], exp[2], str(exp[3]), key=str(exp[0]))


if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()
