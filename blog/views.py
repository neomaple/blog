from django.shortcuts import render,HttpResponse,redirect
from django.db.models import Count
from bs4 import BeautifulSoup
import os
from django.http import JsonResponse
import json
from django.db.models import F
from django.db import transaction
# JsonResponse 能直接返回Json格式的字符串
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from blog.models import *
from cnblog import settings

# Create your views here.
# 基于用户认证组件和Ajax实现登陆验证（图片验证码）
def login(request):

    if request.method == "POST":

        response = {"user":None,"msg":None}

        user = request.POST.get("user")
        psw = request.POST.get("psw")
        valid_code = request.POST.get("valid_code")

        valid_code_str = request.session.get("valid_code_str")  # 获取储存到 session 中的验证码

        if valid_code.upper() == valid_code_str.upper():
            user_obj = auth.authenticate(username=user,password=psw)
            if user_obj:
                # 此处是Ajax的POST请求；Ajax的POST时返回的不能是 render 或者 redirect（返回这两个没有意义），通常返回的是一个字典（如：HttpResponse）；# Ajax POST请求时，只需要返回给前端一个结果让前端知道后端发生了什么就行
                auth.login(request,user_obj)  # 注册session
                print("request.user测试",request.user)  # auth.login(request,user_obj)，不管是用什么变量注册的，取这个全局变量时，都是利用 request.user
                response["user"] = user_obj.username
            else:
                response["msg"] = "用户名密码错误！"
        else:
            response["msg"] = "验证码错误！"

        # 利用JsonResponse返回数据时，前端的Jquery会自动把该数据解析成相应的数据类型
        return JsonResponse(response)

    return render(request,"login.html")

def get_validCode_img(request):

    from blog.utils.validCode import get_valid_code_img
    data = get_valid_code_img(request)

    return HttpResponse(data)

"""
登陆验证功能总结：
1. 一次请求会伴随着多次请求（加载静态文件）
2. PIL模块
3. session的存储（验证码要存到session中）
4. 验证码刷新（ .src+="?" ）
"""


def index(request):

    article_list = Article.objects.all() # 获取所有的文章对象列表

    return render(request,"index.html",{"article_list":article_list})


from blog.utils.myForms import UserForm  # 实际项目中，所有导入的文件要统一一起放到最上面
# 基于form组件和Ajax实现注册功能
def register(request):
    # 判断请求是否为Ajax请求
    if request.is_ajax():
        print(request.POST)
        print(request.FILES)

        form = UserForm(request.POST)

        # Ajax的请求通常需要返回一个字典，用于告诉前端发生了什么事
        response = {"user":None,"msg":None}

        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")

            # 生成一条用户记录
            # 不要用 create() 创建创建记录，因为这个create 出来的记录是明文的 密码；应该用 create_user() 或者 create_superuser()； 这两种方法能将 password 变成 密文；返回值是插入的这条记录对象
            # 在 form.cleaned_data 里面获取 user,psw,email; request.FILES中获取文件
            user = form.cleaned_data.get("user")
            print("user",user)
            psw = form.cleaned_data.get("psw")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            # /static/ 中放的是服务器自己的文件；/media/放的是用户上传的文件
            """
            if avatar_obj:  # avatar_obj 不为空，说明用户上传了头像；此时需要把 avatar_obj传给 avatar 字段
                user_obj = UserInfo.objects.create_user(username=user,password=psw,email=email,avatar=avatar_obj)
            else: # avatar_obj 为空，说明用户没上传头像；此时就不要 写 avatar 字段，这样创建记录时 avatar 字段才会使用 default；注意：avatar字段 上传为空 和 不上传 是不一样的，只有不上传（创建记录时不给 avatar 字段传值）
                user_obj = UserInfo.objects.create_user(username=user, password=psw, email=email)
            """
            # 上面的两行代码可做如下优化：
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
            UserInfo.objects.create_user(username=user,password=psw,email=email,**extra)
            # 先定义一个空字典，如果 avatar_obj 有值，就把 avatar_obj 传到这个字典中，再把这个字典放入 create_user()中；由于 extra是一个字典，所以需要加上 **

            """
            一旦在settings.py中配置了 media 文件（"media"是project中的一个文件夹名，可放在project下，也可放在 app 下）：
		        MEDIA_ROOT = os.path.join(BASE_DIR,"media")
	        Django会自动实现如下功能：
		        FileField字段（如UserInfo表中）和ImageField字段，Django会将所有文件对象下载到MEDIA_ROOT中的 avatars（因为UserInfo表中是：upload_to="avatars/"）文件夹中（如果MEDIA_ROOT中没有 avatars 这个文件夹，Django会自动创建 ）；user_obj的avatar存的是文件的相对路径
            """

        else:
            print(form.cleaned_data)
            print(form.errors)

            response["msg"] = form.errors
        return JsonResponse(response)

    form = UserForm()
    return render(request,"register.html",{"form":form})

