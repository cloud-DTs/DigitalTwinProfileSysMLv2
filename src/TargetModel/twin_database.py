from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from .twin_model import TwinModel

if TYPE_CHECKING:
    from .twin import Twin

class TwinDataBaseTier(Enum):
    HOT = "HOT"
    COLD = "COLD"

class TwinDataBaseType(Enum):
    RELATIONAL = "RELATIONAL"
    TIMESERIES = "TIMESERIES"

@dataclass
class TwinDatabase(TwinModel):
    tier: TwinDataBaseTier = TwinDataBaseTier.HOT
    dbType: TwinDataBaseType = TwinDataBaseType.RELATIONAL
    retentionDays: int = 30
    parentTwin: Twin = None
