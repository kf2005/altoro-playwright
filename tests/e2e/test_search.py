import pytest
import re
from playwright.sync_api import Page, expect


def test_search_valid_keyword(page: Page):
    # 1. open the homepage
    page.goto("/")

    # 2. fill the search box with "loan"
    page.locator("#query").fill("loan")

    # 3. press Enter to submit the search
    page.locator("#query").press("Enter")

    # 4. the URL should now contain the search query
    expect(page).to_have_url(re.compile("query=loan"))

    # 5. the Search Results heading should be visible
    expect(page.get_by_role("heading", name="Search Results")).to_be_visible()

    # 6. the keyword should be shown on the results page
    expect(page.locator("body")).to_contain_text("loan")


def test_search_empty(page: Page):
    # 1. open the homepage
    page.goto("/")

    # 2. leave the search box empty and press Enter
    page.locator("#query").fill("")
    page.locator("#query").press("Enter")

    # 3. the URL should have an empty query
    expect(page).to_have_url(re.compile(r"query=$"))

    # 4. the page should still load normally with the heading
    expect(page.get_by_role("heading", name="Search Results")).to_be_visible()

    # 5. it should show the "no results" message
    expect(page.locator("body")).to_contain_text("No results were found")

    # 6. it should NOT show a server error
    expect(page.locator("body")).not_to_contain_text("Exception")
    
@pytest.mark.xfail(reason="BUG: search is vulnerable to reflected XSS", strict=True)
def test_search_special_characters(page: Page):
    # record any popup (alert) that appears
    popups = []
    page.on("dialog", lambda dialog: (popups.append(dialog.message), dialog.dismiss()))

    # search for a script tag
    page.goto("/")
    page.locator("#query").fill("<script>alert(1)</script>")
    page.locator("#query").press("Enter")
    page.wait_for_load_state()

    # a safe site shows the text, it does NOT run it
    assert popups == [], f"Script ran! Popup said: {popups}"


def test_search_long_input(page: Page):
    long_text = "a" * 1000

    page.goto("/")
    page.locator("#query").fill(long_text)
    page.locator("#query").press("Enter")

    # page should still load normally, with no server error
    expect(page.get_by_role("heading", name="Search Results")).to_be_visible()
    expect(page.locator("body")).not_to_contain_text("Exception")