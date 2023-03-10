from fastapi import FastAPI
from minio import Minio
from pydantic import BaseModel
from typing import List
from os import listdir, stat
from os.path import join


class MinioStoreInfo(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool


class WorkflowStoreInfo(BaseModel):
    minio: MinioStoreInfo
    destination_bucket: str
    destination_path: str
    result_directory: str = "/output"
    result_files: List[str]


app = FastAPI()


@app.post("/store_result/")
async def store_result(store_info: WorkflowStoreInfo):

    client = Minio(
        endpoint=store_info.minio.endpoint,
        access_key=store_info.minio.access_key,
        secret_key=store_info.minio.secret_key,
        secure=store_info.minio.secure)

    available_files = listdir(store_info.result_directory)
    for filename in store_info.result_files:
        if filename in available_files:
            filename_abs = join(store_info.result_directory, filename)
            file_length = stat(filename_abs).st_size
            file = open(filename_abs, mode="br")
            client.put_object(
                bucket_name=store_info.destination_bucket,
                object_name=join(store_info.destination_path, filename),
                data=file,
                length=file_length)
