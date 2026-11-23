from celery import Celery
from app.config import settings

celery_app = Celery("stem_player", broker=settings.redis_url, backend=settings.redis_url,
                    include=["app.worker.tasks"])
celery_app.conf.update(
    task_track_started=True,        # чтобы видеть STARTED, а не только PENDING
    result_expires=60 * 60 * 24,    # результаты в Redis живут сутки
    worker_prefetch_multiplier=1,   # не забирать в запас длинные задачи
    task_acks_late=True,            # задача вернётся в очередь, если воркер упал
)
