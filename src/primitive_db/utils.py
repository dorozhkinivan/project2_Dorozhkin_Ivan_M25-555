import json

from src.primitive_db.constants import DB_FILE


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