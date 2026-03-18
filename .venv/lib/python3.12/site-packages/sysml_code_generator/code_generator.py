from typing import IO

from sysml_code_generator.container import Container
from sysml_code_generator.generator_registry import get_generator
from sysml_code_generator.interface.result import Result


class CodeGenerator:
    def __init__(
        self,
        container: Container = None,
    ):
        self.__container = container or Container()
        self.__module_detector = self.__container.module_detector

    def generate_from_json_stream(
        self,
        json_data: IO,
        element_name: str,
        generator_type: str,
    ) -> Result:
        loader = self.__container.json_loader

        loader.load_from_stream(
            json_data=json_data,
            repository=self.__container.repository,
        )

        generator = get_generator(
            generator_type=generator_type,
            container=self.__container,
        )

        result = generator.generate(
            element_name=element_name,
        )

        return result

    def generate_from_api_endpoint(
        self,
        api_base_url: str,
        project_name: str,
        verify_ssl: bool,
        element_name: str,
        generator_type: str,
    ) -> Result:
        finder = self.__container.api_finder
        loader = self.__container.api_loader

        project_data = finder.find_project_by_name(
            api_base_url=api_base_url,
            project_name=project_name,
            verify_ssl=verify_ssl,
        )

        project_id = project_data["project_id"]
        branch_id = project_data["default_branch"]

        commit_id = finder.find_commit(
            api_base_url=api_base_url,
            project_id=project_id,
            branch_id=branch_id,
            verify_ssl=verify_ssl,
        )

        loader.load_from_api(
            api_url=api_base_url,
            project_id=project_id,
            commit_id=commit_id,
            repository=self.__container.repository,
            verify_ssl=verify_ssl,
        )

        generator = get_generator(
            generator_type=generator_type,
            container=self.__container,
        )

        result = generator.generate(
            element_name=element_name,
        )

        return result
