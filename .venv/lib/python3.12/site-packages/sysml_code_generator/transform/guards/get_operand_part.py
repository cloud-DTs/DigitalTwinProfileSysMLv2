from typing import Union

from sysml_code_generator.interface.repository_interface import RepositoryInterface
from sysml_code_generator.model.generator.guard.operand import Operand
from sysml_code_generator.model.sysml.attribute_usage import AttributeUsage
from sysml_code_generator.model.sysml.reference_usage import ReferenceUsage


def get_operand_part(
    expression: Union[ReferenceUsage, AttributeUsage], repository: RepositoryInterface
) -> Operand:
    data_type = expression.get_first_data_type(repository)

    name = expression.name
    # also has a qualified name, but we want to track to the usage instance via dot operator

    if name == "":
        raise ValueError("Missing name on reference usage.")

    return Operand(name=name, data_type=data_type, path=[])
