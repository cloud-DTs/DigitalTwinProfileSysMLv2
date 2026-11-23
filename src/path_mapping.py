import os
from pathlib import Path

PATH_MAP_ENV = "DTP_PATH_MAP"


def normalize_path_prefix(path: str) -> str:
    return path.replace("\\", "/").rstrip("/")


def map_configured_path(path: str) -> str:
    if not path or path == "None":
        return path

    normalized_path = normalize_path_prefix(path)
    for mapping in os.getenv(PATH_MAP_ENV, "").split(";"):
        if "=" not in mapping:
            continue

        source_prefix, target_prefix = mapping.split("=", 1)
        source_prefix = normalize_path_prefix(source_prefix.strip())
        target_prefix = target_prefix.strip()

        if not source_prefix or not target_prefix:
            continue

        if normalized_path == source_prefix:
            return target_prefix

        if normalized_path.startswith(source_prefix + "/"):
            relative_path = normalized_path[len(source_prefix) + 1:]
            return str(Path(target_prefix, *relative_path.split("/")))

    return path
