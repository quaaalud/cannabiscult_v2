from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    Text,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base_class import Base


class User(Base):
    username = Column(String, unique=True, nullable=False)
    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
        primary_key=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    phone = Column(String, nullable=True)
    zip_code = Column(
        String,
        nullable=False,
    )
    password = Column(String, nullable=False)
    agree_tos = Column(Boolean(), default=True)
    can_vote = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    strain_lists = relationship("UserStrainList", back_populates="user")


class UserStrainList(Base):
    __tablename__ = "user_strain_list"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    email = Column(
        Text,
        ForeignKey("user.email", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    strain = Column(Text, nullable=False)
    cultivator = Column(Text, nullable=False)
    to_review = Column(Boolean, nullable=False, default=True)
    product_type = Column(Text, nullable=True)
    # Relationship to user model, assuming 'User' is the name of the user model
    user = relationship("User", back_populates="strain_lists")
