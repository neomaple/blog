"""CRMsystem URL Configuration

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
# from django.contrib import admin
from django.urls import path,re_path,include

from kingadmin import views

urlpatterns = [
    re_path(r"^$",views.app_index,name="app_index"),
    re_path(r"^(\w+)/$",views.models_of_single_app,name="models_of_single_app"),
    re_path(r"^(\w+)/(\w+)/$",views.model_obj_list,name="model_obj_list"),
    re_path(r"^(\w+)/(\w+)/(\d+)/change/$",views.table_obj_edit,name="table_obj_edit"),
    re_path(r"^(\w+)/(\w+)/add/$",views.table_obj_add,name="table_obj_add"),
    re_path(r"^(\w+)/(\w+)/(\d+)/delete/$",views.obj_delete,name="obj_delete"),
    path(r"login/",views.login),
    path(r"logout/",views.logout),
]
