#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""

    # Diretório base do projeto (onde fica o manage.py)
    BASE_DIR = Path(__file__).resolve().parent

    # Garante que o diretório do projeto está no sys.path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    # Garante que a pasta ifteca_project também está no sys.path
    PROJECT_DIR = BASE_DIR / "ifteca_project"
    if PROJECT_DIR.exists() and str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))

    # Força o módulo de settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ifteca_project.settings")

    print("manage.py em:", __file__)
    print("BASE_DIR =", BASE_DIR)
    print("sys.path contém ifteca_project?", any("ifteca_project" in p for p in sys.path))
    print("DJANGO_SETTINGS_MODULE =", os.environ.get("DJANGO_SETTINGS_MODULE"))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
