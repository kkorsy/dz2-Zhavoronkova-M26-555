import json
import os


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



def load_table_data(table_name: str) -> list[dict]:
    """Загружает список записей из data/<table_name>.json."""

    try:
        with open(f"data/{table_name}.json") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise TypeError("Данные таблицы должны быть JSON-массивом.")
    return data


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет список записей в data/<table_name>.json."""

    os.makedirs("data", exist_ok=True)
    with open(f"data/{table_name}.json", "w") as file:
        json.dump(data, file, indent=4)
