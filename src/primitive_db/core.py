from src.primitive_db.constants import SUPPORTED_TYPES


def create_table(metadata: dict, table_name: str, args: list) -> dict:
    """
    Создает новую таблицу в метаданных.
    args: список строк вида ['col1:type', 'col2:type']
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    columns = [{"name": "ID", "type": "int"}]  # ID добавляем всегда первым

    for arg in args:
        if ":" not in arg:
            raise ValueError(f"Некорректный формат столбца: {arg}. "
                             f"Ожидается 'имя:тип'.")

        col_name, col_type = arg.split(":", 1)

        if col_type not in SUPPORTED_TYPES:
            raise ValueError(
                f"Неизвестный тип данных: {col_type}. "
                f"Допустимые: {', '.join(SUPPORTED_TYPES)}"
            )

        columns.append({"name": col_name, "type": col_type})

    metadata[table_name] = columns
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


def get_table_schema_str(metadata: dict, table_name: str) -> str:
    """Вспомогательная функция для красивого вывода структуры при создании."""
    columns = metadata[table_name]
    # Преобразуем список словарей обратно в строку вида "ID:int, name:str"
    return ", ".join([f"{col['name']}:{col['type']}" for col in columns])