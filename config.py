import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_SCHEMA_NAME = os.environ.get("DATABASE_SCHEMA_NAME")
