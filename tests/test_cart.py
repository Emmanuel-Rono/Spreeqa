import json
import os

import pytest

from pages.Product_page import ProductPage
from pages.cart_page import CartPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_cart_contains_selected_product_and_variant(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    cart = CartPage()
    item = cart.item(product.name)
    assert item == {"name": product.name, "options": product.options,
                    "unit_price": product.unit_price, "quantity": 1}
    assert product.sku
    assert cart.subtotal() == product.unit_price


@pytest.mark.regression
def test_quantity_updates_subtotal(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    cart = CartPage()
    cart.increase_quantity(product.name, 2)
    cart.wait_for_subtotal(product.unit_price * 2)
    assert cart.item(product.name)["quantity"] == 2
    assert cart.subtotal() == product.unit_price * 2


@pytest.mark.regression
def test_cart_survives_page_refresh(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    cart = CartPage()
    cart.increase_quantity(product.name, 2)
    cart.wait_for_subtotal(product.unit_price * 2)
    cart.refresh()
    assert cart.item(product.name)["quantity"] == 2
    assert cart.item(product.name)["options"] == product.options
    assert cart.subtotal() == product.unit_price * 2


@pytest.mark.regression
def test_remove_last_item_empties_cart(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    page = ProductPage()
    page.open_product(slug)
    page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = page.snapshot()
    page.add_to_cart(product)
    page.open_cart()
    cart = CartPage()
    cart.remove(product.name)
    assert cart.empty_heading() == "Your cart is empty"
    assert not cart.has_item(product.name)


@pytest.mark.regression
def test_empty_cart_returns_to_products(browser):
    cart = CartPage()
    cart.open_cart()
    assert cart.empty_heading() == "Your cart is empty"
    cart.continue_shopping()
    assert cart.current_path().endswith("/products")
