from typing import Optional


def get_optional_id(data: dict, field: str) -> Optional[str]:
    value = data.get(field)

    if value is None:
        return None

    if not isinstance(value, dict):
        raise ValueError("Expected data field to be a dict.")

    if "@id" not in value:
        raise ValueError(
            "Expected data item to have @id field which might be an empty string."
        )

    return value["@id"]


def get_id(data: dict, field: str) -> str:
    id_ = get_optional_id(data, field)

    if id_ is None:
        raise ValueError("No ID in API data.")

    return id_


def get_string(data: dict, field: str) -> str:
    value = data.get(field)

    if data is None:
        return ""

    return str(value)


def get_bool(data: dict, field: str) -> bool:
    value = data.get(field)

    if data is None:
        return False

    if isinstance(value, str):  # syson bullshit
        if value == "True" or value == "true" or value == "1":
            bool_value = True
        elif value == "False" or value == "false" or value == "0":
            bool_value = False
        else:
            raise ValueError(f"Unexpected value in bool field: {field} {value}")
    elif isinstance(value, bool):
        bool_value = value
    else:
        type_ = type(value)
        raise ValueError(f"Unexpected type in bool field: {field} {type_}")

    return bool_value


def get_list_of_ids(data, field) -> list[str]:
    ids = []

    values = data.get(field)

    if values is None:
        return ids

    if not isinstance(values, list):
        raise ValueError("Expected data to be a list.")

    for item in values:
        if not isinstance(item, dict):
            raise ValueError("Expected data item to be a dict.")

        if "@id" not in item:
            raise ValueError("Expected data item to have @id field.")

        ids.append(item["@id"])

    return ids
