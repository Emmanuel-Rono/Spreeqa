import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from dotenv import load_dotenv
from helium import get_driver, kill_browser, start_chrome
from selenium.webdriver import ChromeOptions

from core.config import Settings

load_dotenv(Path(__file__).parent / ".env")


def pytest_addoption(parser):
    parser.addoption("--base-url", default=None, help="Storefront URL including /us/en")
    parser.addoption("--headed", action="store_true", help="Show Chrome")
    parser.addoption("--run-payments", action="store_true", help="Enable Stripe test purchases")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-payments"):
        for item in items:
            if "payment" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Pass --run-payments to enable test purchases"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "report_" + report.when, report)


@pytest.fixture
def browser(request, monkeypatch):
    settings = Settings.from_env(request.config.getoption("--base-url"),
                                 request.config.getoption("--headed"))
    monkeypatch.setenv("BASE_URL", settings.base_url)
    monkeypatch.setenv("WAIT_TIMEOUT", str(settings.timeout))
    options = ChromeOptions()
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-dev-shm-usage")
    if settings.driver_path:
        driver_path = Path(settings.driver_path)
        if not driver_path.is_file():
            pytest.fail("CHROMEDRIVER_PATH must point to an existing ChromeDriver executable")
        monkeypatch.setenv("PATH", str(driver_path.parent) + os.pathsep + os.environ.get("PATH", ""))
    start_chrome(headless=settings.headless, options=options)
    driver = get_driver()
    try:
        driver.set_page_load_timeout(60)
        driver.set_window_size(1440, 1000)
        yield driver
    finally:
        if any(getattr(request.node, "report_" + phase, None) is not None and
               getattr(request.node, "report_" + phase).failed for phase in ("setup", "call")):
            directory = Path("reports/failures")
            directory.mkdir(parents=True, exist_ok=True)
            name = request.node.name + "-" + hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:8]
            try:
                driver.execute_script("document.querySelectorAll('input[type=password]').forEach(e => e.style.visibility='hidden')")
                driver.save_screenshot(str(directory / (name + ".png")))
                url = urlsplit(driver.current_url)
                (directory / (name + ".json")).write_text(json.dumps({
                    "url": url._replace(query="", fragment="").geturl(), "title": driver.title
                }), encoding="utf-8")
            except Exception as error:
                import warnings
                warnings.warn("Could not save browser diagnostics: {}".format(type(error).__name__))
        kill_browser()
