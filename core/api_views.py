from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.http import require_GET

# 定义你的共享目录根路径（确保路径存在）
SHARED_ROOT = Path(r"D:\金冶文件库")


def build_tree(path: Path):
    tree = []
    try:
        for item in sorted(path.iterdir()):
            if item.is_dir():
                tree.append({
                    "label": item.name,
                    "path": str(item.resolve()),
                    "children": build_tree(item)
                })
    except PermissionError:
        pass
    return tree


@require_GET
def get_folder_tree(request):
    tree = build_tree(SHARED_ROOT)
    return JsonResponse(tree, safe=False)
