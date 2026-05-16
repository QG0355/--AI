import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

parser = argparse.ArgumentParser()
parser.add_argument("--username", required=True)
parser.add_argument("--password", required=True)
parser.add_argument("--role", default="student")
args = parser.parse_args()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "it_backend.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
user, created = User.objects.get_or_create(username=args.username, defaults={"role": args.role})
user.role = args.role
user.set_password(args.password)
user.save()

token, _ = Token.objects.get_or_create(user=user)

print(f"user_ready username={user.username} role={user.role} created={created}")
print(f"token={token.key}")
