from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey, create_engine,
    String, DateTime, LargeBinary
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped,
    mapped_column, relationship, Session
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    public_key: Mapped[bytes] = mapped_column(LargeBinary(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message", foreign_keys="Message.recipient_id", back_populates="recipient"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    recipient: Mapped["User"] = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_messages"
    )

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, sender_id={self.sender_id!r})"


engine = create_engine(
    "mysql+pymysql://safetalk_user:safetalk_password@localhost/safeTalk",
    echo=True
)
Base.metadata.create_all(engine)