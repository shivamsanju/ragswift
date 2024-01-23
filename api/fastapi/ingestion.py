import os
import shutil

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ray.job_submission import JobSubmissionClient

from schema.base import GithubIngestionPayload, S3IngestionPayload
from settings import settings

router = APIRouter()

current_dir = os.getcwd()
runtime_dir = os.path.join(current_dir, "runtime")


def create_runtime_files():
    if not os.path.exists(runtime_dir):
        os.makedirs(runtime_dir, mode=0o777, exist_ok=True)
        shutil.copytree("jobs", os.path.join(runtime_dir, os.path.basename("jobs")))
        shutil.copytree("schema", os.path.join(runtime_dir, os.path.basename("schema")))
        shutil.copy("settings.py", runtime_dir)
        shutil.copy("constants.py", runtime_dir)
        shutil.copy(".env", runtime_dir)
        print("Runtime files copied successfully.")


@router.post("/github")
async def submit_github_ingestion_job(payload: GithubIngestionPayload):
    create_runtime_files()
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    job_id = client.submit_job(
        entrypoint=f"python -m jobs.ingestion.job --payload '{payload.model_dump_json()}'",
        runtime_env={"working_dir": runtime_dir},
    )
    return JSONResponse(status_code=200, content={"job_id": job_id})


@router.post("/s3")
async def submit_s3_ingestion_job(payload: S3IngestionPayload):
    create_runtime_files()
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    job_id = client.submit_job(
        entrypoint=f"python -m jobs.ingestion.job --payload '{payload.model_dump_json()}'",
        runtime_env={"working_dir": runtime_dir},
    )
    return JSONResponse(status_code=200, content={"job_id": job_id})


@router.get("/jobs")
async def list_jobs():
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    jobs = client.list_jobs()
    result = [job.json() for job in jobs]
    return JSONResponse(status_code=200, content={"jobs": result})


@router.delete("/{job_id}")
async def stop_job(job_id: str):
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    result = client.stop_job(job_id)
    return JSONResponse(status_code=200, content={"result": result})


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    status = client.get_job_status(job_id)
    logs = client.get_job_logs(job_id)
    info = client.get_job_info(job_id)
    return JSONResponse(
        status_code=200, content={"status": status, "logs": logs, "info": info.json()}
    )
