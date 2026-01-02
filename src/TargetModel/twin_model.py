from dataclasses import dataclass
from typing import List, Optional

import uuid
@dataclass
class TwinModel():
    id: Optional[str] = None
    name: Optional[str] = None

    def to_hierarchy_dict(self) ->dict:
        return {}

    def to_iot_device_dict(self) -> dict:
        return {}

    def to_event_dict(self) -> dict:
        return {}

    def to_config_dict(self) -> dict:
        return {}
