from django.forms import ModelForm
from django.core.exceptions import ValidationError

def dynamic_create_model_form(admin_class):
    """动态生成ModelForm"""
    class Meta:
        model = admin_class.model
        fields = "__all__"

    dynamic_model_form = type("DynamicModelForm",(ModelForm,),{"Meta":Meta})

    def __new__(cls,*args,**kwargs):
        # 遍历数据库的所有字段和字段对应的对象
        for field_name,field_obj in cls.base_fields.items():  # model类.base_fields：   # 字典，key包含所有的字段名，value包含所有的字段对象：{"字段名":字段对象,...}
            # 为每个字段对象的组件添加class属性
            field_obj.widget.attrs["class"] = "form-control"

            if not getattr(admin_class,"is_form_add"):  # 排除添加页面
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs["disabled"] = "disabled"

        # 创建当前类的实例 ---> 即创建子类
        return ModelForm.__new__(cls)

    def clean(self):
        """ 添加全局钩子，判断 readonly_fields 字段中的内容在前端是否发生改变 """
        for field in admin_class.readonly_fields:
            if not getattr(admin_class,"is_form_add"): # 编辑页面
                field_value_from_db = getattr(self.instance,field)  # 利用 getattr()方法获取到该对象的这个字段在数据库中的值
                field_value_from_input = self.cleaned_data.get(field)  # 利用 cleaned_data.get() 的方法获取从前端传过来的值

                if field_value_from_db == field_value_from_input:
                    return self.cleaned_data
                else:
                    self.add_error(field,"Readonly field,should not be %s but %s "%(field_value_from_input,field_value_from_db))  # add_error(field,"错误信息")：添加字段级别的错误
            else:
                return self.cleaned_data

    # 为该类添加 __new__ 静态方法，当调用该类的时候，会先执行 __new__ 方法，创建对象
    setattr(dynamic_model_form,"__new__",__new__)
    setattr(dynamic_model_form,"clean",clean)  # 添加全局钩子

    return dynamic_model_form