import logging
import shutil
import subprocess
import sys

from app.config import settings
from app.storage import input_path, job_dir, stem_path
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

DEMUCS_TIMEOUT_SEC = 1800
STEM_ORDER = ("vocals", "drums", "bass", "other")


@celery_app.task(bind=True)
def separate(self, job_id: str):
    job_path = job_dir(job_id)
    input_file = input_path(job_id)
    if not input_file.is_file():
        raise RuntimeError(f"Input file not found: {input_file}")
    logger.info("Starting separation for job %s", job_id)

    tmp_out = job_path / "tmp"
    shutil.rmtree(tmp_out, ignore_errors=True)
    tmp_out.mkdir(parents=True)
    (job_path / "stems").mkdir(parents=True, exist_ok=True)

    try:
        cmd = [
            sys.executable, "-m", "demucs",
            "-n", settings.demucs_model,
            "-d", settings.demucs_device,
            "--mp3",
            "-o", str(tmp_out),
            str(input_file),
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DEMUCS_TIMEOUT_SEC,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Demucs timed out after {DEMUCS_TIMEOUT_SEC} seconds"
            ) from None
        if proc.returncode != 0:
            raise RuntimeError(f"Demucs failed: {proc.stderr[-2000:]}")

        model_out = tmp_out / settings.demucs_model / input_file.stem
        missing = [name for name in STEM_ORDER if not (model_out / f"{name}.mp3").is_file()]
        if missing:
            raise RuntimeError(f"Missing stems: {', '.join(missing)}")

        for name in STEM_ORDER:
            (model_out / f"{name}.mp3").replace(stem_path(job_id, name))
    finally:
        shutil.rmtree(tmp_out, ignore_errors=True)

    logger.info("Separation finished for job %s", job_id)
    return {"stems": list(STEM_ORDER)}
