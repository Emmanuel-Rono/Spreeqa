import re
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

from faker import Faker


@dataclass(frozen=True)
class Customer:
    first_name: str
    last_name: str
    email: str
    password: str = field(repr=False)


def new_customer():
    fake = Faker("en_US")
    return Customer(fake.first_name(), fake.last_name(),
                    "spreeqa-{}@example.com".format(uuid4().hex), "Spreeqa-Test-2026!")


@dataclass(frozen=True)
class Product:
    name: str
    slug: str
    sku: str
    options: str
    unit_price: Decimal
    currency: str


@dataclass(frozen=True)
class Address:
    first_name: str = "Test"
    last_name: str = "Customer"
    country: str = "United States"
    address1: str = "123 Test Street"
    city: str = "New York"
    state: str = "New York"
    postal_code: str = "10001"
    phone: str = "2125550100"


def usd_amount(text):
    """Parse US storefront money exactly; reject other or ambiguous currencies."""
    match = re.fullmatch(r"\s*(?:USD\s*)?\$\s*(-?\d{1,3}(?:,\d{3})*|-?\d+)\.(\d{2})\s*", text)
    if not match:
        raise ValueError("Expected a US-dollar amount, received {!r}".format(text))
    return Decimal(match.group(1).replace(",", "") + "." + match.group(2))
