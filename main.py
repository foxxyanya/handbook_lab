import tkinter as tk

from src.app.app import HandbookUI
from src.db.connector import DataBaseConnector

if __name__ == '__main__':
    tables_cfg = {
        'city': {
            'cols': ['name', 'country_id', 'population', 'area', 'date_of_foundation'],
            'dep_tables': ['country']
        },
        'country': {
            'cols': ['name', 'population', 'area', 'continent', 'date_of_foundation'],
            'dep_tables': []
        }
    }


    db_proxy = DataBaseConnector(
        db_filename='lab2.db',
        tables_cfg=tables_cfg
    )

    root = tk.Tk()
    app = HandbookUI(root, db_proxy)
    root.mainloop()
