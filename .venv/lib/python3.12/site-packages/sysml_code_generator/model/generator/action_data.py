from dataclasses import dataclass

from sysml_code_generator.model.sysml.action_usage import ActionUsage


@dataclass
class ActionData:
    name: str
    steps: list[ActionUsage]
