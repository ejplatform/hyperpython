import pytest

import hyperpython


@pytest.fixture
def func():
    return


@pytest.fixture(autouse=True)
def hyperpython_function(doctest_namespace):
    hp_namespace = {
        k: v for k, v in vars(hyperpython).items() if not k.startswith('_')
    }
    doctest_namespace.update(hp_namespace)
