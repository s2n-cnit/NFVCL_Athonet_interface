"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it)
"""
from __future__ import annotations
from typing import List, Union
from pydantic import BaseModel
from models import MiniFree5gcModel, Free5gck8sBlueCreateModel
from utils import BandwidthConvertion


class AddImsiRequest(BaseModel):
    imsi: str
    sliceId: str
    usedDataRateUL: int
    usedDataRateDL: int

    @classmethod
    def fromAthonetSliceModel(cls, msg: AthonetSlice) -> AddImsiRequest:
        addImsiRequest = AddImsiRequest()
        addImsiRequest.imsi = ""
        addImsiRequest.sliceId = msg.sliceId
        addImsiRequest.usedDataRateDL = msg.expDataRateDL
        addImsiRequest.usedDataRateUL = msg.expDataRateUL
        return addImsiRequest

class AthonetSlice(BaseModel):
    sliceId: str
    site: str
    expDataRateUL: int
    expDataRateDL: int
    userDensity: int
    userSpeed: int
    trafficType: str
    imsi: List[str]

    @classmethod
    def fromFree5gc(cls, msg: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel]) -> AthonetSlice:
        athonetSlice = AthonetSlice()
        athonetSlice.sliceId = ""
        athonetSlice.site = ""
        athonetSlice.expDataRateUL = BandwidthConvertion.convert(
            msg.config.sliceProfiles[0].profileParams.sliceAmbr, "Mbps")
        athonetSlice.expDataRateDL = BandwidthConvertion.convert(
            msg.config.sliceProfiles[0].profileParams.sliceAmbr, "Mbps")
        athonetSlice.userDensity = msg.config.sliceProfiles[0]. profileParams.maximumNumberUE
        athonetSlice.userSpeed = BandwidthConvertion.convert(
            msg.config.sliceProfiles[0].profileParams.ueAmbr, "Mbps")
        athonetSlice.trafficType = ""
        athonetSlice.imsi = []
        return athonetSlice