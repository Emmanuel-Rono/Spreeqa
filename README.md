# SPRREQA

SPRREQA tests the Spree demo store using Python, pytest, Selenium, and Helium. It covers signup, login, product browsing, adding items to the cart, and opening checkout. GitHub Actions runs tests and saves reports.

## Install

Install Python, Git, and Google Chrome. In Windows PowerShell, run:

```powershell
git clone https://github.com/Emmanuel-Rono/SPRREQA.git
cd SPRREQA
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file in the project folder with your Spree demo test account details:

```dotenv
TEST_USER_EMAIL=your_test_email
TEST_USER_PASSWORD=your_test_password
```

Use an existing account for login. Signup needs an email that is not already registered. Keep your `.env` file private.

## Run

Run all tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

Run only the login test:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_login.py -v
```

Screenshots are saved in `reports/`. GitHub Actions results are shown in the repository's Actions tab.
