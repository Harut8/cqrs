import celery

from app.settings import APP_SETTINGS


class Celery(celery.Celery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autodiscover_tasks()


celery_app = Celery(
    "celery_app",
    broker=APP_SETTINGS.CELERY.CELERY_BROKER_URL,
    backend=APP_SETTINGS.CELERY.CELERY_RESULT_BACKEND,
    include=["app.helpers.celery_tasks"],
)
