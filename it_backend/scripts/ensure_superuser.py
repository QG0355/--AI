import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

parser = argparse.ArgumentParser()
parser.add_argument("--username", default=os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"))
parser.add_argument("--email", default=os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com"))
parser.add_argument("--password", default=os.environ.get("DJANGO_SUPERUSER_PASSWORD"))
args = parser.parse_args()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "it_backend.settings")

import django

django.setup()

from django.contrib.auth import get_user_model

username = args.username
email = args.email
password = args.password

if not password:
    raise SystemExit("Missing password (use --password or DJANGO_SUPERUSER_PASSWORD)")

User = get_user_model()
user, created = User.objects.get_or_create(
    username=username,
    defaults={"email": email, "is_staff": True, "is_superuser": True},
)

user.is_staff = True
user.is_superuser = True
if email:
    user.email = email
user.set_password(password)
user.save()

print(f"superuser_ready username={username} created={created}")
