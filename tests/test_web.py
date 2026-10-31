import pytest
from django.test import Client

from db.import_json import import_data


@pytest.fixture(autouse=True)
def database():
    import_data()


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/accidents/",
        "/accidents/1/",
        "/accidents/search/?severity=emergency",
        "/accidents/participants/",
        "/accidents/statistics/",
    ],
)
def test_pages_open(url):
    response = Client().get(url)
    assert response.status_code == 200


def test_unknown_accident_returns_404():
    response = Client().get("/accidents/999/")
    assert response.status_code == 404
