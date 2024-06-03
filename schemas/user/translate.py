from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranslateSchema(BaseModel):
    altitude_1: float
    length_1: float
    altitude_2: float
    length_2: float
    