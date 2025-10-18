from django.shortcuts import render,get_object_or_404,redirect
from .models import CustomUser, MagicLinkToken, IPWhitelist,ErrorSite,Carantin, IPWhitelistOnOrOff,ModeLog,Link_file
from rest_framework import generics, permissions,status
from .serializers import UserSerializer,LoginSerializer,MagicLinkTokenSerializer
from .permissions import IsWorkerOrMore,IsAdminOrMore,IsSuperAdmin
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as auth_login ,logout
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
import requests
from django.contrib import messages
import secrets
import string


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

class UserPagination(PageNumberPagination):
    page_size = 10  # пользователей на одной странице
    page_size_query_param = "page_size"
    max_page_size = 50


def generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
                    auth_login(request, user)
                    return redirect("profile")  # перенаправление после входа
        else:
            messages.error(request, "Wrong email or password")

    return render(request, 'login.html')


def error_page(request,exception=None):
    return render(request, 'error_page.html', status=404)

def analyse_contrat(request):
    return render(request, 'analyse_contrat.html')

def approbation_contrat(request):
    return render(request, 'approbation_contrat.html')

def contract_archiving(request):
    return render(request, 'contract_archiving.html')

def contract_management_automation(request):
    return render(request, 'contract_management_automation.html')

def contract_negotiation(request):
    return render(request, 'contract_negotiation.html')

def contract_signature(request):
    return render(request, 'contract_signature.html')

def dynamic_contract_template(request):
    return render(request, 'dynamic_contract_template.html')

def ebooks(request):
    return render(request, 'ebooks.html')

def generation_contract(request):
    return render(request, 'generation_contract.html')

def internal_collaboration(request):
    return render(request, 'internal_collaboration.html')

def oro_AI(request):
    return render(request, 'oro_AI.html')

def partners(request):
    return render(request, 'partners.html')

def pricing(request):
    return render(request, 'pricing.html')

def suivi_contrat(request):
    return render(request, 'suivi_contrat.html')

def templates_clauses(request):
    return render(request, 'templates_clauses.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    link = Link_file.objects.first()
    return render(request, 'profile.html',{"link": link})


def user_logout(request):
    logout(request)  # Очистит сессию пользователя
    return redirect("login")  # После выхода перекинет на страницу логина


def get_device_type(user_agent: str) -> str:
    """Простейшее определение устройства по User-Agent"""
    user_agent = user_agent.lower()
    if any(mobile in user_agent for mobile in ["iphone", "android", "blackberry", "mobile", "ipad", "tablet"]):
        return "mobile/tablet"
    else:
        return "desktop"



def magic_login(request, token):

    if request.user.is_authenticated:
        try:
            magic_token = MagicLinkToken.objects.get(token=token, used=False)
            magic_token.used = True
            magic_token.save()
        except MagicLinkToken.DoesNotExist:
            return redirect("/")
        return redirect("/")  # уже в системе, просто идём на главную
    
    # достаём токен из БД
    magic_token = get_object_or_404(MagicLinkToken, token=token, used=False)

    # авторизация пользователя
    auth_login(request, magic_token.user)



    # токен становится использованным
    magic_token.used = True
    magic_token.save()

    # добавляем IP в whitelist
    ip = request.META.get("REMOTE_ADDR")
    IPWhitelist.objects.get_or_create(ip_address=ip)

    user_agent = request.META.get("HTTP_USER_AGENT", "")
    device_type = get_device_type(user_agent)

    magic_token.user.device = device_type
    magic_token.user.ip = ip
    magic_token.user.save()
    text = (
        f"✅ Новый вход по ссылке в почте!\n\n"
        f"👤 Пользователь: {magic_token.user.username}\n"
        f"🌍 IP: {ip}\n"
        f"💻 Устройство: {device_type}\n"
    )
    send_telegram_message(magic_token.user.telegram_group_id,text)
    return redirect("/") 


class CreateMagicLinkAPIView(APIView):
    permission_classes = [IsAdminOrMore]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # создаём токен для нового пользователя
        token = MagicLinkToken.objects.create(user=user)
        serializer = MagicLinkTokenSerializer(token, context={'request': request})
        return Response(serializer.data, status=201)

#503
class EnableMaintenanceView(APIView):
    permission_classes = [IsAdminOrMore]  # твой кастомный пермишн

    def post(self, request):
        # создаём заглушку, если её нет
        ErrorSite.objects.get_or_create(title="Maintenance")
        return Response({"message": "503 mode enabled"}, status=status.HTTP_200_OK)


class DisableMaintenanceView(APIView):
    permission_classes = [IsAdminOrMore]  # твой кастомный пермишн

    def post(self, request):
        # удаляем все объекты заглушки
        ErrorSite.objects.all().delete()
        return Response({"message": "503 mode disabled"}, status=status.HTTP_200_OK)

#API views

# 🔹 Список всех пользователей
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]
    pagination_class = UserPagination

    def get_queryset(self):
        return CustomUser.objects.filter(role='user')
    
