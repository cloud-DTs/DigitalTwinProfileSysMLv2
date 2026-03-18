from sysml_code_generator.interface.result import Result, ResultFile
from sysml_code_generator.model.template.state_c.state_variables import StateVariables
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.rendering_task import RenderingTask

stm_c_template = "state_c/state_machine/stm.c.jinja"
stm_h_template = "state_c/state_machine/stm.h.jinja"


def generate_state_machine_code(
    renderer: Renderer,
    template_vars: StateVariables,
) -> list[ResultFile]:
    return renderer.render(
        tasks=[
            RenderingTask(
                template_name=stm_c_template,
                output_filename=f"{template_vars.name.lower()}.c",
                variables=template_vars,
            ),
            RenderingTask(
                template_name=stm_h_template,
                output_filename=f"{template_vars.name.lower()}.h",
                variables=template_vars,
            ),
        ],
    )
