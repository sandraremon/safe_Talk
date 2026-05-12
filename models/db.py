from datetime import datetime, timezone
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
from sqlalchemy import (
    ForeignKey, create_engine,
    String, DateTime, LargeBinary
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped,
    mapped_column,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)

    username: Mapped[str] = mapped_column(String(255), unique=True)

    password_hash: Mapped[str] = mapped_column(String(128))

    public_key: Mapped[str] = mapped_column(String(1000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    recipient_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    ciphertext: Mapped[bytes] = mapped_column(LargeBinary)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(
    DATABASE_URL,
    echo=True
)


Base.metadata.create_all(engine)