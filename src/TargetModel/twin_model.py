from dataclasses import dataclass
from typing import List, Optional

import uuid
@dataclass
class TwinModel():
    id: Optional[str] = None
    name: Optional[str] = None

    def get_unique_id(self) -> str:
        return self.id