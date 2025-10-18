from sqlalchemy.orm import Session
import aiohttp
from models import UserSession, SessionLocal

class DjangoAPIClient:
    def __init__(self, base_url: str, bot_secret: str):
        self.base_url = base_url.rstrip('/')
        self.bot_secret = bot_secret
    
    async def _get_session_data(self, user_id: int) -> dict:
        """Получаем сессию пользователя из БД"""
        db_session = SessionLocal()
        try:
            user_session = db_session.query(UserSession).filter(
                UserSession.user_id == user_id
            ).first()
            
            if not user_session:
                raise SessionExpiredError("User not authenticated")
                
            return {
                'sessionid': user_session.sessionid,
                'csrftoken': user_session.csrftoken
            }
        finally:
            db_session.close()
    
    async def _save_session_data(self, user_id: int, session_data: dict):
        """Сохраняем сессию пользователя в БД"""
        db_session = SessionLocal()
        try:
            user_session = db_session.query(UserSession).filter(
                UserSession.user_id == user_id
            ).first()
            
            if user_session:
                user_session.sessionid = session_data.get('sessionid')
                user_session.csrftoken = session_data.get('csrftoken')
            else:
                user_session = UserSession(
                    user_id=user_id,
                    sessionid=session_data.get('sessionid'),
                    csrftoken=session_data.get('csrftoken')
                )
                db_session.add(user_session)
            
            db_session.commit()
        finally:
            db_session.close()
    
    async def _make_request(self, user_id: int, method: str, endpoint: str, **kwargs):
        """Универсальный метод для выполнения запросов"""
        try:
            session_data = await self._get_session_data(user_id)
            
            cookies = {
                'sessionid': session_data['sessionid'],
                'csrftoken': session_data['csrftoken']
            }
            
            headers = kwargs.get('headers', {})
            # Добавляем секретный заголовок для ВСЕХ запросов
            headers['X-Telegram-Bot-Secret'] = self.bot_secret
            
            if method.upper() in ['POST', 'PUT', 'PATCH', 'DELETE']:
                headers['X-CSRFToken'] = session_data['csrftoken']
            
            kwargs['headers'] = headers
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with aiohttp.ClientSession(cookies=cookies) as session:
                async with session.request(method, url, **kwargs) as response:
                    
                    # Проверяем истекшую сессию
                    if response.status in [401, 403]:
                        await self._invalidate_session(user_id)
                        raise SessionExpiredError("Сессия истекла")
                    if response.status == 204 or response.content_type == '':
                        return {}, response.status  # возвращаем пустой словарь
                    else:
                        return await response.json(), response.status
                    
        except Exception as e:
            raise e
    
    async def _invalidate_session(self, user_id: int):
        """Удаляем истекшую сессию"""
        db_session = SessionLocal()
        try:
            user_session = db_session.query(UserSession).filter(
                UserSession.user_id == user_id
            ).first()
            if user_session:
                db_session.delete(user_session)
                db_session.commit()
        finally:
            db_session.close()
    
    async def login(self, user_id: int, username: str, password: str):
        """Метод для авторизации"""
        login_url = f"{self.base_url}/api/login/"
        
        headers = {
        "X-Telegram-Bot-Secret": self.bot_secret,  # твой кастомный ключ, если нужен
        }

        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                login_url,
                data={'username': username, 'password': password},
                headers=headers,
                allow_redirects=False
            ) as response:
                
                data = await response.json()

                if response.status in (200, 302):
                    
                    set_cookies = response.headers.getall('Set-Cookie', [])
                    session_cookie = None
                    csrf_cookie = None
                    for cookie_str in set_cookies:
                        if cookie_str.startswith("sessionid="):
                            session_cookie = cookie_str.split(";", 1)[0].split("=", 1)[1]
                        elif cookie_str.startswith("csrftoken="):
                            csrf_cookie = cookie_str.split(";", 1)[0].split("=", 1)[1]
                    session_data = {}
                    
                    if session_cookie:
                        session_data['sessionid'] = session_cookie
                    if csrf_cookie:
                        session_data['csrftoken'] = csrf_cookie

                    if session_data:
                        await self._save_session_data(user_id, session_data)
                    
                    # Считаем, что успешный логин — если статус 200 и JSON верный
                    return True, data
                
                return False, data
    
    # Упрощенные методы
    async def get(self, user_id: int, endpoint: str, **kwargs):
        return await self._make_request(user_id, 'GET', endpoint, **kwargs)
    
    async def post(self, user_id: int, endpoint: str, **kwargs):
        return await self._make_request(user_id, 'POST', endpoint, **kwargs)
    
    async def put(self, user_id: int, endpoint: str, **kwargs):
        return await self._make_request(user_id, 'PUT', endpoint, **kwargs)
    
    async def delete(self, user_id: int, endpoint: str, **kwargs):
        return await self._make_request(user_id, 'DELETE', endpoint, **kwargs)
    
    async def get_user_role(self, user_id: int):
        data, status = await self._make_request(user_id, "GET", "api/profile/")
        if status == 200:
            role = data.get("role")
            if role:
                return role
            # если API вернул 200, но нет поля role → считаем это "нет доступа", но НЕ сессия истекла
            return None  
        elif status in (401, 403):
            # только тут кидаем, если реально просрочена
            raise SessionExpiredError("User not authenticated")
        else:
            return None
        

    async def get_user_stats(self, user_id: int):
        data, status = await self._make_request(user_id, "GET", "api/user-stats/")
        if status == 200:
            return data  # тут уже {"workers_count": ..., "users_count": ..., "created_by_me_count": ...}
        else:
            return None
        
    async def get_system_states(self, user_id: int):
        data, status = await self._make_request(user_id, "GET", "api/mode/states/")
        if status == 200:
            return data
        return None

class SessionExpiredError(Exception):
    pass