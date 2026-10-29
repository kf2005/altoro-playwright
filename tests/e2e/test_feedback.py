import pytest
import re
from playwright.sync_api import Page, expect

# B4
def test_feedback_valid_submission(page: Page):
    # 1. open the feedback form
    page.goto("/feedback.jsp")

    # 2. fill in all fields
    page.locator('input[name="name"]').fill("Test User")
    page.locator('input[name="email_addr"]').fill("test@example.com")
    page.locator('input[name="subject"]').fill("Testing")
    page.locator('textarea[name="comments"]').fill("This is a test message")

    # 3. submit
    page.get_by_role("button", name="Submit").click()

    # 4. we should land on the sendFeedback page
    expect(page).to_have_url(re.compile("sendFeedback"))

    # 5. the Thank You heading should show
    expect(page.get_by_role("heading", name="Thank You")).to_be_visible()

    # 6. the message should include our name and email
    expect(page.locator("body")).to_contain_text("Test User")
    expect(page.locator("body")).to_contain_text("test@example.com")

# B5
@pytest.mark.xfail(reason="BUG: empty feedback form is accepted with no validation", strict=True)
def test_feedback_empty_fields(page: Page):
    # 1. open the form and submit it with every field empty
    page.goto("/feedback.jsp")
    page.get_by_role("button", name="Submit").click()

    # 2. the site does at least warn that the email is wrong
    expect(page.locator("body")).to_contain_text("email you gave is incorrect")

    # 3. but a proper form should NOT show the Thank You page
    expect(page.get_by_role("heading", name="Thank You")).not_to_be_visible(timeout=3000)

# B6
def test_feedback_invalid_email(page: Page):
    # 1. fill the form with a valid name/subject/comment but a bad email
    page.goto("/feedback.jsp")
    page.locator('input[name="name"]').fill("Test User")
    page.locator('input[name="email_addr"]').fill("not-an-email")
    page.locator('input[name="subject"]').fill("Testing")
    page.locator('textarea[name="comments"]').fill("Invalid email test")

    # 2. submit
    page.get_by_role("button", name="Submit").click()

    # 3. the site should warn that the email is incorrect
    expect(page.locator("body")).to_contain_text("email you gave is incorrect")

    # 4. and it should NOT say a reply will be sent to that email
    expect(page.locator("body")).not_to_contain_text("reply will be sent")