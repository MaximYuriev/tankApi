from sqlalchemy import Identity, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
import uuid
Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    user_id: Mapped[int] = mapped_column(Identity(start=1),primary_key=True)
    username: Mapped[str]
    login: Mapped[str]
    email: Mapped[str] = mapped_column(nullable=True)
    email_verify: Mapped[bool] = mapped_column(nullable=True)
    password: Mapped[str]

class Session(Base):
    __tablename__ = 'session'
    session_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.user_id, ondelete="CASCADE"))
    desktop_status: Mapped[bool]

