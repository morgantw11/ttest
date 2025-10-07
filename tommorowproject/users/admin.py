from django.contrib import admin
from .models import CustomUser, IPWhitelist,MagicLinkToken


admin.site.register(CustomUser)

admin.site.register(IPWhitelist)
admin.site.register(MagicLinkToken)