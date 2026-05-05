####### TRANSITIONS - GUARDS - VARIABLES ###################

for variable in get_guard_variables(
    guards=guards,
    repository=self.__repository,
):
    variable_data = Variable(
        name=c_operand_variable(variable),
        data_type=map_data_type(
            variable.data_type
        ),  # TODO: leave it to the renderer to map
        data_type_sysml=variable.data_type,
    )

    variables.variables.append(variable_data)
