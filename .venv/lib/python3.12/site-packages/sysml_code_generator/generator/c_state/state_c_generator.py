from sysml_code_generator.interface.generator_interface import GeneratorInterface
from sysml_code_generator.interface.result import Result
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.generate_state_machine_code import (
    generate_state_machine_code,
)
from sysml_code_generator.search.state.state_machine_loader import StateMachineLoader
from sysml_code_generator.transform.state.state_machine_transformer import (
    StateMachineTransformer,
)


class StateMachineCGenerator(GeneratorInterface):
    def __init__(
        self,
        state_machine_loader: StateMachineLoader,
        transformer: StateMachineTransformer,
        renderer: Renderer,
        logger,
    ):
        self.__state_machine_loader = state_machine_loader
        self.__transformer = transformer
        self.__renderer = renderer
        self.__logger = logger

    def generate(
        self,
        element_name: str,
    ) -> Result:
        state_machine_data = self.__state_machine_loader.load(
            qualified_name=element_name,
        )

        template_vars = self.__transformer.transform(
            state_machine_data=state_machine_data,
        )

        self.__logger.info("Generating state machine code.")

        results = generate_state_machine_code(
            renderer=self.__renderer,
            template_vars=template_vars,
        )

        self.__logger.info("Finished state machine code generation.")

        return Result(
            files=results,
            info={
                "module_name": template_vars.name.lower(),
            },
        )
