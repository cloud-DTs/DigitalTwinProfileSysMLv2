from sysml_code_generator.interface.generator_interface import GeneratorInterface
from sysml_code_generator.interface.result import Result
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.generate_action_code import generate_action_code
from sysml_code_generator.search.action.action_loader import ActionLoader
from sysml_code_generator.transform.action.action_to_template_variables import (
    action_to_template_variables,
)


class ActionCGenerator(GeneratorInterface):
    def __init__(
        self,
        action_loader: ActionLoader,
        renderer: Renderer,
    ):
        self.__action_loader = action_loader
        self.__renderer = renderer

    def generate(
        self,
        element_name: str,
        build: bool = False,
    ) -> Result:
        raise NotImplementedError("Actions are not yet supported.")

        action_data = self.__action_loader.load(
            qualified_name=element_name,
        )

        template_vars = action_to_template_variables(
            action_data=action_data,
        )

        files = generate_action_code(
            renderer=self.__renderer,
            template_vars=template_vars,
        )

        return Result(
            files=files,
            info={},
        )
