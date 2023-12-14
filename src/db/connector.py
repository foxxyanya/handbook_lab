import sqlite3
from typing import Optional, List, Dict
from datetime import datetime

class DataBaseConnector:
    # Example of Schema of tables_cfg
    #tables_deps = {
    #    'cities': {
    #        'cols': ['name', 'country_id', 'population', 'area', 'date_of_foundation'],
    #        'dep_tables': ['counties']
    #    },
    #    'counties': {
    #        'cols': ['name', 'population', 'area', 'continent', 'date_of_foundation'],
    #        'dep_tables': None
    #    }
    #}

    def __init__(self, db_filename: str, tables_cfg):
        self.con = sqlite3.connect(db_filename)
        self.cursor = self.con.cursor()
        
        self.tables_cfg = tables_cfg

    def _select_full_table_query(self, table_name: str):
        cols = list(filter(lambda col: 'id' not in col, self.tables_cfg[table_name]['cols']))

        #add to date cols correct format
        cols_names_in_query = [ 
            f'{table_name}.{col}' if 'date' not in col else f"strftime('%d-%m-%Y', {table_name}.{col})"
            for col in cols
        ]

        deps_cols = [
            f'{table}.name'
            for table in self.tables_cfg[table_name]['dep_tables']
        ]

        query = f"""
                SELECT {','.join(cols_names_in_query)} {'' if not deps_cols else ','} {','.join(deps_cols)}
                FROM {table_name} {" ".join(f' INNER JOIN {dep_table} on {table_name}.{dep_table}_id = {dep_table}.id ' for dep_table in self.tables_cfg[table_name]['dep_tables'])}
        """

        return query, (cols, deps_cols)
    
    def get_dep_tables_name_mapping(self, table_name: str):
        dep_tables_name_mapping = dict()

        for dep_table_name in self.tables_cfg[table_name]['dep_tables']:
            self.cursor.execute(
                f"""
                    SELECT name, id
                    FROM {dep_table_name}
                """
            )
            dep_table_name_col = self.cursor.fetchall()
            dep_tables_name_mapping[dep_table_name] = {
                name: id   
                for name, id in dep_table_name_col 
            }

        return dep_tables_name_mapping


    def add_record(self, table_name: str, item: Dict):
        print(
            f"""
            INSERT INTO {table_name}({','.join(item.keys())})
            VALUES({','.join(['?'] * len(self.tables_cfg[table_name]['cols']))});
            """
        )


        self.cursor.execute(
            f"""
            INSERT INTO {table_name}({','.join(item.keys())})
            VALUES({','.join(['?'] * len(self.tables_cfg[table_name]['cols']))});
            """,
            list(item.values())
        )
        self.con.commit()

    def get_record(self, table_name: str, id: int):
        query, (cols, deps_cols) = self._select_full_table_query(table_name)
        record_cols = [*cols, *deps_cols]

        self.cursor.execute(query + f" WHERE {table_name}.id = {id}")
        record = self.cursor.fetchone()

        record_dict = {
            col_name: value
            for col_name, value in zip(record_cols, record)
        }

        return record_dict  

    def remove_record(self, table_name: str, id: int):
        self.cursor.execute(
            f"""
                DELETE FROM {table_name} WHERE {table_name}.id = {id};
            """
        )
        self.con.commit()

    def edit_record(self, table_name, id: int, item_changes: Dict):
        self.cursor.execute(
            f"""
                UPDATE {table_name}
                SET {','.join(f"{col} = ?" for col in item_changes.keys())}
                WHERE {table_name}.id = {id}
            """,
            [value for value in item_changes.values()]
        )
        self.con.commit()

    def fetch_all(self, 
                  table_name: str, 
                  sort_col: Optional[str] = None, 
                  ascending: bool = False
    ):    
        query, (cols, deps_cols) = self._select_full_table_query(table_name)

        if sort_col:
            query += f" ORDER BY {table_name}.{sort_col} {'ASC' if ascending else 'DESC'}"

        print(query)


        self.cursor.execute(query)
        data = self.cursor.fetchall()

        meta = {
            'cols': [*cols, *deps_cols],
        }

        return data, meta