def logout(request):
    auth.logout(request)  # 作用等同于： request.session.flush()；# 会把 django_session 表中 相应的记录删除

    return redirect("/login/")

from django.db.models.functions import TruncMonth
# 个人站点视图函数
def home_site(request,username,**kwargs):
    print("username",username)
    # UserInfo.objects.filter(username=username).exists()：也可以用 .exists() 判断是否存在
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,"not_found.html")


    #  查询当前站点对象
    # blog = user.blog

    # 当前用户或者当前站点对应的所有文章全部读取出来
    # 方式一：基于对象查询
    # article_list = user.article_set.all()
    # 方式二：基于双下划线
    article_list = Article.objects.filter(user=user)


    # kwargs 用于区分访问的是站点页面还是站点下的跳转页面
    if kwargs: # 跳转页面
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        # 跳转页面时，只有 article_list 发生了变化，其它的参数没有变
        if condition == "archive": # 如： param = "2018-05"
            year,month = param.split("-")
            article_list = article_list.filter(create_time__year=year,create_time__month=month)
        elif condition == "category":
            article_list = article_list.filter(category__title=param)
        else:
            article_list = article_list.filter(tags__title=param)


    # 利用 inclusion_tag 时，数据无需在此处读取
    """
    # 语法：“每一个”后的表模型.objects.values("pk").annotate(聚合函数(关联表__统计字段)).values("表模型的所有字段")
    # 查询每一个分类名称以及对应的文章数
    ret = Category.objects.values("pk").annotate(c=Count("article__title")).values("title","c")
    print(ret)
    
    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values("title","c")
    print(cate_list)
    
    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title","c")
    print(tag_list)
    
    # 查询当前站点每一个年月的名称以及对应的文章数
    # 方式一：通过 extra() 函数 和 date_format 构建出了 "年-月"字段
    date_list = Article.objects.filter(user=user).extra(select={"y_m_date":"date_format(create_time,'%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values("y_m_date","c")  # annotate()之前要先 .values()
    print(date_list)
    
    # 方式二：利用 TruncMonth
    # ret = Article.objects.filter(user=user).annotate(month=TruncMonth('create_time')).values("month").annotate(c=Count("nid")).values("month","c")
    # print(ret)
    
    return render(request,"home_site.html",locals())
    """

    return render(request, "home_site.html", {"username": username, "article_list": article_list})

"""
# 由于 article_detail() 和 home_site() 函数都需要读取 标签、分类和日期归档的数据，我们把其定义为一个函数
def get_classification_data(username):

    user = UserInfo.objects.filter(username=username).first()

    #  查询当前站点对象
    blog = user.blog

    # ret = Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")

    cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values("title", "c")

    tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")

    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time,'%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values(
        "y_m_date", "c")  # annotate()之前要先 .values()
    return {"blog":blog,"cate_list":cate_list,"tag_list":tag_list,"date_list":date_list}
"""

def article_detail(request,username,article_id):

    # 也需要先把 标签、分类、日期归档的数据读取出来
    # 方式一：
    # content = get_classification_data(username)

    # 方式二：利用 inclusion_tag ：inclusion_tag能把数据和样式结合成一个标签函数，通过 inclusion_tag 能够获取到一整套的 html 数据（数据和样式结合成一个整体）

    # 渲染文章详情
    # 获取文章数据
    article_obj = Article.objects.filter(pk=article_id).first()
    print(article_obj)

    # render渲染根评论
    comment_list = Comment.objects.filter(article_id=article_id).all()  # 这篇文章的所有评论

    return render(request,"article_detail.html",{"username":username,"article_obj":article_obj,"comment_list":comment_list})


def digg(request):

    # urlencoded 编码格式传到后端的数据类型是 字符串 格式化的
    is_up = json.loads(request.POST.get("is_up"))  # 所以 request.POST.get("is_up") 是字符串格式（值为字符串"true" 或 字符串"false"）；所以需要用 json.loads() 反序列化
    article_id = request.POST.get("article_id")
    user_id = request.user.pk   # 点赞人即当前登陆人；从session中获取

    # 先判断该用户是否已经对这篇文章做过点赞或者反对的操作
    is_handled = ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    response = {"state":True}  # Ajax通常返回字典
    if not is_handled:
        # 在点赞表中生成记录
        ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)

        # 在ArticleUpDown表生成一条赞（踩）记录，就应该对应把 Article表中的 up_count(down_count)字段加1
        queryset = Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count")+1)  # QuerySet 调用 update()
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = is_handled.is_up  # 告诉前端 该用户已经对这篇文章做过什么操作（“点赞”、“反对”）

    return JsonResponse(response)

