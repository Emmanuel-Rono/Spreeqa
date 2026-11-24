import os
import re
from urllib.parse import urlsplit

from helium import S, click, find_all, get_driver, select, wait_until, write

from core.data import usd_amount
from core.stripe_payment import fill_stripe_test_card


class CheckoutPage:
    def __init__(self):
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))
        self.payment_method = os.getenv("STRIPE_PAYMENT_METHOD", "Credit Card")

    def submit_incomplete(self):
        if S("//button[@id='policy-consent']").exists():
            click (S("//button[@id='policy-consent']"))
        click(S("//button[normalize-space()='Pay Now']"))

    def address_errors(self):
        errors = S("#checkout-section-address p.text-red-700")
        wait_until(errors.exists, timeout_secs=self.timeout)
        return [error.web_element.text for error in find_all(errors)]

    def email_value(self):
        return S("#email").web_element.get_attribute("value")

    def address_value(self):
        return S("#ship-address1").web_element.get_attribute("value")

    def fill_address(self, address):
        select(S("#ship-country").web_element, address.country)
        write(address.first_name, into=S("#ship-first_name"))
        write(address.last_name, into=S("#ship-last_name"))
        write(address.address1, into=S("#ship-address1"))
        write(address.city, into=S("#ship-city"))
        write(address.postal_code, into=S("#ship-postal_code"))
        write(address.phone, into=S("#ship-phone"))
        wait_until(lambda: S("#ship-state").web_element.is_enabled() and address.state in
                   [option.web_element.text for option in find_all(S("#ship-state option"))],
                   timeout_secs=self.timeout)
        select(S("#ship-state").web_element, address.state)
        # Clicking outside the address fields triggers Spree's address save.
        click(S("#checkout-section-shipping"))

    def choose_shipping(self):
        rate = S("#checkout-section-shipping [role='radio']")
        wait_until(rate.exists, timeout_secs=self.timeout)
        click(rate)
        wait_until(lambda: rate.web_element.get_attribute("aria-checked") == "true", timeout_secs=self.timeout)

    def summary_text(self):
        return S("main").web_element.text

    def total(self):
        total = S("//span[normalize-space(.)='Total']/following-sibling::div/span[last()]")
        wait_until(total.exists, timeout_secs=self.timeout)
        return usd_amount(total.web_element.text)

    def pay_with_stripe_test_card(self):
        click(self.payment_method)
        fill_stripe_test_card()
        if S("#policy-consent").exists():
            consent = S("#policy-consent")
            if consent.web_element.get_attribute("data-state") != "checked":
                click(consent)
        total = self.total()
        click(S("main button.w-full.mt-8"))
        # Submit once: never automatically retry a payment click.
        wait_until(lambda: "/order-placed/" in self.current_path(), timeout_secs=90)
        return total

    def order_number(self):
        wait_until(lambda: re.search(r"order\s*#\s*([A-Za-z0-9-]+)", self.summary_text(), re.I),
                   timeout_secs=self.timeout)
        return re.search(r"order\s*#\s*([A-Za-z0-9-]+)", self.summary_text(), re.I).group(1)

    def current_path(self):
        return urlsplit(get_driver().current_url).path
