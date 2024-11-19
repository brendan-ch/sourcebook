from typing import Optional

from flask import g

from datarepos.user_repo import UserRepo


def get_user_repository():
    repository: Optional[UserRepo] = getattr(g, '_user_repository', None)
    if not repository or not repository.connection_is_open:
        repository = g._user_repository = UserRepo()
    return repository

