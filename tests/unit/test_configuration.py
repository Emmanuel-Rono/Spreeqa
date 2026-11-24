from decimal import Decimal

import pytest

from core.config import Settings, env_bool
from core.data import new_customer, usd_amount


@pytest.mark.parametrize("value, expected", [("true", True), ("false", False), (" TRUE ", True)])
def test_boolean_flags(monkeypatch, value, expected):
    monkeypatch.setenv("HEADLESS", value)
    assert env_bool("HEADLESS") is expected


def test_invalid_boolean_is_rejected(monkeypatch):
    monkeypatch.setenv("HEADLESS", "yes")
    with pytest.raises(ValueError, match="HEADLESS"):
        env_bool("HEADLESS")


def test_storefront_paths_keep_market_and_language(monkeypatch):
    monkeypatch.setenv("TEST_PRODUCT_OPTIONS", '["Red", "M"]')
    settings = Settings.from_env("http://localhost:3001/us/en/", headed=True)
    assert settings.url("/account") == "http://localhost:3001/us/en/account"
    assert settings.product_options == ("Red", "M")
    assert settings.headless is False


@pytest.mark.parametrize("url", ["localhost:3001", "file:///tmp/store", "https://a.test/?q=x", "https://u:p@a.test"])
def test_invalid_base_urls_are_rejected(url):
    with pytest.raises(ValueError):
        Settings.from_env(url)


@pytest.mark.parametrize("text, expected", [("$19.99", "19.99"), ("$1,234.50", "1234.50"),
                                          ("USD $0.10", "0.10"), ("$-5.00", "-5.00")])
def test_money_is_exact(text, expected):
    assert usd_amount(text) == Decimal(expected)
    assert usd_amount("$0.10") * 3 == Decimal("0.30")


@pytest.mark.parametrize("text", ["€19,99", "$1,2.00", "free", "$1.234", "$NaN"])
def test_invalid_or_other_market_prices_are_rejected(text):
    with pytest.raises(ValueError):
        usd_amount(text)


def test_customers_are_unique_and_password_is_not_in_repr():
    first, second = new_customer(), new_customer()
    assert first.email != second.email
    assert first.email.endswith("@example.com")
    assert first.password not in repr(first)

