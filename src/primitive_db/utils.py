import json
import os

from src.primitive_db.constants import DB_FILE

DATA_DIR = "data"

def load_metadata(filepath: str = DB_FILE) -> dict:
    """
    Загружает данные из JSON-файла.
    Если файл не найден или пуст, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_metadata(data: dict, filepath: str = DB_FILE) -> None:
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _ensure_data_dir():
    """Создает директорию для данных, если она не существует."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_table_path(table_name: str) -> str:
    """Возвращает путь к файлу данных таблицы."""
    _ensure_data_dir()
    return os.path.join(DATA_DIR, f"{table_name}.json")

def load_table_data(table_name: str) -> list[dict]:
    """Загружает список записей из JSON-файла таблицы."""
    filepath = get_table_path(table_name)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет список записей в JSON-файл."""
    filepath = get_table_path(table_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)