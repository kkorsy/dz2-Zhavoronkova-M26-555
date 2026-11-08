def split_command(command: str) -> list[str] | None:
    """Разделяет команду на части, сохраняя кавычки и пробелы внутри строк."""

    parts = _split_outside_quotes(command, " ")
    if parts is None:
        return None

    result = []
    for part in parts:
        if part != "":
            result.append(part)
    return result


def parse_args_create_table(args: list[str]) -> tuple[str, dict[str, str]] | None:
    """Возвращает имя таблицы и словарь столбцов или None при ошибке"""

    if len(args) < 2:
        print("Ошибка: неверное число аргументов")
        return
    table_name = _parse_table_name(args[0])
    if table_name is None:
        return

    columns = {}
    for column in args[1:]:
        if column.startswith(("'", '"')):
            parsed_column = parse_value(column)
            if not isinstance(parsed_column, str):
                return
            column = parsed_column
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Ожидается имя:тип. Попробуйте снова.")
            return

        column_name, column_type = column.split(":")
        if not column_name.strip() or not column_type.strip():
            print(
                f"Некорректное значение: {column}. "
                "Имя и тип не могут быть пустыми. Попробуйте снова."
            )
            return

        if column_name in columns:
            print(
                f"Некорректное значение: {column_name}. "
                "Имя столбца указано несколько раз. Попробуйте снова."
            )
            return

        columns[column_name] = column_type

    return table_name, columns


def parse_args_drop_table(args: list[str]) -> str | None:
    """Возвращает имя таблицы или None при ошибке"""

    if len(args) != 1:
        print("Ошибка: неверное число аргументов")
        return
    return _parse_table_name(args[0])


def parse_args_insert(args: list[str]) -> tuple[str, list] | None:
    """Разбирает into <таблица> values (...) в имя таблицы и список значений."""

    if len(args) < 4 or args[0] != "into" or args[2] != "values":
        print("Ошибка: ожидается insert into <имя_таблицы> values (...).")
        return None

    table_name = _parse_table_name(args[1])
    if table_name is None:
        return None
    values = parse_insert_values(" ".join(args[3:]))
    if values is None:
        return None
    return table_name, values


def parse_args_select(args: list[str]) -> tuple[str, dict | None] | None:
    """Разбирает from <таблица> с необязательным условием where."""

    if len(args) < 2 or args[0] != "from":
        print("Ошибка: ожидается select from <имя_таблицы> [where <столбец> = <значение>].")
        return None

    table_name = _parse_table_name(args[1])
    if table_name is None:
        return None
    if len(args) == 2:
        return table_name, None
    if args[2] != "where" or len(args) < 4:
        print("Ошибка: ожидается where <столбец> = <значение>.")
        return None

    where_clause = parse_where_clause(" ".join(args[3:]))
    if where_clause is None:
        return None
    return table_name, where_clause


def parse_args_update(args: list[str]) -> tuple[str, dict, dict] | None:
    """Разбирает <таблица> set <присваивание> where <условие>."""

    if len(args) < 5 or args[1] != "set" or "where" not in args[3:]:
        print("Ошибка: ожидается update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>.")
        return None

    table_name = _parse_table_name(args[0])
    if table_name is None:
        return None
    where_index = args.index("where", 3)
    set_clause = parse_set_clause(" ".join(args[2:where_index]))
    if set_clause is None:
        return None
    where_clause = parse_where_clause(" ".join(args[where_index + 1:]))
    if where_clause is None:
        return None
    return table_name, set_clause, where_clause


def parse_args_delete(args: list[str]) -> tuple[str, dict] | None:
    """Разбирает from <таблица> where <условие>."""

    if len(args) < 4 or args[0] != "from" or args[2] != "where":
        print("Ошибка: ожидается delete from <имя_таблицы> where <столбец> = <значение>.")
        return None

    table_name = _parse_table_name(args[1])
    if table_name is None:
        return None
    where_clause = parse_where_clause(" ".join(args[3:]))
    if where_clause is None:
        return None
    return table_name, where_clause


def parse_args_info(args: list[str]) -> str | None:
    """Возвращает имя таблицы для команды info."""

    if len(args) != 1:
        print("Ошибка: ожидается info <имя_таблицы>.")
        return None
    return _parse_table_name(args[0])


def _parse_table_name(table_name: str) -> str | None:
    """Проверяет имя таблицы и убирает внешние кавычки, если они есть."""

    if table_name.startswith(("'", '"')):
        parsed_name = parse_value(table_name)
        if not isinstance(parsed_name, str):
            return None
        table_name = parsed_name
    if not table_name.strip():
        print("Ошибка: имя таблицы не может быть пустым.")
        return None
    return table_name


def parse_value(value: str) -> str | int | bool | None:
    """Преобразует текстовое значение в str, int или bool."""

    value = value.strip()
    if not value:
        print("Ошибка: значение не может быть пустым.")
        return None

    if value[0] in {"'", '"'}:
        if len(value) < 2 or value[-1] != value[0] or value[0] in value[1:-1]:
            print(f"Некорректная строка: {value}.")
            return None
        return value[1:-1]

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        print(
            f"Некорректное значение: {value}. "
            "Ожидается целое число, true/false или строка в кавычках."
        )
        return None


def parse_insert_values(values: str) -> list[str | int | bool] | None:
    """Преобразует фрагмент после values в список типизированных значений."""

    values = values.strip()
    if not values.startswith("(") or not values.endswith(")"):
        print("Ошибка: значения insert должны быть заключены в круглые скобки.")
        return None

    content = values[1:-1].strip()
    if not content:
        return []

    parts = _split_outside_quotes(content, ",")
    if parts is None:
        return None

    result = []
    for part in parts:
        value = parse_value(part)
        if value is None:
            return None
        result.append(value)
    return result


def parse_where_clause(condition: str) -> dict[str, str | int | bool] | None:
    """Разбирает равенство после where в словарь условия."""
    return _parse_assignment(condition)


def parse_set_clause(assignment: str) -> dict[str, str | int | bool] | None:
    """Разбирает присваивание между set и where в словарь новых значений"""
    return _parse_assignment(assignment)


def _split_outside_quotes(text: str, separator: str) -> list[str] | None:
    """Разделяет текст по символу separator только вне кавычек."""

    parts = []
    start = 0
    quote = None

    for index, char in enumerate(text):
        if quote is not None:
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == separator or (separator == " " and char.isspace()):
            parts.append(text[start:index].strip())
            start = index + 1

    if quote is not None:
        print("Ошибка: незакрытая кавычка в значении.")
        return None

    parts.append(text[start:].strip())
    return parts


def _parse_assignment(expression: str) -> dict[str, str | int | bool] | None:
    """Разбирает общее для where и set выражение вида столбец = значение."""

    parts = _split_outside_quotes(expression, "=")
    if parts is None:
        return None
    if len(parts) != 2:
        print("Ошибка: ожидается выражение вида столбец = значение.")
        return None

    column_name, value = parts
    if column_name == "":
        print("Ошибка: имя столбца не может быть пустым.")
        return None
    parsed_value = parse_value(value)
    if parsed_value is None:
        return None
    return {column_name: parsed_value}
