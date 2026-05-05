from sysml_code_generator.interface.result import ResultFile
from sysml_code_generator.model.template.action_c.action_variables import (
    ActionVariables,
)
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.rendering_task import RenderingTask

action_c_template = "action_c/action.c.jinja"
action_h_template = "action_c/action.h.jinja"


def generate_action_code(
    renderer: Renderer,
    template_vars: ActionVariables,
) -> list[ResultFile]:
    return renderer.render(
        tasks=[
            RenderingTask(
                template_name=action_c_template,
                output_filename="action.c",
                variables=template_vars,
            ),
            RenderingTask(
                template_name=action_h_template,
                output_filename="action.h",
                variables=template_vars,
            ),
        ],
    )
