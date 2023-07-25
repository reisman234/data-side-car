import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from minio import Minio
# pylint: disable=E0611
from pydantic import BaseModel
from typing import List
from os import listdir, uname
from os.path import join

from progress import Progress

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)


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


class StoreResult(BaseModel):
    success: List[str] = list()
    failed: List[str] = list()


app = FastAPI()


@app.on_event("startup")
async def startup():
    logging.info(uname())


@app.get("/health/")
async def get_health():
    return {"status": "ok"}


@app.post("/store/")
async def store_result(store_info: WorkflowStoreInfo):

    client = Minio(
        endpoint=store_info.minio.endpoint,
        access_key=store_info.minio.access_key,
        secret_key=store_info.minio.secret_key,
        secure=store_info.minio.secure)

    logging.info("""workflow store information received:
                 \tdestination_bucket: \t%s
                 \tdestination_path: \t%s
                 \tresult_directory: \t%s
                 \tresult_files: \t%s
                 """, store_info.destination_bucket, store_info.destination_path, store_info.result_directory,
                 store_info.result_files)

    available_files = listdir(store_info.result_directory)
    store_log = StoreResult()
    for filename in store_info.result_files:
        if filename in available_files:
            logging.info("store file: %s", filename)

            filename_abs = join(store_info.result_directory, filename)

            client.fput_object(
                bucket_name=store_info.destination_bucket,
                object_name=join(store_info.destination_path, filename),
                file_path=filename_abs,
                progress=Progress()
            )
            store_log.success.append(filename)
        else:
            logging.error("file not exists %s", filename)
            store_log.failed.append(filename)

    logging.info("store finished: %s", store_log)

    return JSONResponse(content=store_log.json())
