from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schema.base import IngestionPayload
from ray.job_submission import JobSubmissionClient
from settings import settings

router = APIRouter()


@router.post("/")
async def submit_ingestion_job(payload: IngestionPayload):
    client = JobSubmissionClient(settings.RAY_DASHBOARD_ADDRESS)
    job_id = client.submit_job(
        entrypoint=f"python -m jobs.ingestion.job --payload '{payload.model_dump_json()}'",
        runtime_env={"working_dir": "./"},
    )
    print(job_id)
    return JSONResponse(status_code=200, content={"job_id": payload.asset_id})


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
        status_code=200, content={"status": status, "logs": logs, "info": info}
    )
