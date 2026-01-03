import os
from pathlib import Path

from django.contrib.auth import get_user_model

from core.models import FileResource

SHARED_ROOT = Path(r"D:\金冶文件库")


def check_file_integrity():
    print("[调度] 正在执行文件一致性检查...")

    # 步骤一：标记数据库中丢失的文件（包括 path 为空 或 不存在）
    for file in FileResource.objects.all():
        if not file.path:
            if "（文件缺失）" not in (file.description or ""):
                file.description = (file.description or "") + "（文件缺失）"
                file.save()
                print(f"[缺失] {file.name} - path 为空")
            continue

        path = Path(file.path)
        if not path.exists():
            if "（文件缺失）" not in (file.description or ""):
                file.description = (file.description or "") + "（文件缺失）"
                file.save()
                print(f"[缺失] {file.name} - 路径不存在")

    # 步骤二：发现磁盘中新出现的文件
    disk_file_set = set()
    for root, dirs, files in os.walk(SHARED_ROOT):
        for fname in files:
            full_path = Path(root) / fname
            disk_file_set.add(str(full_path.resolve()))

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
                category="other",
                readable_roles=["admin"],
                editable_roles=["admin"]
            )
            print(f"[新增] 已添加新文件记录：{path}")

    print("[调度] 文件一致性检查完成。")
