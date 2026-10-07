import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FastAPI S3 upload server is running"}


@app.post("/files/upload")
def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required",
        )

    if not S3_BUCKET_NAME:
        raise HTTPException(
            status_code=500,
            detail="S3 bucket is not configured",
        )

    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            file.filename,
        )
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=500,
            detail="File upload to S3 failed",
        )

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "bucket": S3_BUCKET_NAME,
    }