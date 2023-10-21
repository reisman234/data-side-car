from unittest import TestCase
import os
import zipfile
import typing

from main import zip_result
from main import Minio


class TestStorage(TestCase):

    def setUp(self) -> None:
        self.storage_client = Minio(
            endpoint="localhost:9000",
            access_key="rootuser",
            secret_key="rootpass",
            secure=False
        )

        self.target_directory = "data"
        self.output_file = os.path.join(self.target_directory, "result.zip")

        self.file_paths: typing.List[str] = []
        for root, _, files in os.walk(self.target_directory):
            for file in files:
                # Use glob to filter files if needed (e.g., "*.txt" for all text files)
                # Remove the glob part if you want to list all files.
                self.file_paths.append(os.path.join(root, file))

        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isfile(self.output_file):
            os.remove(self.output_file)
        return super().tearDown()

    def test_zip(self):

        self.assertFalse(os.path.isfile(self.output_file),
                         f"output_file: {self.output_file} should not exist")

        ok = zip_result(target_directory=self.target_directory,
                        output_file=self.output_file
                        )

        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(self.output_file))

    def test_zip_file(self):

        self.assertFalse(os.path.isfile(self.output_file),
                         f"output_file: {self.output_file} should not exist")

        zip_result(target_directory=self.target_directory,
                   output_file=self.output_file
                   )

        self.assertTrue(os.path.isfile(self.output_file))
        with zipfile.ZipFile(self.output_file) as zip_file:
            file_list = zip_file.namelist()

        result_zip_file_names = [f.split(sep="/", maxsplit=1)[1] for f in self.file_paths]
        self.assertListEqual(file_list, result_zip_file_names)
