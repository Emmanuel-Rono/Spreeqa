import os

import pytest

from core.data import new_customer
from pages.AccountsPage import AccountsPage
from pages.LoginPage import LoginPage
from pages.RegisterPage import RegisterPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_registration_logout_and_login(browser):
    customer = new_customer()
    registration = RegisterPage()
    registration.open_registration()
    registration.register(customer)
    account = AccountsPage()
    assert "Account Overview" in account.overview()
    assert customer.email in account.identity()
    assert customer.first_name in account.identity()
    account.sign_out()
    login = LoginPage()
    assert login.is_signed_out()
    login.login(customer.email, customer.password)
    assert "Account Overview" in account.overview()
    assert customer.email in account.identity()


@pytest.mark.smoke
def test_existing_customer_can_login(browser):
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")
    assert email and password, "Set TEST_USER_EMAIL and TEST_USER_PASSWORD to an existing local customer"
    login = LoginPage()
    login.open_login_page()
    login.login(email, password)
    account = AccountsPage()
    assert "Account Overview" in account.overview()
    assert email in account.identity()


@pytest.mark.regression
def test_login_rejects_wrong_password(browser):
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")
    assert email and password, "Set TEST_USER_EMAIL and TEST_USER_PASSWORD to an existing local customer"
    login = LoginPage()
    login.open_login_page()
    login.login(email, password)
    account = AccountsPage()
    assert "Account Overview" in account.overview()
    account.sign_out()
    login.login(email, password + "-incorrect")
    assert login.error_message()
    assert login.is_signed_out()


@pytest.mark.regression
def test_guest_order_history_requires_login(browser):
    login = LoginPage()
    login.open_order_history_as_guest()
    assert login.is_signed_out()
    assert login.current_path().endswith("/account")


@pytest.mark.regression
def test_registration_rejects_password_mismatch(browser):
    customer = new_customer()
    registration = RegisterPage()
    registration.open_registration()
    registration.register(customer, confirmation=customer.password + "-different")
    assert registration.error_message()
    assert registration.current_path().endswith("/account/register")


@pytest.mark.regression
def test_registration_requires_policy_consent(browser):
    customer = new_customer()
    registration = RegisterPage()
    registration.open_registration()
    registration.register(customer, accept_terms=False)
    assert registration.error_message()
    assert not registration.policies_accepted()
    assert registration.current_path().endswith("/account/register")


@pytest.mark.regression
def test_existing_customer_has_empty_order_history(browser):
    email = os.getenv("TEST_EMPTY_USER_EMAIL")
    password = os.getenv("TEST_EMPTY_USER_PASSWORD")
    assert email and password, "Set TEST_EMPTY_USER_EMAIL and TEST_EMPTY_USER_PASSWORD to an existing customer with no orders"
    assert email.casefold() != os.getenv("TEST_USER_EMAIL", "").casefold(), "Use a separate empty-history account, never the purchase account"
    login = LoginPage()
    login.open_login_page()
    login.login(email, password)
    account = AccountsPage()
    assert "Account Overview" in account.overview()
    account.open_orders()
    assert account.empty_orders_message() == "No orders yet"
