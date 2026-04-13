#!/usr/bin/env python
import os
import sys

def main():
    """Executa as tarefas administrativas do Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Verifique se ele está instalado "
            "no seu ambiente virtual (venv) e se o PYTHONPATH está correto."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()