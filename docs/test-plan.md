# Test coverage

These are implemented scenarios, not a claim that all have passed on the local store.
Check the latest run reports for results. Tests target English labels and USD prices.

| Area | Scenario | Main assertions |
| --- | --- | --- |
| Account | Register, sign out, and sign back in | New customer's email/name and account overview |
| Account | Existing customer signs in | Account overview and matching email |
| Account | Wrong password | Error and no authenticated overview |
| Account | Guest visits order history | Redirect to sign in |
| Account | Password confirmation differs | Error and registration page retained |
| Account | No policy consent | Error, unchecked consent, no account redirect |
| Account | Existing customer with no orders | Empty history after explicit login |
| Search | Search known product | Named result, matching product slug |
| Search | No matching product | Empty state and no product cards |
| Cart | Add selected variant | Name, options, quantity, price, subtotal |
| Cart | Increase quantity | Quantity two, exact decimal subtotal |
| Cart | Reload cart | Item, options, quantity, subtotal persist |
| Cart | Remove last item | Empty cart and removed row absent |
| Cart | Empty cart navigation | Continue shopping reaches products |
| Checkout | Reach checkout | Selected item/options and summary total |
| Checkout | Missing address | Address errors and checkout retained |
| Purchase (opt-in) | Sign in, search, cart, shipping, Stripe test payment, history | Confirmed order number and persisted items/address/total |

## Data rules

- Signup tests generate unique customer details and explicitly register through the UI.
- Login and purchase tests explicitly sign in with `TEST_USER_EMAIL` and
  `TEST_USER_PASSWORD`, configured for an existing customer on the target store.
- Empty-history coverage uses a separate existing customer configured through
  `TEST_EMPTY_USER_EMAIL` and `TEST_EMPTY_USER_PASSWORD`. Keep this account free of orders.
- No fixture registers customers, signs in, opens products, or fills carts.
- Use a disposable local/test database. Test-created accounts and completed orders remain
  available for investigation; reset/reseed that database between batches as needed.
- Tests never depend on another test's run order. Every test gets a new browser session.
- Configure one known product with stable USD pricing, no automatic discount, and stock
  for at least two units. Replenish stock before repeat purchase runs.
- Configure option labels using `TEST_PRODUCT_OPTIONS`; the selected SKU is captured
  before purchase. No silent fallback to another product on failure.
- Payment coverage is skipped unless `--run-payments` is passed. A skip is not a pass.
- The purchase uses a Stripe test card and refuses frames containing a live key or
  whose test mode cannot be verified. It submits once, with no automatic payment retry.

## Smoke and regression

Smoke: account round trip, existing customer login, selected cart item, checkout reachability.
Regression: errors, search, cart changes/persistence, checkout validation.
Payment: separate opt-in purchase journey; it is not included in the smoke claim.

## Scope

Standalone page classes call Helium directly, with no BasePage inheritance. Tests assert through page objects rather
than calling Selenium directly. Stripe's cross-origin frame handling is isolated
in `core/stripe_payment.py`; driver settings and failure diagnostics use Helium's underlying driver where required.

One US market, one seller, one product, and the shipped English storefront.
Other currencies, multi-seller purchases, 3DS, wallets, refunds, and browser engines
other than Chrome are not covered yet.

Selectors were checked against the local `Spree-store/apps/storefront` source and
its upstream E2E helpers. Cart, search, checkout and payment still need live verification.

## Validation on 24 November 2026

- Before the setup simplification, 6 Helium account tests passed in 117.19 seconds
  (`reports/standalone-accounts.xml`, local and gitignored). This is historical evidence.
- After the setup simplification: 19 helper checks passed; all 36 cases collect.
- Existing-account browser tests require the two configured test customers and
  have not yet been verified with this setup.
- Cart, search, checkout and Stripe purchase have not been validated against a
  configured, seeded store. The last sample-data attempt required an admin account.
- Workflow YAML parses successfully. These changes have not been run on GitHub.
