import os
from urllib.parse import urlsplit

from helium import S, Text, click, get_driver, go_to, wait_until, write


class LoginPage:
    def __init__(self):
        self.url = os.getenv("BASE_URL", "http://localhost:3001/us/en").rstrip("/") + "/account"
        self.timeout = int(os.getenv("WAIT_TIMEOUT", "30"))

    def open_login_page(self):
        go_to(self.url)
        wait_until(S("#email").exists, timeout_secs=self.timeout)

    def open_order_history_as_guest(self):
        go_to(self.url + "/orders")
        wait_until(S("#email").exists, timeout_secs=self.timeout)

    def login(self, email, password):
        write(email, into="Email")
        write(password, into=S("#password"))
        click("Sign In")

    def error_message(self):
        error = S("[role='alert']")
        wait_until(error.exists, timeout_secs=self.timeout)
        return error.web_element.text.strip()

    def is_signed_out(self):
        wait_until(S("#email").exists, timeout_secs=self.timeout)
        return not Text("Account Overview").exists()

    def current_path(self):
        return urlsplit(get_driver().current_url).path
