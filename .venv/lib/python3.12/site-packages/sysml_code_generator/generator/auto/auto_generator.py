from sysml_code_generator.interface.generator_interface import GeneratorInterface
from sysml_code_generator.interface.result import Result
from sysml_code_generator.tool.module_detector import ModuleDetector


class AutoGenerator(GeneratorInterface):
    def __init__(
        self,
        module_detector: ModuleDetector,
    ):
        self.__module_detector = module_detector

    def generate(
        self,
        element_name: str,
        build: bool = False,
    ) -> Result:
        generator = self.__module_detector.detect(element_name=element_name)

        return generator.generate(
            element_name=element_name,
        )
