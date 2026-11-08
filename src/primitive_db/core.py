from primitive_db import utils
from primitive_db.constants import ALLOWED_TYPES, COLUMN_TYPES, ID_COLUMN_NAME, INT_TYPE
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

select_cache = create_cacher()


def _validate_value(column_name: str, value, column_type: str) -> None:
    """Проверяет тип значения; ошибку обрабатывает декоратор вызывающего действия."""

    if column_type not in COLUMN_TYPES:
        raise ValueError(f"Неизвестный тип данных {column_type}.")
    if type(value) is not COLUMN_TYPES[column_type]:
        raise ValueError(f"Столбец {column_name} должен иметь тип {column_type}.")


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: dict) -> dict | None:
    """Создает таблицу и возвращает обновленные метаданные."""

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if ID_COLUMN_NAME in columns and columns[ID_COLUMN_NAME] != INT_TYPE:
        raise ValueError(f"Столбец {ID_COLUMN_NAME} должен иметь тип {INT_TYPE}.")

    for column_name, column_type in columns.items():
        if column_type not in ALLOWED_TYPES:
            raise ValueError(f"Неизвестный тип данных {column_type} у столбца "
                             f"{column_name}. Допустимые типы: {ALLOWED_TYPES}.")

    columns = {ID_COLUMN_NAME: INT_TYPE, **columns}
    metadata[table_name] = columns
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удаляет таблицу и возвращает обновленные метаданные."""

    del metadata[table_name]
    return metadata


@handle_db_errors
def list_tables(metadata: dict) -> None:
    """Выводит список существующих таблиц"""

    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list) -> list[dict] | None:
    """Добавляет запись и возвращает обновлённый список записей таблицы."""

    columns = []
    for column_name in metadata[table_name]:
        if column_name != ID_COLUMN_NAME:
            columns.append(column_name)
    if len(values) != len(columns):
        raise ValueError(f"Ожидается {len(columns)} значений без ID, "
                         f"получено {len(values)}.")

    record = {}
    for column_name, value in zip(columns, values):
        column_type = metadata[table_name][column_name]
        _validate_value(column_name, value, column_type)
        record[column_name] = value

    table_data = utils.load_table_data(table_name)
    new_id = 1
    for row in table_data:
        if row[ID_COLUMN_NAME] >= new_id:
            new_id = row[ID_COLUMN_NAME] + 1
    table_data.append({ID_COLUMN_NAME: new_id, **record})
    return table_data


@handle_db_errors
def prepare_table_data(
    metadata: dict, table_name: str, clauses: list[dict | None]
) -> list[dict] | None:
    """Проверяет таблицу и значения по схеме, затем загружает записи."""

    columns = metadata[table_name]

    for clause in clauses:
        if clause is None:
            continue
        for column_name, value in clause.items():
            column_type = columns[column_name]
            _validate_value(column_name, value, column_type)
    return utils.load_table_data(table_name)


@handle_db_errors
@log_time
def select(
    table_data: list[dict], where_clause: dict | None = None
) -> list[dict] | None:
    """Возвращает список записей, подходящих под where_clause."""

    if where_clause is not None and len(where_clause) != 1:
        raise ValueError("Ожидается одно условие.")

    def get_result():
        if where_clause is None:
            return table_data

        (target_column,) = where_clause
        target_value = where_clause[target_column]
        selected_data = []
        for row in table_data:
            if type(row[target_column]) is type(target_value) \
                    and row[target_column] == target_value:
                selected_data.append(row)
        return selected_data

    key = (repr(table_data), repr(where_clause))
    return select_cache(key, get_result)


@handle_db_errors
def update(
    table_data: list[dict], set_clause: dict, where_clause: dict
) -> list[dict] | None:
    """Обновляет подходящие записи и возвращает список данных."""

    if len(set_clause) != 1:
        raise ValueError("Ожидается одно новое значение.")

    if len(where_clause) != 1:
        raise ValueError("Ожидается одно условие.")

    (target_column,) = set_clause
    if target_column == ID_COLUMN_NAME:
        raise ValueError("Нельзя изменять автоматически созданный ID.")

    if len(table_data) == 0:
        print("Подходящие записи не найдены.")
        return table_data

    for clause in [set_clause, where_clause]:
        (column_name,) = clause
        column_type = type(table_data[0][column_name]).__name__
        _validate_value(column_name, clause[column_name], column_type)

    target_value = set_clause[target_column]
    (condition_column,) = where_clause
    condition_value = where_clause[condition_column]

    updated_count = 0
    for row in table_data:
        if type(row[condition_column]) is type(condition_value) \
                and row[condition_column] == condition_value:
            row[target_column] = target_value
            updated_count += 1
            print(f"Запись с ID={row[ID_COLUMN_NAME]} успешно обновлена.")
    if updated_count == 0:
        print("Подходящие записи не найдены.")
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list[dict], where_clause: dict) -> list[dict] | None:
    """Удаляет записи по условию и возвращает список оставшихся записей."""

    if len(where_clause) != 1:
        raise ValueError("Ожидается одно условие.")

    if len(table_data) == 0:
        print("Подходящие записи не найдены.")
        return table_data

    (target_column,) = where_clause
    target_value = where_clause[target_column]

    remaining_data = []
    for row in table_data:
        if type(row[target_column]) is type(target_value) \
                and row[target_column] == target_value:
            print(f"Запись с ID={row[ID_COLUMN_NAME]} успешно удалена.")
        else:
            remaining_data.append(row)
    if len(remaining_data) == len(table_data):
        print("Подходящие записи не найдены.")
    return remaining_data


@handle_db_errors
def info(metadata: dict, table_name: str) -> None:
    """Выводит имя таблицы, её столбцы с типами и количество записей."""

    table_columns = metadata[table_name]
    table_data = utils.load_table_data(table_name)
    columns = []
    for column_name, column_type in table_columns.items():
        columns.append(f"{column_name}:{column_type}")

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(table_data)}")
