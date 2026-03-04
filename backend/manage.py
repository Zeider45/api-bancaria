#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # If the settings module is not set in the environment, default to 'config.settings'.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Add the apps directory to the Python path so we can import apps.users as users
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "apps"))

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
