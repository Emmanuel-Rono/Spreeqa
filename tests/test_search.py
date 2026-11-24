import json
import os
from uuid import uuid4

import pytest

from pages.Product_page import ProductPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


@pytest.mark.regression
def test_search_finds_known_product(browser):
    slug = os.getenv("TEST_PRODUCT_SLUG")
    assert slug, "Set TEST_PRODUCT_SLUG to a stocked local product"
    product_page = ProductPage()
    product_page.open_product(slug)
    product_page.choose_options(json.loads(os.getenv("TEST_PRODUCT_OPTIONS", "[]")))
    product = product_page.snapshot()
    products = ProductsPage()
    products.open_products()
    products.search(product.name)
    assert product.name in products.result_names()
    products.open_result(product.name)
    assert product_page.snapshot().slug == product.slug


@pytest.mark.regression
def test_search_has_no_results(browser):
    products = ProductsPage()
    products.open_products()
    products.search("spreeqa-no-match-" + uuid4().hex)
    assert products.empty_message() == "No products found"
    assert not products.has_results()
