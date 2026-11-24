# Spreeqa

Spreeqa tests a Spree shopping site with Python, pytest, and Helium.
It covers accounts, search, cart changes, and checkout checks. An optional test
places a Stripe test order and checks order history. Tests use their own accounts
and a known product. GitHub Actions runs checks and saves reports.

The default target is your local Spree store. Implemented browser tests are not
a claim of passing coverage; see the [test plan](docs/test-plan.md) and run reports.

Each page is a standalone class with direct Helium calls: `go_to`, `write`,
`click`, and `wait_until`. There is no BasePage or inherited action layer.
Normal controls use labels; icon buttons use attributes such as `aria-label`
through Helium's `S` selector. Direct Selenium use is limited to browser settings,
diagnostics, and the Stripe iframe helper in `core/stripe_payment.py`.

## Install

Install Python 3.12 (the CI version), Git, and Google Chrome. In PowerShell:

```powershell
git clone https://github.com/Emmanuel-Rono/Spreeqa.git
cd Spreeqa
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy the example settings:

```powershell
Copy-Item .env.example .env
```

Edit `.env`: set `BASE_URL` to the running storefront (including `/us/en`) and
`TEST_PRODUCT_SLUG` to a known stocked USD product. For a chosen variant, set
`TEST_PRODUCT_OPTIONS` to its option labels, for example `["Red", "M"]`.
Use a stable price, no automatic discount, and stock of at least two units.
Accounts are generated automatically. No personal login is required.

Keep `.env` private. Tests create customers, carts and (when enabled) orders;
use a store/database reserved for testing.

## Start the local store

Spree is the application under test, not code written by this project.
Use the [official installer](https://spreecommerce.org/docs/developer/getting-started/quickstart)
to create a separate store with the Next.js storefront and sample data.
The installer requires Node.js 24+, npm 9+, and running Docker.

From the generated store folder, start the backend:

```powershell
npx spree dev
```

In another terminal, from that store folder:

```powershell
cd apps/storefront
npm run dev
```

Confirm store setup is complete and `/us/en/products` loads before browser tests.
Configure US shipping and a stocked product. The first Next.js page build can take
time; open the products page once before starting the suite.

If it reports `Valid API key required`, correct `SPREE_PUBLISHABLE_KEY` in the
store's `apps/storefront/.env.local` using a valid publishable key for that backend,
then restart the storefront. Keep store keys out of this repository.

## Run

Run browser tests without payment:

```powershell
.\venv\Scripts\python.exe -m pytest -m "ui and not payment" -v --junitxml=reports/results.xml
```

Run the smoke suite visibly:

```powershell
.\venv\Scripts\python.exe -m pytest -m smoke --headed -v
```

Run helper checks without a store or browser:

```powershell
.\venv\Scripts\python.exe -m pytest tests/unit -v
```

`HEADLESS=true` hides Chrome; `--headed` overrides it. `--base-url URL` overrides
the configured storefront. `CHROMEDRIVER_PATH` optionally selects an existing
driver matching Chrome when automatic driver download is unavailable.

## Test purchase

Configure Stripe test-mode keys on the **store backend and storefront**, plus US
shipping rates. This framework does not configure or store gateway secrets.
Set `STRIPE_PAYMENT_METHOD` to the exact displayed name of the test gateway
(default `Credit Card`). Then run:

```powershell
.\venv\Scripts\python.exe -m pytest -m payment --run-payments -v --junitxml=reports/payment.xml
```

The test uses `4242 4242 4242 4242`, verifies Stripe's frame carries a test key,
and submits once. An unverified/live gateway fails the test.
Without `--run-payments`, payment coverage is explicitly skipped.

## Reports and GitHub Actions

Failures save a screenshot and URL/title under `reports/failures/`. Password
fields are hidden; full HTML, cookies, and form values are not saved.
JUnit XML is produced by the commands above. Reports are gitignored.

Every push/PR runs helper checks and browser-test discovery. Browser execution
also runs when repository variable `STOREFRONT_URL` points to a test store reachable
by the GitHub runner. Set `TEST_PRODUCT_SLUG` and optionally `TEST_PRODUCT_OPTIONS`
as repository variables too. A manual run can supply the storefront URL and enable
payment coverage. Results and report downloads appear in the Actions tab.

Without a reachable configured store, the browser job is **not run**. A passing
helper-check job does not mean browser tests passed. `localhost` on GitHub is
the runner, not your laptop. Starting/seeding Spree inside CI remains future work;
the workflow currently expects a separately started test environment.

## Project layout

- `core/`: settings, unique customers, decimal money parsing.
- `pages/`: account, listing, product, cart, checkout interactions.
- `tests/`: independent browser journeys and their assertions.
- `tests/unit/`: configuration and data helper checks.
- `docs/test-plan.md`: scenarios, data rules, and coverage limits.

For a portfolio, share this repository, a recent passing browser report, and a
short recording of one journey. State the tested Spree version and skipped
coverage. Do not publish credentials or claim the Spree store as your own app.
