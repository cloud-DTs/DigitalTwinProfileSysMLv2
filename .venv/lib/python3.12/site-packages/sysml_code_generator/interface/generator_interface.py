from typing import Protocol

from sysml_code_generator.interface.result import Result


class GeneratorInterface(Protocol):
    def generate(
        self,
        element_name: str,
    ) -> Result:
        raise NotImplementedError()

    def build(
        self,
        logger,
        folder: str,
        result: Result,
    ) -> None:
        raise NotImplementedError()
