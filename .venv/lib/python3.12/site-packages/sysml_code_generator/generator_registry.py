from sysml_code_generator.container import Container
from sysml_code_generator.interface.generator_interface import GeneratorInterface


def get_generator(generator_type: str, container: Container) -> GeneratorInterface:
    generators = {
        "auto": container.auto_module,
        "state_c": container.state_machine_c_generator,
        "state_c_sim_cli": container.state_machine_sim_cli_generator,
        "state_c_sim_gui": container.state_machine_sim_gui_generator,
        "action_c": container.action_c_generator,
    }

    generator = generators.get(generator_type)

    if generator is None:
        raise ValueError(f"No generator with type found: {generator_type}")

    return generator
