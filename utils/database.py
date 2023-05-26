"""
Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""
from pymongo import MongoClient
from utils import create_logger

logger = create_logger("Database")

class Database():
    def __init__(self, mongoUser: str = None, mongoPassword: str = None,
                 mongoIP: str = None, mongoPort: int = 27017, mongoDbName: str = None ):
        if not mongoDbName:
            logger.error("Mongo DB name is not specified")
            raise ValueError("Mongo DB name is not specified")
        self.mongoUrl = "mongodb+srv://{}{}".format(
                (mongoUser+":"+mongoPassword+"@" if mongoUser else ""),
                mongoIP+":"+str(mongoPort)
            )
        self.mongoClient = MongoClient(self.mongoUrl)
        self.db = self.mongoClient[mongoDbName]

    def __read(self, collectionName: str = None, queryFilter: dict = None) -> dict | [dict]:
        if not collectionName:
            raise ValueError("collection name is empty")
        return self.db[collectionName].find(queryFilter)

    def __write(self, collectionName: str = None, data = None):
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
        if not collectionName:
            raise ValueError("collection name is empty")
        if not queryFilter:
            raise ValueError("query filter is empty")
        self.db[collectionName].delete_one(queryFilter)

