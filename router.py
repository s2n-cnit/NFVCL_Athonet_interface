"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from athonetRestApi import AthonetRestAPI
from utils import create_logger, Database
from typing import Union, List
from models import *

athonetHost = "127.0.0.1"

logger = create_logger("Router")

db = Database()

class RestAnswer202(BaseModel):
    description: str = "operation submitted"
    status: str = "submitted"

router = APIRouter(
    prefix="/v1",
    tags=["NorthRouter"],
    responses={404:{"description": "Not found"}}
)

athonetInterface = AthonetRestAPI(athonetHost)

def getSliceFromSlices(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel],
                       athonetSlicesList: List[AthonetSlice]) -> Union[AthonetSlice,None]:
    """
    Choose the better slice
    :param free5gcMessage:
    :param athonetSlicesList:
    :return:
    """
    athonetSliceSearch = AthonetSlice.fromFree5gc(free5gcMessage)
    for item in athonetSlicesList:
        if (
                item.expDataRateUL >= athonetSliceSearch.expDataRateUL and
                item.expDataRateDL >= athonetSliceSearch.expDataRateDL and
                item.userDensity >= athonetSliceSearch.userDensity and
                item.userSpeed >= athonetSliceSearch.userSpeed
        ):
            return athonetSliceSearch
    return None

@router.post("/addslice", response_model=RestAnswer202)
async def addImsiToSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel]):
    try:
        readySlices: AthonetSlice | [AthonetSlice] = db.readAthonetSlices()
        if type(readySlices) != List:
            readySlicesList = [readySlices]
        else:
            readySlicesList = readySlices
        imsiToAdd = free5gcMessage.config.subscribers[0].imsi
        foundSlice = next((item for item in readySlicesList
                           if imsiToAdd in item.imsi), None)
        if foundSlice:
            logger.info("The IMSI ({}) is yet registered in the slice {}".format(imsiToAdd, foundSlice.sliceId))
            raise HTTPException(status_code=404,
                                detail="The IMSI ({}) is yet registered in the slice {}".format(imsiToAdd, foundSlice.sliceId))
        else:
            athonetSlice = getSliceFromSlices(free5gcMessage, readySlicesList)
            if not athonetSlice:
                logger.warn("No slice on Athonet match requirements")
                raise HTTPException(status_code=502, detail="No slice on Athonet match requirements")
            addImsiToSlice = AddImsiRequest.fromAthonetSliceModel(athonetSlice)
            addImsiToSlice.imsi = imsiToAdd
            athonetInterface.addImsiToSlice(addImsiToSlice)
    except Exception as e:
        logger.warn("Impossible to add the slice: {} - {}".format(free5gcMessage, e))
        raise HTTPException(status_code=502, detail="Impossible to add the slice: {} - {}"
                            .format(free5gcMessage, e))

@router.post("/delslice", response_model=RestAnswer202)
async def delImsiFromSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel]):
    try:
        readySlices: AthonetSlice | [AthonetSlice] = db.readAthonetSlices()
        if type(readySlices) != List:
            readySlicesList = [readySlices]
        else:
            readySlicesList = readySlices
        imsiToRemove = free5gcMessage.config.subscribers[0].imsi
        foundSlice = next((item for item in readySlicesList
                           if imsiToRemove in item.imsi), None)
        if not foundSlice:
            logger.warn("IMSI ({}) was not registered. Nothing to remove".format(imsiToRemove))
            raise HTTPException(status_code=502, detail="IMSI ({}) wan not registered."
                                                         " Nothing to remove".format(imsiToRemove))

        # TODO: Athonet REST API to remove IMSI from slice
        raise HTTPException(status_code=404,
                            detail="Athonet REST API to remove IMSI is not yet implemented")
    except Exception as e:
        logger.warn("Impossible to delete IMSI ({}) from slice"
                    .format(free5gcMessage.config.subscribers[0].imsi))
        raise HTTPException(status_code=502, detail="Impossible to delete IMSI ({}) from slice: {}"
                            .format(free5gcMessage.config.subscribers[0].imsi, e))


@router.post("/checkslice", response_model=RestAnswer202)
async def checkImsiInSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel]):
    try:
        readySlices: AthonetSlice | [AthonetSlice] = db.readAthonetSlices()
        if type(readySlices) != List:
            readySlicesList = [readySlices]
        else:
            readySlicesList = readySlices
        imsiToCheck = free5gcMessage.config.subscribers[0].imsi
        foundSlice = next((item for item in readySlicesList
                           if imsiToCheck in item.imsi), None)
        if not foundSlice:
            raise HTTPException(status_code=404, detail="IMSI not yet associated to the slice")
    except Exception as e:
        raise HTTPException(status_code=502, detail="Impossible to check the slice status: {}"
                            .format(e))

@router.post("/south/addslices", response_model=RestAnswer202)
async def addSlices(athonetSlices: Union[AthonetSlice, List[AthonetSlice]]):
    logger.info("Received message from Athonet: {}".format(athonetSlices))
    try:
        db.writeAthonetSlices(athonetSlices)
    except Exception as e:
        logger.warn("Impossible to write the slices on the DB")
        raise HTTPException(status_code=502, detail="Impossible to accept the slices")





























