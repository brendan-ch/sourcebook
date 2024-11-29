from typing import Optional

import mysql.connector
from flask import g, current_app

from datarepos.content_repo import ContentRepo
from datarepos.course_repo import CourseRepo
from datarepos.user_repo import UserRepo

def get_content_repository():
    repository: Optional[ContentRepo] = getattr(g, '_content_repository', None)
    if not repository or not repository.connection_is_open:
        config = vars(current_app.config["DB_CONFIG_OBJECT"])
        if not config:
            raise RuntimeError("No database configured.")

        connection = mysql.connector.connect(**config)
        repository = g._content_repository = ContentRepo(connection)
    return repository

def get_user_repository():
    repository: Optional[UserRepo] = getattr(g, '_user_repository', None)
    if not repository or not repository.connection_is_open:
        config = vars(current_app.config["DB_CONFIG_OBJECT"])
        if not config:
            raise RuntimeError("No database configured.")

        connection = mysql.connector.connect(**config)
        repository = g._user_repository = UserRepo(connection)
    return repository

def get_course_repository():
    repository: Optional[CourseRepo] = getattr(g, '_course_repository', None)
    if not repository or not repository.connection_is_open:
        config = vars(current_app.config["DB_CONFIG_OBJECT"])
        if not config:
            raise RuntimeError("No database configured.")

        connection = mysql.connector.connect(**config)
        repository = g._course_repository = CourseRepo(connection)
    return repository
