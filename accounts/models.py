from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('production', '生产部'),
        ('quality', '品质部'),
        ('admin_office', '行政部'),
        ('viewer', '普通查看'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)