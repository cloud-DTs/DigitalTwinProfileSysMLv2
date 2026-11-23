import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from apiserver import process_sysml


class ProcessSysmlTests(unittest.TestCase):
    def message(self, message_type, content, message_id="command-id"):
        return {
            "parent_header": {"msg_id": message_id},
            "header": {"msg_type": message_type},
            "content": content,
        }

    def test_text_validation_errors_and_warnings_abort_command(self):
        for marker in ["ERROR:", "WARNING:"]:
            for message_type in ["execute_result", "stream"]:
                with self.subTest(marker=marker, message_type=message_type):
                    client = MagicMock()
                    client.execute.return_value = "command-id"
                    content = (
                        {"data": {"text/plain": f"{marker} invalid model"}}
                        if message_type == "execute_result"
                        else {"name": "stderr", "text": f"{marker} invalid model"}
                    )
                    client.get_iopub_msg.side_effect = [
                        self.message(message_type, content),
                        self.message("status", {"execution_state": "idle"}),
                    ]
                    with self.assertRaisesRegex(RuntimeError, "invalid model"):
                        process_sysml.run_command(client, "package Model {}", 1)

    def test_unrelated_kernel_errors_are_ignored(self):
        client = MagicMock()
        client.execute.return_value = "command-id"
        client.get_iopub_msg.side_effect = [
            self.message("error", {"evalue": "other request"}, "other-id"),
            self.message("status", {"execution_state": "idle"}),
        ]
        process_sysml.run_command(client, "package Model {}", 1)

    def test_reads_stdin_and_uses_unique_export_package(self):
        client = MagicMock()
        with tempfile.TemporaryDirectory() as directory:
            export_path = Path(directory) / "export.json"

            def execute(client, command, timeout):
                if command.startswith("%export "):
                    export_path.write_text("[]", encoding="utf-8")

            with (
                patch.dict(os.environ, {"SYSML_CONTENT": ""}),
                patch.object(process_sysml.sys, "stdin", io.StringIO("part Model;")),
                patch.object(process_sysml, "EXPORT_PATH", export_path),
                patch.object(process_sysml, "connect_to_kernel", return_value=client),
                patch.object(process_sysml, "run_command", side_effect=execute) as run,
            ):
                process_sysml.run_task()

            command = run.call_args_list[0].args[1]
            self.assertIn("part Model;", command)
            package_name = command.split()[1]
            self.assertTrue(package_name.startswith("GeneratedExport_"))
            self.assertEqual(run.call_args_list[1].args[1], f"%export {package_name}")
            self.assertEqual(export_path.read_text(encoding="utf-8"), "[]")
        client.stop_channels.assert_called_once()

    def test_rejects_empty_export(self):
        client = MagicMock()
        with tempfile.TemporaryDirectory() as directory:
            export_path = Path(directory) / "export.json"

            def execute(client, command, timeout):
                if command.startswith("%export "):
                    export_path.touch()

            with (
                patch.dict(os.environ, {"SYSML_CONTENT": "part Model;"}),
                patch.object(process_sysml.sys, "stdin", io.StringIO("part Model;")),
                patch.object(process_sysml, "EXPORT_PATH", export_path),
                patch.object(process_sysml, "connect_to_kernel", return_value=client),
                patch.object(process_sysml, "run_command", side_effect=execute),
            ):
                with self.assertRaisesRegex(RuntimeError, "empty"):
                    process_sysml.run_task()
        client.stop_channels.assert_called_once()

    def test_removes_stale_export_before_loading_model(self):
        client = MagicMock()
        with tempfile.TemporaryDirectory() as directory:
            export_path = Path(directory) / "export.json"
            export_path.write_text("stale export", encoding="utf-8")

            def execute(client, command, timeout):
                self.assertFalse(export_path.exists())
                raise RuntimeError("invalid model")

            with (
                patch.dict(os.environ, {"SYSML_CONTENT": "part Model;"}),
                patch.object(process_sysml.sys, "stdin", io.StringIO("part Model;")),
                patch.object(process_sysml, "EXPORT_PATH", export_path),
                patch.object(process_sysml, "connect_to_kernel", return_value=client),
                patch.object(process_sysml, "run_command", side_effect=execute),
            ):
                with self.assertRaisesRegex(RuntimeError, "invalid model"):
                    process_sysml.run_task()
        client.stop_channels.assert_called_once()

    def test_stops_channels_when_kernel_readiness_fails(self):
        client = MagicMock()
        client.wait_for_ready.side_effect = RuntimeError("kernel unavailable")
        with (
            patch.object(process_sysml, "latest_connection_file", return_value=Path("kernel.json")),
            patch.object(process_sysml, "BlockingKernelClient", return_value=client),
        ):
            with self.assertRaisesRegex(RuntimeError, "kernel unavailable"):
                process_sysml.connect_to_kernel()
        client.stop_channels.assert_called_once()


if __name__ == "__main__":
    unittest.main()
