from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import *

admin.site.register(CustomUser, BaseUserAdmin)