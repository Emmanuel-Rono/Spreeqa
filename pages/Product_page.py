import json
import os
from urllib.parse import quote, urlsplit

from helium import Button, S, Text, click, find_all, get_driver, go_to, wait_until

from core.data import Product, usd_amount


class ProductPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/products"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))

    def open_product(self, slug):
        go_to(self.url + "/" + quote(slug, safe=""))
        wait_until(Button("Add to Cart").exists, timeout_secs=self.timeout)

    def choose_options(self, values):
        for value in values:
            color = S("main button[title={}]".format(json.dumps(value, ensure_ascii=False)))
            if color.exists():
                click(color)
            else:
                click(Button(value))
        wait_until(Button("Add to Cart").is_enabled, timeout_secs=self.timeout)

    def snapshot(self):
        name = S("main h1").web_element.text.strip()
        price = S("main h1 ~ div > span.text-3xl").web_element.text
        sku = S("main dl > div:first-child dd").web_element.text.strip()
        options = find_all(S("main dl > div:nth-child(2) dd"))
        slug = urlsplit(get_driver().current_url).path.rstrip("/").split("/")[-1]
        return Product(name, slug, sku, options[0].web_element.text.strip() if options else "",
                       usd_amount(price), "USD")

    def add_to_cart(self, product):
        click("Add to Cart")
        wait_until(S("[role='dialog'] a[href$='/cart']").exists, timeout_secs=self.timeout)

    def open_cart(self):
        click("View Cart")
        wait_until(Text("Shopping Cart").exists, timeout_secs=self.timeout)
