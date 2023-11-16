"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from athonetRestApi import AthonetRestAPI
from utils import create_logger, Database
from typing import Union, List
from models import *

athonetParametersFile = "athonethost.txt"
imsiListFile = "imsilist.txt"
logger = create_logger("Router")

db = Database(mongoDbName="Athonet")

class RestAnswer202(BaseModel):
    description: str = "operation submitted"
    status: str = "submitted"

router = APIRouter(
    prefix="",
    tags=["Router"],
    responses={404:{"description": "Not found"}}
)

try:
    with open(athonetParametersFile, "r") as f:
        athonetHost = f.readline().split("\n")[0]
        athonetPort = f.readline().split("\n")[0]
        f.close()
        logger.info("Read from file (\"{}\"): Athonet host-port: {} - {}".format(athonetParametersFile,
                                                                                 athonetHost, athonetPort))
except Exception as e:
    logger.error("Impossible to read the file \"{}\"".format(athonetParametersFile))
    raise ValueError("Impossible to read the file \"{}\"".format(athonetParametersFile))

athonetInterface = AthonetRestAPI(athonetHost, athonetPort)

def getImsiListFromFile(fileName: str = ""):
    # imsiList is a list of IMSI, like:
    # 001010000000001
    # 001010000000002
    # ...
    imsiList = []
    try:
        with open(imsiListFile, "r") as f:
            imsiList = f.read().splitlines()
    except Exception as e:
        logger.error("Impossible to read the file \"{}\"".format(imsiListFile))
        raise ValueError("Impossible to read the file \"{}\"".format(imsiListFile))
    return imsiList

def restCallback(callback, requestedOperation, blueId, sessionId, status):
    if callback:
        logger.info("Generating callback message")
        headers = {
                "Content-type": "application/json",
                "Accept": "application/json"
                }
        data = {
                "blueprint":
                {
                    "id": blueId,
                    "type": "Free5GC_K8s"
                },
                "requested_operation": requestedOperation,
                "session_id": blueId,
                "status": status
              }
        r = None
        try:
            r = requests.post(callback, json=data, params=None, verify=False, stream=True, headers=headers)
            return r
        except Exception as e:
            logger.error("Error - posting callback: ", e)
    else:
        logger.info("No callback message is specified")
        return None

def getSliceFromSlices(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel],
                       athonetSlicesList: List[AthonetSlice]) -> Union[AthonetSlice,None]:
    """
    Choose the better slice.
    It uses two algorithm:
     1 - search using the slice name. ex: "EMBB0000001" -> "Induce-5G-Athens-EMBB1"
     2 - search using slice parameters: userDensity, userSpeed and type
    :param free5gcMessage:
    :param athonetSlicesList:
    :return:
    """
    athonetSliceSearch = AthonetSlice.fromFree5gc(free5gcMessage)
    logger.info("requested SLICE: {}".format(athonetSliceSearch))
    for item in athonetSlicesList:
        logger.info("1/2 - comparing (using sliceId) to: {}".format(item))
        if (
                ("{}{}".format(free5gcMessage.config.sliceProfiles[0].sliceType,
                                  int(free5gcMessage.config.sliceProfiles[0].sliceId, 16))).lower() in item.sliceId.lower()
        ):
            return item
    for item in athonetSlicesList:
        logger.info("2/2 - comparing (using parameters) to: {}".format(item))
        if (
                    # expDataRateUL/DL will be set up
                    #item.expDataRateUL >= athonetSliceSearch.expDataRateUL and
                    #item.expDataRateDL >= athonetSliceSearch.expDataRateDL and
                    (item.userDensity >= athonetSliceSearch.userDensity or item.userDensity == 0) and
                    (item.userSpeed >= athonetSliceSearch.userSpeed or item.userSpeed == 0) and
                    item.type.lower() == athonetSliceSearch.type.lower()
        ):
            return item
    return None


def checkAndAddSliceType(sliceType: str, athonetSlices: Union[AthonetSlice, List[AthonetSlice]]):
    if sliceType in {"urllc", "embb"}:
        if type(athonetSlices) != list:
            athonetSlices.type = sliceType
        else:
            for slice in athonetSlices:
                slice.type = sliceType
    else:
        logger.error("slice type \"{}\" not supported".format(sliceType))
        raise Exception("slice type \"{}\" not supported".format(sliceType))


