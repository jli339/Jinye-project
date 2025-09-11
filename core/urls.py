from django.urls import path

from . import api_views
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('files/', views.file_list, name='file_list'),

    path('edit/<int:file_id>/', views.edit_permissions, name='edit_permissions'),

    path('logs/', views.action_log_list, name='action_log_list'),

    path('', views.index, name='index'),

    path("api/folder_tree/", api_views.get_folder_tree, name="folder_tree"),
    path('clean_invalid/', views.clean_invalid_files, name='clean_invalid_files'),

    path('files/bulk_edit/', views.bulk_edit_permissions, name='bulk_edit_permissions'),
]
