#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beatstore.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедись, что он установлен "
            "и что виртуальное окружение активировано."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
