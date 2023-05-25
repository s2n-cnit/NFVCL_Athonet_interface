"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it)
"""
from __future__ import annotations
from typing import List
from pydantic import BaseModel


class AddImsiRequest(BaseModel):
    imsi: str
    sliceId: str
    usedDataRateUL: int
    usedDataRateDL: int


class AthonetSlice(BaseModel):
    sliceId: str
    site: str
    expDataRateUL: int
    expDataRateDL: int
    userDensity: int
    userSpeed: int
    trafficType: str
    imsi: List[str]