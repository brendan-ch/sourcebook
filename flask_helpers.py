from flask import session

from flask_repository_getters import get_user_repository


def get_user_from_session():
    user = None
    if "user_uuid" in session and session["user_uuid"]:
        user_repo = get_user_repository()
        user = user_repo.get_user_from_uuid_if_exists(session["user_uuid"])
    return user
