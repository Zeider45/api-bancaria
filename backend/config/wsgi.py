import os
from pathlib import Path

try:
	from dotenv import load_dotenv
except Exception:  # pragma: no cover
	load_dotenv = None

from django.core.wsgi import get_wsgi_application

if load_dotenv is not None:
	this_file = Path(__file__).resolve()
	backend_dir = this_file.parents[1]
	repo_root = this_file.parents[2]
	load_dotenv(backend_dir / '.env', override=False)
	load_dotenv(repo_root / '.env', override=False)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
