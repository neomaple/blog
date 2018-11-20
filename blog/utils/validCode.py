from random import randint
import random
def get_random_color():  # 用于随机生成颜色
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def get_valid_code_img(request):

    """
    # 方式二：通过磁盘（open就是操作磁盘）
    # 动态生成一张图片（pip install pillow：先下载安装pillow模块）

    from PIL import Image
    img = Image.new("RGB",(260,33),color=get_random_color())  # new()里面有三个参数：第一个表示模式（RGB表示彩色），第二个表示图片宽高（需要和css中设置的宽高一致），第三个表示背景颜色 # 得到一个Image对象img
    # 把随机生成的 img 对象存到一个文件中
    with open("validCode.png","wb") as f:
        img.save(f,"png")  # 把 img 以 png的格式存到 f 文件中

    # 把动态生成的图片发送给客户端
    with open("validCode.png","rb") as f:
        data = f.read()
    """
    """
    # 方式三：通过内存
    from io import BytesIO
    # BytesIO是内存管理工具
    from PIL import Image
    img = Image.new("RGB", (260, 33), color=get_random_color())
    # 内存处理
    f = BytesIO()  # f就是一个内存句柄
    img.save(f,"png")  # 把img保存到内存句柄中；# save()之后就能把img保存到内存中
    data = f.getvalue()  # 把保存到内存中的数据读取出来
    # BytesIO会有一个自动清除内存的操作
    """
    # 方式四：给生成的图片（画板）中添加文字
    from io import BytesIO
    # BytesIO是内存管理工具
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (260, 33), color=get_random_color())  # new()里面有三个参数：第一个表示模式（RGB表示彩色），第二个表示图片宽高（需要和css中设置的宽高一致），第三个表示背景颜色 # 得到一个Image对象img
    # 往画板中添加文字
    draw = ImageDraw.Draw(img)  # 得到一个draw对象 # 可这么理解：用ImageDraw这个画笔往 img 画板上书写
    kumo_font = ImageFont.truetype("static/font/KumoFont.ttf",
                                   size=20)  # 定义字体；第一个参数是字体样式的路径，第二个是字体大小 # 路径中 static 前不能加 /

    valid_code_str = ""  # 用于保存验证码
    for i in range(4):
        random_num = str(randint(0, 9))  # 数字
        random_lower = chr(randint(97, 122))  # 小写
        random_upper = chr(randint(65, 90))  # 大写
        random_char = random.choice([random_num, random_lower, random_upper])
        draw.text((i * 60 + 30, 5), random_char, get_random_color(),
                  font=kumo_font)  # draw.text()：利用draw对象往画板里面书写文字；第一个参数是一个元组(x,y)，表示横坐标、纵坐标的距离；第二个参数表示文字内容；第三个参数表示字体颜色；第四个表示字体样式
        valid_code_str += random_char

    # 验证图片的噪点、噪线
    width = 260
    height = 33  # width 和 height要和前端验证图片的宽高一致
    # 噪线
    for i in range(5):
        x1 = randint(0, width)
        y1 = randint(0, height)  # (x1,y1)是线的起点
        x2 = randint(0, width)
        y2 = randint(0, height)  # (x2,y2)是线的终点
        draw.line((x1, y1, x2, y2), fill=get_random_color())
    # 噪点
    for i in range(100):
        draw.point([randint(0, width), randint(0, height)], fill=get_random_color())  # 在给定的坐标点上画一些点。
        x = randint(0, width)
        y = randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())  # 在给定的区域内，在开始和结束角度之间绘制一条弧（圆的一部分）
    # 参考链接： https://blog.csdn.net/icamera0/article/details/50747084

    # 重点：储存随机生成的验证码（不能用 global 的方式去处理验证码 valid_code_str，因为此时当有其他用户登陆时验证码会被别人刷新掉；正确的方式是把该验证码存到 session 中 ）
    request.session["valid_code_str"] = valid_code_str  # 注意：这句代码执行了三个操作过程

    # 内存处理
    f = BytesIO()  # f就是一个内存句柄
    img.save(f, "png")  # 把img保存到内存句柄中；# save()之后就能把img保存到内存中
    data = f.getvalue()  # 把保存到内存中的数据读取出来
    # BytesIO会有一个自动清除内存的操作

    return data