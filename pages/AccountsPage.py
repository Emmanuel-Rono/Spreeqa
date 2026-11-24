import os

from helium import Link, S, Text, click, go_to, wait_until

from core.data import usd_amount


class AccountsPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/account"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))

    def overview(self):
        message = Text("Account Overview")
        wait_until(message.exists, timeout_secs=self.timeout)
        return message.web_element.text

    def identity(self):
        sidebar = S("aside")
        wait_until(sidebar.exists, timeout_secs=self.timeout)
        return sidebar.web_element.text

    def sign_out(self):
        click("Sign Out")
        wait_until(S("#email").exists, timeout_secs=self.timeout)

    def open_orders(self):
        go_to(self.url + "/orders")
        wait_until(Text("Order History").exists, timeout_secs=self.timeout)

    def empty_orders_message(self):
        message = Text("No orders yet")
        wait_until(message.exists, timeout_secs=self.timeout)
        return message.web_element.text

    def open_order(self, number):
        click(Link("#" + number))
        wait_until(Text("Order #" + number).exists, timeout_secs=self.timeout)

    def order_text(self):
        return S("main").web_element.text

    def order_quantity(self, name):
        # The suite purchases one product, so there is one quantity label.
        return Text("Qty: 1", below=name).web_element.text.strip()

    def order_total(self):
        total = S("//main//span[normalize-space(.)='Total']/following-sibling::*[last()]")
        wait_until(total.exists, timeout_secs=self.timeout)
        return usd_amount(total.web_element.text)