class UserListViewWorkers(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]
    pagination_class = UserPagination

    def get_queryset(self):
        return CustomUser.objects.filter(role__in=['super_admin', 'admin', 'worker'])


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]


class UserCreatedByMeListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]
    pagination_class = UserPagination

    def get_queryset(self):
        return CustomUser.objects.filter(created_by=self.request.user).filter(role='user')


# 🔹 Создать пользователя
class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]  # только авторизованные могут создавать

    def perform_create(self, serializer):
        user = serializer.save(created_by=self.request.user)
        user.set_password(user.password)
        user.save()


# 🔹 Изменить пользователя (по id)ProfileView
class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]
    
    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True  # <- вот тут самое главное
        return super().get_serializer(*args, **kwargs)


# 🔹 Удалить пользователя (по id)
class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsWorkerOrMore]

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "role": user.role
        })

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_block:
                return Response({"detail": "Ваш аккаунт заблокирован"}, status=status.HTTP_403_FORBIDDEN)
            
            # логиним пользователя в сессии Django
            auth_login(request, user)

            return Response({
                "message": "Вы успешно вошли",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                }
            })
        else:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)




# -----------------------------
# Карантин
# -----------------------------
class CarantinOn(APIView):
    permission_classes = [IsWorkerOrMore]  # поменяй при необходимости

    def get(self, request, *args, **kwargs):
        Carantin.objects.create(title=timezone.now().strftime("%H%M%S"))
        ModeLog.objects.create(action="carantin_on", user=request.user)
        return Response({"status": "ok", "action": "carantin_on"})

class CarantinOf(APIView):
    permission_classes = [IsWorkerOrMore]

    def get(self, request, *args, **kwargs):
        Carantin.objects.all().delete()
        ModeLog.objects.create(action="carantin_off", user=request.user)
        return Response({"status": "ok", "action": "carantin_off"})
    

# -----------------------------
# Ошибка 503
# -----------------------------
class ErrorOn(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, *args, **kwargs):
        ErrorSite.objects.create(title=timezone.now().strftime("%H%M%S"))
        ModeLog.objects.create(action="error_503_on", user=request.user)
        return Response({"status": "ok", "action": "error_503_on"})

class ErrorOf(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, *args, **kwargs):
        ErrorSite.objects.all().delete()
        ModeLog.objects.create(action="error_503_off", user=request.user)
        return Response({"status": "ok", "action": "error_503_off"})
    

# -----------------------------
# White-list
# -----------------------------
class WhitelistOn(APIView):
    permission_classes = [IsAdminOrMore]

    def get(self, request, *args, **kwargs):
        IPWhitelistOnOrOff.objects.create(title=timezone.now().strftime("%H%M%S"))
        ModeLog.objects.create(action="whitelist_on", user=request.user)
        return Response({"status": "ok", "action": "whitelist_off"})

