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
    gig_resp = _create_gig(client, poster["access_token"])
    gig_id = gig_resp.get_json()["gig"]["id"]

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


def test_full_gig_lifecycle_apply_accept_complete_review(client):
    poster, hustler = _register_two_users(client)
    gig_resp = _create_gig(client, poster["access_token"])
    gig_id = gig_resp.get_json()["gig"]["id"]

    apply_resp = client.post(
        f"/api/gigs/{gig_id}/applications",
        json={"proposal_text": "I can do this in 2 hours."},
        headers=auth_header(hustler["access_token"]),
    )
    assert apply_resp.status_code == 201
    application_id = apply_resp.get_json()["application"]["id"]

    accept_resp = client.patch(
        f"/api/applications/{application_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )
    assert accept_resp.status_code == 200
    assert accept_resp.get_json()["gig"]["status"] == "IN_PROGRESS"

    complete_resp = client.post(
        f"/api/gigs/{gig_id}/complete", headers=auth_header(poster["access_token"])
    )
    assert complete_resp.status_code == 200
    assert complete_resp.get_json()["gig"]["status"] == "COMPLETED"
    assert complete_resp.get_json()["needs_review"] is True

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

    hustler_profile = client.get(f"/api/auth/me", headers=auth_header(hustler["access_token"]))
    assert hustler_profile.get_json()["user"]["avg_rating"] == 5.0
