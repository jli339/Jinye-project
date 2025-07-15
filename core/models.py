# Create your models here.
from django.conf import settings
from django.db import models


class FileResource(models.Model):
    objects = None
    CATEGORY_CHOICES = [
        ('drawing', '图纸'),
        ('report', '报告'),
        ('client', '客户资料'),
        ('other', '其他'),
    ]

    name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)  # 新增字段：接收上传文件
    path = models.CharField(max_length=1024, blank=True)
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
        return self.name or self.file.name

    def get_file_url(self):
        return self.file.url if self.file else ''

    def get_file_path(self):
        return self.file.path if self.file else ''


class ActionLog(models.Model):
    objects = None
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
