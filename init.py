import os
import logging
import json
from configparser import ConfigParser
from minio import Minio
from typing import List
from zipfile import ZipFile

from models import WorkflowInputResource, ServiceResourceType


###############
# CONFIGURATION
###############

CONFIG_FILE_PATH = os.environ.get("CONFIG_FILE_PATH", "./config/workflow-api.cfg")

logging.basicConfig(level=logging.DEBUG)
logging.debug("load config file %s", {CONFIG_FILE_PATH})

CONFIG = ConfigParser()
CONFIG.read(CONFIG_FILE_PATH)

if not CONFIG.has_section("workflow_api"):
    raise ValueError("config has no workflow_api section")

if not CONFIG.has_section("minio"):
    raise ValueError("config has no minio section")
MINIO_CONFIG = CONFIG["minio"]


DATA_DESTINATION = os.environ.get("DATA_DESTINATION")
if not DATA_DESTINATION:
    raise ValueError("DATA_DESTINATION not set")

INPUT_INIT_CONFIG = os.environ.get("INPUT_INIT_CONFIG")
if not INPUT_INIT_CONFIG:
    raise ValueError("INPUT_INIT_CONFIG not set")

if not os.path.isfile(INPUT_INIT_CONFIG):
    raise FileNotFoundError(f"INPUT_INIT_CONFIG {INPUT_INIT_CONFIG} not a file")


def load_input_config(json_file: str) -> List[WorkflowInputResource]:
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return [WorkflowInputResource.parse_obj(entry) for entry in data]


input_config = load_input_config(INPUT_INIT_CONFIG)
if not input_config:
    raise RuntimeError("Fail: input_config could'n load")

client = Minio(
    endpoint=MINIO_CONFIG.get("endpoint"),
    access_key=MINIO_CONFIG.get("access_key"),
    secret_key=MINIO_CONFIG.get("secret_key"),
    secure=MINIO_CONFIG.getboolean("secure")
)


def transfer_input(_input_config: List[WorkflowInputResource],
                   destination: str,
                   storage_client: Minio):
    for entry in _input_config:
        (bucket_name, resource_path) = entry.storage_source.split("/",
                                                                  maxsplit=1)
        storage_client.fget_object(bucket_name=bucket_name,
                                   object_name=resource_path,
                                   file_path=os.path.join(destination, entry.resource_name))


def extract_containers(_input_config: List[WorkflowInputResource],
                       destination: str):
    for entry in _input_config:
        if entry.type != ServiceResourceType.data_zip:
            continue
        with ZipFile(os.path.join(destination, entry.resource_name)) as zip_file:
            zip_file.extractall(path=destination)
        os.remove(os.path.join(destination, entry.resource_name))


transfer_input(_input_config=input_config,
               destination=DATA_DESTINATION,
               storage_client=client)

extract_containers(_input_config=input_config,
                   destination=DATA_DESTINATION)

logging.debug("init completed")
