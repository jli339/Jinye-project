from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden,Http404
from .models import FileResource
# from .forms import FileResourceForm
from .forms import FileUploadForm
from django.core.paginator import Paginator
from .models import ActionLog
from django.conf import settings
import os
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST,request.FILES, user=request.user)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = request.user

            # 如果是普通用户，自动设定权限字段为其自身角色
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
    if not file.can_view(request.user):
        return HttpResponseForbidden("没有访问权限")
    file_path = file.file.path

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404("文件未找到")

    # 记录日志
    ActionLog.objects.create(
        user=request.user,
        file=file,
        action='download'
    )

    # 返回文件响应
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file.name)

@login_required
def file_list(request):
    user = request.user
    query = request.GET.get('q')
    category = request.GET.get('category')

    files = FileResource.objects.all()

    # 权限过滤：只有可见的文件才展示
    files = [f for f in files if f.can_view(user)]

    # 动态检测物理文件是否存在
    for f in files:
        f.exists_on_disk = os.path.exists(os.path.join(settings.MEDIA_ROOT, f.file.name))

    # 查询过滤
    if query:
        files = [f for f in files if query.lower() in f.name.lower() or query.lower() in (f.description or '').lower()]

    if category:
        files = [f for f in files if f.category == category]

    # 分页处理
    paginator = Paginator(files, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/file_list.html', {
        'files': page_obj,
        'query': query,
        'category': category,
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