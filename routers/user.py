from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.database import get_session
from schemas.user import User
from schemas.user import Session as SignInUser
from routers.auth import find_session_on_db, password_hash
from utils.exceptions import session_not_exist, user_not_found, iternal_server_error, login_is_not_unique, \
    login_is_not_correct, username_is_not_unique, password_is_not_correct

user_router = APIRouter(prefix='/user', tags=['User'])


async def preprocessing_edit_user(session:Annotated[SignInUser, Depends(find_session_on_db)],db:Session=Depends(get_session)):
    if session is None:
        raise session_not_exist

    query = select(User).where(User.user_id == session.fk_user_id)
    user = await db.scalar(query)
    if user is None:
        raise user_not_found
    return user

async def commit_results_on_db(db:Session=Depends(get_session)):
    try:
        await db.commit()
        return True
    except SQLAlchemyError:
        await db.rollback()
        raise iternal_server_error

@user_router.patch('/edit/login')
async def edit_user_login(user:Annotated[User, Depends(preprocessing_edit_user)],
                          old_login:Annotated[str,Body()],
                          new_login:Annotated[str,Body()],
                          db:Session=Depends(get_session)):

    query = select(User).where(and_(User.user_id == user.user_id, User.login == old_login))
    old_login_check = await db.scalar(query)
    if old_login_check is None:
        raise login_is_not_correct

    query = select(User).where(User.login == new_login)
    new_login_check = await db.scalar(query)
    if new_login_check is not None:
        raise login_is_not_unique

    user.login = new_login
    await commit_results_on_db(db)
    return {"detail":"Логин успешно изменен","data":None}

@user_router.patch('/edit/username')
async def edit_user_username(user:Annotated[User, Depends(preprocessing_edit_user)],
                          new_username:Annotated[str,Body()],
                          db:Session=Depends(get_session)):

    query = select(User).where(User.username == new_username)
    new_username_check = await db.scalar(query)
    if new_username_check is not None:
        raise username_is_not_unique

    user.username = new_username
    await commit_results_on_db(db)
    return {"detail":"Имя пользователя успешно изменено","data":None}

@user_router.patch('/edit/password')
async def edit_user_password(user:Annotated[User, Depends(preprocessing_edit_user)],
                          old_password:Annotated[str,Body()],
                          new_password:Annotated[str,Body()],
                          db:Session=Depends(get_session)):

    old_password = password_hash(old_password)
    query = select(User).where(and_(User.user_id == user.user_id, User.password == old_password))
    old_password_check = await db.scalar(query)
    if old_password_check is None:
        raise password_is_not_correct

    new_password = password_hash(new_password)
    user.password = new_password

    await commit_results_on_db(db)
    return {"detail":"Пароль успешно изменен!","data":None}
