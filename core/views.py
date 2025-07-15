# Create your views here.

import shutil
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import escape_uri_path
from django.views.decorators.http import require_POST

# from .forms import FileResourceForm
from .forms import FileUploadForm
from .models import ActionLog
from .models import FileResource


# Create your views here.


def index(request):
    return render(request, 'core/index.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = request.user

            uploaded_file = request.FILES.get('file')
            target_path = request.POST.get('target_path')

            if uploaded_file and target_path:
                # 保存上传文件到临时 media/uploads/
                file_obj.file.save(uploaded_file.name, uploaded_file)

                # 克隆到目标路径
                dest = Path(target_path).resolve() / uploaded_file.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file_obj.file.path, dest)

                # 删除 media 中原始文件
                file_obj.file.delete(save=False)

                # 写入其他信息
                file_obj.original_filename = uploaded_file.name
                file_obj.path = str(dest.resolve())

            if request.user.role != 'admin':
                file_obj.readable_roles = [request.user.role]
                file_obj.editable_roles = []

            file_obj.save()
            ActionLog.objects.create(
                user=request.user,
                file=file_obj,
                action='upload',
                ip=request.META.get('REMOTE_ADDR')
            )
            return redirect('file_list')
    else:
        form = FileUploadForm(user=request.user)

    return render(request, 'core/upload.html', {'form': form})


def download_file(request, file_id):
    file = get_object_or_404(FileResource, id=file_id)

    # 权限校验
    if not file.can_view(request.user):
        return HttpResponseForbidden("没有访问权限")

    # 从目标路径加载文件（非 media 临时区）
    abs_path = Path(file.path)

    if not abs_path.exists() or not abs_path.is_file():
        raise Http404("目标文件不存在，可能已被移除或移动")

    filename = file.original_filename or abs_path.name

    # 记录日志
    ActionLog.objects.create(
        user=request.user,
        file=file,
        action='download'
    )

    # 返回文件响应
    return FileResponse(open(abs_path, 'rb'), as_attachment=True, filename=escape_uri_path(filename))


@login_required
def file_list(request):
    user = request.user
    query = request.GET.get('q', '')
    path_filter = request.GET.get('path', '')

    files = FileResource.objects.all()

    # 权限过滤
    files = [f for f in files if f.can_view(user)]

    # 搜索过滤
    if query:
        files = [
            f for f in files
            if query.lower() in (f.name or '').lower()
               or query.lower() in (f.description or '').lower()
               or query.lower() in (f.path or '').lower()
        ]

    # 路径过滤
    if path_filter:
        files = [f for f in files if f.path and f.path.startswith(path_filter)]

    # 标记物理文件是否存在
    for f in files:
        f.exists_on_disk = Path(f.path).exists()

    return render(request, 'core/file_list.html', {
        'files': files,
        'query': query,
        'path_filter': path_filter,
    })


@login_required
def edit_permissions(request, file_id):
    file = get_object_or_404(FileResource, id=file_id)

    # 只允许管理员操作
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden("您没有权限修改此文件权限。")

    if request.method == 'POST':
        form = FileUploadForm(request.POST, instance=file, user=request.user)
        if form.is_valid():
            form.save()
            ActionLog.objects.create(
                user=request.user,
                file=file,
                action='edit',
                ip=request.META.get('REMOTE_ADDR')
            )
            return redirect('file_list')
    else:
        form = FileUploadForm(instance=file, user=request.user)

    return render(request, 'core/edit_permissions.html', {'form': form, 'file': file})


@login_required
def action_log_list(request):
    # 统一管理员访问权限判断
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden("您无权查看操作日志。")

    logs = ActionLog.objects.select_related('user', 'file').order_by('-timestamp')
    return render(request, 'core/action_log_list.html', {'logs': logs})


@login_required
@require_POST
def clean_invalid_files(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("仅管理员可执行此操作")

    to_delete = [
        f for f in FileResource.objects.all()
        if not f.path or not Path(f.path).exists()
    ]
    deleted_count = len(to_delete)
    for f in to_delete:
        f.delete()

    ActionLog.objects.create(
        user=request.user,
        file=None,
        action='clean_invalid',
        ip=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f"已成功删除 {deleted_count} 条无效记录。")
    return redirect('file_list')
