import os

import prompt
from prettytable import PrettyTable

from primitive_db import core, parser, utils

METADATA_FILEPATH = "db_meta.json"
COMMAND_INDEX = 0


def run() -> None:
    """Основной цикл программы."""
    print_help()
    while True:
        metadata = utils.load_metadata(METADATA_FILEPATH)
        user_input = prompt.string("Введите команду: ")
        if not isinstance(user_input, str):
            continue
        splitted_input = parser.split_command(user_input)
        if splitted_input is None or len(splitted_input) == 0:
            continue

        cmd, args = splitted_input[COMMAND_INDEX], splitted_input[COMMAND_INDEX + 1:]
        if cmd in ["help", "exit", "list_tables"] and len(args) != 0:
            print("Ошибка: эта команда не принимает аргументы.")
            continue

        match cmd:
            case "help":
                print_help()
            case "exit":
                return
            case "create_table":
                prepared_args = parser.parse_args_create_table(args)
                if prepared_args is not None:
                    result = core.create_table(metadata, *prepared_args)
                    if result is not None:
                        utils.save_metadata(METADATA_FILEPATH, result)
                        print(f"Таблица {prepared_args[0]} успешно создана")
            case "list_tables":
                core.list_tables(metadata)
            case "drop_table":
                table_name = parser.parse_args_drop_table(args)
                if table_name is not None:
                    result = core.drop_table(metadata, table_name)
                    if result is not None:
                        filepath = f"data/{table_name}.json"
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        utils.save_metadata(METADATA_FILEPATH, result)
                        print(f"Таблица {table_name} успешно удалена")
            case "insert":
                prepared_args = parser.parse_args_insert(args)
                if prepared_args is not None:
                    table_name, values = prepared_args
                    result = core.insert(metadata, table_name, values)
                    if result is not None:
                        utils.save_table_data(table_name, result)
                        new_id = result[-1][core.ID_COLUMN_NAME]
                        print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
            case "select":
                prepared_args = parser.parse_args_select(args)
                if prepared_args is not None:
                    table_name, where_clause = prepared_args
                    table_data = core.prepare_table_data(metadata, table_name, [where_clause])
                    if table_data is None:
                        continue
                    result = core.select(table_data, where_clause)
                    if result is not None:
                        print_table(metadata, table_name, result)
            case "update":
                prepared_args = parser.parse_args_update(args)
                if prepared_args is not None:
                    table_name, set_clause, where_clause = prepared_args
                    table_data = core.prepare_table_data(metadata, table_name, [set_clause, where_clause])
                    if table_data is None:
                        continue
                    result = core.update(table_data, set_clause, where_clause)
                    if result is not None:
                        utils.save_table_data(table_name, result)
            case "delete":
                prepared_args = parser.parse_args_delete(args)
                if prepared_args is not None:
                    table_name, where_clause = prepared_args
                    table_data = core.prepare_table_data(metadata, table_name, [where_clause])
                    if table_data is None:
                        continue
                    result = core.delete(table_data, where_clause)
                    if result is not None:
                        utils.save_table_data(table_name, result)
            case "info":
                table_name = parser.parse_args_info(args)
                if table_name is not None:
                    core.info(metadata, table_name)
            case _:
                print(f"Функции {cmd} нет. Попробуйте снова")


def print_help() -> None:
    """Выводит список доступных команд"""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> update <имя_таблицы> set <столбец> = <новое_значение> where <столбец_условия> = <значение_условия> - обновить записи")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить записи по условию")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Выводит записи через PrettyTable в порядке столбцов из metadata."""

    if len(table_data) == 0:
        print("Подходящие записи не найдены.")
        return

    table = PrettyTable()
    columns = list(metadata[table_name].keys())
    table.field_names = columns
    for row in table_data:
        values = []
        for column_name in columns:
            values.append(row[column_name])
        table.add_row(values)
    print(table)
