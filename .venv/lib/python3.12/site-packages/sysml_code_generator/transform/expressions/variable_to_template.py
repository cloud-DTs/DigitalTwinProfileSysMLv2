from sysml_code_generator.model.generator.guard.operand import Operand


def c_operand_variable(operand: Operand) -> str:
    name = operand.name

    if len(operand.path) > 0:
        path = "__".join(operand.path)
        name = "__".join([path, operand.name])

    return name
