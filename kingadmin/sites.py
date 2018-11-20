from kingadmin.base_admin import BaseKingAdmin


class AdminSite(BaseKingAdmin):
    def __init__(self):
        self.enabled_admin = {}

    # 注册的目的是让视图中能够获取到 admin_class 和 model_class
    # 格式： {app_name:{表名:自定义admin}}
    def register(self,model_class,admin_class=None):
        print(model_class,admin_class)

        app_label = model_class._meta.app_label  # 获取该 model类 所在的 app
        model_name = model_class._meta.model_name  # 获取该 model类 的数据表名

        if not admin_class: # 如果 admin_class 为空，就把BaseKingAdmin赋值给 admin_class
            admin_class = BaseKingAdmin() # admin_class为空的时候需要将 BaseKingAdmin类 进行实例化。为了避免多个model共享同一个BaseKingAdmin内存地址；要不然当有多个admin_class为空的Register()时，最后一个的 BaseKingAdmin.model = model_class 会将前面的 覆盖掉；但BaseKingAdmin 实例化后将是一个个彼此独立的对象
        else:
            admin_class = admin_class()
        admin_class.model = model_class  # 把 model_class 的 admin_class 绑定在一起；

        if app_label not in self.enabled_admin:  # 这个 app 名不在 enabled_admin 这个字典中，就把其添加到里面
            self.enabled_admin[app_label] = {}
        self.enabled_admin[app_label][model_name] = admin_class  # 把APP名称、表名、和自定义Admin 按上面的格式添加到 enabled_admin 字典中


site = AdminSite()  # 不管多少APP中导入该模块，AdminSite()只实例化了一次