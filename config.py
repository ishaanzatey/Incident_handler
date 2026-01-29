import os
from dotenv import load_dotenv

load_dotenv()

# ServiceNow
SN_url = os.getenv("SN_url")
SN_username = os.getenv("SN_username")
SN_password = os.getenv("SN_password")
ASSIGNMENT_GROUP_SYS_ID = os.getenv("ASSIGNMENT_GROUP_SYS_ID")

# Postgres
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

required = [
    SN_url, SN_username, SN_password, ASSIGNMENT_GROUP_SYS_ID,
    PG_HOST, PG_DB, PG_USER, PG_PASSWORD
]

if not all(required):
    raise EnvironmentError("Missing required environment variables")
