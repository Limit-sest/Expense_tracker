import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print

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

    expenses.append(
        {
            'amount': amount,
            'name': name,
            'date': datetime.today().isoformat()
        }
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

if __name__ == '__main__':
    while True:
        main()