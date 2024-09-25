from fastapi import HTTPException

iternal_server_error = HTTPException(status_code=500, detail='Непредвиденная ошибка!')

login_is_not_unique = HTTPException(status_code=400,detail="Логин уже используется в системе")

username_is_not_unique = HTTPException(status_code=400, detail="Имя пользователя занято")

not_user_ex = HTTPException(status_code=400, detail="Неверный логин или пароль")

session_not_exist = HTTPException(status_code=403, detail="Сессия не существует")

user_not_found = HTTPException(status_code=404, detail="Пользователь не найден")

cookie_not_found = HTTPException(status_code=404, detail="Куки не найдены")

login_is_not_correct = HTTPException(status_code=400, detail="Данный пользователь использует другой логин")

password_is_not_correct = HTTPException(status_code=400, detail="Старый пароль указан неверно")