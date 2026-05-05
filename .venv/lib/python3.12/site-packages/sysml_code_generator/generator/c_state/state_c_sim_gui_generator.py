from sysml_code_generator.interface.generator_interface import GeneratorInterface
from sysml_code_generator.interface.result import Result
from sysml_code_generator.model.template.state_c.state_variables import StateVariables
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.generate_state_machine_code import (
    generate_state_machine_code,
)
from sysml_code_generator.renderer.simulator.renderer import generate_simulator_code
from sysml_code_generator.search.state.state_machine_loader import StateMachineLoader
from sysml_code_generator.tool.compile_gui_simulator import compile_gui_simulator
from sysml_code_generator.transform.state.state_machine_transformer import (
    StateMachineTransformer,
)


class StateMachineSimGuiGenerator(GeneratorInterface):
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

        state_machine_results = generate_state_machine_code(
            renderer=self.__renderer,
            template_vars=template_vars,
        )

        self.__logger.info("Generating simulator code.")

        simulator_results = generate_simulator_code(
            renderer=self.__renderer,
            template_vars=template_vars,
        )

        self.__logger.info("Finished state machine code generation.")

        return Result(
            files=state_machine_results + simulator_results,
            info={
                "module_name": template_vars.name.lower(),
            },
        )

    def build(
        self,
        logger,
        folder: str,
        result: Result,
    ) -> None:
        compile_gui_simulator(
            logger=self.__logger,
            output_folder=folder,
            module_name=result.info["module_name"],
        )
