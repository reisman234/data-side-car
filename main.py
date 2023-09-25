import io
import logging
import os
import zipfile
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from minio import Minio
# pylint: disable=E0611
from pydantic import BaseModel
from typing import List
import os
from os import listdir, uname
from os.path import join
import typing

import models
from progress import Progress

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)


class StoreResult(BaseModel):
    success: List[str] = list()
    failed: List[str] = list()


MB = 1024*1024
MB_64 = 64*MB


def zip_result(target_directory: str,
               output_file: str):
    """
        creates a zip archive from a target_directory
        and writes it to the provided location.

        Returns:
            True: If a zip_file was created
            False: If no zip_file was created because no data in target_directory
    """

    file_paths: typing.List[str] = []
    for root, _, files in os.walk(target_directory):
        for file in files:
            file_paths.append(os.path.join(root, file))

    if not file_paths:
        return False

    # create a temp zip archive on storage
    if not output_file:
        output_file = os.path.join(target_directory, "result.zip")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            # remove the name of the containing folder
            new_file_path = file_path.split("/", maxsplit=1)[1]
            zip_file.write(filename=file_path,
                           arcname=new_file_path)
    return True


def save_zip(s3_client: Minio,
             zip_file: str,
             bucket_name: str,
             object_name: str
             ):

    s3_client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=zip_file,
        progress=Progress()
    )


app = FastAPI()


@app.on_event("startup")
async def startup():
    logging.info(uname())


@app.get("/health/")
async def get_health():
    return {"status": "ok"}


@app.post("/store/")
async def store_result(store_info: models.WorkflowStoreInfo):

    client = Minio(
        endpoint=store_info.minio.endpoint,
        access_key=store_info.minio.access_key,
        secret_key=store_info.minio.secret_key,
        secure=store_info.minio.secure)

    logging.info("""workflow store information received:
                 \tdestination_bucket: \t%s
                 \tdestination_path: \t%s
                 \tresult_directory: \t%s
                 \tresult_resources: \t%s
                 """, store_info.destination_bucket, store_info.destination_path, store_info.result_directory,
                 store_info.result_resources)

    store_log = StoreResult()
    for resource in store_info.result_resources:

        s3_object_name = os.path.join(store_info.destination_path, resource.resource_name)

        if resource.type == models.ServiceResourceType.data_zip:
            zip_file = os.path.join(store_info.result_directory, resource.resource_name)

            is_ok = zip_result(target_directory=store_info.result_directory,
                               output_file=zip_file)
            if not is_ok:
                logging.info("no zip_file created, no content in %s",
                             store_info.result_directory)
                continue

            if os.path.isfile(zip_file):
                upload_file_path = zip_file

        elif resource.type == models.ServiceResourceType.data:
            available_files = listdir(store_info.result_directory)

            if resource.resource_name in available_files:

                upload_file_path = os.path.join(store_info.result_directory, resource.resource_name)

        if upload_file_path:

            logging.info("store file: %s", resource.resource_name)
            store_log.success.append(resource.resource_name)
            client.fput_object(
                bucket_name=store_info.destination_bucket,
                object_name=s3_object_name,
                file_path=upload_file_path,
                progress=Progress()
            )

        else:
            logging.error("error while processing %s", resource.resource_name)
            store_log.failed.append(resource.resource_name)

    logging.info("store finished: %s", store_log)

    return JSONResponse(content=store_log.json())
