import os
import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db import core, decorators, parser, utils
from src.primitive_db.constants import DB_FILE


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values "
          "(<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - "
          "прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - "
          "удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главный цикл приложения."""
    print_help()

    # Инициализируем кэш (замыкание) перед запуском цикла
    db_cacher = decorators.create_cacher()

    while True:
        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка парсинга команды. Проверьте парность кавычек.")
            continue

        if not args:
            continue

        command = args[0]
        # Загружаем актуальное состояние перед каждой операцией
        metadata = utils.load_metadata(DB_FILE)

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            tables = list(metadata.keys())
            if tables:
                for table in tables:
                    print(f"- {table}")
            else:
                print("База данных пуста.")

        # --- Управление таблицами ---
        elif command == "create_table":
            if len(args) < 2:
                print("Ошибка: Укажите имя таблицы.")
                continue

            table_name = args[1]
            column_defs = args[2:]

            # Декораторы в core обрабатывают ошибки. Если успех - вернется dict.
            new_metadata = core.create_table(metadata, table_name, column_defs)

            if new_metadata is not None:
                utils.save_metadata(new_metadata, DB_FILE)
                # Получаем красивую строку схемы для вывода (не сохраняем)
                schema = core.get_table_schema_str(new_metadata, table_name)
                print(f'Таблица "{table_name}" успешно создана '
                      f'со столбцами: {schema}')

        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Укажите имя таблицы.")
                continue

            table_name = args[1]

            # core.drop_table теперь спрашивает подтверждение (@confirm_action)
            new_metadata = core.drop_table(metadata, table_name)

            if new_metadata is not None:
                utils.save_metadata(new_metadata, DB_FILE)
                # Удаляем физический файл данных, если он есть
                file_path = utils.get_table_path(table_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f'Таблица "{table_name}" успешно удалена.')

        # --- CRUD операции ---

        elif command == "insert":
            if len(args) < 4 or args[1] != "into":
                print("Ошибка синтаксиса. Используйте: "
                      "insert into <table> values (...)")
                continue

            table_name = args[2]
            values_list = parser.parse_insert_values(args)

            data = utils.load_table_data(table_name)
            # core.insert использует @log_time и @handle_db_errors
            new_record = core.insert(metadata, table_name, data, values_list)

            if new_record is not None:
                utils.save_table_data(table_name, data)
                print(f"Запись с ID={new_record['ID']} успешно "
                      f"добавлена в таблицу \"{table_name}\".")

        elif command == "select":
            if len(args) < 3 or args[1] != "from":
                print("Ошибка синтаксиса. Используйте: select from <table> ...")
                continue

            table_name = args[2]
            where_clause = parser.parse_where_clause(args)

            if table_name not in metadata:
                print(f"Таблица {table_name} не существует.")
                continue

            # Формируем уникальный ключ для кэша
            cache_key = (table_name, str(where_clause))

            # Оборачиваем вызов в функцию для кэшера
            def fetch_data_operation():
                current_data = utils.load_table_data(table_name)
                return core.select(current_data, where_clause)

            # Вызываем через замыкание-кэшер
            result = db_cacher(cache_key, fetch_data_operation)

            # Если вернулся None (ошибка внутри core), ничего не делаем
            if result is not None:
                # Вывод через PrettyTable
                pt = PrettyTable()
                headers = [col["name"] for col in metadata[table_name]]
                pt.field_names = headers

                if result:
                    for row in result:
                        pt.add_row([row.get(h) for h in headers])
                    print(pt)
                else:
                    print("Записи не найдены.")

        elif command == "delete":
            if len(args) < 5 or args[1] != "from":
                print("Ошибка синтаксиса.")
                continue

            table_name = args[2]
            where_clause = parser.parse_where_clause(args)
            data = utils.load_table_data(table_name)

            # core.delete спрашивает подтверждение
            new_data = core.delete(data, where_clause)

            if new_data is not None:
                utils.save_table_data(table_name, new_data)
                print(f"Записи успешно удалены из таблицы \"{table_name}\".")

        elif command == "update":
            if len(args) < 6:
                print("Ошибка синтаксиса.")
                continue

            table_name = args[1]
            set_clause = parser.parse_set_clause(args)
            where_clause = parser.parse_where_clause(args)
            data = utils.load_table_data(table_name)

            # core.update изменяет данные
            updated_data = core.update(
                metadata, table_name, data, set_clause, where_clause
            )

            if updated_data is not None:
                utils.save_table_data(table_name, updated_data)
                print(f"Записи в таблице \"{table_name}\" успешно обновлены.")

        elif command == "info":
            if len(args) < 2:
                continue
            table_name = args[1]
            if table_name in metadata:
                print(f"Таблица: {table_name}")
                schema_str = ", ".join([f"{c['name']}:{c['type']}"
                                        for c in metadata[table_name]
                                        ])
                print(f"Столбцы: {schema_str}")
                data = utils.load_table_data(table_name)
                print(f"Количество записей: {len(data)}")
            else:
                print("Таблица не найдена")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
