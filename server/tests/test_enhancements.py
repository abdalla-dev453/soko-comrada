"""Tests for messaging, student ID verification, and search/filtering."""

import pytest
from app.models.opportunity import Gig, OpportunityType, CompensationType
from app.models.user import User, UserType
from tests.conftest import auth_header


def _create_user(client, email, name, user_type="STUDENT"):
    res = client.post(
        "/api/auth/register/student",
        json={
            "name": name,
            "email": email,
            "password": "Password12345!",
            "phone_number": "0712345678",
            "university": "JKUAT",
            "campus_location": "Juja",
        },
    )
    return res.get_json()


def test_messaging_between_participants(client):
    poster = _create_user(client, "poster_msg@jkuat.ac.ke", "Poster Person")
    seeker = _create_user(client, "seeker_msg@jkuat.ac.ke", "Seeker Person")

    # Poster creates gig
    gig_res = client.post(
        "/api/gigs",
        json={
            "title": "Build a React Portfolio",
            "description": "Need a responsive personal portfolio with Tailwind.",
            "category": "gigs_work",
            "budget": 3000,
            "campus_location": "Juja",
        },
        headers=auth_header(poster["access_token"]),
    )
    gig_id = gig_res.get_json()["gig"]["id"]

    # Seeker applies
    client.post(
        f"/api/gigs/{gig_id}/applications",
        json={"proposal_text": "I can build this portfolio!"},
        headers=auth_header(seeker["access_token"]),
    )

    # Seeker sends message to poster
    msg_res = client.post(
        "/api/messages",
        json={
            "opportunity_id": gig_id,
            "recipient_id": poster["user"]["id"],
            "content": "Hello! I applied to your gig.",
        },
        headers=auth_header(seeker["access_token"]),
    )
    assert msg_res.status_code == 201
    assert msg_res.get_json()["message"]["content"] == "Hello! I applied to your gig."

    # Poster views thread
    thread_res = client.get(
        f"/api/messages/opportunity/{gig_id}?with_user={seeker['user']['id']}",
        headers=auth_header(poster["access_token"]),
    )
    assert thread_res.status_code == 200
    messages = thread_res.get_json()["messages"]
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello! I applied to your gig."


def test_opportunity_search_and_filter(client):
    poster = _create_user(client, "poster_search@jkuat.ac.ke", "Poster Search")
    client.post(
        "/api/gigs",
        json={
            "title": "Maths and Calculus Tutoring",
            "description": "Calculus 1 tutor for second semester revision.",
            "category": "tutoring",
            "budget": 1500,
            "campus_location": "UoN Chiromo",
        },
        headers=auth_header(poster["access_token"]),
    )

    # Search by keyword "Calculus"
    search_res = client.get("/api/gigs?q=Calculus")
    assert search_res.status_code == 200
    gigs = search_res.get_json()["gigs"]
    assert any("Calculus" in g["title"] or "Calculus" in g["description"] for g in gigs)

    # Filter by campus "UoN Chiromo"
    campus_res = client.get("/api/gigs?campus=UoN+Chiromo")
    assert campus_res.status_code == 200
    assert len(campus_res.get_json()["gigs"]) >= 1


def test_student_id_verification(client):
    student = _create_user(client, "student_verify@jkuat.ac.ke", "Student ID Check")
    res = client.post(
        "/api/auth/verify-student-id",
        json={
            "student_id_number": "SCT211-0045/2023",
            "student_id_document_url": "https://example.com/student_card.jpg",
        },
        headers=auth_header(student["access_token"]),
    )
    assert res.status_code == 200
    assert res.get_json()["user"]["is_verified_student"] is True
