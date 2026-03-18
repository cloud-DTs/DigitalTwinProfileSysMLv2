import os
import subprocess


def compile_gui_simulator(
    logger,
    output_folder: str,
    module_name: str,
):
    if os.name != "nt":
        raise NotImplementedError(
            "The GUI simulator compilation is only available for Windows."
        )

    original_dir = os.getcwd()
    os.chdir(output_folder)

    try:
        logger.info("Compiling Simulator with gcc.")

        output_file = f"{module_name.lower()}.c"

        subprocess.run(
            [
                "gcc",
                "-shared",
                "-fPIC",
                "simulator.c",
                output_file,
                "-o",
                "integration.dll",
            ],
            check=True,
        )

        logger.info(f"Compiled file: {output_file}")

        logger.info("Building standalone simulator executable with pyinstaller.")

        subprocess.run(
            [
                "pyinstaller",
                "-F",
                "--add-binary",
                "integration.dll;.",
                "--log-level",
                "WARN",
                "-y",
                "--distpath=.",
                "simulator.py",
            ],
            check=True,
        )

        logger.info(f"Built executable for simulator.py (e.g. simulator.exe).")

    finally:
        os.chdir(original_dir)
