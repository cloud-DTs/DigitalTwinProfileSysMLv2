from sysml_code_generator.model.generator.action_data import ActionData
from sysml_code_generator.model.template.action_c.action_variables import (
    ActionVariables,
    Function,
)


def action_to_template_variables(action_data: ActionData) -> ActionVariables:
    main_function_inputs = []  # TODO
    main_function_outputs = []  # TODO

    main_function = Function(
        name=action_data.name,
        inputs=main_function_inputs,
        outputs=main_function_outputs,
    )

    sub_functions = []

    for step in action_data.steps:
        inputs = []  # TODO
        outputs = []  # TODO

        sub_functions.append(Function(name=step.name, inputs=inputs, outputs=outputs))

    return ActionVariables(
        main_function=main_function,
        sub_functions=sub_functions,
    )
