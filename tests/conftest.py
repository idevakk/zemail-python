import pytest
import respx

from zemail import ZemailClient


@pytest.fixture
def api_key():
    return "zm_live_testkey123"


@pytest.fixture
def base_url():
    return "https://zemail.me/api"


@pytest.fixture
def client(api_key, base_url):
    with ZemailClient(api_key=api_key, base_url=base_url) as c:
        yield c


@pytest.fixture
def mock_api():
    with respx.mock(base_url="https://zemail.me/api") as respx_mock:
        yield respx_mock
