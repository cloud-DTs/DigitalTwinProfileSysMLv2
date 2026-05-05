from dataclasses import dataclass

from sysml_code_generator.model.template.action_c.parameter import Parameter


@dataclass
class Function:
    name: str
    inputs: list[Parameter]
    outputs: list[Parameter]
