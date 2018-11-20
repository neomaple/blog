from django import template
from django.db.models import Count
from blog.models import *

register = template.Library()

@register.inclusion_tag("classification.html")  # inclusion_tag()中的参数表示所要引入的一套模板文件
def get_classification_data(username):  # get_classification_data() 这个方法一旦被调用，它会先执行下面的数据查询，查询完之后会把下面的字典返回 "classification.html" 这个模板文件（没有返回给调用者），因为 "classification.html" 文件会需要下面的这几个变量；下面的变量传给 "classification.html"之后会进行 render 渲染，渲染成一堆完整的 html标签
    user = UserInfo.objects.filter(username=username).first()

    #  查询当前站点对象
    blog = user.blog

    cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values("title", "c")

    tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")

    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time,'%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values(
        "y_m_date", "c")  # annotate()之前要先 .values()
    return {"username":username,"blog": blog, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}