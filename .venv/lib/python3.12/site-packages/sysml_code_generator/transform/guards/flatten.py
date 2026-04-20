from typing import Union

from sysml_code_generator.model.generator.guard.part import ExpressionPart
from sysml_code_generator.model.sysml.sysml_entity import SysMLEntity


def flatten(
    expression_parts: list[Union[ExpressionPart, SysMLEntity]],
) -> list[Union[ExpressionPart, SysMLEntity]]:
    parts_flat = []

    for part in expression_parts:
        if isinstance(part, list):
            # recurse
            flat_parts = flatten(part)

            for flat_part in flat_parts:
                parts_flat.append(flat_part)
        else:
            parts_flat.append(part)

    return parts_flat
