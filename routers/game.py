from typing import Annotated

from fastapi import APIRouter, status, Response
from fastapi.params import Depends

from db.database import get_session
from sqlalchemy import select, func, desc, exc
from sqlalchemy.orm import Session

from schemas.game import Game
from schemas.user import User
from schemas.user import Session as SignInSession
from routers.auth import find_session_on_db
from utils.exceptions import iternal_server_error, user_not_found, session_not_exist
from pydantic_models.game import GameData, GameDTO
from pydantic_models.user import UserStatDTO, UserRateDTO

from fastapi_cache.decorator import cache

game_router = APIRouter(prefix='/game', tags=['Game'])

async def check_user_existing_by_id(user_id:int, db_session:Session = Depends(get_session)):
    query = select(User).where(User.user_id == user_id)
    user = await db_session.scalar(query)
    if user is None:
        return False
    return True

@game_router.post('/add')
async def add_new_game_data(data:GameData, session:Annotated[SignInSession,Depends(find_session_on_db)], db:Session=Depends(get_session)):
    if session is None:
        raise session_not_exist
    game_data = Game(
        user_id=session.fk_user_id,
        game_time=data.game_time,
        game_date=data.game_date,
        player_score=data.player_score,
        player_kill=data.player_kill,
        player_shot=data.player_shot,
        all_shot=data.all_shot
    )
    try:
        db.add(game_data)
        await db.commit()
        return {"detail":"Данные успешно добавлены","data":None}
    except exc.SQLAlchemyError:
        await db.rollback()
        raise iternal_server_error

@game_router.get('/profile/{user_id}')
@cache(expire=30)
async def get_user_statistics_by_id(user_id:int,check_user_exist:Annotated[bool,Depends(check_user_existing_by_id)], db:Session = Depends(get_session)):
    if not check_user_exist:
        raise user_not_found
    query = (
        select(
            User.username,
            func.max(Game.player_score).label("high_score"),
            func.sum(Game.player_kill).label("all_kills"),
            func.sum(Game.player_shot).label("all_shots"),
            func.count(Game.user_id).label("games")
        ).select_from(User)
        .join(Game, Game.user_id == User.user_id, isouter=True)
        .where(User.user_id == user_id)
        .group_by(User.username)
    )
    res = await db.execute(query)
    result_orm = res.first()
    result_dto = UserStatDTO.model_validate(result_orm, from_attributes=True)
    return {"detail":"Данные успешно добавлены","data":result_dto}

@game_router.get('/profile/{user_id}/games')
@cache(expire=30)
async def get_users_games_by_id(user_id:int, check_user_exist:Annotated[bool,Depends(check_user_existing_by_id)], db:Session = Depends(get_session),offset:int = 0):
    if not check_user_exist:
        raise user_not_found
    query = (
        select(Game)
        .where(Game.user_id == user_id)
        .order_by(Game.game_id.desc())
        .limit(5)
        .offset(offset)
    )
    res = await db.execute(query)
    result_orm = res.scalars().all()
    result_dto = [GameDTO.model_validate(row, from_attributes=True) for row in result_orm]
    return {"detail":"Данные о пользователе","data":result_dto}


@game_router.get('/rating')
@cache(expire=60)
async def get_top_10_players(db:Session = Depends(get_session)):
    query = (
        select(
            func.max(Game.player_score).label("high_score"),
            func.sum(Game.player_kill).label("all_kills"),
            func.sum(Game.player_shot).label("all_shots"),
            func.count(Game.user_id).label("games"),
            User.user_id,
            User.username,
        )
        .join(User, Game.user_id == User.user_id)
        .group_by(User.username,User.user_id)
        .order_by(desc("high_score"))
        .limit(10)
    )
    res = await db.execute(query)
    result_orm = res.all()
    result_dto = [UserRateDTO.model_validate(row, from_attributes=True) for row in result_orm]
    return {"detail":"Рейтинг пользователей","data":result_dto}