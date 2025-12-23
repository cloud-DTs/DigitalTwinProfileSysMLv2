from dataclasses import dataclass
from typing import List, Optional
import shortuuid
import uuid
@dataclass
class TwinModel:
    id: Optional[str] = None
    name: Optional[str] = None

    def get_unique_id(self) -> str:
        base_id = self.id.split('_')[0] 
        return shortuuid.encode(uuid.UUID(base_id))