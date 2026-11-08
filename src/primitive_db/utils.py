import json


def load_metadata(filepath: str) -> dict:
    """Загружает данные из JSON-файла.
    Если файл не найден, возвращает пустой словарь {}"""
    try:
        with open(filepath) as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}

    if not isinstance(metadata, dict):
        raise TypeError("Метаданные должны быть JSON-объектом.")
    return metadata


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет переданные данные в JSON-файл"""
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def prepare_args_create_table(args: list[str]) -> tuple[str, dict[str, str]] | None:
    """Возвращает имя таблицы и словарь столбцов или None при ошибке"""
    if len(args) < 2:
        print("Ошибка: неверное число аргументов")
        return
    table_name = args[0]
    if not table_name.strip():
        print(f"Некорректное значение: имя таблицы не может быть пустым. Попробуйте снова.")
        return

    columns = {}
    for column in args[1:]:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Ожидается имя:тип. Попробуйте снова.")
            return

        column_name, column_type = column.split(":")
        if not column_name.strip() or not column_type.strip():
            print(f"Некорректное значение: {column}. "
                "Имя и тип не могут быть пустыми. Попробуйте снова.")
            return

        if column_name in columns:
            print(f"Некорректное значение: {column_name}. "
                "Имя столбца указано несколько раз. Попробуйте снова.")
            return

        columns[column_name] = column_type

    return table_name, columns


def prepare_args_drop_table(args: list[str]) -> str | None:
    """Возвращает имя таблицы или None при ошибке"""
    if len(args) != 1:
        print("Ошибка: неверное число аргументов")
        return
    if not args[0].strip():
        print(f"Некорректное значение: имя таблицы не может быть пустым. Попробуйте снова.")
        return
    return args[0]
