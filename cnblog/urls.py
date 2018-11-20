"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include

from blog import views

# 配置MEDIA_URL
from django.views.static import serve
from cnblog import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^kingadmin/",include("kingadmin.urls")),
    path(r"login/",views.login),
    path(r"get_validCode_img/",views.get_validCode_img),
    path(r"index/",views.index),
    # IP+端口的根目录也是 index
    re_path(r"^$",views.index),
    path(r"register/",views.register),
    path(r"logout/",views.logout),
    # 输入框文件上传路径
    path(r"upload/",views.upload),
    # 点赞
    path(r"digg/",views.digg),
    # 评论
    path(r"comment/",views.comment),
    path(r"get_comment_tree/",views.get_comment_tree),

    # 后台管理url
    re_path("cn_backend/$",views.cn_backend),
    re_path("cn_backend/add_article/$",views.add_article),
    re_path(r"article/(\d+)/edit/$",views.edit_article),
    re_path("article/(\d+)/delete/$",views.delete_article),

    # 配置MEDIA_URL
    re_path(r"media/(?P<path>.*)/$",serve,{"document_root":settings.MEDIA_ROOT}),

    # 个人站点的url
    re_path(r"^(?P<username>\w+)/$",views.home_site),
    # 个人站点页面的跳转
    re_path(r"^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/$",views.home_site),

    # 文章详情页
    re_path(r"(?P<username>\w+)/articles/(?P<article_id>\d+)/$",views.article_detail)

]
