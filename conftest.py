import pytest


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    # Compatibility with pytest 9.2 for the pytest-playwright fallback fixture.
    return pytestconfig.getoption("--base-url") or pytestconfig.getini("base_url") or None
