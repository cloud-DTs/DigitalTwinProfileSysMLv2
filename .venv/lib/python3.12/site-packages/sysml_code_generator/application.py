import argparse
import os

from sysml_code_generator.code_generator import CodeGenerator
from sysml_code_generator.configuration import Configuration
from sysml_code_generator.container import Container
from sysml_code_generator.generator_registry import get_generator


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    example_file = os.path.join(dir_path, "example", "traffic_light.json")

    parser = argparse.ArgumentParser(
        prog="SysML v2 Code Generator",
        description="Generate executable code from a SysML v2 model.",
    )

    json_argument_group = parser.add_argument_group("JSON source")
    api_argument_group = parser.add_argument_group("API source")

    json_argument_group.add_argument(
        "--json",
        help="URL of a json file to load the model from.",
        default=example_file,
    )

    parser.add_argument(
        "--element",
        help="Qualified name of the element to build code for.",
        default="TrafficLightExample::TrafficLight",
    )

    parser.add_argument(
        "--output",
        help="Existing folder for the generated files.",
        default=os.getcwd(),
    )

    parser.add_argument(
        "--build",
        help="Compile the result. May need additional installed software on the system.",
        action="store_true",
    )

    parser.add_argument(
        "--generator",
        help="Generator type. ",
        choices=[
            "auto",
            "state_c",
            "state_c_sim_cli",
            "state_c_sim_gui",
            "action_c",
        ],
        default="auto",
    )

    api_argument_group.add_argument(
        "--api_url",
        help="Base URL of the API to fetch the data from.",
    )

    api_argument_group.add_argument(
        "--project_name",
        help="Project name.",
    )

    api_argument_group.add_argument(
        "--disable_ssl_verification",
        help="",
        action="store_true",
    )

    args = parser.parse_args()

    config = Configuration()
    container = Container(config=config)
    application = CodeGenerator(container=container)
    file_writer = container.file_writer

    if args.api_url:
        result = application.generate_from_api_endpoint(
            api_base_url=args.api_url,
            project_name=args.project_name,
            verify_ssl=not args.disable_ssl_verification,
            element_name=args.element,
            generator_type=args.generator,
        )
    else:
        with open(args.json) as input_stream:
            result = application.generate_from_json_stream(
                json_data=input_stream,
                element_name=args.element,
                generator_type=args.generator,
            )

    file_writer.write(
        results=result.files,
        output_folder=args.output,
    )

    if args.build:
        generator = get_generator(
            generator_type=args.generator,
            container=container,
        )

        generator.build(
            logger=container.logger,
            result=result,
            folder=args.output,
        )


if __name__ == "__main__":
    main()
