import json
import os
from urllib.parse import urlsplit

from helium import S, Text, click, find_all, get_driver, go_to, refresh, wait_until

from core.data import usd_amount


class CartPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/cart"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))

    def open_cart(self):
        go_to(self.url)

    def item_selector(self, name):
        # Select the cart row containing this product's labelled Remove button.
        label = json.dumps("Remove " + name, ensure_ascii=False)
        return "main div:has(> div > button[aria-label={}])".format(label)

    def has_item(self, name):
        return S(self.item_selector(name)).exists()

    def item(self, name):
        row = self.item_selector(name)
        wait_until(S(row).exists, timeout_secs=self.timeout)
        details = row + " > div:has(> h3)"
        paragraphs = find_all(S(details + " > p"))
        return {
            "name": S(details + " > h3").web_element.text.strip(),
            "options": paragraphs[0].web_element.text.strip() if len(paragraphs) > 1 else "",
            "unit_price": usd_amount(S(details + " > p:last-child").web_element.text),
            "quantity": int(S(row + " input[aria-label='Quantity']").web_element.get_attribute("value")),
        }

    def subtotal(self):
        subtotal = S("main dl > div:first-child dd")
        wait_until(subtotal.exists, timeout_secs=self.timeout)
        return usd_amount(subtotal.web_element.text)

    def wait_for_subtotal(self, amount):
        wait_until(lambda: self.subtotal() == amount, timeout_secs=self.timeout)
        return self.subtotal()

    def increase_quantity(self, name, expected):
        button = S(self.item_selector(name) + " button[aria-label='Increase quantity']")
        click(button)
        wait_until(lambda: self.item(name)["quantity"] == expected, timeout_secs=self.timeout)
        wait_until(lambda: button.web_element.is_enabled(), timeout_secs=self.timeout)

    def remove(self, name):
        # The icon has no text, but Spree gives its button an aria-label.
        label = json.dumps("Remove " + name, ensure_ascii=False)
        remove_button = S("main button[aria-label={}]".format(label))
        wait_until(remove_button.exists, timeout_secs=self.timeout)
        click(remove_button)

    def empty_heading(self):
        message = Text("Your cart is empty")
        wait_until(message.exists, timeout_secs=self.timeout)
        return message.web_element.text

    def checkout(self):
        click("Proceed to Checkout")
        wait_until(S("#checkout-section-address").exists, timeout_secs=self.timeout)

    def continue_shopping(self):
        click("Continue Shopping")
        wait_until(S("main h3 a[href*='/products/']").exists, timeout_secs=self.timeout)

    def refresh(self):
        refresh()
        wait_until(Text("Shopping Cart").exists, timeout_secs=self.timeout)

    def current_path(self):
        return urlsplit(get_driver().current_url).path
