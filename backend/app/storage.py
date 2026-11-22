import pathlib
import uuid

# Обязательно определяем базовую директорию
BASE_DIR = pathlib.Path("/data/jobs")
VALID_STEMS = {"vocals", "drums", "bass", "other"}

def job_dir(job_id):
    try:
        # Валидация UUID
        valid_uuid = uuid.UUID(job_id)
    except ValueError:
        # Если невалидный — прерываем выполнение с ошибкой
        raise ValueError(f"Invalid job_id: {job_id}")
    
    # Возвращаем путь (используем имя dir_path, чтобы не путать с классом Path)
    dir_path = BASE_DIR / str(valid_uuid)
    return dir_path

def input_path(job_id):
    # job_dir() уже возвращает объект Path
    dir_path = job_dir(job_id)
    # Используем оператор / для склейки путей и сразу возвращаем результат
    return dir_path / "input.mp3"

def stem_path(job_id, stem):
    if stem not in VALID_STEMS:
        raise ValueError(f"Incorrect stem: {stem}")
    
    dir_path = job_dir(job_id)
    # Обратите внимание на кавычки у "stems"
    return dir_path / "stems" / f"{stem}.mp3"

def job_exists(job_id):
    # Если job_id невалидный, job_dir выбросит исключение (это нормально)
    try:
        dir_path = job_dir(job_id)
    except ValueError:
        return False # Если UUID невалидный, значит и задачи нет
        
    # Проверяем наличие конкретного файла
    meta_file = dir_path / "meta.json"
    return meta_file.exists()

class FileTooLargeError(Exception):
    """Кастомное исключение для превышения размера файла."""
    pass

def save_upload_file_stream(file, destination: pathlib.Path, max_bytes: int, chunk_size: int = 1024 * 1024):
    """
    Потоково сохраняет UploadFile на диск.
    Возвращает реальный размер сохраненного файла.
    """
    total_size = 0
    try:
        with open(destination, "wb") as buffer:
            # Читаем чанками
            while chunk := file.file.read(chunk_size):
                total_size += len(chunk)
                if total_size > max_bytes:
                    raise FileTooLargeError(f"Превышен лимит в {max_bytes} байт")
                buffer.write(chunk)
        return total_size
    except Exception as e:
        # При ЛЮБОЙ ошибке (лимит, диск переполнен) удаляем недописанный файл
        if destination.exists():
            destination.unlink()
        raise e # Пробрасываем ошибку наверх