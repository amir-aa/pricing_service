from peewee import *
from playhouse.pool import PooledMySQLDatabase
import os
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_host = os.environ.get("DB_HOST")
db_password = os.environ.get("DB_PASSWORD")

if not all([db_name, db_user, db_host, db_password]):
    raise ValueError("One or more required environment variables are missing",str([db_name, db_user, db_host, db_password]))
else:
    print("All environment variables are set",str([db_name, db_user, db_host, db_password]) )        
def get_db():
 
    db = PooledMySQLDatabase(
    str(os.environ.get("DB_NAME")),
    max_connections=32,
    stale_timeout=100,
    user=str(os.environ.get("DB_USER")),
    password=str(os.environ.get("DB_PASSWORD")),
    host=str(os.environ.get("DB_HOST")),
    port=3306

            )
    return db
