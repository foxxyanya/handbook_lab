import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional, Dict

from tkcalendar import DateEntry

from src.db.connector import DataBaseConnector
from src.app.tkinter_utils import StringVarWithMapping

class HandbookUI:
    _entry_extractors = {
        DateEntry: lambda entry: str(entry.get_date().strftime('%Y-%m-%d')), 
        tk.Entry: lambda entry: entry.get(),
        tk.StringVar: lambda entry: entry.get(),
    }


    def __init__(self, root, db_connector: DataBaseConnector):
        self.db_connector = db_connector

        self.root = root
        self.root.title("ФИО, курс, группу, год")

        self._create_widgets()

    def _create_widgets(self):
        self._curr_table = tk.StringVar()
        all_tables = ['country', 'city']

        table_name_title = tk.Label(self.root, text='Название таблицы')
        table_name_title.grid(row=0, column=0, padx=10, sticky='w')

        col_to_sort_name_title = tk.Label(self.root, text='Имя колонки для сортировки')
        col_to_sort_name_title.grid(row=0, column=1, padx=10, sticky='w')

        col_to_sort_name_title = tk.Label(self.root, text='Возрастание/убывание')
        col_to_sort_name_title.grid(row=0, column=2, padx=10, sticky='w')

        self.reference_combobox = ttk.Combobox(self.root, textvariable=self._curr_table, values=all_tables)
        self.reference_combobox.grid(row=1, column=0, padx=10, sticky='w')
        self.reference_combobox.bind("<<ComboboxSelected>>", self.load_data)

        self._curr_col_to_sort = tk.StringVar()

        self.col_combobox = ttk.Combobox(self.root, textvariable=self._curr_col_to_sort, values=[])
        self.col_combobox.grid(row=1, column=1, padx=10, sticky='w')

        self._curr_sort_strategy = tk.StringVar()

        self._curr_sort_strategy_combobox = ttk.Combobox(self.root, textvariable=self._curr_sort_strategy, values=['По Возрастанию', 'По убыванию', 'Без Сортировки'])
        self._curr_sort_strategy_combobox.grid(row=1, column=2, padx=10, sticky='w')

        self.tree = ttk.Treeview(self.root, show='headings')
        self.tree.grid(row=2, column=0, padx=10, sticky='w')

        self.add_button = tk.Button(self.root, text='Add', command=self.add_record)
        self.add_button.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.edit_button = tk.Button(self.root, text='Edit', command=self.edit_record)
        self.edit_button.grid(row=3, column=0, padx=90, pady=5, sticky='w')

        self.delete_button = tk.Button(self.root, text='Remove', command=self.delete_record)
        self.delete_button.grid(row=3, column=0, padx=170, pady=5, sticky='w')

        self.sort_button = tk.Button(self.root, text='Sort', command=self.load_data)
        self.sort_button.grid(row=3, column=0, padx=290, pady=5, sticky='w')

    def load_data(self, event=None):
        curr_table = self._curr_table.get()

        if curr_table:
            self.display_table(curr_table)

    def display_table(self, table_name):
        col_to_sort = self._curr_col_to_sort.get()
        sort_strategy = self._curr_sort_strategy.get()

        fetch_args = {}

        if col_to_sort and sort_strategy != 'Без Сортировки':
            fetch_args.update(
                {
                    'sort_col': col_to_sort,
                    'ascending': False if sort_strategy == 'По убыванию' else True
                }
            )

        data, meta = self.db_connector.fetch_all(table_name, **fetch_args)
        
        self.col_combobox['values'] = meta['cols']

        self.tree["columns"] = meta['cols']
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert('', 'end', values=row)

    def add_record(self):
        curr_table = self._curr_table.get()

        if curr_table:
            self._record_changes_window(curr_table, self._add_record_from_entries)

    def _add_record_from_entries(self, 
                                 table_name: str, 
                                 entries: List, 
                                 window: tk.Toplevel, 
                                 dep_tables_name_mapping: Dict,
                                 **kwargs
    ):
        record = {}

        for col_name, entry in entries.items():
            handled = False

            dep_table_name = col_name.split('.')[0]
            if  dep_table_name in dep_tables_name_mapping:
                col_name = f"{col_name.split('.')[0]}_id"

            for entry_type, handler in HandbookUI._entry_extractors.items():
                if isinstance(entry, entry_type):
                    record[col_name] = handler(entry)
                    handled = True
                    break
                    
            if not handled:
                raise Exception(f'Unknown entry type {type(entry)}')
        
        self.db_connector.add_record(table_name, record)
        window.destroy()
        window.update()

        self.load_data()
    
    def _record_changes_window(self, 
                               table_name: str, 
                               exit_button_handler: Callable, #Callable[[str, Dict, tk.Toplevel]],
                               default_values_from_id: Optional[int] = None, 
    ):
        window = tk.Toplevel(self.root)
        window.title(f'Changing {table_name}')

        dep_tables_name_mapping = self.db_connector.get_dep_tables_name_mapping(table_name)
        
        if default_values_from_id:
            default_col_values = self.db_connector.get_record(table_name, default_values_from_id)

        cols_entry = {}

        for curr_row, col_name in enumerate(self.tree['columns']):
            label = tk.Label(window, text=f'{col_name}: ')
            label.grid(row=curr_row, column=0, padx=10, pady=10)

            col_dep_table = col_name.split('.')[0]
            
            if 'date' in col_name:
                cols_entry[col_name] = DateEntry(window, locale='ru_RU')
                if default_values_from_id and col_name in default_col_values:
                    cols_entry[col_name].set_date(default_col_values[col_name])

                cols_entry[col_name].grid(row=curr_row, column=1, padx=10, pady=10)

            elif col_dep_table in dep_tables_name_mapping:
                cols_entry[col_name] = StringVarWithMapping(
                    mapping = dep_tables_name_mapping[col_dep_table],
                    value = default_col_values[col_name]
                    if default_values_from_id and col_name in default_col_values
                    else ''
                )
                pos_values = list(dep_tables_name_mapping[col_dep_table].keys())

                combobox = ttk.Combobox(window, 
                                        textvariable=cols_entry[col_name], 
                                        values=pos_values
                )
                combobox.grid(row=curr_row, column=1, padx=10, pady=10)

            else:
                cols_entry[col_name] = tk.Entry(window)
                cols_entry[col_name].insert(
                    0, 
                    default_col_values[col_name]
                    if default_values_from_id and col_name in default_col_values
                    else ''
                ) 
                cols_entry[col_name].grid(row=curr_row, column=1, padx=10, pady=10)

        handler_kwargs = {
            'dep_tables_name_mapping': dep_tables_name_mapping
        }

        if default_values_from_id:
            handler_kwargs.update(
                {            
                    'id': default_values_from_id,
                    'default_col_values': default_col_values,
                }
            )

        add_button = tk.Button(window, 
                               text='Apply', 
                               command=lambda: exit_button_handler(table_name, cols_entry, window, **handler_kwargs)
        )
        add_button.grid(row=len(cols_entry), column=0, columnspan=2, pady=10)

    def edit_record(self):
        curr_table = self._curr_table.get()

        if curr_table:
            selected_iid = self.tree.focus()
            if selected_iid:
                item_index = self.tree.index(selected_iid) + 1

                self._record_changes_window(curr_table, self._edit_record_from_entries, item_index)

    def _edit_record_from_entries(self, 
                                  table_name: str, 
                                  entries: List, 
                                  window: tk.Toplevel,
                                  id: int, 
                                  default_col_values: Dict,
                                  dep_tables_name_mapping: Dict,
                                  **kwargs):
        record_changes = {}

        for col_name, entry in entries.items():
            handled = False

            for entry_type, handler in HandbookUI._entry_extractors.items():
                if isinstance(entry, entry_type):
                    new_value = handler(entry)
                    prev_value = default_col_values[col_name]

                    dep_table_name = col_name.split('.')[0]
                    if  dep_table_name in dep_tables_name_mapping:
                        prev_value = dep_tables_name_mapping[dep_table_name][prev_value]
                        col_name = f"{col_name.split('.')[0]}_id"


                    if str(prev_value) != new_value:
                        record_changes[col_name] = new_value
                    
                    handled = True
                    break
                    
            if not handled:
                raise Exception(f'Unknown entry type {type(entry)}')
        
        self.db_connector.edit_record(table_name, id, record_changes)
        window.destroy()
        window.update()

        self.load_data()

    def delete_record(self):
        curr_table = self._curr_table.get()

        if curr_table:
            selected_iid = self.tree.focus()
            if selected_iid:
                item_index = self.tree.index(selected_iid)
                self.db_connector.remove_record(curr_table, item_index)
                self.load_data()
