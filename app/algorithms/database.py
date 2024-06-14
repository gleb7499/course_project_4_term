import sqlite3 as sq
from datetime import datetime

companies = ['apple', 'xiaomi', 'samsung', 'poco', 'honor', 'realme', 'huawei', 'tcl', 'vivo', 'infinix', 'tecno', 'redmi']


class Database:
    """Класс для работы с базой данных."""

    def __init__(self):
        try:
            self._connector = sq.connect("../Data/data.db")
            self._cursor = self._connector.cursor()
            self._connector.execute("PRAGMA foreign_keys = ON;")
            self._create_tables()
            self._clear_table("Duplicates")
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка при попытке доступа к базе данных: {e}") from None

    def _create_tables(self):
        """Создает таблицы в базе данных, если они еще не существуют."""
        try:
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Companies (
                                Name TEXT PRIMARY KEY
                                )""")
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Selection (
                                SelectionID INTEGER PRIMARY KEY AUTOINCREMENT,
                                Date TEXT,
                                TotalProducts INTEGER
                                )""")
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Products (
                                ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
                                SelectionID INTEGER,
                                Name TEXT,
                                Price INTEGER,
                                Page INTEGER,
                                FOREIGN KEY (SelectionID) REFERENCES Selection (SelectionID)
                                )""")
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Duplicates (
                                DuplicateID INTEGER PRIMARY KEY AUTOINCREMENT,
                                ProductID INTEGER,
                                SelectionID INTEGER,
                                Name TEXT,
                                Price INTEGER,
                                Page INTEGER,
                                FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
                                )""")
            for comp in companies:
                try:
                    self._cursor.execute("INSERT INTO Companies VALUES(?)", (comp,))
                except sq.Error:
                    continue
            self._connector.commit()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка создания таблиц в базе данных: {e}") from None

    def _clear_table(self, name_table):
        """Очищает таблицу."""
        try:
            self._cursor.execute(f'DELETE FROM {name_table}')
            self._cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{name_table}'")
            self._connector.commit()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка очищения данных таблицы '{name_table}' в базе данных: {e}") from None

    def delete_data_from_table(self, name_table, num_del):
        """Удаляет элемент из таблицы."""
        try:
            self._cursor.execute(f"SELECT * FROM {name_table} LIMIT 1")
            first_column_name = self._cursor.description[0][0]
            self._cursor.execute(f'DELETE FROM {name_table} WHERE {first_column_name} = ?', (num_del,))
            self._connector.commit()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка удаления строк в таблице '{name_table}': {e}") from None

    def do_database(self, master):
        """Заполняет базу данных данными из master."""
        self._clear_table('Products')
        try:
            self._cursor.execute("INSERT INTO Selection VALUES(NULL, ?, ?)", (datetime.now(), master.total))
            self._connector.commit()
            SelectionID = self._cursor.lastrowid
            for element in master.data:
                for page in element.page:
                    for name, price in zip(element.names, element.prices):
                        name_company = name.split(' ')[0]
                        self._cursor.execute("SELECT * FROM Companies WHERE Name = ?", (name_company.lower(),))
                        company = self._cursor.fetchone()
                        if company is None:
                            raise Exception(f"Ошибка получения данных!\nКомпания {name_company} не соответствует справочнику компаний") from None
                        self._cursor.execute("SELECT * FROM Products WHERE Name = ? AND Price = ?", (name, price))
                        cur = self._cursor.fetchone()
                        if cur is not None:
                            self._cursor.execute('INSERT INTO Duplicates VALUES(NULL, ?, ?, ?, ?, ?)', (cur[0], SelectionID, name, price, page))
                        else:
                            self._cursor.execute("INSERT INTO Products VALUES(NULL, ?, ?, ?, ?)", (SelectionID, name, price, page))
            self._connector.commit()
        except (sq.Error or Exception) as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка при работе с базой данных: {e}") from None

    def get_data(self, tableName):
        """Возвращает все строки из указанной таблицы."""
        try:
            self._cursor.execute(f"SELECT * FROM {tableName}")
            return self._cursor.fetchall()
        except sq.Error as e:
            if self._connector:
                self._connector.rollback()
            raise sq.Error(f"Произошла ошибка при получении данных из таблицы {tableName}: {e}") from None

    def get_company(self, company):
        try:
            self._cursor.execute("SELECT * FROM Companies WHERE Name = ?", (company,))
            if self._cursor.fetchone() is None:
                return False
            return True
        except sq.Error as e:
            raise sq.Error(f"Ошибка доступа к таблице Companies\n{e}") from None

    def close(self):
        """Закрывает курсор и соединение с базой данных."""
        self._cursor.close()
        self._connector.close()
