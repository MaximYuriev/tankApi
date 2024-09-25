from pydantic import BaseModel

class SignUpUser(BaseModel):
    login: str
    username: str
    password: str

class SignInUser(BaseModel):
    login: str
    password: str
    desktop_status: bool = False

class UserEdit(SignUpUser):
    login: str|None = None
    username: str|None = None
    password: str|None = None
    email: str|None = None

class UserStatDTO(BaseModel):
    username: str
    high_score: int|None
    all_kills: int|None
    all_shots: int|None
    games: int|None

class UserRateDTO(UserStatDTO):
    user_id:int
