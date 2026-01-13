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


def _cast_type(value: str, target_type: str):
    """Преобразует строковое значение в нужный тип."""
    try:
        if target_type == "int":
            return int(value)
        elif target_type == "bool":
            return value.lower() == "true"
        elif target_type == "str":
            return str(value)
    except ValueError:
        raise ValueError(f"Невозможно преобразовать '{value}' в тип {target_type}")
    return value


def insert(metadata: dict, table_name: str, table_data: list, values: list) -> dict:
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name} не существует.")

    schema = metadata[table_name]
    # Схема содержит ID первым элементом. Значения пользователя не содержат ID.
    expected_cols = schema[1:]

    if len(values) != len(expected_cols):
        raise ValueError(
            f"Ожидалось {len(expected_cols)} значений, получено {len(values)}. "
            f"Столбцы: {[c['name'] for c in expected_cols]}"
        )

    new_row = {}

    # Генерация ID
    if not table_data:
        new_id = 1
    else:
        new_id = max(row["ID"] for row in table_data) + 1
    new_row["ID"] = new_id

    # Валидация и кастинг типов
    for col_def, val in zip(expected_cols, values):
        col_name = col_def["name"]
        col_type = col_def["type"]
        new_row[col_name] = _cast_type(val, col_type)

    table_data.append(new_row)
    return new_row


def select(table_data: list, where_clause: dict = None) -> list:
    if not where_clause:
        return table_data

    result = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            # Сравниваем как строки, чтобы не кастить типы обратно для поиска
            if str(row.get(key)) != str(val):
                match = False
                break
        if match:
            result.append(row)
    return result


def delete(table_data: list, where_clause: dict) -> list:
    if not where_clause:
        raise ValueError("Для удаления необходимо указать условие WHERE.")

    initial_len = len(table_data)
    # Оставляем только те, которые НЕ совпадают с условием
    new_data = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if str(row.get(key)) != str(val):
                match = False
                break

        if not match:
            new_data.append(row)

    if len(new_data) == initial_len:
        raise ValueError("Записи по заданному условию не найдены.")

    return new_data


def update(metadata: dict, table_name: str, table_data: list,
           set_clause: dict, where_clause: dict) -> list:
    if not where_clause:
        raise ValueError("Для обновления необходимо указать условие WHERE.")
    if not set_clause:
        raise ValueError("Не указаны данные для обновления (SET ...).")

    schema = metadata[table_name]
    col_types = {col["name"]: col["type"] for col in schema}

    updated_count = 0
    for row in table_data:
        # Проверяем условие WHERE
        match = True
        for k, v in where_clause.items():
            if str(row.get(k)) != str(v):
                match = False
                break

        if match:
            # Применяем обновления
            for col, val in set_clause.items():
                if col not in col_types:
                    raise ValueError(f"Столбец {col} не существует.")
                if col == "ID":
                    raise ValueError("Нельзя изменять ID.")

                row[col] = _cast_type(val, col_types[col])
            updated_count += 1

    if updated_count == 0:
        raise ValueError("Записи для обновления не найдены.")

    return table_data