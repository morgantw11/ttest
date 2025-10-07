from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Главный админ'),
        ('admin', 'Админ'),
        ('worker', 'Воркер'),
        ('user', 'Обычный пользователь'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    big_text = models.CharField(max_length=100, blank=True, null=True)
    norm_text = models.CharField(max_length=300, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    file_name = models.CharField(max_length=100, blank=True, null=True)
    is_block = models.BooleanField(default=False)
    emeil_sends = models.IntegerField(default=0)
    telegram_group_id = models.BigIntegerField(null=True, blank=True)  
    
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users"  
    )
    def is_admin(self):
        return self.role == 'admin'

    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_worker(self):
        return self.role == 'worker'



class MagicLinkToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used 

    def __str__(self):
        return f"{self.user} | {self.token}"


class IPWhitelist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    def __str__(self):
        return self.ip_address


class ErrorSite(models.Model):
    title = models.CharField(max_length=5)

    def __str__(self):
        return self.title
    
class Carantin(models.Model):
    title = models.CharField(max_length=5)

    def __str__(self):
        return self.title
    
class IPWhitelistOnOrOff(models.Model):
    title = models.CharField(max_length=5)

    def __str__(self):
        return self.title
    


class ModeLog(models.Model):
    ACTION_CHOICES = [
        ("carantin_on", "Карантин включен"),
        ("carantin_off", "Карантин выключен"),
        ("error_503_on", "Ошибка 503 включена"),
        ("error_503_off", "Ошибка 503 выключена"),
        ("whitelist_on", "Белый список включен"),
        ("whitelist_off", "Белый список выключен"),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.get_action_display()} ({self.user})"
    



class Link_file(models.Model):
    text = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.text}"