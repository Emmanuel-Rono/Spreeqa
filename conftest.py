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


@pytest.fixture(autouse=True)
def browser():
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    start_chrome(headless=headless)
    try:
        yield
    finally:
        kill_browser()