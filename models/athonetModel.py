"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it)
"""
from __future__ import annotations
from typing import List, Union
from pydantic import BaseModel
from models.blue5gModel import MiniFree5gcModel, Free5gck8sBlueCreateModel
from utils import BandwidthConvertion


class AddImsiRequest(BaseModel):
    imsi: str = ""
    sliceId: str = ""
    usedDataRateUL: int = 0
    usedDataRateDL: int = 0

    @classmethod
    def fromAthonetSliceModel(cls, msg: AthonetSlice) -> AddImsiRequest:
        addImsiRequest = AddImsiRequest()
        addImsiRequest.imsi = ""
        addImsiRequest.sliceId = msg.sliceId
        addImsiRequest.usedDataRateDL = msg.expDataRateDL
        addImsiRequest.usedDataRateUL = msg.expDataRateUL
        return addImsiRequest

class AthonetSlice(BaseModel):
    sliceId: str = ""
    site: str = ""
    expDataRateUL: int = 0
    expDataRateDL: int = 0
    userDensity: int = 0
    userSpeed: int = 0
    trafficType: str = ""
    imsi: List[Union[str, None]] = []
    type: str = ""

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
        athonetSlice.type = msg.config.sliceProfiles[0].sliceType
        return athonetSlice
