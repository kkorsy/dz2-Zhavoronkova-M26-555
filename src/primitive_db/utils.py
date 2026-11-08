import json
import os

from primitive_db.constants import DATA_DIRECTORY, JSON_INDENT


def get_table_filepath(table_name: str) -> str:
    """Возвращает путь к JSON-файлу таблицы."""
    return os.path.join(DATA_DIRECTORY, f"{table_name}.json")


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
        json.dump(data, file, indent=JSON_INDENT)


def load_table_data(table_name: str) -> list[dict]:
    """Загружает список записей из data/<table_name>.json."""

    try:
        with open(get_table_filepath(table_name)) as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise TypeError("Данные таблицы должны быть JSON-массивом.")
    return data


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет список записей в data/<table_name>.json."""

    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    with open(get_table_filepath(table_name), "w") as file:
        json.dump(data, file, indent=JSON_INDENT)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл таблицы, если он существует."""
    filepath = get_table_filepath(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)
