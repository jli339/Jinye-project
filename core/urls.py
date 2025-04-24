from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
path('files/', views.file_list, name='file_list'),

path('edit/<int:file_id>/', views.edit_permissions, name='edit_permissions'),

path('logs/', views.action_log_list, name='action_log_list'),

]