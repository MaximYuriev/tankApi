import datetime

from sqlalchemy import Identity, ForeignKey
from schemas.user import Base, User
from sqlalchemy.orm import Mapped, mapped_column


class Game(Base):
    __tablename__ = 'game'
    game_id: Mapped[int] = mapped_column(Identity(start=1),primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.user_id))
    game_time: Mapped[str]
    game_date: Mapped[datetime.date]
    player_score: Mapped[int]
    player_kill: Mapped[int]
    player_shot: Mapped[int]
    all_shot: Mapped[int]

