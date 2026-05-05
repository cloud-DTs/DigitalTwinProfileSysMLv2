from dataclasses import dataclass


@dataclass
class ResultFile:
    filename: str
    content: str


@dataclass
class Result:
    files: list[ResultFile]
    info: dict
