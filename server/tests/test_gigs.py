"""Tests for the gigs blueprint — covers the full lifecycle including
Phase 6 two-sided completion and dispute flow."""

from tests.conftest import auth_header, register_user


def _register_two_users(client):
    poster_resp = register_user(client, email="poster@jkuat.ac.ke", name="Poster One")
    hustler_resp = register_user(client, email="hustler@jkuat.ac.ke", name="Hustler One")
    return poster_resp.get_json(), hustler_resp.get_json()


def _create_gig(client, token, **overrides):
    payload = {
        "title": "Format my essay",
        "description": "Need APA formatting done by tomorrow morning, 10 pages.",
        "budget": "500.00",
        "gig_type": "TASK_NEEDED",
        "category": "writing",
        "campus_location": "JKUAT Juja",
        "is_urgent": True,
    }
    payload.update(overrides)
    return client.post("/api/gigs", json=payload, headers=auth_header(token))


def test_create_and_fetch_gig(client):
    poster, _ = _register_two_users(client)
    resp = _create_gig(client, poster["access_token"])
    assert resp.status_code == 201
    gig_id = resp.get_json()["gig"]["id"]

    detail = client.get(f"/api/gigs/{gig_id}")
    assert detail.status_code == 200
    assert detail.get_json()["gig"]["title"] == "Format my essay"


def test_feed_filters_by_campus_and_category(client):
    poster, _ = _register_two_users(client)
    _create_gig(client, poster["access_token"], campus_location="JKUAT Juja", category="writing")
    _create_gig(client, poster["access_token"], campus_location="KU Main", category="cleaning")

    resp = client.get("/api/gigs?campus=JKUAT Juja&category=writing")
    assert resp.status_code == 200
    gigs = resp.get_json()["gigs"]
    assert len(gigs) == 1
    assert gigs[0]["campus_location"] == "JKUAT Juja"


def test_cannot_apply_to_own_gig(client):
    poster, _ = _register_two_users(client)
    gig_id = _create_gig(client, poster["access_token"]).get_json()["gig"]["id"]

    resp = client.post(
        f"/api/gigs/{gig_id}/applications",
        json={"proposal_text": "I'll do it"},
        headers=auth_header(poster["access_token"]),
    )
    assert resp.status_code == 403


def test_my_gigs_lists_only_own_posted_gigs(client):
    poster, hustler = _register_two_users(client)
    _create_gig(client, poster["access_token"], title="Poster's gig")
    _create_gig(client, hustler["access_token"], title="Hustler's gig")

    resp = client.get("/api/gigs/mine", headers=auth_header(poster["access_token"]))
    assert resp.status_code == 200
    gigs = resp.get_json()["gigs"]
    assert len(gigs) == 1
    assert gigs[0]["title"] == "Poster's gig"


