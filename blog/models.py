from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):  # 通过继承AbstractUser，就能实现往 django 自带的 auth_user表中添加字段的功能；因为User类也是继承的AbstractUser
    "用户信息"
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    # 下面的 default 的路径有疑问 ？？？
    avatar = models.FileField(upload_to="avatars/", default="/avatars/default.png")  # avatar 这个字段不传的时候（avatar字段为空时，也是上传了 avatar字段），才会使用 default 的默认值
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)  # auto_now_add=True表示默认取当前时间

    blog = models.OneToOneField(to="Blog", to_field="nid", null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    "博客信息表（站点表）"
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="个人博客标题", max_length=64)
    site_name = models.CharField(verbose_name="站点名称", max_length=64)
    theme = models.CharField(verbose_name="博客主题", max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    "博主个人文章分类表（和Blog表是一对多关系，所以和UserInfo表也是一对多关系）"
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="分类标题", max_length=32)
    blog = models.ForeignKey(verbose_name="所属博客", to="Blog", to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    "博客标签"
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="标签名称", max_length=32)
    blog = models.ForeignKey(verbose_name="所属博客", to="Blog", to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    "文章表"
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name="文章标题")
    desc = models.CharField(max_length=255, verbose_name="文章描述")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    # 上面三个 count 是为了减少统计评论数等时的跨表查询（添加评论等时即让对应count自加1）

    user = models.ForeignKey(verbose_name="作者", to="UserInfo", to_field="nid",on_delete=models.CASCADE)
    category = models.ForeignKey(to="Category", to_field="nid", null=True,on_delete=models.CASCADE)
    tags = models.ManyToManyField(
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag")
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name="文章", to="Article", to_field="nid",on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name="标签", to="Tag", to_field="nid",on_delete=models.CASCADE)

    class Meta(object):  # 表示联合唯一
        unique_together = [
            ("article", "tag"),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


class ArticleUpDown(models.Model):
    "点赞表"
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey("UserInfo", null=True,on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True,on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ("article", "user"),
        ]


class Comment(models.Model):
    "评论表（哪个用户在哪个时间对哪篇文章做了什么评论）"

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name="评论者", to="UserInfo", to_field="nid",on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name="评论文章", to="Article", to_field="nid",on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    content = models.CharField(verbose_name="评论内容", max_length=255)

    parent_comment = models.ForeignKey("self",null=True,on_delete=models.CASCADE)  # 用这行代码去构建评论树； # ForeignKey("self")表示自关联（自己关联自己；等同于：ForeignKey("Comment")）

    def __str__(self):
        return self.content

    # 根评论：对文章的评论
    # 子评论：对评论的评论
