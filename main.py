import json
import os
from datetime import datetime
from time import sleep

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input
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

def add_expense():
    amount = float(input('Price of your expense: $'))
    name = input('Short description of your expense: ')

    if amount <= 0:
        print('Please enter a number greater than 0.')
        amount = float(input('Price of your expense: $'))

    expenses = read_expenses()

    ids = []
    for exp in expenses:
        exp_id = exp[0]
        ids.append(exp_id)

    expenses.append(
        [
            ids.max() + 1,
            datetime.today().strftime("%m-%d-%Y"),
            name,
            amount
        ]
    )
    write_expenses(expenses)
    print('[green]Expense added successfully.[/green]')
    print('\n')

def list_expenses():
    expenses = read_expenses()

    table = Table(title="Your expenses")
    table.add_column('ID')
    table.add_column('Expense')
    table.add_column('Amount', no_wrap=True)
    table.add_column('Date', no_wrap=True)

    for exp in expenses:
        id = expenses.index(exp) + 1
        table.add_row(str(id), exp['name'], str(exp['amount']), datetime.fromisoformat(exp['date']).strftime('%Y-%m-%d'))

    console = Console()
    console.print(table)
    print('\n')

def delete_expense():
    expenses = read_expenses()

    list_expenses()
    try:
        id = int(input('Enter ID to delete: '))
        if id <= 0 or id > len(expenses):
            raise ValueError
    except ValueError:
        print('[red]Please enter a valid ID.[/red]')
        delete_expense()
    else:
        if input('Do you really want to delete this expense? [y/N]: ').lower() != 'y':
            return

        expenses.pop(id - 1)
        write_expenses(expenses)
        print('[green]Expense deleted successfully.[/green]')
        print('\n')

def main():
    options = ("Exit", "Add an expense", "List expenses", "Delete expense")
    table = Table()
    table.add_column(style="cyan", no_wrap=True)
    table.add_column("Select an option")

    for option in options:
        table.add_row(str(options.index(option)), option)

    console = Console()
    console.print(table)

    selected = input(f'\nSelect an option (0-{len(options)-1}): ')
    if selected == '0':
        exit()
    elif selected == '1':
        print('\n')
        add_expense()
    elif selected == '2':
        print('\n')
        list_expenses()
    elif selected == '3':
        print('\n')
        delete_expense()
    else:
        print('[red]Please enter a valid option.[/red]')

class Add(Screen):
    def compose(self) -> ComposeResult:
        yield Header(name='Add an expense')
        yield Input(placeholder="Short description of the expense", type="text")
        yield Input(placeholder="Cost of the expense", type="number")

    @on(Input.Submitted)
    def submit(self) -> None:
        app.pop_screen()

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
