import time


def handle_db_errors(func):
    """Выводит сообщение об ошибке базы данных и возвращает None."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. "
                  "Возможно, база данных не инициализирована.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except (OSError, TypeError) as error:
            print(f"Ошибка базы данных: {error}")
        return None

    return wrapper


def confirm_action(action_name: str):
    """Запрашивает подтверждение перед выполнением действия."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.strip() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Выводит время выполнения функции в секундах."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return wrapper


def create_cacher():
    """Возвращает функцию, которая хранит результаты в словаре замыкания."""

    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
