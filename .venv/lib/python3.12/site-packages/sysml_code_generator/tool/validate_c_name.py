import re

from sysml_code_generator.exception.unsupported_name_error import UnsupportedNameError


def validate_c_name(
    name: str,
) -> None:
    validation_regex = "^[a-zA-Z_][a-zA-Z0-9_]*$"

    is_valid = re.match(validation_regex, name)

    if not is_valid:
        raise UnsupportedNameError(f"Unsupported character in name: {name}")
