from dataclasses import dataclass

from sysml_code_generator.model.generator.guard.part import ExpressionPart


@dataclass
class Operand(ExpressionPart):
    data_type: str
    path: list[str]  # e.g. ["system", "subsystem", ...]