class WhitelistOf(APIView):
    permission_classes = [IsAdminOrMore]

    def get(self, request, *args, **kwargs):
        IPWhitelistOnOrOff.objects.all().delete()
        ModeLog.objects.create(action="whitelist_off", user=request.user)
        return Response({"status": "ok", "action": "whitelist_on"})
    




class AddIPToWhitelist(APIView):
    permission_classes = [IsWorkerOrMore]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        user = get_object_or_404(CustomUser, id=user_id)

        if user.ip:
            created = IPWhitelist.objects.get_or_create(ip_address=user.ip)
            return Response({
            "status": "ok",
            "action": "add",
            "created": created
            })
        return Response({
            "status": "error",
            "message": "у пользователся еще нету айпи"
        })
    

class DeleteIPToWhitelist(APIView):
    permission_classes = [IsWorkerOrMore]

    def delete(self, request, *args, **kwargs):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"status": "error", "message": "Не указан user_id"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        if not user.ip:
            return Response({"status": "error", "message": "У пользователя нет IP"}, status=status.HTTP_400_BAD_REQUEST)
        

        deleted_count, _ = IPWhitelist.objects.filter(ip_address=user.ip).delete()

        if deleted_count == 0:
            return Response({"status": "error", "message": "IP не найден в whitelist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "ok",
            "action": "remove",
            "ip_address": user.ip
        }, status=status.HTTP_200_OK)
    

class UserStatsView(APIView):
    permission_classes = [IsWorkerOrMore]

    def get(self, request):
        workers_count = CustomUser.objects.filter(role__in=['super_admin', 'admin', 'worker']).count()
        users_count = CustomUser.objects.filter(role='user').count()
        created_by_me_count = CustomUser.objects.filter(created_by=request.user).filter(role='user').count()

        profile_data = {
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "last_login": request.user.last_login,  
        }

        return Response({
            "workers_count": workers_count,
            "users_count": users_count,
            "created_by_me_count": created_by_me_count,
            "profile_data":profile_data,
        })
    
class SystemStatesView(APIView):
    permission_classes = [IsWorkerOrMore]  # можно поставить IsWorkerOrMore

    def get(self, request, *args, **kwargs):
        states = {
            "carantin": Carantin.objects.exists(),
            "error_503": ErrorSite.objects.exists(),
            "whitelist": IPWhitelistOnOrOff.objects.exists(),
        }
        return Response(states)
    

class ModeLogList(APIView):
    permission_classes = [IsWorkerOrMore]
    pagination_class = UserPagination

    def get(self, request, *args, **kwargs):
        logs = ModeLog.objects.all().order_by('-created_at')[:50]  # последние 50 записей
        data = [
            {
                "date": log.created_at.strftime("%Y-%m-%d %H:%M"),
                "action": log.get_action_display(),
                "user": log.user.username if log.user else "Система"
            }
            for log in logs
        ]
        return Response(data)
    

class LinkInfo(APIView):
    permission_classes = [IsWorkerOrMore]
    def get(self, request):
        link = Link_file.objects.first()
        if link:
            return Response({"link": link.text}, status=status.HTTP_200_OK)
        return Response({"link": None}, status=status.HTTP_200_OK)
    

class LinkDelete(APIView):
    permission_classes = [IsWorkerOrMore]
    def delete(self, request):
        Link_file.objects.all().delete()
        return Response({"message": "All links deleted"}, status=status.HTTP_200_OK)
    

class LinkCreate(APIView):
    permission_classes = [IsWorkerOrMore]
    def post(self, request):
        new_link = request.data.get("link")

        Link_file.objects.all().delete()

        link = Link_file.objects.create(text=new_link)
        return Response({"message": "Link created", "link": link.text}, status=status.HTTP_201_CREATED)
    


class ResetPasswordAPIView(APIView):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        new_password = generate_password()
        user.set_password(new_password)
        user.save()
        return Response({"new_password": new_password}, status=status.HTTP_200_OK)