@router.post("/nfvcl/v1/api/blue/Free5GC_K8s/{blue_id}/add_slice", response_model=RestAnswer202)
async def addImsiToSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel], blue_id: str):
    try:
        logger.info("Received message from OSS: {}".format(free5gcMessage))
        callback = free5gcMessage.callbackURL
        readySlices = db.readAthonetSlices()
        if type(readySlices) != list:
            readySlicesList = [readySlices]
        else:
            readySlicesList = readySlices
        #for subscriber in free5gcMessage.config.subscribers:
        for imsiToAdd in getImsiListFromFile():
            logger.info("IMSI to add: {}".format(imsiToAdd))
            foundSlice = next((item for item in readySlicesList
                               if imsiToAdd in item.imsi), None)
            if foundSlice:
                logger.info("The IMSI ({}) is yet registered in the slice {}".format(imsiToAdd, foundSlice.sliceId))
                # raise HTTPException(status_code=404,
                #                     detail="The IMSI ({}) is yet registered in the slice {}".
                #                     format(imsiToAdd, foundSlice.sliceId))
            athonetSlice = getSliceFromSlices(free5gcMessage, readySlicesList)
            if not athonetSlice:
                logger.warn("No slice on Athonet match requirements")
                raise HTTPException(status_code=502, detail="No slice on Athonet match requirements")
            else:
                logger.info("FOUND GOOD SLICE: {}".format(athonetSlice))
            addImsiToSlice = AddImsiRequest.fromAthonetSliceModel(athonetSlice)
            addImsiToSlice.imsi = imsiToAdd
            athonetInterface.addImsiToSlice(addImsiToSlice)
        restCallback(callback, "add_slice", blue_id, blue_id, "ready")
        return RestAnswer202()
    except Exception as e:
        restCallback(callback, "add_slice", blue_id, blue_id, "failed")
        logger.warn("Impossible to add the slice: {} - {}".format(free5gcMessage, e))
        raise HTTPException(status_code=404, detail="Impossible to add the slice: {} - {}"
                            .format(free5gcMessage, e))

@router.delete("/nfvcl/v1/api/blue/Free5GC_K8s/{blue_id}/del_slice", response_model=RestAnswer202)
async def delImsiFromSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel], blue_id: str):
    try:
        logger.info("Received message from OSS: {}".format(free5gcMessage))
        callback = free5gcMessage.callbackURL
        readySlices = db.readAthonetSlices()
        if type(readySlices) != list:
            readySlicesList = [readySlices]
        else:
            readySlicesList = readySlices
        #for subscriber in free5gcMessage.config.subscribers:
        for imsiToRemove in getImsiListFromFile():
            logger.info("IMSI to remove: {}".format(imsiToRemove))
            foundSlice = next((item for item in readySlicesList
                               if imsiToRemove in item.imsi), None)
            if not foundSlice:
                logger.warn("IMSI ({}) was not registered. Nothing to remove".format(imsiToRemove))
                raise HTTPException(status_code=502, detail="IMSI ({}) wan not registered."
                                                             " Nothing to remove".format(imsiToRemove))

            # TODO: Athonet-OTE Interface doesn't de-attach IMSI
            # raise HTTPException(status_code=404,
            #                     detail="Athonet REST API to remove IMSI is not yet implemented")
        restCallback(callback, "del_slice", blue_id, blue_id, "ready")
        return RestAnswer202()
    except Exception as e:
        restCallback(callback, "del_slice", blue_id, blue_id, "failed")
        logger.warn("Impossible to delete IMSI from slice: {}".format(e))
        raise HTTPException(status_code=404, detail="Impossible to delete IMSI from slice: {}"
                            .format(e))


@router.post("/nfvcl/v1/api/blue/Free5GC_K8s/{blue_id}/check_slice", response_model=RestAnswer202)
async def checkImsiInSlice(free5gcMessage: Union[Free5gck8sBlueCreateModel, MiniFree5gcModel], blue_id: str):
    try:
        logger.info("Received message from OSS: {}".format(free5gcMessage))
        readySlicesList= db.readAthonetSlices()
        logger.info("read from DB: {}".format(readySlicesList))
        for imsiToCheck in getImsiListFromFile():
            logger.info("imsi to check: {}".format(imsiToCheck))
            for item in readySlicesList:
                logger.info("item.imsi: {}".format(item.imsi))
            foundSlice = next((item for item in readySlicesList
                               if imsiToCheck in item.imsi), None)
            logger.info("found slice: {}".format(foundSlice))
            if not foundSlice:
                raise HTTPException(status_code=404, detail="IMSI not yet associated to the slice")
        return RestAnswer202()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Impossible to check the slice status: {}"
                            .format(e))


@router.post("/api/v1/sliceInventory/SB/reportSliceParameters/{sliceType}", response_model=RestAnswer202)
async def addSlices(sliceType: str, athonetSlices: Union[AthonetSlice, List[AthonetSlice]]):
    logger.info("Received message from Athonet ({}): {}".format(sliceType, athonetSlices))
    try:
        checkAndAddSliceType(sliceType, athonetSlices)
        db.writeAthonetSlices(athonetSlices)
        return RestAnswer202()
    except Exception as e:
        logger.warn("Impossible to write the slices ({}) on the DB: {}".format(sliceType, e))
        raise HTTPException(status_code=404, detail="Impossible to accept the slices: {}".format(e))


@router.delete("/api/v1/sliceInventory/SB/reportSliceParameters/{sliceType}", response_model=RestAnswer202)
async def addSlices(sliceType: str, athonetSlices: Union[AthonetSlice, List[AthonetSlice]]):
    logger.info("Received message from Athonet ({}): {}".format(sliceType, athonetSlices))
    try:
        checkAndAddSliceType(sliceType, athonetSlices)
        db.deleteAthonetSlices(athonetSlices)
        return RestAnswer202()
    except Exception as e:
        logger.warn("Impossible to delete the slices ({}) on the DB: {}".format(sliceType, e))
        raise HTTPException(status_code=404, detail="Impossible to accept the slices: {}".format(e))



































