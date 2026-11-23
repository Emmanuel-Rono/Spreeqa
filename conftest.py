from pathlib import Path
from dotenv import load_dotenv
import pytest
from helium import kill_browser
import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from helium import start_chrome, kill_browser

load_dotenv(Path(__file__).resolve().parent / ".env")


import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from helium import start_chrome, kill_browser, get_driver

load_dotenv(Path(__file__).resolve().parent / ".env")


@pytest.fixture(autouse=True)
def browser(request):
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    start_chrome(headless=headless)
    get_driver().set_window_size(1440, 1000)

    try:
        yield
    finally:
        try:
            driver = get_driver()
            reports = Path("reports")
            reports.mkdir(exist_ok=True)

            driver.save_screenshot(
                str(reports / f"{request.node.name}.png")
            )
            print(f"Browser URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
        except Exception as error:
            print(f"Could not capture browser diagnostics: {error}")
        finally:
            kill_browser()