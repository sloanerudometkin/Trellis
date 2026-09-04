from trellis import create_app

from conftest import fake_jwt_decoder


def test_health_endpoint_is_rate_limited() -> None:
    class RateLimitTestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_DECODER = staticmethod(fake_jwt_decoder)
        RATELIMIT_ENABLED = True
        RATELIMIT_STORAGE_URI = "memory://"

    app = create_app(RateLimitTestConfig)
    client = app.test_client()

    for _ in range(60):
        assert client.get("/api/v1/health").status_code == 200

    response = client.get("/api/v1/health")
    assert response.status_code == 429
    assert response.get_json()["error"] == "too_many_requests"
