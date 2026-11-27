"""A number that is not finite is the caller's error, not the server's (DR-14).

Review of 27 Nov 2026: `GET /api/proportions/gibbs-ionic?column_diameter=inf&members=true`
answered 500 with `ValueError: cannot convert float NaN to integer` in the log. FastAPI parses
`inf` and `nan` as floats, and nothing downstream expects them.
"""
import pytest

CASES = [
    "/api/proportions/gibbs-ionic?column_diameter=inf&members=true",
    "/api/proportions/gibbs-ionic?column_diameter=nan",
    "/api/proportions/gibbs-ionic?module=-inf",
    "/api/proportions/gibbs-ionic?ceiling_height=nan&members=true",
    "/api/authorities/ionic?column_diameter=inf",
    "/api/kit/craftsman?ceiling_height=nan",
]


@pytest.mark.parametrize("url", CASES)
def test_a_non_finite_number_is_a_422_naming_the_argument(client, url):
    r = client.get(url)
    assert r.status_code == 422, f"{url} answered {r.status_code}"
    name = url.split("?", 1)[1].split("=", 1)[0]
    assert name in r.text


@pytest.mark.parametrize("url", [
    "/api/proportions/gibbs-ionic?column_diameter=12&members=true",
    "/api/authorities/ionic?column_diameter=12",
    "/api/kit/craftsman?ceiling_height=108",
])
def test_an_ordinary_number_is_still_answered(client, url):
    assert client.get(url).status_code == 200
