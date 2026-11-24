import os
from urllib.parse import parse_qs, urlsplit

from helium import ENTER, Link, S, Text, click, find_all, get_driver, go_to, press, wait_until, write


class ProductsPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/products"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))
        self.product_links = "main h3 a[href*='/products/']"

    def open_products(self):
        go_to(self.url)
        wait_until(S(self.product_links).exists, timeout_secs=self.timeout)

    def search(self, query):
        click(S("button[aria-controls='search-overlay']"))
        search_field = S("#search-overlay input[type='search']")
        wait_until(search_field.exists, timeout_secs=self.timeout)
        write(query, into=search_field)
        press(ENTER)
        wait_until(lambda: parse_qs(urlsplit(get_driver().current_url).query).get("q") == [query],
                   timeout_secs=self.timeout)

    def result_names(self):
        wait_until(S(self.product_links).exists, timeout_secs=self.timeout)
        return [link.web_element.text.strip() for link in find_all(S(self.product_links))]

    def has_results(self):
        return S(self.product_links).exists()

    def empty_message(self):
        message = Text("No products found")
        wait_until(message.exists, timeout_secs=self.timeout)
        return message.web_element.text

    def open_result(self, name):
        click(Link(name))
        wait_until(S("main h1").exists, timeout_secs=self.timeout)
