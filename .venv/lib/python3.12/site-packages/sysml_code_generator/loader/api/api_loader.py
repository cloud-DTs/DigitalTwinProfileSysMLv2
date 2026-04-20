from logging import Logger

from sysml_code_generator.loader.api.api import Api
from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.mapper.api_mapper import ApiMapper
from sysml_code_generator.mapper.exceptions import NoMappingForSysMLType


class ApiLoader:
    def __init__(
        self,
        api: Api,
        mapper: ApiMapper,
        logger: Logger,
    ):
        self.__api = api
        self.__mapper = mapper
        self.__logger = logger

    def load_from_api(
        self,
        api_url: str,
        project_id: str,
        commit_id: str,
        repository: Repository,
        verify_ssl: bool = True,
    ):
        project_id_quoted = self.__api.quote(project_id)
        commit_id_quoted = self.__api.quote(commit_id)

        # TODO: paging
        elements_url = f"/projects/{project_id_quoted}/commits/{commit_id_quoted}/elements?page[size]=100000"

        elements_data = self.__api.request(
            api_base_url=api_url,
            relative_url=elements_url,
            data={},
            method="GET",
            verify_ssl=verify_ssl,
        )

        for element in elements_data:
            try:
                instance = self.__mapper.map(element)
                repository.add_item(instance)
                self.__logger.debug(
                    f"Loaded element {element['@type']} {element['@id']}"
                )
            except NoMappingForSysMLType:
                self.__logger.warning(
                    f"Skipped element {element['@type']} {element['@id']}"
                )
                pass
