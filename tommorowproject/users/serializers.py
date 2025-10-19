from rest_framework import serializers
from .models import CustomUser,MagicLinkToken
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "email", "role", "big_text",
            "norm_text", "date_create", "ip", "device",
            "file_name", "is_block", "emeil_sends", "created_by","password","telegram_group_id","last_login"
        ]
        read_only_fields = ["id", "date_create","created_by"] 


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)



class MagicLinkTokenSerializer(serializers.ModelSerializer):
    magic_link = serializers.SerializerMethodField()

    class Meta:
        model = MagicLinkToken
        fields = ['token', 'magic_link', 'used']

    def get_magic_link(self, obj):
        request = self.context.get("request")
        base_url = os.getenv("BOT_TOKEN")
        # строим полный URL для магической ссылки
        return base_url(f"{base_url}/magic-login/{obj.token}/")