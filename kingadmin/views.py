from django.shortcuts import render, redirect,HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
import json
from kingadmin import forms
from kingadmin import app_setup
app_setup.kingadmin_auto_discover()  # 程序一启动，就把所有的 kingadmin.py 中的代码加载进来

from kingadmin.sites import site  # 把 site 这个 AdminSite()的实例化对象导入进来

print("site.enalbed_admin",site.enabled_admin)
# Create your views here.

def login(request):
    error_msg = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(username=username, password=password)
        print(user)
        if user:
            auth.login(request, user)
            next_url = request.GET.get("next", "/kingadmin/")  # 如果没有 "next"，则跳转到 "/kingadmin/" 路径

            return redirect(next_url)
        else:
            error_msg = "用户名、密码错误"

    # settings 中的模板文件 TEMPLATES 中的 "DIRS" 也需要配置：把kingadmin中的 templates 路径添加到其中
    return render(request, "kingadmin/login.html",{"error_msg":error_msg})     # render()中的第二个参数路径会和settings 中TEMPLATES配置的DIRS路径进行拼接


def logout(request):
    auth.logout(request)
    return redirect("/kingadmin/login/")

# kingadmin 首页
@login_required
def app_index(request):
    enabled_admin = site.enabled_admin  # 如： {"crm":{"customerinfo":自定义类}}

    return render(request,"kingadmin/app_index.html",{"enabled_admin":enabled_admin})

@login_required
def models_of_single_app(request,app_name):
    enabled_admin = site.enabled_admin
    # print("models_of_single_app enabled_admin",enabled_admin.items())
    table_dict = enabled_admin.get(app_name)
    print("table_dict",table_dict)
    return render(request,"kingadmin/models_of_single_app.html",{"table_dict":table_dict,"app_name":app_name})


# 定义一个函数专门处理 过滤数据 (admin_class.list_filter中的字段)
def get_filter_data(request,querysets):
    filter_conditions = {}
    for key,val in request.GET.items():  # request.GET 是一个 QueryDict，其 value 是一个列表，所以不能直接 models.表名.objects.filter(**request.GET)
        if key in ["_p","_q","_o"]:continue  # _p,_q,_q对应的请求数据不添加到 filter_conditions 中

        if val: # 只有当 val 有值的时候，才把 这对 key-value 当做过滤条件添加到 filter_condition 中
            filter_conditions[key] = val

    # 通过 querysets.filter(**filter_conditions) 去过滤 要在前端展示的数据；filter_condition 也传给前端，用于过滤条件的显示
    return querysets.filter(**filter_conditions),filter_conditions

# 搜索功能
def get_search_data(request,querysets,admin_class):
    search_text = request.GET.get("_q","")
    # print("search text",search_text)
    q = Q()
    q.connector = "OR"
    if search_text:
        for search_field in admin_class.search_fields:
            q.children.append(("%s__contains"%search_field,search_text))

    return querysets.filter(q),search_text

# 排序功能
def get_sorted_data(request,querysets,admin_class):
    sorted_column = request.GET.get("_o","")
    sorted_condition = {}
    if sorted_column:
        sorted_field = admin_class.list_display[abs(int(sorted_column))] # 排序字段
        sorted_condition[sorted_field] = sorted_column  # 如：{"id":"-0"}
        if sorted_column.startswith("-"):  # "-" 开头，说明按降序排列
            sorted_field = "-%s"%sorted_field

        return querysets.order_by(sorted_field),sorted_condition  # 把排序字典也返回
    return querysets,sorted_condition