def test_full_gig_lifecycle_two_sided_completion(client):
    """Phase 6: gig finishes only when both poster AND hustler confirm."""
    poster, hustler = _register_two_users(client)
    gig_id = _create_gig(client, poster["access_token"]).get_json()["gig"]["id"]

    # Hustler applies
    application_id = client.post(
        f"/api/gigs/{gig_id}/applications",
        json={"proposal_text": "I can do this in 2 hours."},
        headers=auth_header(hustler["access_token"]),
    ).get_json()["application"]["id"]

    # Poster accepts — gig moves to IN_PROGRESS
    accept_resp = client.patch(
        f"/api/applications/{application_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )
    assert accept_resp.status_code == 200
    assert accept_resp.get_json()["gig"]["status"] == "IN_PROGRESS"

    # Poster marks complete — first side → PENDING_CONFIRMATION
    first_complete = client.post(
        f"/api/gigs/{gig_id}/complete",
        headers=auth_header(poster["access_token"]),
    )
    assert first_complete.status_code == 200
    body = first_complete.get_json()
    assert body["gig"]["status"] == "PENDING_CONFIRMATION"
    assert body["awaiting_confirmation_from"] == "counterparty"
    assert body["needs_review"] is False

    # Hustler confirms — second side → COMPLETED
    second_complete = client.post(
        f"/api/gigs/{gig_id}/complete",
        headers=auth_header(hustler["access_token"]),
    )
    assert second_complete.status_code == 200
    body2 = second_complete.get_json()
    assert body2["gig"]["status"] == "COMPLETED"
    assert body2["needs_review"] is True


def test_dispute_completion(client, db, app):
    """Phase 6: the non-confirming party can dispute instead of confirming."""
    poster, hustler = _register_two_users(client)
    gig_id = _create_gig(client, poster["access_token"]).get_json()["gig"]["id"]

    app_id = client.post(
        f"/api/gigs/{gig_id}/applications",
        json={},
        headers=auth_header(hustler["access_token"]),
    ).get_json()["application"]["id"]

    client.patch(
        f"/api/applications/{app_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )

    # Poster requests completion
    client.post(f"/api/gigs/{gig_id}/complete", headers=auth_header(poster["access_token"]))

    # Hustler disputes instead of confirming
    dispute_resp = client.post(
        f"/api/gigs/{gig_id}/dispute",
        json={"reason": "Work was never actually done."},
        headers=auth_header(hustler["access_token"]),
    )
    assert dispute_resp.status_code == 200
    assert dispute_resp.get_json()["gig"]["status"] == "DISPUTED"


def test_full_gig_lifecycle_with_review(client):
    """Complete lifecycle including two-sided completion and review."""
    poster, hustler = _register_two_users(client)
    gig_id = _create_gig(client, poster["access_token"]).get_json()["gig"]["id"]

    app_id = client.post(
        f"/api/gigs/{gig_id}/applications",
        json={"proposal_text": "I can do this."},
        headers=auth_header(hustler["access_token"]),
    ).get_json()["application"]["id"]

    client.patch(
        f"/api/applications/{app_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )

    # Both parties confirm
    client.post(f"/api/gigs/{gig_id}/complete", headers=auth_header(poster["access_token"]))
    client.post(f"/api/gigs/{gig_id}/complete", headers=auth_header(hustler["access_token"]))

    # Poster reviews hustler
    review_resp = client.post(
        "/api/reviews",
        json={
            "gig_id": gig_id,
            "reviewee_id": hustler["user"]["id"],
            "rating": 5,
            "comment": "Fast and reliable!",
        },
        headers=auth_header(poster["access_token"]),
    )
    assert review_resp.status_code == 201

    # Confirm avg_rating updated
    profile = client.get("/api/auth/me", headers=auth_header(hustler["access_token"]))
    assert profile.get_json()["user"]["avg_rating"] == 5.0


def test_multi_slot_gig(client):
    """Phase 8: a gig with slots_needed=2 stays open until both slots are filled."""
    poster, _ = _register_two_users(client)
    third_resp = register_user(client, email="third@jkuat.ac.ke", name="Third User")
    third = third_resp.get_json()

    gig_id = _create_gig(
        client, poster["access_token"], title="Event setup", slots_needed=2
    ).get_json()["gig"]["id"]

    app1_id = client.post(
        f"/api/gigs/{gig_id}/applications", json={},
        headers=auth_header(register_user(client, email="h1@jkuat.ac.ke", name="H1").get_json()["access_token"])
    ).get_json()["application"]["id"]
    app2_id = client.post(
        f"/api/gigs/{gig_id}/applications", json={},
        headers=auth_header(third["access_token"])
    ).get_json()["application"]["id"]

    # Accept first — gig still OPEN (1 of 2 slots filled)
    resp1 = client.patch(
        f"/api/applications/{app1_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )
    assert resp1.get_json()["gig"]["status"] == "OPEN"

    # Accept second — gig moves to IN_PROGRESS (all slots filled)
    resp2 = client.patch(
        f"/api/applications/{app2_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )
    assert resp2.get_json()["gig"]["status"] == "IN_PROGRESS"


def test_moderation_flags_risky_gig(client):
    """Phase 9: a gig with academic-integrity keywords is held for review."""
    poster, _ = _register_two_users(client)
    resp = _create_gig(
        client,
        poster["access_token"],
        title="Do my assignment for me",
        description="Need someone to write my essay and submit it on my behalf.",
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["gig"]["status"] == "OPEN"          # created, not rejected
    assert body["gig"].get("flagged_for_review") is not False  # flagged internally
    assert "message" in body                          # user-facing notice

    # Flagged gig should NOT appear in the public feed
    feed = client.get("/api/gigs?campus=JKUAT Juja")
    feed_ids = [g["id"] for g in feed.get_json()["gigs"]]
    assert body["gig"]["id"] not in feed_ids


def test_landmark_filter(client):
    """Phase 8: sub-campus landmark appears in feed filter."""
    poster, _ = _register_two_users(client)
    _create_gig(client, poster["access_token"], title="Gate B gig", landmark="Gate B")
    _create_gig(client, poster["access_token"], title="Hostel gig", landmark="Hostel 5")

    resp = client.get("/api/gigs?campus=JKUAT Juja&near=Gate B")
    titles = [g["title"] for g in resp.get_json()["gigs"]]
    assert "Gate B gig" in titles
    assert "Hostel gig" not in titles
