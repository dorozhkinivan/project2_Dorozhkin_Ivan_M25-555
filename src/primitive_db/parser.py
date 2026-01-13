def clean_value(val: str) -> str:
    """Удаляет лишние кавычки и запятые из значения."""
    return val.strip('",\'')


def parse_where_clause(args: list[str]) -> dict:
    """
    Парсит часть команды после WHERE.
    Ожидается формат: ['col', '=', 'val']
    Поддерживает пока только одно условие.
    """
    if not args or len(args) < 3:
        return {}

    # Ищем индекс слова where, если оно попало в args
    start_idx = 0
    if "where" in args:
        start_idx = args.index("where") + 1

    if start_idx + 2 >= len(args):
        return {}

    col = args[start_idx]
    op = args[start_idx + 1]
    val = args[start_idx + 2]

    if op != "=":
        return {}  # Пока поддерживаем только равенство

    return {col: clean_value(val)}


def parse_set_clause(args: list[str]) -> dict:
    """
    Парсит часть команды для UPDATE (SET col = val).
    Возвращает словарь изменений.
    Останавливается, если встречает 'where'.
    """
    if "set" not in args:
        return {}

    start = args.index("set") + 1
    end = args.index("where") if "where" in args else len(args)

    set_part = args[start:end]
    updates = {}

    # Проходим тройками: col = val
    # Учитываем, что values могут склеиться или быть с запятыми
    i = 0
    while i < len(set_part) - 2:
        col = set_part[i]
        # set_part[i+1] должен быть "="
        val = clean_value(set_part[i + 2])
        updates[col] = val
        i += 3  # переходим к следующей тройке или концу

    return updates


def parse_insert_values(raw_args: list[str]) -> list[str]:
    """
    Вытаскивает значения из команды insert.
    Работает с сырым списком токенов, ищет слово `values` и обрабатывает всё что после.
    """
    if "values" not in raw_args:
        return []

    val_idx = raw_args.index("values") + 1
    # Собираем всё что после values в одну строку, чтобы убрать скобки
    values_raw = " ".join(raw_args[val_idx:])
    values_raw = values_raw.replace("(", "").replace(")", "")

    parts = [clean_value(p.strip()) for p in values_raw.split(",")]
    return parts