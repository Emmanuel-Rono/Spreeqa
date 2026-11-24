import os
from urllib.parse import urlsplit

from helium import S, click, get_driver, go_to, wait_until, write


class RegisterPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/account/register"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))

    def open_registration(self):
        go_to(self.url)
        wait_until(S("#firstName").exists, timeout_secs=self.timeout)

    def register(self, customer, confirmation=None, accept_terms=True):
        write(customer.first_name, into="First name")
        write(customer.last_name, into="Last name")
        write(customer.email, into="Email")
        write(customer.password, into=S("#password"))
        write(customer.password if confirmation is None else confirmation, into=S("#passwordConfirmation"))
        if accept_terms:
            click(S("#policy-consent"))
        click("Create Account")

    def error_message(self):
        error = S("[role='alert']")
        wait_until(error.exists, timeout_secs=self.timeout)
        return error.web_element.text.strip()

    def policies_accepted(self):
        return S("#policy-consent").web_element.get_attribute("data-state") == "checked"

    def current_path(self):
        return urlsplit(get_driver().current_url).path
