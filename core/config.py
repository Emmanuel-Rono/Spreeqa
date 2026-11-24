import json
import os
from dataclasses import dataclass
from urllib.parse import urlsplit


def env_bool(name, default=False):
    value = os.getenv(name, str(default)).strip().lower()
    if value not in {"true", "false"}:
        raise ValueError("{} must be 'true' or 'false'".format(name))
    return value == "true"


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout: int = 30
    headless: bool = True
    product_slug: str = ""
    product_options: tuple = ()
    driver_path: str = ""
    stripe_payment_method: str = "Credit Card"

    def url(self, path=""):
        return self.base_url.rstrip("/") + ("/" + path.lstrip("/") if path else "")

    @classmethod
    def from_env(cls, base_url=None, headed=False):
        base_url = (base_url or os.getenv("BASE_URL", "http://localhost:3001/us/en")).rstrip("/")
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("BASE_URL must be a full storefront URL without a query or fragment")
        if parsed.username or parsed.password:
            raise ValueError("Do not include credentials in BASE_URL")
        timeout = int(os.getenv("WAIT_TIMEOUT", "30"))
        if timeout <= 0:
            raise ValueError("WAIT_TIMEOUT must be positive")
        options = json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]"))
        if not isinstance(options, list) or not all(isinstance(x, str) and x for x in options):
            raise ValueError('TEST_PRODUCT_OPTIONS must be a JSON list, such as ["Red", "M"]')
        return cls(base_url, timeout, False if headed else env_bool("HEADLESS", True),
                   os.getenv("TEST_PRODUCT_SLUG", ""), tuple(options), os.getenv("CHROMEDRIVER_PATH", ""),
                   os.getenv("STRIPE_PAYMENT_METHOD", "Credit Card"))
