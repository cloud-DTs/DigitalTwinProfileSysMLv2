import os
import subprocess


def compile_cli_simulator(
    logger,
    output_folder: str,
    module_name: str,
):
    original_dir = os.getcwd()
    os.chdir(output_folder)

    try:
        logger.info("Compiling Simulator with gcc.")
        output_file = f"{module_name.lower()}.exe"

        if os.name != "nt":
            output_file = f"{module_name.lower()}"

        subprocess.run(
            [
                "gcc",
                f"{module_name.lower()}.c",
                "-o",
                output_file,
            ],
            check=True,
        )

        logger.info(f"Compiled CLI simulator: {output_file}")

    finally:
        os.chdir(original_dir)
