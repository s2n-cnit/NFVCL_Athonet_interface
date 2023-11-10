"""Blue5gModel

Base model for 5g blueprints (NFVCL)

Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, constr, HttpUrl


class Pool(BaseModel):
    cidr: str


class SubDataNets(BaseModel):
    net_name: str = Field(..., description="set net-name, exp: 'boh'")
    dnn: str = Field(..., description="set dnn, exp: 'internet'")
    dns: str
    pools: List[Pool]
    uplinkAmbr: Optional[str]
    downlinkAmbr: Optional[str]
    default5qi: Optional[str]


class NetworkEndPoints(BaseModel):
    mgt: Optional[str] = None
    wan: Optional[str] = None
    data_nets: List[SubDataNets]


class SubFlows(BaseModel):
    flowId: str = Field(..., description="set flow Id, exp: f0")
    ipAddrFilter: Optional[str] = Field(None, description="set IP address filter")
    qi: constr(regex=r"[0-9]")
    gfbr: Optional[str] = Field(..., description="set gfbr, exp: 100Mbps")


class SubpduSessions(BaseModel):
    pduSessionId: str = Field(..., description="set pduSession Id, exp: p0")
    pduSessionAmbr: Optional[str] = Field(..., description="set pduSessionAmbr, exp: 10Mbps")
    flows: List[SubFlows] = Field(default=[])


class SubProfileParams(BaseModel):
    isolationLevel: Literal["ISOLATION", "NO_ISOLATION"]
    sliceAmbr: Optional[str] = Field('1000Mbps', description="Set sliceAmber, exp: 1000Mbps")
    ueAmbr: Optional[str] = Field('50Mbps', description="Set ueAmbr, exp: 50Mbps")
    maximumNumberUE: Optional[int]
    pduSessions: List[SubpduSessions]


class SubLocationConstraints(BaseModel):
    geographicalAreaId: str
    # fixme: Double check for the length
    tai: constr(regex=r"^[0-9]+$") = Field(..., min_length=10, max_length=11)


class SubEnabledUEList(BaseModel):
    ICCID: str = Field("*", description="set the ICCID")


class SubSliceProfiles(BaseModel):
    sliceId: str
    sliceType: Literal["EMBB", "URLLC", "MMTC"]
    dnnList: List[str] = Field([], description="set dnn-list as a listst on names")
    profileParams: SubProfileParams
    locationConstraints: List[SubLocationConstraints]
    enabledUEList: List[SubEnabledUEList]


class SubSnssai(BaseModel):
    sliceId: str
    sliceType: Literal["EMBB", "URLLC", "MMTC"]
    pduSessionIds: List[str] = Field(..., description="Set Default slices parameters, exp: ['p0', 'p1']")
    default_slice: Optional[bool]


class SubSubscribers(BaseModel):
    imsi: constr(regex=r'^[0-9]*$', min_length=15, max_length=15)
    k: constr(regex=r'^[a-fA-F0-9]+$', min_length=32, max_length=32)
    opc: constr(regex=r'^[a-fA-F0-9]+$', min_length=32, max_length=32)
    snssai: List[SubSnssai]


class SubConfig(BaseModel):
    network_endpoints: NetworkEndPoints
    plmn: constr(regex=r'^[0-9]*$', min_length=5, max_length=6) = Field(
        ...,
        description='PLMN identifier of the mobile network'
    )
    sliceProfiles: Optional[List[SubSliceProfiles]] = Field(..., description="Set Default slices parameters")
    subscribers: List[SubSubscribers]


class SubSlices(BaseModel):
    sliceType: Literal["EMBB", "URLLC", "MMTC"]
    sliceId: str


class SubArea(BaseModel):
    id: int
    nci: str
    idLength: int
    core: bool = Field(default=True)
    slices: Optional[List[SubSlices]] = Field(default=[],description="set slices ")


class Create5gModel(BaseModel):
    type: Literal["5G"]
    callbackURL: Optional[HttpUrl] = Field(
        default='',
        description='url that will be used to notify when the topology terraform ends'
    )
    config: SubConfig
    areas: List[SubArea] = Field(..., description="Set area")


class Free5gck8sBlueCreateModel(Create5gModel):
    type: Literal["Free5GC_K8s"]


#######################################################################
# Simplified model
class MiniDataNet(BaseModel):
    default5qi : str


class MiniNetworkEndpoints(BaseModel):
    data_nets: List[MiniDataNet]


class MiniProfileParams(BaseModel):
    sliceAmbr: str
    ueAmbr = str
    maximumNumberUE = int


class MiniSliceProfile(BaseModel):
    sliceId: str
    sliceType: str
    profileParams: MiniProfileParams


class MiniSubscriber(BaseModel):
    imsi: str


class MiniConfig(BaseModel):
    network_endpoints: MiniNetworkEndpoints
    sliceProfiles: List[MiniSliceProfile]
    subscribers: List[MiniSubscriber]


class MiniFree5gcModel(BaseModel):
    callbackURL: Optional[HttpUrl] = Field(
        default='',
        description='url that will be used to notify when the topology terraform ends'
    )
    config: MiniConfig


























