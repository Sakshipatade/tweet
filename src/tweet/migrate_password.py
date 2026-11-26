from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from tweet.database import SessionLocal
from tweet.models.user import User
from tweet.security import hashPassword

db = SessionLocal()

try:
    users = db.scalars(select(User)).all()

    for user in users:
        user.password = hashPassword(user.password)

    db.commit()
    print("All passwords hashed...")
except SQLAlchemyError as exc:
    db.rollback()
    print("Password migration failed.")
    raise
finally:
    db.close()