from django import template
from django.utils.safestring import mark_safe
import datetime

register = template.Library()

@register.simple_tag
def build_table_row(row_obj,admin_class,current_page_num):
    """生成一条记录的 html element"""
    # 返回 自定义Admin list_display 展示的 <tbody> 的一整行 <tr>
    ele = ""
    if admin_class.list_display: # list_display中有值，展示其中的字段
        for index,column in enumerate(admin_class.list_display):
            # 判断 字段对象的 choices 属性是否为一个空列表，如果不是空列表，说明这个字段含有 choices
            field_obj = admin_class.model._meta.get_field(column)
            if field_obj.choices:  # 该字段有 choices
                filter_data = getattr(row_obj,"get_%s_display"%column)()  # 对象记录.get_有choices的字段名_display()：获取 choices 对应的值；getattr(row_obj,"get_%s_display"%filter_column) 得到的是一个方法（绑定关系），所以需要后面加上 ()
            else:
                filter_data = getattr(row_obj,column)

            if index == 0:
                ele += "<td><a href='%s/change/?_p=%s'>%s</a></td>" % (row_obj.pk,current_page_num,filter_data)
            else:
                ele += "<td>%s</td>" % filter_data
    else: # list_display中没值，展示表的 __str__
        ele += "<td><a href='%s/change/?_p=%s'>%s</a></td>"%(row_obj.pk,current_page_num,row_obj)

    return mark_safe(ele)

# 过滤功能：在前端的展示
@register.simple_tag
def build_filter_ele(admin_class):
    element = ""

    # 由于 时间类型 没有 get_choices() 方法,需要自己处理 时间数据;还是按照 get_choices() 方法做一个列表套元组的数据
    datetime_obj = datetime.datetime.now()  # 获取当前时间对象
    date_list = [
        ("","-----"),
        (datetime_obj.strftime("%Y-%m-%d"),"Today"),
        # 直接让 datetime对象变成 "YYYY-MM-DD" 的形式
        ((datetime_obj - datetime.timedelta(7)).strftime("%Y-%m-%d"),"7天内"),
        ((datetime_obj.replace(day=1)).strftime("%Y-%m-%d"),"这个月"),
        ((datetime_obj - datetime.timedelta(90)).strftime("%Y-%m-%d"),"3个月内"),
        ((datetime_obj.replace(month=1,day=1)).strftime("%Y-%m-%d"),"ThisYear"),
        ("","AnyDate")
    ]

    for filter_column in admin_class.list_filter: # 循环过滤字段
        field_obj = admin_class.model._meta.get_field(filter_column)  # 获取该字段对象

        options = ""
        filter_conditions = admin_class.filter_conditions

        # 该 字段对象.choices 不为空，说明其 有 choices 或者是 外键字段
        try:
            """
            # 外键字段对象和含有choices的字段对象都有一个方法：.get_choices()，能获取到该字段对应的所有选项（列表套元组的形式），并且会多出一个未选项的元组；调用者：字段对象
            """
            for choice in field_obj.get_choices():  # 循环字段对应的<option>；字段对象.choices：获取到该字段对象对应 的所有选项（列表中套元组的形式）
                """
                先判断过滤字段 filter_column 是否在 filter_conditions 里面；如果在，则需要判断是哪个 <option> 被选中
                """
                selected = ""  # 用于 设置 <option> 的 selected 属性
                if filter_column in filter_conditions: # 过滤字段 filter_column 在 filter_conditions 中
                    # 判断哪个<option> 被选中
                    if str(choice[0]) == filter_conditions.get(filter_column): # filter_conditions.get(filter_column) 是字符串的格式，需要把 选项中的choice[0] 变成字符串
                        selected = "selected"

                options += "<option value='%s' %s>%s</option>"%(choice[0],selected,choice[1])
            element += "<select name='%s' class='form-control'>%s</select>"%(filter_column,options)

        except AttributeError as e:  # 当字段对象没有 get_choices() 方法时（即不是含有choices的字段或者外键字段），需要捕捉到这个异常，并单独处理
            if field_obj.get_internal_type() in ["DateField","DateTimeField"]:  # 获取字段类型： 字段对象.get_internal_type()   # 返回结果为：CharField、DateField 等
                for i in date_list:
                    selected = ""
                    if "%s__gte"%filter_column in filter_conditions:  # 由于 "date" 字段在 <select>的 name 属性中添加了 "__gte"（即 filter_condition中的 "date__gte"）
                        if i[0] == filter_conditions.get("%s__gte"%filter_column):
                            selected = "selected"
                    options += "<option value='%s' %s>%s</option>" % (i[0],selected,i[1])
                element += "<select name='%s__gte' class='form-control'>%s</select>" % (filter_column, options)  # 当是 date 字段时， name属性值 直接设置为 "date__gte"：表示 __gte大于等于

    return mark_safe(element)

# 获取表名：（list_display 为空时）
@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.model_name.title()

# 分页器
@register.simple_tag
def build_paginator(querysets,filter_conditions,search_text,sorted_condition):
    filters = ""
    for k,v in filter_conditions.items(): # 把 过滤条件 添加到分页器的 <a> 标签中
        filters += "&%s=%s"%(k,v)
    sort = ""
    for k,v in sorted_condition.items(): # 把 排序条件 添加到分页器的 <a> 标签中
        sort += "&_o=%s"%v

    ele = ""
    page_range = querysets.paginator.page_range
    current_page_num = querysets.number  # 某一页的page.number ：表示当前的页码数
    max_page_num = querysets.paginator.num_pages
    if max_page_num > 5: # 总页数大于5时，只显示5个；小于等于5页时，就全部显示出来
        if current_page_num - 2 < 1:
            page_range = range(1,6)
        elif current_page_num + 2 > max_page_num:
            page_range = range(max_page_num-4,max_page_num+1)
        else:
            page_range = range(current_page_num-2,current_page_num+3)

    for page_num in page_range:
        li_class = ""
        if page_num == current_page_num:
            li_class = "active"
        ele += '<li class="%s"><a href="?_p=%s%s&_q=%s&_o=%s">%s</a></li>'%(li_class,page_num,filters,search_text,sort,page_num)  # 过滤条件和搜索内容也要添加到 <a>的href中

    return mark_safe(ele)

