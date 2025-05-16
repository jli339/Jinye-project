from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from core.scheduler import check_file_integrity
        import atexit

        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # 添加任务：每 10 分钟执行一次
        scheduler.add_job(
            check_file_integrity,
            trigger='interval',
            minutes=720,
            id='file_integrity_job',
            replace_existing=True
        )

        scheduler.start()
        print("[调度器] 文件一致性任务已启动，每12小时执行一次")

        # 优雅退出调度器
        atexit.register(lambda: scheduler.shutdown(wait=False))
