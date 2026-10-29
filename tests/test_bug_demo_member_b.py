import re
import pytest
from playwright.sync_api import Page, expect

# DELIBERATE BUG: a broken server response that drops the user's name and email
BROKEN_THANK_YOU = """
<html><body>
  <h1>Thank You</h1>
  <p>Thank you for your comments. Our reply will be sent to your email.</p>
</body></html>
"""

@pytest.mark.bugdemo
def test_bug_demo_feedback_missing_details(page: Page):
    # inject the bug: replace the real server reply with the broken one
    page.route(
        "**/sendFeedback",
        lambda route: route.fulfill(status=200, content_type="text/html", body=BROKEN_THANK_YOU),
    )

    # same steps and checks as B4
    page.goto("/feedback.jsp")
    page.locator('input[name="name"]').fill("Test User")
    page.locator('input[name="email_addr"]').fill("test@example.com")
    page.locator('input[name="subject"]').fill("Testing")
    page.locator('textarea[name="comments"]').fill("Bug demo")
    page.get_by_role("button", name="Submit").click()

    expect(page).to_have_url(re.compile("sendFeedback"))
    expect(page.get_by_role("heading", name="Thank You")).to_be_visible()
    expect(page.locator("body")).to_contain_text("Test User")          # <-- this will FAIL
    expect(page.locator("body")).to_contain_text("test@example.com")