# 排序<a>标签的排序请求数据
@register.simple_tag
def create_sorted_column_arg(column,sorted_condition,loop_num):
    if column in sorted_condition:  # 该字段被排序了
        last_sorted_column = sorted_condition[column]
        if last_sorted_column.startswith("-"):
            this_sorted_column = last_sorted_column.strip("-")  # 上次有"-" 这次就把"-"去掉
        else: # 反之则加上"-"
            this_sorted_column = "-%s"%last_sorted_column
        return this_sorted_column
    else:
        return loop_num

# # 排序<a>标签的过滤、搜索请求数据
@register.simple_tag
def render_filter_sort_args(filter_conditions,search_text):
    filters = ""
    search = ""

    if filter_conditions:
        for k,v in filter_conditions.items():
            filters += "&%s=%s" % (k,v)
    if search_text:
        search += "&_q=%s"%search_text
    return filters+search

# 排序箭头
@register.simple_tag
def render_sort_arrow(column,sorted_condition):
    if column in sorted_condition:
        last_sorted_column = sorted_condition[column]
        if last_sorted_column.startswith("-"):
            arrow_direction = "down"
        else:
            arrow_direction = "up"
        ele = "<span class='glyphicon glyphicon-menu-%s'></span>"%arrow_direction
        return mark_safe(ele)
    else:
        return ""

# 上一页、下一页
@register.simple_tag
def next_previous_page_btn(querysets,choice,filter_conditions,search_text,sorted_condition):
    filters = ""
    search = ""
    sort = ""
    if sorted_condition:
        for k, v in sorted_condition.items():  # 把 排序条件 添加到分页器的 <a> 标签中
            sort += "&_o=%s" % v

    if filter_conditions:
        for k, v in filter_conditions.items():
            filters += "&%s=%s" % (k, v)
    if search_text:
        search += "&_q=%s" % search_text

    next_page = ""

    if choice == "next":
        next_page = str(querysets.next_page_number())
    elif choice == "previous":
        next_page = str(querysets.previous_page_number())

    return next_page+filters+search+sort

@register.simple_tag
def get_all_m2m_data(admin_class,form_obj,field_name):
    """获取 filter_horizontal 字段的所有选项数据"""
    field_obj = admin_class.model._meta.get_field(field_name)
    all_data = set(field_obj.related_model.objects.all())

    try:  # 也可用: if form_obj.instance.id:
        selected_data = set(getattr(form_obj.instance, field_name).all())  # 两个都变成集合的形式
    except TypeError:
        selected_data = set()

    return all_data - selected_data # 取差集过滤

@register.simple_tag
def get_selected_m2m_data(form_obj,field_name):
    """获取已选的所有选项数据"""
    try:
        selected_data = getattr(form_obj.instance,field_name).all()  # 先获取到 form_obj的实例对象；getattr(form_obj.instance,field_name).all() 能获取到 form_obj对应实例的该字段所对应的所有选项
    except TypeError:
        selected_data = []

    return selected_data

@register.simple_tag
def display_all_related_objs(obj,site,app_name):
    """
    反向多对多时，只显示第一层的记录；
    反向多对一时，要利用递归显示所有的相关记录
    :param obj:
    :param site:
    :param app_name:
    :return:
    """

    print("site",site)

    model_dict = site.enabled_admin[app_name]  # 用于判断某个表是否 register；register过的表的对象记录才有对应的 <a> 标签
    ele = "<ul>"

    print("obj",obj)
    for reversed_fk_model in obj._meta.related_objects:
        reversed_fk_model_name = reversed_fk_model.name  # 获取反向关联表的表名
        reversed_fk_lookup = "%s_set" % reversed_fk_model_name
        related_reversed_objs = getattr(obj,reversed_fk_lookup).all()   # 获取该记录对象所有反向关联的对象记录
        ele += "<li>%s 中的相关记录有：<ul>"% (reversed_fk_model_name)

        # 判断是多对多还是一对多反向关联；如果是多对多，则不需要再深入查找
        if reversed_fk_model.get_internal_type() == "ManyToManyField":  # 多对多不需要深入查询
            for i in related_reversed_objs:
                if i._meta.model_name in model_dict:
                    ele += "<li><a href='/kingadmin/%s/%s/%s/change'>%s</a> 记录里与[%s]相关的数据也将被删除</li>" % (i._meta.app_label,i._meta.model_name,i.pk,i,obj)
                else:
                    ele += "<li>%s 记录里与[%s]相关的数据也将被删除</li>" % (i, obj)
        else:
            for i in related_reversed_objs:
                if i._meta.model_name in model_dict:
                    ele += "<li><a href='/kingadmin/%s/%s/%s/change'>%s</a> 记录里与[%s]相关的数据也将被删除</li>" % (i._meta.app_label, i._meta.model_name, i.pk, i, obj)
                else:
                    ele += "<li>%s 记录里与[%s]相关的数据也将被删除</li>" % ( i, obj)
                ele += display_all_related_objs(i,site,i._meta.app_label)  # 递归查询所有相关的记录
        ele += "</ul></li>"
    ele += "</ul>"

    return ele
