from django import forms

from .models import FileResource


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileResource
        fields = ['file', 'name', 'description', 'category', 'readable_roles', 'editable_roles']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FileUploadForm, self).__init__(*args, **kwargs)

        self.fields['file'].label = '上传文件'
        self.fields['name'].label = '文件名'
        self.fields['description'].label = '文件描述'
        self.fields['category'].label = '文件分类'
        self.fields['readable_roles'].label = '可读角色'
        self.fields['editable_roles'].label = '可编辑角色'

        ROLE_CHOICES = [
            ('admin', '管理员'),
            ('production', '生产部'),
            ('quality', '品质部'),
            ('admin_office', '行政部'),
            ('viewer', '普通查看'),
        ]

        self.fields['readable_roles'] = forms.MultipleChoiceField(
            choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
        self.fields['editable_roles'] = forms.MultipleChoiceField(
            choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)

        if user and user.role != 'admin':
            # 非管理员用户不能自定义权限字段，使用隐藏字段并默认赋值
            self.fields['readable_roles'].widget = forms.HiddenInput()
            self.fields['editable_roles'].widget = forms.HiddenInput()
