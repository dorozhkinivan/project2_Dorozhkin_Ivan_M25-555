import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db import core, parser, utils
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
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главный цикл приложения."""
    print_help()

    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            args = shlex.split(user_input)

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
                # create_table users name:str age:int
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue

                table_name = args[1]
                column_defs = args[2:]

                metadata = core.create_table(metadata, table_name, column_defs)
                utils.save_metadata(metadata, DB_FILE)

                schema = core.get_table_schema_str(metadata, table_name)
                print(f'Таблица "{table_name}" успешно создана со столбцами: {schema}')

            elif command == "drop_table":
                # drop_table users
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue

                table_name = args[1]

                metadata = core.drop_table(metadata, table_name)
                utils.save_metadata(metadata, DB_FILE)
                print(f'Таблица "{table_name}" успешно удалена.')

            # --- crud операции ---

            elif command == "insert":
                # Синтаксис: insert into <table> values (...)
                if len(args) < 4 or args[1] != "into":
                    print("Ошибка синтаксиса. Используйте: "
                          "insert into <table> values (...)")
                    continue

                table_name = args[2]
                values_list = parser.parse_insert_values(args)  # Наш новый метод

                data = utils.load_table_data(table_name)  # Загружаем данные

                new_record = core.insert(metadata, table_name, data, values_list)

                utils.save_table_data(table_name, data)  # Сохраняем
                print(f"Запись с ID={new_record['ID']} успешно "
                      f"добавлена в таблицу \"{table_name}\".")

            elif command == "select":
                # select from <table> [where col=val]
                if len(args) < 3 or args[1] != "from":
                    print("Ошибка синтаксиса. Используйте: select from <table> ...")
                    continue

                table_name = args[2]
                where_clause = parser.parse_where_clause(args)

                if table_name not in metadata:
                    print(f"Таблица {table_name} не существует.")
                    continue

                data = utils.load_table_data(table_name)
                result = core.select(data, where_clause)

                # Вывод через PrettyTable
                pt = PrettyTable()
                # Получаем заголовки из метаданных, чтобы сохранить порядок
                headers = [col["name"] for col in metadata[table_name]]
                pt.field_names = headers

                if result:
                    for row in result:
                        pt.add_row([row.get(h) for h in headers])
                    print(pt)
                else:
                    print("Записи не найдены.")

            elif command == "delete":
                # delete from <table> where col=val
                if len(args) < 5 or args[1] != "from":
                    print("Ошибка синтаксиса.")
                    continue

                table_name = args[2]
                where_clause = parser.parse_where_clause(args)

                data = utils.load_table_data(table_name)
                # delete возвращает НОВЫЙ список данных
                new_data = core.delete(data, where_clause)

                utils.save_table_data(table_name, new_data)
                print(f"Записи успешно удалены из таблицы \"{table_name}\".")

            elif command == "update":
                # update <table> set col=val where col=val
                if len(args) < 6:
                    print("Ошибка синтаксиса.")
                    continue

                table_name = args[1]
                set_clause = parser.parse_set_clause(args)
                where_clause = parser.parse_where_clause(args)

                data = utils.load_table_data(table_name)
                # update изменяет список data in-place (или возвращает его)
                core.update(metadata, table_name, data, set_clause, where_clause)

                utils.save_table_data(table_name, data)
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

        except ValueError as e:
            # Ловим ошибки бизнес-логики (неверный тип, таблица существует и т.д.)
            print(f"Ошибка: {e}")
        except Exception as e:
            # Ловим непредвиденные ошибки
            print(f"Некорректное значение или ошибка выполнения: {e}. "
                  f"Попробуйте снова.")