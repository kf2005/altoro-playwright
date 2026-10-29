from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    # 1. go to the homepage  →  page.goto(...)
    # 2. check the title contains "Altoro Mutual"  →  expect(page).to_have_title(...)
    pass