import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "django_db: mark a test as using the database")
    setattr(config.option, "migrations", False)

@pytest.fixture(autouse=True)
def _django_db_setup(request):
    pass