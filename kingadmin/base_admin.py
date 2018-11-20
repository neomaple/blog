"""
定义 AdminSite 和 自定义 admin类 的基类
好处：
    1. 如果 自定义admin类 为空，就让 自定义admin类为 这个基类，此时 admin_class.model = model_class 就不会报错
    2. 便于统一给 自定义的admin类 添加功能，便于扩展：扩展的功能添加到 这个基类中，所有的自定义admin类都会有这个功能
"""

from django.shortcuts import render,HttpResponse,redirect
from kingadmin import sites
import json

class BaseKingAdmin(object):
    # 设置为空列表；如果 自定义Admin（admin_class）为 BaseKingAdmin时， admin_class.list_display 等也不会报错

    # 默认的action 写在 BaseKingAdmin 中；同时在 BaseKingAdmin 定义 __init__ 方法，由于 其子类没有 __init__，所以子类实例化的时候会调用 BaseKingAdmin 的 __init__
    def __init__(self):
        if self.default_action[0] not in self.actions:
            self.actions.extend(self.default_action)  # 通过这种方式能够同时保留 子类和基类的 actions

    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 10
    filter_horizontal = []

    readonly_fields = []

    default_action = ["delete_selected_options",]
    actions = []

    def delete_selected_options(self,request,queryset):
        print("通过delete")
        print(request,queryset)
        print(request.path)
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        selected_ids = json.dumps([str(i.pk) for i in queryset])
        print(selected_ids)

        if request.method == "POST":
            print("经过post了")
            if request.POST.get("delete_confirm") == "yes":
                queryset.delete()
                return redirect("/kingadmin/{app_name}/{model_name}/".format(app_name=app_name,model_name=model_name))

        return render(request,"kingadmin/obj_delete.html",{"site":sites.site,
                                                           "action":request._admin_action,
                                                           "selected_ids":selected_ids,
                                                           "app_name":app_name,
                                                           "model_name":model_name,
                                                           "delete_objs":queryset})