def comment(request):
    print(request.POST)


    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk

    with transaction.atomic():  # with transaction.atomic() 里面的内容就会变成同一个事务：同成功或同失败
        # 生成一条评论记录(ajax)
        comment_obj = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        # 数据同步： Article表中的 comment_count 字段要加1
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    # 利用ajax渲染刚刚提交的那条根评论
    response = {}
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")    # create_time是datetime.datetime 类型的对象，对象不能序列化，所以先要将其利用 strftime 转化为 字符串；%X表示 时间（time）格式
    response["username"] = request.user.username
    response["content"] = content

    # 如果该评论为子评论，需要把父评论的信息也返回给客户端
    if pid:
        parent_obj = Comment.objects.filter(pk=pid).first()  # 过滤出主键值等于 pid 的Comment对象即为其父评论
        response["parent_username"] = parent_obj.user.username
        response["parent_content"] = parent_obj.content
        print("parent_obj",parent_obj)
        print("response",response)

    # 发送邮件
    from django.core.mail import send_mail
    from cnblog import settings

    article_obj = Article.objects.filter(pk=article_id).first()

    """
    #语法： send_mail(subject, message, from_email, recipient_list)
    
    send_mail(
        "您的文章《%s》新增了一条评论内容"%article_obj.title,
        content,
        settings.EMAIL_HOST_USER,
        ["380544011@qq.com"]  # 此处的邮箱应该为用户的邮箱
    )  
    # 这样方式的缺点：运行速度太慢；应该用多线程
    """
    from threading import Thread
    t = Thread(target=send_mail,args=("您的文章《%s》新增了一条评论内容"%article_obj.title,content,settings.EMAIL_HOST_USER,["380544011@qq.com"]))
    t.start()


    return JsonResponse(response)

def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    ret = list(Comment.objects.filter(article_id=article_id).order_by("pk").values("pk","content","parent_comment_id"))  # Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id") 是一个QuerySet（类似于[{},{},{}..] ），但其毕竟不是列表，所以需要用 list()方法将其强转为一个列表
    # 子评论一定在与其关联的父评论之后

    # 当用JsonResponse() 返回一个 非字典 的数据类型时， 要将 safe=False，要不然会报错
    return JsonResponse(ret,safe=False)


# 后台管理
@login_required
def cn_backend(request):
    article_list = Article.objects.filter(user=request.user)

    return render(request,"backend/backend.html", locals())

@login_required
def add_article(request):

    if request.method == "POST":
        title = request.POST.get("article_title")
        content = request.POST.get("article_content")
        soup = BeautifulSoup(content, "html.parser")
        # 过滤出去 <script> 标签
        for tag in soup.find_all():
            if tag.name == "script":  # tag.name 表示 标签名（字符串格式）
                tag.decompose()  # 从 soup 中把 该标签 删除
        # 截取文章摘要
        desc = "%s..." % soup.text[0:100]

        Article.objects.create(title=title,desc=desc,content=str(soup),user=request.user)  # str(soup) ：过滤出<script>标签后的标签字符串

        return redirect("/cn_backend/")

    return render(request,"backend/add_article.html",locals())

# 后台编辑文章

def edit_article(request,edit_article_id):
    edit_article_obj = Article.objects.filter(pk=edit_article_id).first()
    if request.method == "POST":
        title = request.POST.get("article_title")
        content = request.POST.get("article_content")
        soup = BeautifulSoup(content, "html.parser")
        # 过滤出去 <script> 标签
        for tag in soup.find_all():
            if tag.name == "script":  # tag.name 表示 标签名（字符串格式）
                tag.decompose()  # 从 soup 中把 该标签 删除
        # 截取文章摘要
        desc = "%s..." % soup.text[0:100]

        Article.objects.filter(pk=edit_article_id).update(title=title,desc=desc,content=str(soup))

        return redirect("/cn_backend/")

    return render(request,"backend/edit_article.html",{"edit_article_obj":edit_article_obj})

# 后台删除文章
def delete_article(request,delete_article_id):
    Article.objects.filter(pk=delete_article_id).delete()
    return redirect("/cn_backend/")

# 输入框文件上传路径
def upload(request):
    print(request.FILES)

    # 下载文件
    img = request.FILES.get("upload_img")
    print(img.name)  # 文件对象都有一个 name 属性， img.name 表示 文件对象的文件名
    path = os.path.join(settings.MEDIA_ROOT,"add_article_img",img.name)  # 文件的绝对路径

    with open(path,"wb") as f:
        for line in img:
            f.write(line)

    # 在前端的输入框中显示上传的文件
    # 下载完成后需要把文件对应的路径（得是json格式的数据）交给前端的文本编辑器
    response = {
        "error":0,
        "url": "/media/add_article_img/%s/"%img.name      # "url"表示前端能够用来预览该文件（如图片）的路径；不是上面的 path 路径，path路径是文件存储的绝对路径，这个路径发给前端没有任何意义
    }

    # import json
    # return HttpResponse(json.dumps(response))
    return JsonResponse(response)