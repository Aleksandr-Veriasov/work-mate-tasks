import csv
import os
from argparse import ArgumentParser, Namespace

from tabulate import tabulate


def read_csv(file_path: str) -> list:
    """ Чтение CSV-файла и возврат данных в виде списка словарей. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def display_table(data: list) -> None:
    """
    Отображение данных в виде таблицы с использованием библиотеки tabulate.
    """
    if not data:
        print('Нет данных для отображения.')
        return

    table: str = tabulate(data, headers='keys', tablefmt='orgtbl')
    print(table)


def filter_data(
        data: list[dict], column: str, value: str, operator: str
) -> list:
    """
    Фильтрация данных по ключу и значению с использованием оператора сравнения.
    Поддерживаются операторы '=', '<', '>'.
    """
    filtered_data: list[dict] = []
    for row in data:
        if column in row:
            if operator == '=' and row[column] == value:
                filtered_data.append(row)
            elif operator == '<' and row[column] < value:
                filtered_data.append(row)
            elif operator == '>' and row[column] > value:
                filtered_data.append(row)
    return filtered_data


def aggregate_data(data: list[dict], column: str, value: str) -> list[dict]:
    """
    Агрегация данных по заданному ключу.
    Возвращает словарь с агрегированными значениями.
    """
    parsed_data: list = []
    for row in data:
        field_value = float(row[column])
        parsed_data.append(field_value)

    if value == 'min':
        result = min(parsed_data)
    elif value == 'max':
        result = max(parsed_data)
    elif value == 'avg':
        result = sum(parsed_data) / len(parsed_data)
    return [{value: result}]


def get_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(
        description='Чтение CSV-файла и отображение его содержимого.'
    )
    parser.add_argument(
        '--file', type=str, required=True, help='Путь к CSV-файлу'
    )
    parser.add_argument(
        '--where',
        type=str,
        required=False,
        help=(
            'Фильтр в формате "столбец=значение или '
            'столбец<значение/столбец>значение"'
        )
    )
    parser.add_argument(
        '--aggregate',
        type=str,
        required=False,
        help=(
            'Агрегация данных, по формату "столбец=функция",'
            'где функция может быть min, max, avg'
        )
    )
    return parser.parse_args(argv)


def main() -> None:
    """ Основная функция для выполнения программы. """
    try:
        args: Namespace = get_args()
        data: list[dict] = read_csv(args.file)
        if args.where:
            # Разбор условия фильтрации
            if '=' in args.where:
                column, value = args.where.split('=')
                operator = '='
            elif '<' in args.where:
                column, value = args.where.split('<')
                operator = '<'
            elif '>' in args.where:
                column, value = args.where.split('>')
                operator = '>'
            else:
                raise ValueError(
                    'Неверный формат фильтрации. Используйте ключ=значение,'
                    ' ключ<значение или ключ>значение.'
                )
            # Фильтрация данных
            data = filter_data(data, column.strip(), value.strip(), operator)
        if args.aggregate:
            # Агрегация данных
            colums, value = args.aggregate.split('=')
            data = aggregate_data(data, colums.strip(), value.strip())
        # Отображение данных в виде таблицы
        display_table(data)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
