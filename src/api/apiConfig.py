import sysml_v2_api_client

def get_configuration(host) -> sysml_v2_api_client.Configuration:
    global CONFIGURATION
    if CONFIGURATION is None:
        CONFIGURATION = sysml_v2_api_client.Configuration(
            host = host
        )
    return CONFIGURATION

def get_api_client(host) -> sysml_v2_api_client.ApiClient:
    configuration = get_configuration(host)
    return sysml_v2_api_client.ApiClient(configuration)

