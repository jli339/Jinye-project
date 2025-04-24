from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class FileResource(models.Model):
    CATEGORY_CHOICES = [
        ('drawing', '图纸'),
        ('report', '报告'),
        ('client', '客户资料'),
        ('other', '其他'),
    ]

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=1024,default=r'C:\Users\Lenovo\Desktop\模拟共享')
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')  # ✅ 新字段
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    readable_roles = models.JSONField(default=list)  # ["admin", "quality"]
    editable_roles = models.JSONField(default=list)  # ["admin"]
    created_at = models.DateTimeField(auto_now_add=True)

    def can_view(self, user):
        return user.role in self.readable_roles or user.is_superuser

    def can_edit(self, user):
        return user.role in self.editable_roles or user.is_superuser

    def __str__(self):
        return self.name


class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('view', '查看'),
        ('edit_permissions', '修改权限'),
        ('upload', '录入'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.ForeignKey(FileResource, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)