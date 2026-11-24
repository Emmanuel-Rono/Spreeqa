"""Selenium fallback for Stripe's cross-origin frame; normal flows use Helium."""
from datetime import date

from helium import get_driver, wait_until
from selenium.webdriver.common.by import By


def fill_stripe_test_card():
    driver = get_driver()

    def card_frame():
        driver.switch_to.default_content()
        for frame in driver.find_elements(By.CSS_SELECTOR, "iframe[title='Secure payment input frame']"):
            src = frame.get_attribute("src") or ""
            if "pk_live_" in src:
                raise RuntimeError("Refusing to use a live Stripe payment gateway")
            driver.switch_to.frame(frame)
            if driver.find_elements(By.NAME, "number"):
                if "pk_test_" not in src:
                    driver.switch_to.default_content()
                    raise RuntimeError("Cannot verify Stripe test mode from the payment frame")
                return True
            driver.switch_to.default_content()
        return False

    try:
        wait_until(card_frame, timeout_secs=60)
        for name, value in (("number", "4242424242424242"),
                            ("expiry", "12{}".format(str(date.today().year + 3)[-2:])),
                            ("cvc", "123")):
            # Keep all cross-origin frame access here, outside page objects.
            field = driver.find_element(By.NAME, name)
            field.clear()
            field.send_keys(value)
        postal = driver.find_elements(By.NAME, "postalCode")
        if postal:
            postal[0].clear()
            postal[0].send_keys("10001")
    finally:
        driver.switch_to.default_content()
