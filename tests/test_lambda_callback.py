import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
import zipfile


CALLBACK_PATH = (
    Path(__file__).resolve().parents[1]
    / "testLambdaFunctions/high-temperature-callback/lambda_function.py"
)


class LambdaCallbackTests(unittest.TestCase):
    def test_callback_loads_without_optional_twin_info(self):
        with patch.dict(os.environ, {}, clear=True):
            callback = runpy.run_path(str(CALLBACK_PATH))
        self.assertEqual(callback["DIGITAL_TWIN_INFO"], {})
        self.assertEqual(
            callback["lambda_handler"]({}, None),
            {"this_is_some_return_data": "hello world!"},
        )

    def test_callback_reads_configured_twin_info(self):
        with patch.dict(os.environ, {"DIGITAL_TWIN_INFO": '{"name": "MGrid"}'}):
            callback = runpy.run_path(str(CALLBACK_PATH))
        self.assertEqual(callback["DIGITAL_TWIN_INFO"], {"name": "MGrid"})

    def test_deployment_archive_contains_current_callback(self):
        with zipfile.ZipFile(CALLBACK_PATH.with_name("zipped.zip")) as archive:
            archived_source = archive.read("lambda_function.py").decode("utf-8")
        self.assertEqual(
            archived_source.splitlines(),
            CALLBACK_PATH.read_text(encoding="utf-8").splitlines(),
        )


if __name__ == "__main__":
    unittest.main()
