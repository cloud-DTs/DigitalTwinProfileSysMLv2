from sysml_code_generator.interface.result import Result, ResultFile
from sysml_code_generator.model.template.state_c.state_variables import StateVariables
from sysml_code_generator.renderer.common_renderer import Renderer
from sysml_code_generator.renderer.rendering_task import RenderingTask

simulator_template = "state_c/simulator/simulator.c.jinja"
gui_template = "state_c/simulator/simulator.py.jinja"
instructions_file = "state_c/simulator/build_instructions.md"


def generate_simulator_code(
    renderer: Renderer,
    template_vars: StateVariables,
) -> list[ResultFile]:
    for variable in template_vars.variables:
        sysml_type = variable.data_type_sysml
        c_type = map_c_type(sysml_type)
        ctype_type = map_ctypes(sysml_type)
        tk_type = map_tk_types(sysml_type)
        default_value_c = map_default_c_values(sysml_type)
        variable.data_type_c = c_type
        variable.data_type_ctype = ctype_type
        variable.data_type_tk_type = tk_type
        variable.default_value_c = default_value_c

    return renderer.render(
        tasks=[
            RenderingTask(
                template_name=simulator_template,
                output_filename="simulator.c",
                variables=template_vars,
            ),
            RenderingTask(
                template_name=gui_template,
                output_filename="simulator.py",
                variables=template_vars,
            ),
            RenderingTask(
                template_name=instructions_file,
                output_filename="build_instructions.md",
                variables={},
            ),
        ]
    )


def map_default_c_values(data_type_sysyml):
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "false",
        "ScalarValues::Integer": "0",
        "ScalarValues::Real": "0",
    }

    if data_type_sysyml not in map_:
        raise ValueError()

    return map_[data_type_sysyml]


def map_ctypes(data_type_sysyml):
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "c_bool",
        "ScalarValues::Integer": "c_int",
        "ScalarValues::Real": "c_double",
    }

    if data_type_sysyml not in map_:
        raise ValueError()

    return map_[data_type_sysyml]


def map_tk_types(data_type_sysyml):
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "BooleanVar",
        "ScalarValues::Integer": "DoubleVar",
        "ScalarValues::Real": "IntVar",
    }

    if data_type_sysyml not in map_:
        raise ValueError()

    return map_[data_type_sysyml]


def map_c_type(data_type_sysyml):
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "bool",
        "ScalarValues::Integer": "int",
        "ScalarValues::Real": "double",
    }

    if data_type_sysyml not in map_:
        raise ValueError()

    return map_[data_type_sysyml]


def map_tk_input(data_type_sysyml):
    map_ = {  # DataTyp qualifiedName
        "ScalarValues::Boolean": "Checkbutton",
        "ScalarValues::Integer": "NumberInput",
        "ScalarValues::Real": "NumberInput",
    }

    if data_type_sysyml not in map_:
        raise ValueError()

    return map_[data_type_sysyml]
