import pytest

SAFE_BODY = {"username": "jsmith", "password1": "demo1234", "password2": "demo1234"}


def test_api_update_without_login(api):
    # try to change a password with NO token at all
    response = api.post("/api/admin/changePassword", data=SAFE_BODY)

    print("No-token status:", response.status, response.text())
    # should be blocked: 401 Unauthorized
    assert response.status == 401


@pytest.mark.xfail(reason="BUG: non-admin user can call admin changePassword (broken access control)", strict=True)
def test_api_update_as_normal_user(api, jsmith_token):
    # try to change a password as jsmith, who is NOT an admin
    response = api.post(
        "/api/admin/changePassword",
        data=SAFE_BODY,
        headers={"Authorization": jsmith_token},
    )
    print("jsmith status:", response.status, response.text())

    # jsmith's password must still work (we sent the same password)
    check = api.post("/api/login", data={"username": "jsmith", "password": "demo1234"})
    assert check.status == 200

    # a normal user should NOT be allowed to use an admin endpoint
    assert response.status in (401, 403)
    
@pytest.mark.xfail(reason="BUG: token still valid after logout (session not invalidated)", strict=True)
def test_api_logout(api, jsmith_token):
    headers = {"Authorization": jsmith_token}

    # 1. before logout: the token should work
    before = api.get("/api/login", headers=headers)
    print("Before logout:", before.status, before.text())
    assert before.status == 200

    # 2. log out
    logout = api.get("/api/logout", headers=headers)
    print("Logout:", logout.status, logout.text())
    assert logout.status == 200

    # 3. after logout: the same token should no longer be logged in   <-- CHANGED
    after = api.get("/api/login", headers=headers, timeout=10000)
    print("After logout:", after.status, after.text())
    assert after.status == 401


def test_api_logout_status_codes(api):
    # logging out without a token should not crash the server
    response = api.get("/api/logout")
    print("Logout without token:", response.status, response.text())
    assert response.status != 500