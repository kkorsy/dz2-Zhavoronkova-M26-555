# Примитивная база данных

## Управление таблицами

| Команда | Описание |
| --- | --- |
| `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` | Создать таблицу |
| `drop_table <имя_таблицы>` | Удалить таблицу |
| `list_tables` | Показать список таблиц |
| `help` | Показать справку |
| `exit` | Завершить работу |

Допустимые типы: `int`, `str`, `bool`. Имена столбцов не должны повторяться.
Столбец `ID:int` добавляется автоматически и располагается первым.
Можно указать его самостоятельно, но только с типом `int`.

Пример работы после запуска приложения:

```
Введите команду: create_table users name:str age:int is_active:bool
Таблица users успешно создана

Введите команду: create_table users name:str
Ошибка: Таблица "users" уже существует.

Введите команду: list_tables
- users

Введите команду: drop_table users
Таблица users успешно удалена

Введите команду: list_tables
Таблиц пока нет.

Введите команду: exit
```

## CRUD-операции

| Команда | Описание |
| --- | --- |
| `insert into <имя_таблицы> values (<значение1>, <значение2>, ...)` | Добавить запись |
| `select from <имя_таблицы>` | Показать все записи |
| `select from <имя_таблицы> where <столбец> = <значение>` | Показать записи по условию |
| `update <имя_таблицы> set <столбец> = <новое_значение> where <столбец> = <значение>` | Обновить записи по условию |
| `delete from <имя_таблицы> where <столбец> = <значение>` | Удалить записи по условию |
| `info <имя_таблицы>` | Показать столбцы и количество записей |

Строковые значения указываются в кавычках, логические — `true` или `false`.
Все поля обязательны. При вставке ID не передаётся, при обновлении не изменяется.
Данные сохраняются в `data/<имя_таблицы>.json`.

Пример работы с таблицей users:

```
create_table users name:str age:int is_active:bool
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
update users set age = 29 where name = "Sergei"
select from users
delete from users where ID = 1
info users
```

## Демонстрация: создание, удаление таблиц

[![asciicast](https://asciinema.org/a/TBI9f6TkTjpeiUSd.svg)](https://asciinema.org/a/TBI9f6TkTjpeiUSd)

## Демонстрация: CRUD операции

[![asciicast](https://asciinema.org/a/hHSgjmiNyTLLrvgW.svg)](https://asciinema.org/a/hHSgjmiNyTLLrvgW)
