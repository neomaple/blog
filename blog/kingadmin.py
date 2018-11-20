from kingadmin import sites
from kingadmin.base_admin import BaseKingAdmin
# from blog import models
from blog.models import *


print("kingadmin.py in blog")

# class UserInfoConfig(BaseKingAdmin):
#     list_display = ['name',]

sites.site.register(UserInfo)
sites.site.register(Blog)