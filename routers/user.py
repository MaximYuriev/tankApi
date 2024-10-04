from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import redis.asyncio as redis

from bgtask.tasks import send_email_hello_world
from config import REDIS_HOST, REDIS_PORT
from db.database import get_session
from schemas.user import User
from schemas.user import Session as SignInUser
from routers.auth import find_session_on_db, password_hash
from utils.exceptions import session_not_exist, user_not_found, iternal_server_error, login_is_not_unique, \
    login_is_not_correct, username_is_not_unique, password_is_not_correct, user_not_auth, email_not_unique, \
    email_is_not_found, email_is_verify, verify_code_is_expired, verify_code_is_not_correct

user_router = APIRouter(prefix='/user', tags=['User'])

async def check_user_existing_by_id(user_id:int, db_session:Session = Depends(get_session)):
    query = select(User).where(User.user_id == user_id)
    user = await db_session.scalar(query)
    if user is None:
        raise user_not_found
    return user.user_id

async def current_user(session:Annotated[SignInUser, Depends(find_session_on_db)],db:Session=Depends(get_session)):
    if session is None:
        raise session_not_exist

    query = select(User).where(User.user_id == session.fk_user_id)
    user = await db.scalar(query)
    if user is None:
        raise user_not_auth
    return user

async def commit_results_on_db(db:Session=Depends(get_session)):
    try:
        await db.commit()
        return True
    except SQLAlchemyError:
        await db.rollback()
        raise iternal_server_error

@user_router.patch('/edit/login')
async def edit_user_login(user:Annotated[User, Depends(current_user)],
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
async def edit_user_username(user:Annotated[User, Depends(current_user)],
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
async def edit_user_password(user:Annotated[User, Depends(current_user)],
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


@user_router.patch('/edit/email')
async def edit_user_email(user:Annotated[User,Depends(current_user)],email:Annotated[str,Body()],db:Session=Depends(get_session)):
    query = select(User).where(User.email == email)
    check_email = await db.scalar(query)
    if check_email is not None:
        raise email_not_unique

    user.email = email
    user.email_verify = False
    await commit_results_on_db(db)

    send_email_hello_world.delay(user.email, user.user_id)

    return {"detail":"Письмо отправлено", "data":None}

@user_router.post('/verify_email')
async def verify_user_email(user:Annotated[User,Depends(current_user)], verify_code:Annotated[int,Body()], db:Session=Depends(get_session)):
    if user.email is None:
        raise email_is_not_found
    if user.email_verify:
        raise email_is_verify

    async with redis.Redis(host=REDIS_HOST, port=REDIS_PORT) as redis_client:
        value = int(await redis_client.get(user.user_id))
        if value is None:
            raise verify_code_is_expired
        if value != verify_code:
            raise verify_code_is_not_correct
        await redis_client.delete(user.user_id)

    user.email_verify = True
    await commit_results_on_db(db)

    return {"detail":"Электронная почта подтверждена!", "data":None}

@user_router.get('/get_verify_code')
def get_new_verify_code(user:Annotated[User,Depends(current_user)]):
    if user.email is None:
        raise email_is_not_found
    if user.email_verify:
        raise email_is_verify

    send_email_hello_world.delay(user.email, user.user_id)

    return {"detail": "Письмо отправлено", "data": None}