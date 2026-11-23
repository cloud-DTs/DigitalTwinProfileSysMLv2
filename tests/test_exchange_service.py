import os
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.exchangeService import ExchangeService


class ExchangeServiceTests(unittest.TestCase):
    def test_read_sysml_files_returns_only_sorted_sysml_files(self):
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            (input_dir / "second.sysml").write_text("", encoding="utf-8")
            (input_dir / "first.sysml").write_text("", encoding="utf-8")
            (input_dir / "ignored.txt").write_text("", encoding="utf-8")

            service = ExchangeService("upload.sh", directory)

            self.assertEqual(
                service.read_sysml_files(),
                [
                    str(input_dir / "first.sysml"),
                    str(input_dir / "second.sysml"),
                ],
            )

    def test_read_sysml_files_returns_empty_for_missing_directory(self):
        service = ExchangeService("upload.sh", "missing-input-directory")

        with self.assertLogs(level="ERROR"):
            self.assertEqual(service.read_sysml_files(), [])

    def test_send_to_api_copies_export_from_configured_container(self):
        process = MagicMock()
        process.stdout = io.StringIO(">> Export finished\nExport path: /home/sysml/export.json\n")
        process.wait.return_value = 0
        process.__enter__.return_value = process
        copy_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="",
        )

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {"SYSML_KERNEL_CONTAINER": "custom-kernel"}),
            patch("src.exchangeService.subprocess.Popen", return_value=process) as popen,
            patch(
                "src.exchangeService.subprocess.run",
                side_effect=[copy_result, copy_result],
            ) as run,
        ):
            upload_script = str(Path(directory) / "uploadSysml.sh")
            service = ExchangeService(upload_script, directory)

            export_path = service.sendToApi(["model.sysml"])

        self.assertEqual(export_path, str(Path(directory) / "export.json"))
        popen.assert_called_once()
        self.assertEqual(
            run.call_args_list[0].args[0],
            [
                "docker",
                "cp",
                "custom-kernel:/home/sysml/export.json",
                str(Path(directory) / "export.json"),
            ],
        )
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["docker", "exec", "custom-kernel", "rm", "-f", "/home/sysml/export.json"],
        )

    def test_failed_upload_does_not_copy_stale_export(self):
        process = MagicMock()
        process.stdout = io.StringIO("Export path: /home/sysml/export.json\n")
        process.wait.return_value = 1
        process.__enter__.return_value = process
        with (
            patch("src.exchangeService.subprocess.Popen", return_value=process),
            patch("src.exchangeService.subprocess.run") as run,
        ):
            with self.assertRaisesRegex(RuntimeError, "exit code 1"):
                ExchangeService("upload.sh", ".").sendToApi(["model.sysml"])
        run.assert_not_called()

    def test_missing_export_path_does_not_start_copy(self):
        for output in ["finished\n", "Export path: \n", "Export path: NOT_FOUND\n"]:
            with self.subTest(output=output):
                process = MagicMock()
                process.stdout = io.StringIO(output)
                process.wait.return_value = 0
                process.__enter__.return_value = process
                with (
                    patch("src.exchangeService.subprocess.Popen", return_value=process),
                    patch("src.exchangeService.subprocess.run") as run,
                ):
                    with self.assertRaises(RuntimeError):
                        ExchangeService("upload.sh", ".").sendToApi(["model.sysml"])
                run.assert_not_called()

    def test_copy_failure_reports_docker_error_and_keeps_container_export(self):
        process = MagicMock()
        process.stdout = io.StringIO("Export path: /home/sysml/export.json\n")
        process.wait.return_value = 0
        process.__enter__.return_value = process
        with (
            patch("src.exchangeService.subprocess.Popen", return_value=process),
            patch(
                "src.exchangeService.subprocess.run",
                return_value=subprocess.CompletedProcess([], 1, "", "copy denied"),
            ) as run,
        ):
            with self.assertRaisesRegex(RuntimeError, "copy denied"):
                ExchangeService("upload.sh", ".").sendToApi(["model.sysml"])
        run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
