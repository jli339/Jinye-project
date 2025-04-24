from django import forms
from .models import FileResource

from django import forms
from .models import FileResource

class FilePathForm(forms.ModelForm):
    class Meta:
        model = FileResource
        fields = ['name', 'path','description','category', 'readable_roles', 'editable_roles']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FilePathForm, self).__init__(*args, **kwargs)

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