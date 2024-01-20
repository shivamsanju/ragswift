from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from .ingestion import router as ingestion_router

app = FastAPI()


@app.get("/")
def healthcheck():
    return "RUNNING"


# Define an exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Define a generic exception handler for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


app.include_router(ingestion_router, prefix="/ingest", tags=["Ingestion"])
