import json
from logging import Logger
from typing import IO

from sysml_code_generator.loader.repository import Repository
from sysml_code_generator.mapper.api_mapper import ApiMapper
from sysml_code_generator.mapper.exceptions import NoMappingForSysMLType


class JsonLoader:
    def __init__(
        self,
        mapper: ApiMapper,
        logger: Logger,
    ):
        self.__mapper = mapper
        self.__logger = logger

    def load_from_file(
        self,
        json_url: str,
        repository: Repository,
    ) -> None:
        with open(json_url, "rb") as file_handle:
            self.load_from_stream(
                json_data=file_handle,
                repository=repository,
            )

    def load_from_stream(
        self,
        json_data: IO,
        repository: Repository,
    ) -> None:
        data = json.load(json_data)

        skipped = set()

        for item in data:
            id_ = item["identity"]["@id"]
            element = item["payload"]
            type_ = element["@type"]

            element["@id"] = id_  # to be compatible with API data structure

            try:
                instance = self.__mapper.map(element)

                repository.add_item(instance)

                self.__logger.debug(f"Loaded element {type_} {id_}")

            except NoMappingForSysMLType:
                self.__logger.debug(f"Skipped element {type_} {id_}")

                skipped.add(element["@type"])

                pass

        if len(skipped) > 0:
            self.__logger.info(
                "Found not implemented element types during loading: "
                + ", ".join(skipped)
            )
