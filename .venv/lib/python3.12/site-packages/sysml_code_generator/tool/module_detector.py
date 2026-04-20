from sysml_code_generator.exception.element_not_found_error import ElementNotFoundError
from sysml_code_generator.exception.unsupported_model_error import UnsupportedModelError
from sysml_code_generator.generator.c_action.action_c_generator import ActionCGenerator
from sysml_code_generator.generator.c_state.state_c_generator import (
    StateMachineCGenerator,
)
from sysml_code_generator.interface.generator_interface import GeneratorInterface
from sysml_code_generator.model.sysml.action_usage import ActionUsage
from sysml_code_generator.model.sysml.state_definition import StateDefinition
from sysml_code_generator.model.sysml.state_usage import StateUsage
from sysml_code_generator.search.search import Search


class ModuleDetector:
    # usability: detect module by element type

    def __init__(
        self,
        logger,
        search: Search,
        state_machine_c_generator: StateMachineCGenerator,
        action_c_generator: ActionCGenerator,
    ):
        self.__logger = logger
        self.__search = search
        self.__state_machine_c_generator = state_machine_c_generator
        self.__action_c_generator = action_c_generator

    def detect(self, element_name: str) -> GeneratorInterface:
        element = self.__search.get_by_qualified_name(
            qualified_name=element_name,
        )

        if isinstance(element, StateDefinition) or isinstance(element, StateUsage):
            self.__logger.info(f"Detected input element type: {element.type_}")
            return self.__state_machine_c_generator

        elif isinstance(element, ActionUsage):
            self.__logger.info(f"Detected input element type: {element.type_}")
            return self.__action_c_generator

        elif element is None:
            raise ElementNotFoundError(f"Element not found: {element_name}")

        else:
            raise UnsupportedModelError(
                f"No code generation implemented for type: {element.type_}"
            )
