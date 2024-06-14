import math
import sys
import tkinter
import customtkinter
import sqlite3 as sq
import pytest
from CTkTable import *
from PIL import Image

from algorithms.database import Database
from algorithms.parsing import Parsing

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("../res/Themes/blue.json")


class App(customtkinter.CTk):
    """Главный класс приложения, наследующийся от customtkinter.CTk."""

    def __init__(self):
        """Инициализирует главное окно приложения и создает начальный интерфейс."""
        super().__init__()
        self.after(0, lambda: self.state('zoomed'))
        self.title("my app")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        try:
            self.database = Database()
        except sq.Error as e:
            self.show_error(f'Ошибка создания экземпляра класса Database:\n{e}', True)
        self.parsing = Parsing()

        self.rows_per_page = 50
        self.page_number = 0
        self.AMOUNT_ROW_IN_TABLE = 50

        self.data_1 = self.init_table('Selection')
        self.data_2 = self.init_table('Products')
        self.copy = self.init_table('Duplicates')

        self.file_for_test = open('../Data/tests.txt', 'a+', encoding='utf-8')
        self.file_for_test.truncate(0)
        self.string_for_text_box = 'Результаты тестирования\n'
        self.len_file_for_test = len(self.string_for_text_box)

        self.set_for_selected_row = set()

        COLUMN_1 = [['№ п/п', 'Дата и время', 'Общее количество продуктов']]
        COLUMN_2 = [['№ п/п', 'Номер выборки', 'Название', 'Цена', 'Страница']]
        COLUMN_3 = [['№ п/п', 'Номер продукта', 'Номер выборки', 'Название', 'Цена', 'Страница']]

        # индикатор выполнения действий в приложении
        self.frame_for_progress_bar = customtkinter.CTkFrame(master=self, height=36)
        self.frame_for_progress_bar.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.frame_for_progress_bar.grid_columnconfigure(0, weight=1)
        self.frame_for_progress_bar.grid_rowconfigure((0, 2), weight=1)
        self.frame_for_progress_bar.grid_propagate(False)

        self.string_for_label_bar = tkinter.StringVar(self.frame_for_progress_bar)

        self.label_bar = customtkinter.CTkLabel(master=self.frame_for_progress_bar,
                                                textvariable=self.string_for_label_bar,
                                                font=customtkinter.CTkFont(size=13))
        self.label_bar.grid(row=1, column=1, padx=(0, 20), sticky='e')

        self.bar = customtkinter.CTkProgressBar(master=self.frame_for_progress_bar, mode='determinate')
        self.bar.grid(row=1, column=2, padx=(0, 20), sticky="e")
        self.bar.set(1)

        # три раздела
        self.tab_view = customtkinter.CTkTabview(self, command=self.change_data_on_page)
        self.tab_view.grid(row=0, column=0, padx=10, sticky='nsew')
        self.selection_view = self.tab_view.add('Выборка')
        self.result_view = self.tab_view.add('Результат')
        self.information_view = self.tab_view.add('Информация')

        # работа с 1-ым разделом
        self.selection_view.grid_rowconfigure(2, weight=1)
        self.selection_view.grid_columnconfigure(0, weight=1)

        # фрейм для кнопок управления
        self.frame = customtkinter.CTkFrame(self.selection_view)
        self.frame.grid(row=0, column=0, sticky='nsew', pady=(0, 25), padx=(25, 0))
        self.frame.grid_columnconfigure((0, 2, 6, 8, 10), weight=1)

        # кнопка "Назад"
        self.previous_button = customtkinter.CTkButton(self.frame, text="Назад", command=self.previous_page)
        self.previous_button.grid(row=0, column=1)

        # надпись "Страница: "
        self.label_page = customtkinter.CTkLabel(self.frame, text='Страница: ')
        self.label_page.grid(row=0, column=3, padx=(0, 7))

        # ввод номера страницы
        self.page_num_entry_1 = customtkinter.CTkEntry(self.frame, validate="key", validatecommand=(
            self.frame.register(lambda char: char.isdigit()), '%S'))
        self.page_num_entry_1.bind('<Return>', lambda event: self.go_to_the_page())
        self.page_num_entry_1.grid(row=0, column=4, padx=(0, 10))

        # переход к странице по номеру
        self.go_to_the_page_button = customtkinter.CTkButton(self.frame, fg_color="transparent", border_width=2,
                                                             text_color=("gray10", "#DCE4EE"), text='Перейти',
                                                             command=self.go_to_the_page)
        self.go_to_the_page_button.grid(row=0, column=5)

        # общее количество страниц
        self.label_number_of_page_1 = customtkinter.CTkLabel(self.frame,
                                                             text=f'1-{math.ceil(len(self.data_1) / self.AMOUNT_ROW_IN_TABLE)}')
        self.label_number_of_page_1.grid(row=0, column=7)

        # кнопка "Вперед"
        self.next_page_button = customtkinter.CTkButton(self.frame, text="Вперед", command=self.next_page)
        self.next_page_button.grid(row=0, column=9)

        # кнопка для обновления таблицы
        self.update_table_button = customtkinter.CTkButton(self.frame, width=40,
                                                           image=customtkinter.CTkImage(Image.open(
                                                               '../res/Image/refresh.ico')),
                                                           text='', command=self.update_table)
        self.update_table_button.grid(row=0, column=11)

        # фрейм заголовков таблицы
        self.frame = customtkinter.CTkFrame(self.selection_view)
        self.frame.grid(row=1, column=0, sticky='nsew', padx=(25, 0))
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.head_1 = CTkTable(self.frame, row=1, column=3, values=COLUMN_1)
        self.head_1.grid(row=0, column=0, sticky='nsew')

        # скролл и таблица внутри
        self.scroll_frame = customtkinter.CTkScrollableFrame(self.selection_view)
        self.scroll_frame.grid(row=2, column=0, sticky='nsew')
        self.scroll_frame.grid_rowconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.table_selection_1 = CTkTable(master=self.scroll_frame, row=self.rows_per_page, column=3,
                                          command=self.selection)
        self.table_selection_1.grid(row=0, column=0, sticky='nsew')

        # кнопка для парсинга сайта
        self.frame = customtkinter.CTkFrame(master=self.selection_view)
        self.frame.grid_columnconfigure((0, 2, 4), weight=1)
        self.frame.grid(row=3, column=0, sticky='nsew')

        self.but_for_parsing = customtkinter.CTkButton(master=self.frame, image=customtkinter.CTkImage(
            Image.open('../res/Image/parsing.ico')), text='Считать данные', compound='top',
                                                       command=self.go_parsing_and_block_but)
        self.but_for_parsing.grid(row=0, column=1, sticky='nsew')

        # кнопка для проведения тестов
        self.but_for_pytest = customtkinter.CTkButton(self.frame, image=customtkinter.CTkImage(
            Image.open('../res/Image/pytest.ico')), text="Провести тесты", compound='top', command=self.do_pytest)
        self.but_for_pytest.grid(row=0, column=3, padx=(0, 0), sticky='nsew')

        # работа со 2-ым разделом
        self.result_view.grid_rowconfigure(2, weight=1)
        self.result_view.grid_columnconfigure(0, weight=1)

        # фрейм для кнопок управления
        self.frame = customtkinter.CTkFrame(self.result_view)
        self.frame.grid(row=0, column=0, sticky='nsew', pady=(0, 25), padx=(25, 0))
        self.frame.grid_columnconfigure((0, 2, 6, 8, 10), weight=1)

        # кнопка "Назад"
        self.previous_button = customtkinter.CTkButton(self.frame, text="Назад", command=self.previous_page)
        self.previous_button.grid(row=0, column=1)

        # надпись "Страница: "
        self.label_page = customtkinter.CTkLabel(self.frame, text='Страница: ')
        self.label_page.grid(row=0, column=3, padx=(0, 7))

        # ввод номера страницы
        self.page_num_entry_2 = customtkinter.CTkEntry(self.frame, validate="key", validatecommand=(
            self.frame.register(lambda char: char.isdigit()), '%S'))
        self.page_num_entry_2.bind('<Return>', lambda event: self.go_to_the_page())
        self.page_num_entry_2.grid(row=0, column=4, padx=(0, 10))

        # переход к странице по номеру
        self.go_to_the_page_button = customtkinter.CTkButton(self.frame, fg_color="transparent", border_width=2,
                                                             text_color=("gray10", "#DCE4EE"), text='Перейти',
                                                             command=self.go_to_the_page)
        self.go_to_the_page_button.grid(row=0, column=5)

        # общее количество страниц
        self.label_number_of_page_2 = customtkinter.CTkLabel(self.frame,
                                                             text=f'1-{math.ceil(len(self.data_2) / self.AMOUNT_ROW_IN_TABLE)}')
        self.label_number_of_page_2.grid(row=0, column=7)

        # кнопка "Вперед"
        self.next_page_button = customtkinter.CTkButton(self.frame, text="Вперед", command=self.next_page)
        self.next_page_button.grid(row=0, column=9)

        # кнопка для обновления таблицы
        self.update_table_button = customtkinter.CTkButton(self.frame, width=40,
                                                           image=customtkinter.CTkImage(
                                                               Image.open('../res/Image/refresh.ico')),
                                                           text='', command=self.update_table)
        self.update_table_button.grid(row=0, column=11)

        # фрейм заголовков таблицы
        self.frame = customtkinter.CTkFrame(self.result_view)
        self.frame.grid(row=1, column=0, sticky='nsew', padx=(25, 0))
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.head_2 = CTkTable(self.frame, row=1, column=5, values=COLUMN_2)
        self.head_2.grid(row=0, column=0, sticky='nsew')

        # скролл и таблица внутри
        self.scroll_frame = customtkinter.CTkScrollableFrame(self.result_view)
        self.scroll_frame.grid(row=2, column=0, sticky='nsew')
        self.scroll_frame.grid_rowconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.table_selection_2 = CTkTable(master=self.scroll_frame, row=self.rows_per_page, column=5,
                                          command=self.selection)
        self.table_selection_2.grid(row=0, column=0, sticky='nsew')

        # работа с 3-им разделом
        self.information_view.grid_rowconfigure(0, weight=1)
        self.information_view.grid_columnconfigure(0, weight=1)
        self.information_view.grid_columnconfigure(1, weight=1)

        # результаты тестов
        self.textbox_for_pytest = customtkinter.CTkTextbox(master=self.information_view, activate_scrollbars=True)
        self.textbox_for_pytest.insert('1.0', self.string_for_text_box)
        self.textbox_for_pytest.configure(state='disabled')
        self.textbox_for_pytest.grid(row=0, column=0, sticky='nsew')

        # скролл и таблица для повторок внутри
        self.frame = customtkinter.CTkFrame(self.information_view)
        self.frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((2, 4), weight=1)

        self.head_3 = CTkTable(self.frame, row=1, column=6, values=COLUMN_3)
        self.head_3.grid(row=0, column=0, sticky='nsew')

        self.label_of_table_information_view = customtkinter.CTkLabel(self.frame, text='Таблица дубликатов')
        self.label_of_table_information_view.grid(row=1, column=0, pady=(5, 0), sticky='nsew')

        self.scroll_frame = customtkinter.CTkScrollableFrame(self.frame)
        self.scroll_frame.grid(row=2, column=0, sticky='nsew')
        self.scroll_frame.grid_rowconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.table_selection_3 = CTkTable(master=self.scroll_frame, row=self.rows_per_page, column=6,
                                          command=self.selection)
        self.table_selection_3.grid(row=0, column=0, sticky='nsew')

        self.label_of_table_information_view = customtkinter.CTkLabel(self.frame, text='Таблица оригиналов')
        self.label_of_table_information_view.grid(row=3, column=0, pady=(5, 0), sticky='nsew')

        self.scroll_frame = customtkinter.CTkScrollableFrame(self.frame)
        self.scroll_frame.grid(row=4, column=0, sticky='nsew')
        self.scroll_frame.grid_rowconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.table_selection_4 = CTkTable(master=self.scroll_frame, row=self.rows_per_page, column=6,
                                          command=self.selection)
        self.table_selection_4.grid(row=0, column=0, sticky='nsew')

        # привязка кнопки "Удалить" к соответствующей клавише
        self.bind_all('<Delete>', lambda event: self.are_you_sure_window())

        self.update_table_all()

    def are_you_sure_window(self):
        """Создает всплывающее окно с подтверждением удаления выбранных элементов."""
        if len(self.set_for_selected_row) == 0:
            return

        def destroy():
            are_you_sure.destroy()

        def delete_selected_row():
            destroy()
            self.delete_selected_row()

        are_you_sure = customtkinter.CTk()
        are_you_sure.resizable(False, False)
        are_you_sure.grid_rowconfigure(0, weight=1)
        are_you_sure.grid_columnconfigure(0, weight=1)
        window_width = 340
        window_height = 100
        master_x = self.winfo_x()
        master_y = self.winfo_y()
        master_width = self.winfo_width()
        master_height = self.winfo_height()
        position_top = int(master_y + master_height / 2 - window_height / 2)
        position_right = int(master_x + master_width / 2 - window_width / 2)
        are_you_sure.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        question_label = customtkinter.CTkLabel(master=are_you_sure, text='Желаете удалить выбранные элементы?')
        question_label.grid(row=0, column=0, sticky='nsew')

        frame = customtkinter.CTkFrame(are_you_sure, fg_color='transparent')
        frame.grid(row=1, column=0, sticky='nsew')

        back_button = customtkinter.CTkButton(master=frame, text='Отмена', command=destroy)
        back_button.grid(row=0, column=0, sticky='nsew', padx=15, pady=10)

        delete_button = customtkinter.CTkButton(master=frame, fg_color="transparent", border_width=2,
                                                text_color=("gray10", "#DCE4EE"), text='Удалить',
                                                command=delete_selected_row)
        delete_button.grid(row=0, column=1, sticky='nsew', padx=15, pady=10)

        are_you_sure.grab_set_global()
        are_you_sure.mainloop()

    def delete_selected_row(self):
        """Удаляет выбранные строки из текущей таблицы."""
        self.string_for_label_bar.set('Удаление элементов из таблицы...')
        self.update()
        cur_tab = self.tab_view.get()
        if cur_tab == 'Информация':
            return
        print(self.set_for_selected_row)
        for curr in reversed(sorted(self.set_for_selected_row)):
            if cur_tab == 'Выборка':
                self.data_1.remove(self.data_1[curr])
                try:
                    self.database.delete_data_from_table(name_table='Selection', num_del=self.table_selection_1.get_row(curr)[0])
                except sq.Error as e:
                    self.show_error(e, False)
                self.table_selection_1.delete_row(curr)
            elif cur_tab == 'Результат':
                self.data_2.remove(self.data_2[curr])
                self.table_selection_2.delete_row(curr)
                self.database.delete_data_from_table(name_table='Products', num_del=curr)
        self.update()
        self.string_for_label_bar.set('')

    def selection(self, block):
        """Выделяет выбранные строки и добавляет их в список выделенных строк."""
        cur_tab = self.tab_view.get()
        row = block.get('row')
        is_selected = lambda: block.get('args').get('fg_color') != ['#36719F', '#144870']
        if cur_tab == 'Выборка':
            if is_selected():
                self.table_selection_1.select_row(row)
                self.set_for_selected_row.add(row)
            else:
                self.table_selection_1.deselect_row(row)
                self.set_for_selected_row.remove(row)
        elif cur_tab == 'Результат':
            if is_selected():
                self.table_selection_2.select_row(row)
                self.set_for_selected_row.add(row)
            else:
                self.table_selection_2.deselect_row(row)
                self.set_for_selected_row.remove(row)
        else:
            if is_selected():
                self.table_selection_3.select_row(row)
                self.table_selection_4.select_row(row)
            else:
                self.table_selection_3.deselect_row(row)
                self.table_selection_4.deselect_row(row)

    def do_pytest(self):
        """Выполняет тесты pytest и выводит результаты в текстовое поле."""
        self.string_for_label_bar.set('Выполнение тестов...')
        self.but_for_pytest.configure(state='disabled')
        self.but_for_parsing.configure(state='disabled')
        self.update()
        sys.stdout = self.file_for_test
        pytest.main(['-v', 'Test/test_site.py'])
        self.file_for_test.seek(self.len_file_for_test)
        read = self.file_for_test.read()
        self.textbox_for_pytest.configure(state='normal')
        self.textbox_for_pytest.insert(str(self.len_file_for_test) + '.0', read)
        self.textbox_for_pytest.configure(state='disabled')
        self.len_file_for_test = len(read) + self.len_file_for_test
        sys.stdout = sys.__stdout__
        self.tab_view.set('Информация')
        self.but_for_pytest.configure(state='normal')
        self.but_for_parsing.configure(state='normal')
        self.update()
        self.string_for_label_bar.set('')

    def go_parsing_and_block_but(self):
        """Запускает процесс парсинга сайта и блокирует кнопку парсинга во время выполнения."""
        self.string_for_label_bar.set('Парсинг сайта...')
        self.but_for_parsing.configure(state='disabled')
        self.update()
        try:
            self.parsing.do_parsing()
        except Exception as e:
            self.show_error(f'Произошла ошибка при парсинге сайта!\n{e}', True)
        try:
            self.database.do_database(self.parsing)
        except sq.Error as e:
            self.show_error(f"Ошибка базы данных!\n{e}", True)
        self.but_for_parsing.configure(state='normal')
        self.but_for_parsing.configure(image=customtkinter.CTkImage(Image.open('../res/Image/parsing_ok.ico')))
        self.data_1 = self.init_table('Selection')
        self.data_2 = self.init_table('Products')
        self.copy = self.init_table('Duplicates')
        self.update_table_all()
        self.table_selection_1.select_row(self.data_1[-1][0] - 1)
        self.update()
        self.after(1500, self.table_selection_1.deselect_row(self.data_1[-1][0] - 1))
        self.after(1500, self.but_for_parsing.configure(image=customtkinter.CTkImage(Image.open('../res/Image/parsing.ico'))))

    def init_table(self, name_table):
        """Инициализирует данные для таблицы с указанным именем."""
        try:
            return self.database.get_data(name_table)
        except sq.Error as e:
            self.show_error(f"Ошибка базы данных!\n{e}", True)
            exit(-1)

    def update_table_all(self):
        """Обновляет все таблицы в приложении."""
        self.string_for_label_bar.set('Обновление таблиц...')
        self.table_selection_1.update_values(self.data_1[0:self.rows_per_page])
        self.label_number_of_page_1.configure(text=f'1-{math.ceil(len(self.data_1) / self.AMOUNT_ROW_IN_TABLE)}')
        self.page_num_entry_1.delete(first_index=0, last_index=len(self.page_num_entry_1.get()))
        self.page_num_entry_1.insert(0, 1)
        self.table_selection_2.update_values(self.data_2[0:self.rows_per_page])
        self.label_number_of_page_2.configure(text=f'1-{math.ceil(len(self.data_2) / self.AMOUNT_ROW_IN_TABLE)}')
        self.page_num_entry_2.delete(first_index=0, last_index=len(self.page_num_entry_2.get()))
        self.page_num_entry_2.insert(0, 1)
        self.table_selection_3.update_values(self.copy)

        def binary_search(data, target):
            low = 0
            high = len(data) - 1

            while low <= high:
                mid = (low + high) // 2
                if data[mid][0] == target:
                    return data[mid]
                elif data[mid][0] < target:
                    low = mid + 1
                else:
                    high = mid - 1
            return None

        result = list()
        for num, curr in enumerate(self.copy, 1):
            buff = binary_search(self.data_2, curr[1])
            rew = list(buff)
            rew.insert(0, num)
            result.append(rew)
        if len(result) != 0:
            self.table_selection_4.update_values(result)

        self.update()
        self.string_for_label_bar.set('')

    def update_table(self):
        """Обновляет текущую таблицу в приложении."""
        self.string_for_label_bar.set('Обновление таблицы...')
        self.update()
        cur_tab = self.tab_view.get()
        start_index = self.page_number * self.rows_per_page
        end_index = start_index + self.rows_per_page
        if cur_tab == 'Выборка':
            data = self.data_1
        else:
            data = self.data_2
        page_data = data[start_index:end_index]
        if cur_tab == 'Выборка':
            self.table_selection_1.update_values(page_data)
            self.label_number_of_page_1.configure(text=f'1-{math.ceil(len(self.data_1) / self.AMOUNT_ROW_IN_TABLE)}')
            self.page_num_entry_1.delete(first_index=0, last_index=len(self.page_num_entry_1.get()))
            self.page_num_entry_1.insert(0, self.page_number + 1)
        elif cur_tab == 'Результат':
            self.table_selection_2.update_values(page_data)
            self.label_number_of_page_2.configure(text=f'1-{math.ceil(len(self.data_2) / self.AMOUNT_ROW_IN_TABLE)}')
            self.page_num_entry_2.delete(first_index=0, last_index=len(self.page_num_entry_2.get()))
            self.page_num_entry_2.insert(0, self.page_number + 1)
        self.update()
        self.string_for_label_bar.set('')

    def next_page(self):
        """Переходит к следующей странице текущей таблицы."""
        cur_tab = self.tab_view.get()
        if cur_tab == 'Выборка':
            if self.page_number <= math.floor(len(self.data_1) / self.AMOUNT_ROW_IN_TABLE) - 1:
                self.page_number += 1
                self.update_table()
        else:
            if self.page_number <= math.floor(len(self.data_2) / self.AMOUNT_ROW_IN_TABLE) - 1:
                self.page_number += 1
                self.update_table()

    def previous_page(self):
        """Переходит к предыдущей странице текущей таблицы."""
        if self.page_number > 0:
            self.page_number -= 1
            self.update_table()

    def go_to_the_page(self):
        """Переходит к указанной странице текущей таблицы."""
        cur_tab = self.tab_view.get()
        if cur_tab == 'Выборка':
            try:
                page = int(self.page_num_entry_1.get()) - 1
            except ValueError:
                return
            limit = math.floor(len(self.data_1) / self.AMOUNT_ROW_IN_TABLE)
        else:
            try:
                page = int(self.page_num_entry_2.get()) - 1
            except ValueError:
                return
            limit = math.floor(len(self.data_2) / self.AMOUNT_ROW_IN_TABLE)
        if 0 <= page <= limit:
            self.page_number = page
            self.update_table()

    def change_data_on_page(self):
        """Обновляет данные на текущей странице при переключении вкладок."""
        self.rows_per_page = 50
        self.page_number = 0
        self.set_for_selected_row.clear()

    def show_error(self, message, is_fatality):
        """Показывает сообщение об ошибке в новом окне."""

        def destroy():
            error_window.destroy()
            if is_fatality:
                self.destroy()
            exit(-1)

        error_window = customtkinter.CTk()
        error_window.grid_columnconfigure(0, weight=1)
        error_window.grid_rowconfigure(0, weight=1)
        window_width = 300
        window_height = 200
        master_x = self.winfo_x()
        master_y = self.winfo_y()
        master_width = self.winfo_width()
        master_height = self.winfo_height()
        position_top = int(master_y + master_height / 2 - window_height / 2)
        position_right = int(master_x + master_width / 2 - window_width / 2)
        error_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        error_label = customtkinter.CTkTextbox(master=error_window, text_color='red')
        error_label.grid(row=0, column=0, sticky='nsew', padx=10, pady=(10, 5))
        error_label.insert('0.0', message)
        error_label.configure(state='disabled')
        ok_button = customtkinter.CTkButton(master=error_window, text="OK", command=destroy)
        ok_button.grid(row=1, column=0, sticky='nsew', padx=10, pady=(5, 10))
        error_window.update()
        error_window.grab_set_global()
        error_window.mainloop()

    def destroy(self):
        """Закрывает соединение с базой данных и файл перед уничтожением окна."""
        self.database.close()
        self.file_for_test.close()
        super().destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