# 展示自定义Admin中的数据
@login_required
def model_obj_list(request,app_name,model_name):
    """取出指定model里的数据返回给前端"""

    admin_class = site.enabled_admin[app_name][model_name]

    # 自定义admin action
    if request.method == "POST":
        selected_action = request.POST.get("action")
        selected_ids = json.loads(request.POST.get("selected_ids"))
        # if not selected_ids:
        #     pass
        # else:
        print(selected_ids)
        querysets = admin_class.model.objects.filter(nid__in=selected_ids)
        admin_action_func = getattr(admin_class,selected_action)
        request._admin_action = selected_action  # 把 selected_action 添加到 request 中
        res = admin_action_func(request,querysets)

        return res

    querysets = admin_class.model.objects.all().order_by("-pk")  # 通过这行代码把数据表中的记录都读取出来 # admin_class.model 就是 model表 类

    # 过滤功能
    querysets,filter_conditions = get_filter_data(request,querysets)
    admin_class.filter_conditions = filter_conditions  # 把过滤条件 设置成 admin_class 的一个属性；这样在前端就能通过 admin_class 直接获取到 filter_conditions

    """ 在过滤的基础上进行以下操作  """

    # 搜索功能
    querysets,search_text = get_search_data(request,querysets,admin_class)

    # 排序功能
    querysets,sorted_condition = get_sorted_data(request,querysets,admin_class)

    # 分页器（在过滤的基础进行分页）
    paginator = Paginator(querysets,admin_class.list_per_page)
    current_page_num = request.GET.get("_p",1)
    print("request.GET.get(_p)",request.GET.get("_p"))
    if not current_page_num:
        print("kwkw ")
        current_page_num = 1
    else:
        current_page_num =int(request.GET.get("_p",1))

    try:
        querysets = paginator.page(current_page_num)  # 当前页
    except EmptyPage:
        querysets = paginator.page(1)
    except PageNotAnInteger:
        querysets = paginator.page(paginator.num_pages)

    return render(request,"kingadmin/model_obj_list.html",{"querysets":querysets,
                                                           "admin_class":admin_class,
                                                           "search_text":search_text,
                                                            "sorted_condition":sorted_condition,
                                                           "current_page_num":current_page_num,
                                                           "app_name":app_name,
                                                           "model_name":model_name
                                                           })

@login_required
def table_obj_edit(request,app_name,model_name,edit_object_id):
    admin_class = site.enabled_admin[app_name][model_name]
    admin_class.is_form_add = False # 判断是添加页面还是编辑页面的标识符
    edit_obj = admin_class.model.objects.filter(pk=edit_object_id).first()
    current_page = request.GET.get("_p",1)  # ?请求体中的数据在 request.GET 中
    # 动态生成ModelForm
    dynamic_model_form = forms.dynamic_create_model_form(admin_class)

    if request.method == "POST":
        form = dynamic_model_form(data=request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect("/kingadmin/%s/%s/?_p=%s"%(app_name,model_name,current_page))
        else:
            return render(request, "kingadmin/table_obj_edit.html", locals())
    else:
        form = dynamic_model_form(instance=edit_obj)

    return render(request,"kingadmin/table_obj_edit.html",locals())

@login_required
def table_obj_add(request,app_name,model_name):
    admin_class = site.enabled_admin[app_name][model_name]
    admin_class.is_form_add = True
    # print("is_form_add from add", admin_class.is_form_add)
    # 动态生成ModelForm
    dynamic_model_form = forms.dynamic_create_model_form(admin_class)

    if request.method == "POST":
        form = dynamic_model_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/kingadmin/%s/%s/"%(app_name,model_name))
    else:
        form = dynamic_model_form()

    return render(request,"kingadmin/table_obj_add.html",locals())


@login_required
def obj_delete(request,app_name,model_name,delete_object_id):
    admin_class = site.enabled_admin[app_name][model_name]
    delete_obj = admin_class.model.objects.filter(pk=delete_object_id)

    if request.method == "POST":
        delete_obj.delete()
        return redirect("/kingadmin/%s/%s/"%(app_name,model_name))

    return render(request,"kingadmin/obj_delete.html",{"app_name":app_name,
                                                       "model_name":model_name,
                                                       "delete_object_id":delete_object_id,
                                                       "delete_objs":delete_obj,
                                                       "site":site})
