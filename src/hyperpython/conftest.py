import sys
import mock

from sidekick import Record, record


class Model:
    __module__ = "django.db.models"


class User(Model, Record):
    first_name: str
    username: str

    def get_absolute_url(self):
        return "/users/" + self.username

    def __str__(self):
        return self.first_name or self.username


sys.modules["django"] = record()
sys.modules["django.contrib"] = record()
sys.modules["django.contrib.auth"] = record(get_user_model=lambda: User)
sys.modules["django.template"] = record()
sys.modules["django.template.loader"] = record(get_template=mock.Mock())
sys.modules["django.middleware"] = record()
sys.modules["django.middleware.csrf"] = record(get_token=lambda _: "csrf-token-value")
