from django import conf
import importlib

def kingadmin_auto_discover():
    # 把每个APP中的  kingadmin 动态导入
    print("conf.settings.INSTALLED_APPS",conf.settings.INSTALLED_APPS)
    for app_name in conf.settings.INSTALLED_APPS:  # 动态获取项目 settings 配置
        try:
            print("33")
            # mod = __import__("%s.kingadmin" % app_name)  # 把每个 app 中的 kingadmin.py 文件动态的导入进来；__import__(模块名)
            mod = importlib.import_module(".kingadmin",app_name)
            # mod = importlib.import_module(".kingadmin",app_name)
            print("mod",mod)
            # print(mod.kingadmin)  # __import__("%s.kingadmin" % app_name) 的模式下才有 mod.kingadmin

            """
            importlib.import_module 和 __import__()的区别：
            import_module()返回指定的包或模块（例如，pkg.mod），而__import__()返回顶级包或模块（pkg）
            参考链接：https://blog.csdn.net/defending/article/details/78095402?locationNum=1&fps=1
            """
        except ModuleNotFoundError:
            pass