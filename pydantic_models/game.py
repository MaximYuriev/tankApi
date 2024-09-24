from pydantic import BaseModel
from datetime import date

class GameData(BaseModel):
    game_time: str
    game_date: date
    player_score: int
    player_kill: int
    player_shot: int
    all_shot: int

class GameDTO(GameData):
    game_id: int
