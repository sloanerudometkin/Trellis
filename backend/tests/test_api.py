def test_health_contract(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json() == {"service": "trellis-api", "status": "ok"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_cors_allows_only_the_configured_frontend(client, app) -> None:
    app.config["FRONTEND_ORIGIN"] = "http://localhost:5173"

    allowed = client.get(
        "/api/v1/health", headers={"Origin": "http://localhost:5173"}
    )
    untrusted = client.get(
        "/api/v1/health", headers={"Origin": "https://untrusted.example"}
    )

    assert allowed.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert "Access-Control-Allow-Origin" not in untrusted.headers


def test_protected_route_requires_bearer_token(client) -> None:
    response = client.get("/api/v1/websites")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_invalid_token_returns_secure_error(client) -> None:
    response = client.get(
        "/api/v1/websites", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "unauthorized",
        "message": "The access token is invalid or expired.",
    }
    assert "traceback" not in response.get_data(as_text=True).lower()


def test_create_website_validates_request_contract(client, user_one_headers) -> None:
    response = client.post(
        "/api/v1/websites",
        headers=user_one_headers,
        json={"url": "not-a-url", "business_name": ""},
    )

    assert response.status_code == 422
    assert response.get_json()["error"] == "validation_error"


def test_each_user_sees_only_their_own_websites(
    client, user_one_headers, user_two_headers
) -> None:
    first = client.post(
        "/api/v1/websites",
        headers=user_one_headers,
        json={
            "url": "https://one.example.com",
            "business_name": "One",
            "business_context": "First user's site",
        },
    )
    second = client.post(
        "/api/v1/websites",
        headers=user_two_headers,
        json={
            "url": "https://two.example.com",
            "business_name": "Two",
            "business_context": "Second user's site",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    first_list = client.get("/api/v1/websites", headers=user_one_headers).get_json()
    second_list = client.get("/api/v1/websites", headers=user_two_headers).get_json()

    assert [website["business_name"] for website in first_list["data"]] == ["One"]
    assert [website["business_name"] for website in second_list["data"]] == ["Two"]


def test_duplicate_website_returns_conflict(client, user_one_headers) -> None:
    payload = {"url": "https://example.com", "business_name": "Example"}
    assert client.post("/api/v1/websites", headers=user_one_headers, json=payload).status_code == 201

    response = client.post("/api/v1/websites", headers=user_one_headers, json=payload)

    assert response.status_code == 409
    assert response.get_json()["error"] == "conflict"


def test_unknown_route_uses_json_error_contract(client) -> None:
    response = client.get("/api/v1/not-a-route")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"] == "not_found"
