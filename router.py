"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
import fastapi
from fastapi import APIRouter
from pydantic import BaseModel
from athonetRestApi import AthonetRestAPI
from utils import create_logger

athonetHost = "127.0.0.1"

logger = create_logger("Router")


northRouter = APIRouter(
    prefix="/v1",
    tags=["NorthRouter"],
    responses={404:{"description": "Not found"}}
)

southRouter = APIRouter(
    prefix="/v1",
    tags=["SouthRouter"],
    responses={404:{"description": "Not found"}}
)

athonetInterface = AthonetRestAPI(athonetHost)


