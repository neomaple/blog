from blog.models import *
# forms 组件
from django import forms
from django.forms import widgets

from django.core.exceptions import ValidationError
class UserForm(forms.Form):
    user = forms.CharField(max_length=32,
                           widget=widgets.TextInput(attrs={"class":"form-control"}),
                           label="用户名",
                           error_messages={"required":"该字段不能为空"})
    psw = forms.CharField(max_length=32,
                          widget=widgets.PasswordInput(attrs={"class":"form-control"}),
                          label="密码",
                          error_messages={"required": "该字段不能为空"})
    re_psw = forms.CharField(max_length=32,
                             widget=widgets.PasswordInput(attrs={"class":"form-control"}),
                             label="确认密码",
                             error_messages={"required": "该字段不能为空"})
    email = forms.EmailField(max_length=32,
                             widget=widgets.EmailInput(attrs={"class":"form-control"}),
                             label="邮箱",
                             error_messages={"required": "该字段不能为空"})
    # 头像字段不是必须的，用户可以传也可以不传；所以没必要校验

    # 局部钩子校验新注册的用户名是否已经存在
    def clean_user(self):
        user = self.cleaned_data.get("user")
        user_obj = UserInfo.objects.filter(username=user).first()

        if not user_obj:
            return user
        else:
            raise ValidationError("该用户名已被注册")

    # 全局钩子校验两次密码是否一致
    def clean(self):
        psw = self.cleaned_data.get("psw")
        re_psw = self.cleaned_data.get("re_psw")

        if psw and re_psw:
            if psw == re_psw:
                return self.cleaned_data
            else:
                raise ValidationError("两次密码不一致！")
        else:
            return self.cleaned_data