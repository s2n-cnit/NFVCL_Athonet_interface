from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import Optional
import logging


def create_logger(name: str) -> logging.getLogger:
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


logger = create_logger("Athonet Simulator")


class AddImsiRequest(BaseModel):
    imsi: str
    sliceId: str
    usedDataRateUL: int
    usedDataRateDL: int


athonetRouter = APIRouter(
    prefix="",
    tags=["athonetSimulator"],
    responses={404: {"description": "Not found"}}
)

@athonetRouter.post("/sliceUEs/attach")
async def addImsi(payload: AddImsiRequest):
    logger.info("Add IMSI to slice")
    logger.info("Payload: {}".format(payload))
    return {}


app = FastAPI(
    title="athonet Simulator",
    version="0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(athonetRouter)