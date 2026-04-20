import requests


class Api:
    def request(
        self,
        api_base_url: str,
        relative_url: str,
        data: dict,
        method: str,
        verify_ssl: bool = True,
    ):
        url = api_base_url + relative_url
        response = requests.request(
            method=method,
            url=url,
            json=data,
            verify=verify_ssl,
        )

        if response.status_code != 200:
            raise Exception("API request failed.", response)

        query_response_json = response.json()

        return query_response_json

    def quote(self, string: str):
        return requests.utils.quote(string, safe="")
