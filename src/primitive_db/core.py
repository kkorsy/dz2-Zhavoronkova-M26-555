ID_COLUMN_NAME = "ID"
INT_TYPE = "int"
STR_TYPE = "str"
BOOL_TYPE = "bool"
ALLOWED_TYPES = [INT_TYPE, STR_TYPE, BOOL_TYPE]


def create_table(metadata: dict, table_name: str, columns: dict) -> dict | None:
    """Создает таблицу в базе данных. В случае успеха возвращает обновленные метаданные"""

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return

    if ID_COLUMN_NAME in columns and columns[ID_COLUMN_NAME] != INT_TYPE:
        print(f"Некорректное значение: {ID_COLUMN_NAME}:{columns[ID_COLUMN_NAME]}. "
            f"Попробуйте снова. Столбец {ID_COLUMN_NAME} должен иметь тип {INT_TYPE}.")
        return

    for column_name, column_type in columns.items():
        if column_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column_name}:{column_type}. "
                f"Попробуйте снова. Допустимые типы: {ALLOWED_TYPES}")
            return

    columns = {ID_COLUMN_NAME: INT_TYPE, **columns}
    metadata[table_name] = columns
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удаляет таблицу из базы данных. В случае успеха возвращает обновленные метаданные"""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    del metadata[table_name]
    return metadata


def list_tables(metadata: dict) -> None:
    """Выводит список существующих таблиц"""

    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")
