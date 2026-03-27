#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


def main():
    """Run administrative tasks."""
    # Load env from files for local execution (outside Docker).
    # Docker Compose injects env vars directly (env_file: .env), so this is harmless there.
    if load_dotenv is not None:
        backend_dir = Path(__file__).resolve().parent
        repo_root = backend_dir.parent
        load_dotenv(backend_dir / '.env', override=False)
        load_dotenv(repo_root / '.env', override=False)

    # Default to development settings if not provided.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
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
