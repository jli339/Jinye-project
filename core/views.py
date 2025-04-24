from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden
from .models import FileResource
# from .forms import FileResourceForm
from .forms import FilePathForm
from django.core.paginator import Paginator
from .models import ActionLog
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FilePathForm(request.POST, user=request.user)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploaded_by = request.user

            # 如果是普通用户，自动设定权限字段为其自身角色
            if request.user.role != 'admin':
                file.readable_roles = [request.user.role]
                file.editable_roles = []
            file.save()
            ActionLog.objects.create(
                user=request.user,
                file=file,
                action='upload',
                ip=request.META.get('REMOTE_ADDR')
            )
            return redirect('file_list')
    else:
        form = FilePathForm(user=request.user)

    return render(request, 'core/upload.html', {'form': form})

def download_file(request, file_id):
    file = get_object_or_404(FileResource, id=file_id)
    if not file.can_view(request.user):
        return HttpResponseForbidden("没有访问权限")
    ActionLog.objects.create(
        user=request.user,
        file=file,
        action='view',
        ip=request.META.get('REMOTE_ADDR')
    )
    return FileResponse(file.path)

@login_required
def file_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    all_files = FileResource.objects.all()
    visible_files = [f for f in all_files if f.can_view(request.user)]

    if query:
        visible_files = [
            f for f in visible_files
            if query.lower() in f.name.lower()
            or query.lower() in f.description.lower()
            or query.lower() in f.path.lower()
        ]



    if category_filter:
        visible_files = [f for f in visible_files if f.category == category_filter]

    paginator = Paginator(visible_files, 10)  # 每页 10 条
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/file_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category_filter': category_filter,
    })
@login_required
def edit_permissions(request, file_id):
    file = get_object_or_404(FileResource, id=file_id)

    # 只允许管理员操作
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden("您没有权限修改此文件权限。")

    if request.method == 'POST':
        form = FilePathForm(request.POST, instance=file, user=request.user)
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
        form = FilePathForm(instance=file, user=request.user)

    return render(request, 'core/edit_permissions.html', {'form': form, 'file': file})

@login_required
def action_log_list(request):
    # 统一管理员访问权限判断
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden("您无权查看操作日志。")

    logs = ActionLog.objects.select_related('user', 'file').order_by('-timestamp')
    return render(request, 'core/action_log_list.html', {'logs': logs})