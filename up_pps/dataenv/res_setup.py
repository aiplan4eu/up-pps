from typing import List
from typing import Any
import numpy as np
from dataclasses import dataclass


@dataclass
class SetupTime:
    resourceCode: str
    firstActivityCode: str
    secondActivityCode: str
    setupTime: int = np.nan
