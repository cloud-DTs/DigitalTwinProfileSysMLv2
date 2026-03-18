from typing import List

from jinja2 import Environment, FileSystemLoader

from sysml_code_generator.interface.result import Result, ResultFile
from sysml_code_generator.renderer.rendering_task import RenderingTask

# https://ttl255.com/jinja2-tutorial-part-3-whitespace-control/


class Renderer:
    __template_definitions: List[RenderingTask]

    def __init__(
        self,
        template_folder: str,
        logger,
    ):
        self.__logger = logger

        self.__jinja = Environment(
            loader=FileSystemLoader(template_folder),
            trim_blocks=True,
        )

    def render(
        self,
        tasks: list[RenderingTask],
    ) -> list[ResultFile]:
        results = []

        for task in tasks:
            template = self.__jinja.get_template(task.template_name)
            output = template.render(variables=task.variables)

            result = ResultFile(
                filename=task.output_filename,
                content=output,
            )

            results.append(result)

        return results
