import csv
from argparse import Namespace

import pytest
from tabulate import tabulate

from main import aggregate_data, display_table, filter_data, get_args, read_csv


def test_read_csv_success(tmp_path):
    # Создаём временный CSV-файл
    file_path = tmp_path / 'test.csv'
    data = [
        {'name': 'iphone 15', 'price': '999'},
        {'name': 'galaxy s23', 'price': '1199'},
    ]

    # Пишем данные в файл
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'price'])
        writer.writeheader()
        writer.writerows(data)

    # Тест: чтение CSV
    result = read_csv(str(file_path))
    assert result == data


def test_read_csv_file_not_found():
    # Тест: файл не существует
    with pytest.raises(FileNotFoundError):
        read_csv('non_existent_file.csv')


@pytest.mark.parametrize(
    'data, expected_output',
    [
        (
            # случай с данными
            [
                {'name': 'iphone 15', 'price': '999'},
                {'name': 'galaxy s23', 'price': '1199'}
            ],
            tabulate([
                {'name': 'iphone 15', 'price': '999'},
                {'name': 'galaxy s23', 'price': '1199'}
            ], headers='keys', tablefmt='orgtbl') + '\n'
        ),
        (
            # случай без данных
            [],
            'Нет данных для отображения.\n'
        ),
    ]
)
def test_display_table_parametrized(data, expected_output, capsys):
    display_table(data)
    captured = capsys.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize(
    'data, column, value, operator, expected',
    [
        # Оператор '='
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple'},
                {'name': 'Galaxy S23', 'brand': 'samsung'}
            ],
            'brand', 'apple', '=', [{'name': 'iPhone 15', 'brand': 'apple'}]
        ),
        # Оператор '<'
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple', 'price': 999},
                {'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}
            ],
            'price', 1000, '<',
            [{'name': 'iPhone 15', 'brand': 'apple', 'price': 999}]
        ),
        # Оператор '>'
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple', 'price': 999},
                {'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}
            ],
            'price', 1000, '>',
            [{'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}]
        )
    ]
)
def test_filter_data(data, column, value, operator, expected):
    result = filter_data(data, column, value, operator)
    assert result == expected


@pytest.mark.parametrize(
    'data, column, value, expected',
    [
        # Минимум
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple', 'price': 999},
                {'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}
            ],
            'price',
            'min',
            [{'min': 999.0}]
        ),
        # Максимум
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple', 'price': 999},
                {'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}
            ],
            'price',
            'max',
            [{'max': 1199.0}]
        ),
        # Среднее
        (
            [
                {'name': 'iPhone 15', 'brand': 'apple', 'price': 999},
                {'name': 'Galaxy S23', 'brand': 'samsung', 'price': 1199}
            ],
            'price',
            'avg',
            [{'avg': 1099.0}]
        ),
    ]
)
def test_aggregate_data(data, column, value, expected):
    result = aggregate_data(data, column, value)
    assert result == expected


@pytest.mark.parametrize(
    'argv, expected',
    [
        # Только обязательный аргумент
        (
            ['--file', 'data.csv'],
            Namespace(file='data.csv', where=None, aggregate=None)
        ),
        # С аргументом where
        (
            ['--file', 'data.csv', '--where', 'price>1000'],
            Namespace(file='data.csv', where='price>1000', aggregate=None)
        ),
        # С аргументами where и aggregate
        (
            ['--file', 'data.csv', '--where', 'price=999',
             '--aggregate', 'price=avg'],
            Namespace(
                file='data.csv', where='price=999', aggregate='price=avg'
            )
        )
    ]
)
def test_get_args_success(argv, expected):
    result = get_args(argv)
    assert result == expected
