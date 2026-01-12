import shlex

import prompt

from src.primitive_db import core, utils
from src.primitive_db.constants import DB_FILE


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
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

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except ValueError as e:
            # Ловим ошибки бизнес-логики (неверный тип, таблица существует и т.д.)
            print(f"Ошибка: {e}")
        except Exception as e:
            # Ловим непредвиденные ошибки
            print(f"Некорректное значение или ошибка выполнения: {e}. "
                  f"Попробуйте снова.")