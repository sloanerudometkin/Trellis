from decimal import Decimal

from conftest import load_json_fixture
from trellis.extensions import db
from trellis.models import (
    AnalysisRun,
    AnalysisStatus,
    Keyword,
    OrganizerItem,
    OrganizerStageHistory,
)
from trellis.recommendation_schemas import RecommendationBatch
from trellis.recommendations import persist_recommendations


def create_completed_plan(client, app, headers, url="https://example.com"):
    website = client.post(
        "/api/v1/websites",
        headers=headers,
        json={"url": url, "business_name": "Example"},
    ).get_json()["data"]
    run = client.post(
        f"/api/v1/websites/{website['id']}/analysis-runs", headers=headers
    ).get_json()["data"]
    with app.app_context():
        saved = db.session.get(AnalysisRun, run["id"])
        saved.keywords.append(
            Keyword(
                phrase="community garden",
                frequency=5,
                tfidf_score=Decimal("0.8"),
            )
        )
        saved.status = AnalysisStatus.COMPLETED
        persist_recommendations(
            saved,
            RecommendationBatch.model_validate(
                load_json_fixture("llm_recommendations_success.json")
            ),
        )
        suggestion_ids = {
            suggestion.category.value: suggestion.id for suggestion in saved.suggestions
        }
    return website, run, suggestion_ids


def test_pending_can_be_dismissed_with_a_reason_and_creates_no_task(
    client, app, user_one_headers
):
    website, _, suggestions = create_completed_plan(client, app, user_one_headers)

    response = client.patch(
        f"/api/v1/suggestions/{suggestions['aeo']}/decision",
        headers=user_one_headers,
        json={"status": "dismissed", "dismiss_reason": "not_relevant"},
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "dismissed"
    assert response.get_json()["data"]["dismiss_reason"] == "not_relevant"
    assert client.get(
        f"/api/v1/websites/{website['id']}/organizer-items",
        headers=user_one_headers,
    ).get_json()["data"] == []


def test_acceptance_is_idempotent_and_creates_exactly_one_backlog_task(
    client, app, user_one_headers
):
    website, _, suggestions = create_completed_plan(client, app, user_one_headers)
    path = f"/api/v1/suggestions/{suggestions['seo_content']}/decision"

    first = client.patch(path, headers=user_one_headers, json={"status": "accepted"})
    second = client.patch(path, headers=user_one_headers, json={"status": "accepted"})

    assert first.status_code == second.status_code == 200
    items = client.get(
        f"/api/v1/websites/{website['id']}/organizer-items",
        headers=user_one_headers,
    ).get_json()["data"]
    assert len(items) == 1
    assert items[0]["suggestion_id"] == suggestions["seo_content"]
    assert items[0]["stage"] == "backlog"
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(OrganizerItem.id))) == 1
        assert db.session.scalar(db.select(db.func.count(OrganizerStageHistory.id))) == 1


def test_reaccepting_a_dismissed_suggestion_clears_reason_and_creates_task(
    client, app, user_one_headers
):
    _, _, suggestions = create_completed_plan(client, app, user_one_headers)
    path = f"/api/v1/suggestions/{suggestions['aeo']}/decision"
    client.patch(
        path,
        headers=user_one_headers,
        json={"status": "dismissed", "dismiss_reason": "too_much_work"},
    )

    response = client.patch(path, headers=user_one_headers, json={"status": "accepted"})

    assert response.get_json()["data"]["status"] == "accepted"
    assert response.get_json()["data"]["dismiss_reason"] is None
    assert response.get_json()["data"]["stage"] == "backlog"


def test_dismissing_an_accepted_suggestion_removes_its_task(
    client, app, user_one_headers
):
    website, _, suggestions = create_completed_plan(client, app, user_one_headers)
    path = f"/api/v1/suggestions/{suggestions['aeo']}/decision"
    client.patch(path, headers=user_one_headers, json={"status": "accepted"})

    response = client.patch(
        path,
        headers=user_one_headers,
        json={"status": "dismissed", "dismiss_reason": "already_doing_this"},
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["stage"] == "suggested"
    assert response.get_json()["data"]["organizer_item_id"] is None
    assert client.get(
        f"/api/v1/websites/{website['id']}/organizer-items",
        headers=user_one_headers,
    ).get_json()["data"] == []


def test_dismiss_reason_is_required_only_for_dismissed(client, app, user_one_headers):
    _, _, suggestions = create_completed_plan(client, app, user_one_headers)
    path = f"/api/v1/suggestions/{suggestions['aeo']}/decision"

    missing = client.patch(
        path, headers=user_one_headers, json={"status": "dismissed"}
    )
    invalid = client.patch(
        path,
        headers=user_one_headers,
        json={"status": "accepted", "dismiss_reason": "other"},
    )

    assert missing.status_code == invalid.status_code == 422


def test_suggestion_and_organizer_update_the_same_canonical_stage(
    client, app, user_one_headers
):
    website, run, suggestions = create_completed_plan(client, app, user_one_headers)
    accepted = client.patch(
        f"/api/v1/suggestions/{suggestions['seo_content']}/decision",
        headers=user_one_headers,
        json={"status": "accepted"},
    ).get_json()["data"]
    item_id = accepted["organizer_item_id"]

    client.patch(
        f"/api/v1/organizer-items/{item_id}",
        headers=user_one_headers,
        json={"stage": "in_production"},
    )
    suggestion_view = client.get(
        f"/api/v1/analysis-runs/{run['id']}", headers=user_one_headers
    ).get_json()["data"]
    assert next(
        item for item in suggestion_view["suggestions"] if item["id"] == suggestions["seo_content"]
    )["stage"] == "in_production"

    client.patch(
        f"/api/v1/suggestions/{suggestions['seo_content']}/stage",
        headers=user_one_headers,
        json={"stage": "published"},
    )
    organizer_view = client.get(
        f"/api/v1/websites/{website['id']}/organizer-items",
        headers=user_one_headers,
    ).get_json()["data"]
    assert organizer_view[0]["stage"] == "published"
    assert organizer_view[0]["published_at"] is not None


def test_invalid_organizer_stage_is_rejected(client, app, user_one_headers):
    _, _, suggestions = create_completed_plan(client, app, user_one_headers)
    accepted = client.patch(
        f"/api/v1/suggestions/{suggestions['seo_content']}/decision",
        headers=user_one_headers,
        json={"status": "accepted"},
    ).get_json()["data"]

    response = client.patch(
        f"/api/v1/organizer-items/{accepted['organizer_item_id']}",
        headers=user_one_headers,
        json={"stage": "not_a_real_stage"},
    )

    assert response.status_code == 422


def test_suggestion_and_task_routes_enforce_website_ownership(
    client, app, user_one_headers, user_two_headers
):
    website, _, suggestions = create_completed_plan(client, app, user_one_headers)
    accepted = client.patch(
        f"/api/v1/suggestions/{suggestions['aeo']}/decision",
        headers=user_one_headers,
        json={"status": "accepted"},
    ).get_json()["data"]

    assert client.patch(
        f"/api/v1/suggestions/{suggestions['aeo']}/decision",
        headers=user_two_headers,
        json={"status": "accepted"},
    ).status_code == 404
    assert client.patch(
        f"/api/v1/organizer-items/{accepted['organizer_item_id']}",
        headers=user_two_headers,
        json={"stage": "in_review"},
    ).status_code == 404
    assert client.get(
        f"/api/v1/websites/{website['id']}/organizer-items",
        headers=user_two_headers,
    ).status_code == 404
