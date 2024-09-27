from typing import Annotated

from db.database import get_session
from fastapi import APIRouter, Response, status, Request, HTTPException
from fastapi.params import Depends

from sqlalchemy import select, and_, exc
from sqlalchemy.orm import Session

import hashlib
import uuid


from schemas.user import User
from schemas.user import Session as SignInSession
from pydantic_models.user import SignUpUser, SignInUser
from config import COOKIES_KEY_NAME

from utils.exceptions import login_is_not_unique, username_is_not_unique, not_user_ex, session_not_exist, iternal_server_error

auth_router = APIRouter(prefix='/auth',tags=['Auth'])


def password_hash(password:str) -> str:
    password_code = password.encode('utf-8')
    hash_password = hashlib.sha256(password_code)
    return hash_password.hexdigest()

def generate_session_id() -> str:
    return uuid.uuid4().hex

async def find_session_on_db(response:Response,request:Request,db: Session=Depends(get_session)):
    cookie_session_id = request.cookies.get(COOKIES_KEY_NAME)
    if cookie_session_id is None:
        return None
    stmt_session = select(SignInSession).where(SignInSession.session_id==cookie_session_id)
    session = await db.scalar(stmt_session)
    if session is None:
        response.delete_cookie(COOKIES_KEY_NAME)
        return None
    return session



@auth_router.post("/registration")
async def registration_user(item:SignUpUser, db:Session=Depends(get_session)):
    query_login = select(User).where(User.login == item.login)
    query_username = select(User).where(User.username == item.username)

    login = await db.scalar(query_login)
    if login is not None:
        raise login_is_not_unique

    username = await db.scalar(query_username)
    if username is not None:
        raise username_is_not_unique

    item.password = password_hash(password=item.password)
    user = User(login=item.login,username=item.username,password=item.password)
    try:
        db.add(user)
        await db.commit()
        return {"detail":"Успешная регистрация!","data":None}
    except exc.SQLAlchemyError:
        await db.rollback()
        raise iternal_server_error


@auth_router.post("/login")
async def login_user(response:Response,item:SignInUser,db:Session=Depends(get_session)):
    item.password = password_hash(password=item.password)
    query = select(User).where(and_(User.login == item.login,User.password == item.password))

    user = await db.scalar(query)
    if user is None:
        raise not_user_ex


    session_id = generate_session_id()

    query_session = select(SignInSession).where(and_(SignInSession.fk_user_id == user.user_id, SignInSession.desktop_status == item.desktop_status))
    session = await db.scalar(query_session)
    if session is not None:
        session.session_id = session_id
        try:
            await db.commit()
        except exc.SQLAlchemyError:
            await db.rollback()
            raise iternal_server_error
    else:
        session = SignInSession(session_id=session_id,fk_user_id=user.user_id,desktop_status=item.desktop_status)
        try:
            db.add(session)
            await db.commit()
        except exc.SQLAlchemyError:
            await db.rollback()
            raise iternal_server_error
    response.set_cookie(key=COOKIES_KEY_NAME,value=session_id, httponly=True)
    return {"detail":"Успешный вход!", "data":None}


@auth_router.get('/logout')
async def logout_user(response:Response, session: Annotated[SignInSession|None,Depends(find_session_on_db)], db: Session=Depends(get_session)):
    if session is None:
        response.status_code = 404
        return {"detail":"Сессия не найдена"}
    try:
        response.delete_cookie(COOKIES_KEY_NAME)
        await db.delete(session)
        await db.commit()
        return {"detail":"Пользователь вышел!", "data":None}
    except exc.SQLAlchemyError:
        await db.rollback()
        raise iternal_server_error