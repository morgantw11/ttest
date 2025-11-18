from django.conf import settings
from django.shortcuts import redirect,render
from .models import IPWhitelist,MagicLinkToken,ErrorSite,Carantin,IPWhitelistOnOrOff
from django.contrib.auth import logout

class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        secret = request.headers.get("X-Telegram-Bot-Secret")
        path = request.path
        user = request.user

        if request.user.is_authenticated and user.is_block:
            return redirect("https://google.com")

        # Разрешаем если есть секретный ключ
        if secret == getattr(settings, "TELEGRAM_BOT_SECRET", None):
            return self.get_response(request)
        
        # 🔹 всегда пропускаем MagicLink урл
        if path.startswith("/invite/"):
            token_str = path.split("/invite/")[-1].strip("/")
            
            if MagicLinkToken.objects.filter(token=token_str, used=False).exists():
                return self.get_response(request)
            else:
                return redirect("https://google.com")  # токен невалидный
    

        # Разрешаем если IP есть в whitelist
        if IPWhitelist.objects.filter(ip_address=ip).exists():
            return self.get_response(request)

        #Выключение айпи листа
        if IPWhitelistOnOrOff.objects.exists():
            return self.get_response(request)

        return redirect("https://google.com")

    def get_client_ip(self, request):
        """Вытащить IP клиента"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip



class MaintenanceModeMiddleware:
    """
    Блокирует весь сайт с 503 если есть хотя бы один объект ErrorSite,
    кроме заданного URL, который используется для управления этим объектом.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_urls = [
            "/api/mode/503/create",
            "/api/mode/503/delete",
        ]


    def __call__(self, request):
        secret = request.headers.get("X-Telegram-Bot-Secret")
        # разрешаем доступ к allowed_url всегда
        if any(request.path.startswith(url) for url in self.allowed_urls):
            return self.get_response(request)
        
        # проверяем, есть ли хотя бы один объект ErrorSite
        if secret == getattr(settings, "TELEGRAM_BOT_SECRET", None):
            return self.get_response(request)
        if ErrorSite.objects.exists():
            # возвращаем 503 страницу
            return render(request, "503.html", status=503)
        

        return self.get_response(request)
    

#Carantin

class QuarantineMiddleware:
    """
    Блокирует доступ обычным пользователям (user) при включенном карантине.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if Carantin.objects.exists():
            user = request.user
            if user.is_authenticated:
                role = user.role
                if role == "user":
                    logout(request)
                    return redirect('')

        return self.get_response(request)
