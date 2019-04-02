import pytest
from sidekick import record


@pytest.fixture(autouse=True)
def add_django_ns(doctest_namespace):
    doctest_namespace.update(request=record())
