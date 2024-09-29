from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic_models.game import GameData
from pydantic_models.user import UserStatDTO
from schemas.user import Session as SignInSession
from routers.auth import find_session_on_db
from routers.game import get_top_10_players, get_user_statistics_by_id, get_users_games_by_id

page_router = APIRouter(prefix='/pages', tags=["Pages"])

templates = Jinja2Templates(directory='templates')

def session_exist(session:SignInSession=Depends(find_session_on_db)):
    if session is None:
        return 0
    return 1

@page_router.get("/home")
def get_base_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    return templates.TemplateResponse("home.html", {"request": request,"session":session_flag})

@page_router.get("/rating")
def get_rating_page(request: Request, session_flag:Annotated[int,Depends(session_exist)], players:list[UserStatDTO]=Depends(get_top_10_players)):
    return templates.TemplateResponse("rate.html", {"request": request,"players":players,"session":session_flag})

@page_router.get("/profile")
def get_profile_page(session:SignInSession=Depends(find_session_on_db)):
    if session is not None:
        return RedirectResponse(f"/pages/profile/{session.fk_user_id}")
    return RedirectResponse("/pages/auth")

@page_router.get("/profile/{user_id}")
def get_profile_id_page(request: Request, session_flag:Annotated[int,Depends(session_exist)], user_stat:Annotated[UserStatDTO|None, Depends(get_user_statistics_by_id)], user_games:Annotated[list[GameData],Depends(get_users_games_by_id)], user_id:int):
    if user_stat is None:
        return RedirectResponse("/pages/home")
    return templates.TemplateResponse("profile.html", {"request": request, "session": session_flag, "user": user_stat,"games":user_games,"id":user_id})

@page_router.get("/auth")
def get_auth_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return templates.TemplateResponse("auth.html", {"request": request,"session":session_flag})
    return RedirectResponse("/pages/profile")

@page_router.get("/reg")
def get_reg_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return templates.TemplateResponse("reg.html", {"request": request,"session":session_flag})
    return RedirectResponse("/pages/profile")

@page_router.get("/settings")
def get_settings_page(session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return RedirectResponse("/pages/auth")
    return RedirectResponse("/pages/settings/lgn")

@page_router.get("/settings/lgn")
def get_edit_login_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return RedirectResponse("/pages/auth")
    return templates.TemplateResponse("ed_log.html", {"request": request,"session":session_flag})

@page_router.get("/settings/usr")
def get_edit_login_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return RedirectResponse("/pages/auth")
    return templates.TemplateResponse("ed_usr.html", {"request": request,"session":session_flag})

@page_router.get("/settings/psw")
def get_edit_login_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return RedirectResponse("/pages/auth")
    return templates.TemplateResponse("ed_psw.html", {"request": request,"session":session_flag})

@page_router.get("/settings/eml")
def get_edit_login_page(request: Request, session_flag:Annotated[int,Depends(session_exist)]):
    if not session_flag:
        return RedirectResponse("/pages/auth")
    return templates.TemplateResponse("ed_email.html", {"request": request,"session":session_flag})