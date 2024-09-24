from pydantic import BaseModel

class SignUpUser(BaseModel):
    login: str
    username: str
    password: str

class SignInUser(BaseModel):
    login: str
    password: str
    desktop_status: bool = False

class UserStatDTO(BaseModel):
    username: str
    high_score: int|None
    all_kills: int|None
    all_shots: int|None
    games: int|None

class UserRateDTO(UserStatDTO):
    user_id:int
