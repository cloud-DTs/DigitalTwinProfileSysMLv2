from sysml_code_generator.interface.result import ResultFile
from sysml_code_generator.model.template.state_c.state_variables import StateVariables
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.rendering_task import RenderingTask
from sysml_code_generator.renderer.simulator.renderer import (
    map_c_type,
    map_default_c_values,
)

stm_c_template = "state_c/standalone/stm.c.jinja"


def generate_standalone_cli(
    renderer: Renderer,
    template_vars: StateVariables,
) -> list[ResultFile]:
    for variable in template_vars.variables:
        sysml_type = variable.data_type_sysml
        c_type = map_c_type(sysml_type)
        default_value_c = map_default_c_values(sysml_type)
        variable.data_type_c = c_type
        variable.default_value_c = default_value_c

    return renderer.render(
        tasks=[
            RenderingTask(
                template_name=stm_c_template,
                output_filename=f"{template_vars.name.lower()}.c",
                variables=template_vars,
            ),
        ],
    )
