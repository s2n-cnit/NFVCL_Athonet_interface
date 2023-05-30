"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
from pymongo import MongoClient
from utils import create_logger
from typing import Union, List
from models import AthonetSlice

logger = create_logger("Database")
athonetSlicesCollectionName = "athonetSlices"

class Database():
    def __init__(self, mongoUser: str = None, mongoPassword: str = None,
                 mongoIP: str = "127.0.0.1", mongoPort: int = 27017, mongoDbName: str = None ):
        if not mongoDbName:
            logger.error("Mongo DB name is not specified")
            raise ValueError("Mongo DB name is not specified")
        self.mongoUrl = "mongodb://{}{}/".format(
                (mongoUser+":"+mongoPassword+"@" if mongoUser else ""),
                mongoIP+":"+str(mongoPort)
            )
        self.mongoClient = MongoClient(self.mongoUrl)
        self.db = self.mongoClient[mongoDbName]

    def __read(self, collectionName: str = None, queryFilter: dict = None) -> List[dict]:
        result = []
        if not collectionName:
            raise ValueError("collection name is empty")
        return list(self.db[collectionName].find(queryFilter))

    def __write(self, collectionName: str = None, data = None):
        logger.info("write")
        if not collectionName:
            raise ValueError("collection name is empty")
        if not data:
            raise ValueError("no data to write in the DB")
        self.db[collectionName].insert_one(data)

    def __update(self, collectionName: str = None, queryFilter: dict = None, newValues: dict = None):
        if not collectionName:
            raise ValueError("collection name is empty")
        if not queryFilter:
            raise ValueError("query filter is empty")
        if not newValues:
            raise ValueError("new values are empty")
        self.db[collectionName].update_one(queryFilter, {"$set": newValues})

    def __delete(self, collectionName: str = None, queryFilter: dict = None):
        logger.info("delete")
        if not collectionName:
            raise ValueError("collection name is empty")
        if not queryFilter:
            raise ValueError("query filter is empty")
        self.db[collectionName].delete_one(queryFilter)

    def writeAthonetSlices(self, data: Union[AthonetSlice, List[AthonetSlice]]):
        """
        Write slice (or array of slices) in the DB as read from Athonet slice manager.
        If it yet exists, remove it and save the new value
        :param data:
        :return:
        """
        try:
            if type(data) != list:
                dataList = [data]
            else:
                dataList = data
            for elem in dataList:
                self.__delete(athonetSlicesCollectionName, {"sliceId": elem.sliceId})
                self.__write(athonetSlicesCollectionName, elem.dict())
        except Exception as e:
            logger.info("Impossible to write slice(s): {} - error: {}". format(data, e))
            raise ValueError("Impossible to write slice(s): {} - error: {}". format(data, e))

    def readAthonetSlices(self, sliceId: dict = None) -> List[AthonetSlice]:
        try:
            sliceList = []
            result = self.__read(athonetSlicesCollectionName, ({"sliceId": sliceId} if sliceId else None))
            for item in result:
                sliceList.append(AthonetSlice(**item))
            return sliceList
        except Exception as e:
            logger.warn("Impossible to read slice(s) from DB: {}".format(e))
            raise ValueError("Impossible to read slice(s) from DB: {}".format(e))



























