from dataclasses import dataclass

from sysml_code_generator.model.template.action_c.function import Function


@dataclass
class ActionVariables:
    main_function: Function
    sub_functions: list[Function]
