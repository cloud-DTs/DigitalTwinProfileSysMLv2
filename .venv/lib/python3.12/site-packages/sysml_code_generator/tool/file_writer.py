import os

from sysml_code_generator.interface.result import Result


class FileWriter:
    def __init__(
        self,
        logger,
    ):
        self.__logger = logger

    def write(
        self,
        results: list[Result],
        output_folder: str,
    ):
        for result in results:
            output_path = os.path.abspath(
                os.path.join(
                    output_folder,
                    result.filename,
                )
            )

            with open(
                output_path,
                "wb",
            ) as output_file:
                output_file.write(result.content.encode("UTF-8"))

            self.__logger.info(f"Wrote file: {output_path}")
