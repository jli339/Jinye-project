import os
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import FileResource

def check_file_integrity():
    print("[调度] 正在执行文件一致性检查...")

    # 步骤一：标记数据库中丢失的文件
    for file in FileResource.objects.all():
        path = os.path.join(settings.MEDIA_ROOT, file.path)
        if not os.path.exists(path):
            if "（文件缺失）" not in (file.description or ""):
                file.description = (file.description or "") + "（文件缺失）"
                file.save()
                print(f"[失效] {file.name}")

    # 步骤二：发现磁盘中新出现的文件
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    disk_file_set = set()
    for root, dirs, files in os.walk(upload_dir):
        for fname in files:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, settings.MEDIA_ROOT)
            disk_file_set.add(rel_path.replace('\\', '/').replace('\\\\', '/'))

    db_file_set = set(FileResource.objects.values_list('path', flat=True))
    new_files = disk_file_set - db_file_set

    if new_files:
        User = get_user_model()
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            print("[错误] 无法找到用户名为 'admin' 的用户，跳过新增同步")
            return

        for path in new_files:
            FileResource.objects.create(
                name=os.path.basename(path),
                path=path,
                uploaded_by=admin_user,
                description="（系统自动同步创建）",
                category="other",  # 默认分类为“其他”
                readable_roles=["admin"],
                editable_roles=["admin"]
            )
            print(f"[新增] 已添加新文件记录：{path}")

    print("[调度] 文件一致性检查完成。")
