from flask import session

from flask_repository_getters import get_user_repository


def get_user_from_session():
    user = None
    if "user_id" in session and session["user_id"]:
        user_repo = get_user_repository()
        user = user_repo.get_user_from_id_if_exists(session["user_id"])
    return user
