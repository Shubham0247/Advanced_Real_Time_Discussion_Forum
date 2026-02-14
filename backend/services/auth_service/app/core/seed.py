from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.services.auth_service.app.models.role import Role


def seed_roles(db: Session):
    """
    Inserts default roles if they do not exist.
    """

    existing_roles = {
        role.name
        for role in db.execute(select(Role)).scalars()
    }

    default_roles = [
        ("admin", "Administrator with full system access"),
        ("moderator", "Moderator with content control permissions"),
        ("member", "Regular user"),
    ]

    for name, description in default_roles:
        if name not in existing_roles:
            db.add(Role(name=name, description=description))

    db.commit()
