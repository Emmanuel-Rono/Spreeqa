import json
import os

import pytest

from core.data import Address
from pages.AccountsPage import AccountsPage
from pages.LoginPage import LoginPage
from pages.Product_page import ProductPage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_cart_opens_checkout_with_selected_product(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    CartPage().checkout()
    checkout = CheckoutPage()
    assert product.name in checkout.summary_text()
    assert product.options in checkout.summary_text()
    assert checkout.total() >= product.unit_price


@pytest.mark.regression
def test_checkout_rejects_missing_address(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    CartPage().checkout()
    checkout = CheckoutPage()
    checkout.submit_incomplete()
    assert checkout.address_errors()
    assert checkout.address_value() == ""
    assert checkout.current_path().endswith("/checkout")


@pytest.mark.payment
def test_purchase_and_order_history(browser):
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")
    assert email and password, "Set TEST_USER_EMAIL and TEST_USER_PASSWORD to an existing local customer"
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    options = json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]"))
    login = LoginPage()
    login.open_login_page()
    login.login(email, password)
    account = AccountsPage()
    assert "Account Overview" in account.overview()
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(options)
    product = page.snapshot()
    products = ProductsPage()
    products.open_products()
    products.search(product.name)
    assert product.name in products.result_names()
    products.open_result(product.name)
    page.choose_options(options)
    assert page.snapshot().sku == product.sku
    page.add_to_cart(product)
    page.open_cart()
    cart = CartPage()
    assert cart.item(product.name)["quantity"] == 1
    assert cart.subtotal() == product.unit_price
    cart.checkout()
    checkout = CheckoutPage()
    assert checkout.email_value() == email
    address = Address()
    checkout.fill_address(address)
    checkout.choose_shipping()
    assert product.name in checkout.summary_text()
    assert product.options in checkout.summary_text()
    total = checkout.pay_with_stripe_test_card()
    number = checkout.order_number()
    assert product.name in checkout.summary_text()
    account.open_orders()
    account.open_order(number)
    assert product.name in account.order_text()
    assert product.options in account.order_text()
    assert address.address1 in account.order_text()
    assert account.order_quantity(product.name) == "Qty: 1"
    assert account.order_total() == total
