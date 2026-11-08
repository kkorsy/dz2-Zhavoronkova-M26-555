import prompt, shlex

from primitive_db import core, utils

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
        splitted_input = shlex.split(user_input)
        if len(splitted_input) == 0:
            continue

        cmd, args = splitted_input[COMMAND_INDEX], splitted_input[COMMAND_INDEX + 1:]
        match cmd:
            case "help":
                print_help()
            case "exit":
                return
            case "create_table":
                prepared_args = utils.prepare_args_create_table(args)
                if prepared_args is not None:
                    result = core.create_table(metadata, *prepared_args)
                    if result is not None:
                        utils.save_metadata(METADATA_FILEPATH, result)
                        print(f"Таблица {prepared_args[0]} успешно создана")
            case "list_tables":
                core.list_tables(metadata)
            case "drop_table":
                table_name = utils.prepare_args_drop_table(args)
                if table_name is not None:
                    result = core.drop_table(metadata, table_name)
                    if result is not None:
                        utils.save_metadata(METADATA_FILEPATH, result)
                        print(f"Таблица {table_name} успешно удалена")
            case _:
                print(f"Функции {cmd} нет. Попробуйте снова")


def print_help() -> None:
    """Выводит список доступных команд"""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
