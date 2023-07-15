from sqlalchemy import Column, Integer, String, Boolean

from db.base_class import Base


class User(Base):
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    username = Column(
        String,unique=True,
        nullable=False
    )
    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    name = Column(
        String,
        nullable=False,
    )
    phone = Column(
        String,
        nullable=True
    )
    zip_code = Column(
        String,
        nullable=False,
    )
    password = Column(
        String,
        nullable=False
    )
    agree_tos = Column(
        Boolean(),
        default=True
    )
    can_vote = Column(
        Boolean(),
        default=False
    )
    is_superuser = Column(
        Boolean(),
        default=False
    )