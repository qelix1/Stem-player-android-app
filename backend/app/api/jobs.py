import json
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.storage import job_dir, input_path, save_upload_file_stream, FileTooLargeError
from app.worker.tasks import separate
router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

MAX_UPLOAD_MB = 50
MAX_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/flac", "audio/ogg", "audio/m4a"}

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_job(file: UploadFile = File(...)):
    # TODO 1: Проверка типа
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат")

    # TODO 2: Создание папки
    job_id = str(uuid.uuid4())
    task_dir = job_dir(job_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    
    file_location = input_path(job_id)

    # TODO 3: Потоковое сохранение
    try:
        save_upload_file_stream(file, file_location, MAX_BYTES)
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail=f"Файл больше {MAX_UPLOAD_MB} МБ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения: {str(e)}")
    finally:
        await file.close()

    # TODO 4: Запись meta.json
    meta_data = {
        "original_filename": file.filename,
        "content_type": file.content_type,
        "created_at": datetime.utcnow().isoformat(),
        "status": "PENDING"
    }
    meta_path = task_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)

    # TODO 5: Отправка в Celery
    # Важно: передаем ТОЛЬКО job_id (строку), а не тяжелые объекты!
    separate.apply_async(args=[job_id], task_id=job_id)

    return {"job_id": job_id}
