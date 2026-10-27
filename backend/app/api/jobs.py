import shutil, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_job(file: UploadFile = File(...)):
    # TODO 1: проверить расширение/content_type (mp3, wav, flac, m4a)
    job_id = str(uuid.uuid4())
    # TODO 2: создать папку задачи
    # TODO 3: сохранить файл ПОТОКОВО, не читая целиком в память:
    #   with open(path, "wb") as out: shutil.copyfileobj(file.file, out)
    #   и по пути считать байты -> если > max_upload_mb, удалить и вернуть 413
    # TODO 4: записать meta.json
    # TODO 5: separate.apply_async(args=[job_id], task_id=job_id)
    return {"job_id": job_id}
