from playwright.sync_api import Page, expect

FAKE_ERROR_PAGE = """
<html><body>
  <h1>Service Unavailable</h1>
  <p>Sorry, something went wrong. Please try again later.</p>
</body></html>
"""


def test_mock_feedback_server_error(page: Page):
    # 1. intercept the form submission and return a fake 500 error
    page.route(
        "**/sendFeedback",
        lambda route: route.fulfill(status=500, content_type="text/html", body=FAKE_ERROR_PAGE),
    )

    # 2. fill in a valid form (this part loads from the REAL site)
    page.goto("/feedback.jsp")
    page.locator('input[name="name"]').fill("Test User")
    page.locator('input[name="email_addr"]').fill("test@example.com")
    page.locator('input[name="subject"]').fill("Testing")
    page.locator('textarea[name="comments"]').fill("Mock 500 test")

    # 3. submit, and capture the response the browser receives
    with page.expect_response("**/sendFeedback") as response_info:
        page.get_by_role("button", name="Submit").click()
    response = response_info.value

    # 4. the browser should have received our fake 500
    assert response.status == 500

    # 5. the user must NOT see a false success message
    expect(page.get_by_role("heading", name="Thank You")).not_to_be_visible()

    # 6. a safe error message should be shown, with no technical details leaked
    expect(page.locator("body")).to_contain_text("something went wrong")
    expect(page.locator("body")).not_to_contain_text("Exception")