from primitive_db import utils

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


def insert(metadata: dict, table_name: str, values: list) -> list[dict] | None:
    """Добавляет запись и возвращает обновлённый список записей таблицы."""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = []
    for column_name in metadata[table_name]:
        if column_name != ID_COLUMN_NAME:
            columns.append(column_name)
    if len(values) != len(columns):
        print(f"Ошибка: Ожидается {len(columns)} значений без ID, получено {len(values)}.")
        return

    expected_types = {INT_TYPE: int, STR_TYPE: str, BOOL_TYPE: bool}
    record = {}
    for column_name, value in zip(columns, values):
        column_type = metadata[table_name][column_name]
        if type(value) is not expected_types.get(column_type):
            print(f"Некорректное значение: Столбец {column_name} должен иметь тип {column_type}. Попробуйте снова.")
            return
        record[column_name] = value

    table_data = utils.load_table_data(table_name)
    new_id = 1
    for row in table_data:
        if row[ID_COLUMN_NAME] >= new_id:
            new_id = row[ID_COLUMN_NAME] + 1
    table_data.append({ID_COLUMN_NAME: new_id, **record})
    return table_data


def prepare_table_data(metadata: dict, table_name: str, clauses: list[dict | None]) -> list[dict] | None:
    """Проверяет таблицу и значения по схеме, затем загружает записи."""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    expected_types = {INT_TYPE: int, STR_TYPE: str, BOOL_TYPE: bool}
    for clause in clauses:
        if clause is None:
            continue
        for column_name, value in clause.items():
            if column_name not in metadata[table_name]:
                print(f'Ошибка: Столбец "{column_name}" не существует.')
                return None
            column_type = metadata[table_name][column_name]
            if type(value) is not expected_types.get(column_type):
                print(f"Некорректное значение: Столбец {column_name} должен иметь тип {column_type}. Попробуйте снова.")
                return None
    return utils.load_table_data(table_name)


def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict] | None:
    """Возвращает список записей, подходящих под where_clause."""

    if where_clause is None:
        return table_data

    if len(where_clause) != 1:
        print("Ошибка: ожидается одно условие.")
        return None

    if len(table_data) == 0:
        return table_data

    target_column = list(where_clause.keys())[0]
    if target_column not in table_data[0]:
        print(f'Ошибка: Столбец "{target_column}" не существует.')
        return None
    target_value = where_clause[target_column]

    selected_data = []
    for row in table_data:
        if (type(row[target_column]) is type(target_value) and row[target_column] == target_value):
            selected_data.append(row)
    return selected_data


def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict] | None:
    """Обновляет подходящие записи и возвращает список данных."""

    if len(set_clause) != 1:
        print("Ошибка: ожидается одно новое значение.")
        return None

    if len(where_clause) != 1:
        print("Ошибка: ожидается одно условие.")
        return None

    target_column = list(set_clause.keys())[0]
    if target_column == ID_COLUMN_NAME:
        print("Ошибка: нельзя изменять автоматически созданный ID.")
        return None

    if len(table_data) == 0:
        print("Подходящие записи не найдены.")
        return table_data

    for clause in [set_clause, where_clause]:
        column_name = list(clause.keys())[0]
        if column_name not in table_data[0]:
            print(f'Ошибка: Столбец "{column_name}" не существует.')
            return None
        if type(clause[column_name]) is not type(table_data[0][column_name]):
            print(f'Некорректное значение: тип столбца "{column_name}" не совпадает. Попробуйте снова.')
            return None

    target_value = set_clause[target_column]
    condition_column = list(where_clause.keys())[0]
    condition_value = where_clause[condition_column]

    updated_count = 0
    for row in table_data:
        if (type(row[condition_column]) is type(condition_value) and row[condition_column] == condition_value):
            row[target_column] = target_value
            updated_count += 1
            print(f'Запись с ID={row[ID_COLUMN_NAME]} успешно обновлена.')
    if updated_count == 0:
        print("Подходящие записи не найдены.")
    return table_data


def delete(table_data: list[dict], where_clause: dict) -> list[dict] | None:
    """Удаляет записи по условию и возвращает список оставшихся записей."""

    if len(where_clause) != 1:
        print("Ошибка: ожидается одно условие.")
        return None

    if len(table_data) == 0:
        print("Подходящие записи не найдены.")
        return table_data

    target_column = list(where_clause.keys())[0]
    if target_column not in table_data[0]:
        print(f'Ошибка: Столбец "{target_column}" не существует.')
        return None
    target_value = where_clause[target_column]

    remaining_data = []
    for row in table_data:
        if (type(row[target_column]) is type(target_value) and row[target_column] == target_value):
            print(f'Запись с ID={row[ID_COLUMN_NAME]} успешно удалена.')
        else:
            remaining_data.append(row)
    if len(remaining_data) == len(table_data):
        print("Подходящие записи не найдены.")
    return remaining_data


def info(metadata: dict, table_name: str) -> None:
    """Выводит имя таблицы, её столбцы с типами и количество записей."""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    table_data = utils.load_table_data(table_name)
    columns = []
    for column_name, column_type in metadata[table_name].items():
        columns.append(f"{column_name}:{column_type}")

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(table_data)}")
