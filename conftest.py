from playwright.sync_api import Playwright
import pytest
import base64
import os
import pytest_html

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture
def api(playwright: Playwright):
    # an HTTP client pointed at the site, ignoring the bad certificate
    context = playwright.request.new_context(
        base_url="https://testfire.net",
        ignore_https_errors=True,
        timeout=15000,   # <-- NEW: give up after 15 seconds instead of 30
    )
    yield context
    context.dispose()


@pytest.fixture
def jsmith_token(api):
    # log in through the API and return the token
    response = api.post("/api/login", data={"username": "jsmith", "password": "demo1234"})
    assert response.status == 200
    return response.json()["Authorization"]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # after each browser test runs, take a screenshot and attach it to the report
    if report.when == "call":
        page = item.funcargs.get("page")
        if page is not None:
            png = page.screenshot(full_page=True)

            # save a copy as a file too
            os.makedirs("reports/screenshots", exist_ok=True)
            name = item.name.replace("[", "_").replace("]", "")
            with open(f"reports/screenshots/{name}.png", "wb") as f:
                f.write(png)

            # embed it in the HTML report
            extras = getattr(report, "extras", [])
            extras.append(pytest_html.extras.image(base64.b64encode(png).decode(), name))
            report.extras = extras