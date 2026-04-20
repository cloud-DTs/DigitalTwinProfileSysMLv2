from logging import Logger
from typing import Optional

from sysml_code_generator.loader.api.api import Api


class ApiFinder:
    def __init__(
        self,
        api: Api,
        logger: Logger,
    ):
        self.__api = api
        self.__logger = logger

    def find_project_by_name(
        self,
        api_base_url: str,
        project_name: str,
        verify_ssl: bool = True,
    ) -> Optional[dict[str, str]]:
        projects_url = f"/projects"

        projects_data = self.__api.request(
            api_base_url=api_base_url,
            relative_url=projects_url,
            data={},
            method="GET",
            verify_ssl=verify_ssl,
        )

        for project_data in projects_data:
            if project_data["name"] == project_name:
                return {
                    "project_id": project_data["@id"],
                    "default_branch": project_data["defaultBranch"]["@id"],
                }

        return None

    def find_commit(
        self,
        api_base_url: str,
        project_id: str,
        branch_id: str,
        verify_ssl: bool = True,
    ) -> str:
        project_id_quoted = self.__api.quote(project_id)
        branch_id_quoted = self.__api.quote(branch_id)

        branch_url = f"/projects/{project_id_quoted}/branches/{branch_id_quoted}"

        data = self.__api.request(
            api_base_url=api_base_url,
            relative_url=branch_url,
            data={},
            method="GET",
            verify_ssl=verify_ssl,
        )

        return data["head"]["@id"]
