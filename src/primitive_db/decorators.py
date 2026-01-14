import functools
import time

import prompt


def handle_db_errors(func):
    """
    Декоратор для перехвата и обработки ошибок БД.
    Оборачивает функцию в try...except и выводит сообщения в консоль.
    В случае ошибки возвращает None.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
        except KeyError as e:
            print(f"Ошибка доступа к данным: {e}")
        except FileNotFoundError:
            print("Ошибка: Файл данных таблицы не найден.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return None

    return wrapper


def confirm_action(action_name: str):
    """
    Фабрика декораторов. Запрашивает подтверждение перед выполнением функции.
    Если пользователь вводит не 'y', функция не выполняется.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"Вы уверены, что хотите выполнить '{action_name}'? [y/n]: "
            answer = prompt.string(msg)

            if answer.lower() == "y":
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return None

        return wrapper

    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()

        duration = end_time - start_time
        print(f"Функция '{func.__name__}' выполнилась за {duration:.4f} секунд.")
        return result

    return wrapper


def create_cacher():
    """
    Создает замыкание для кэширования результатов.
    Возвращает функцию helper(key, func_to_call).
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        # Если нет - выполняем "тяжелую" функцию
        result = value_func()
        cache[key] = result
        return result

    return cache_result