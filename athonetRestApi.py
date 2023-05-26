"""
Athonet REST API

Copyright (c) 2023 - S2N Lab (https://s2n.cnit.it/)
"""

import requests
from utils import create_logger
from models import *


logger = create_logger("Athonet REST interface")


class AthonetRestAPI():
    def __init__(self, athonetIP: str = None, athonetPort: str = "8080"):
        if not athonetIP:
            raise ValueError("Athonet server IP has a NOT valid value: IP=\"{}\"".format(athonetIP))
        else:
            self.athonetURL = "http://{}:{}".format(athonetIP, athonetPort)

        self.urlBase = "{}".format(self.athonetURL)
        self.addImsiUrlExtension = "/sliceUEs/attach"

        self.headers = {"Content-Type": "application/json"}

    def __checkRestResponse(self, response: requests.Response) -> bool:
        rightResponseList = [
            requests.codes.ok, requests.codes.accepted, requests.codes.created, requests.codes.no_content
        ]
        if response.status_code in rightResponseList:
            return True
        else:
            logger.error("REST API response NOT valid: URL: {} -- STATUS CODE: {} -- REASON {}".
                         format(response.url, response.status_code, response.reason))
            return False

    def __restGet(self, restUrl: str = None) -> requests.Response:
        try:
            logger.info("GET Message sent: url={} - no payload".format(restUrl))
            r = requests.get(restUrl, params=None, verify=False, stream=True, headers=self.headers)
            logger.info("GET Response received: url={} - {} - {}".format(restUrl, r, r.json()))
            return r
        except Exception as e:
            logger.error("Impossible to execute GET call: {} -- {}".format(restUrl, e))
            raise ValueError("Impossible to execute GET call: {} -- {}".format(restUrl, e))

    def __restPost(self, restUrl: str = None, data = None) -> requests.Response:
        try:
            logger.info("POST Message sent: url={} - {}".format(restUrl, data))
            r = requests.post(restUrl, json=data, params=None, verify=False, headers=self.headers)
            logger.info("POST Response received: url={} - {} - {}".format(restUrl, r, r.json()))
            return r
        except Exception as e:
            logger.error("Impossible to execute POST call: {} --- {}".format(restUrl, e))
            raise ValueError("Impossible to execute POST call: {} --- {}".format(restUrl, e))

    def __restDelete(self, restUrl: str = None, data = None) -> requests.Response:
        try:
            logger.info("DELETE Message sent: url={} - {}".format(restUrl, data))
            r = requests.delete(restUrl, json=data, params=None, verify=False, headers=self.headers)
            logger.info("DELETE Response received: url={} - {} - {}".format(restUrl, r, r.json()))
            return r
        except Exception as e:
            logger.error("Impossible to execute DELETE call: {} --- {}".format(restUrl, e))
            raise ValueError("Impossible to execute DELETE call: {} --- {}".format(restUrl, e))

    def addImsiToSlice(self, data: AddImsiRequest):
        """
        Add an Imsi to the specific slice
        :param data:
        :return:
        """
        if not data:
            raise ValueError("data for payload is empty")
        url = "{}{}".format(self.urlBase, self.addImsiUrlExtension)
        try:
            r  =self.__restPost(restUrl=url, data=data.dict())
            if not self.__checkRestResponse(r):
                raise ValueError("response return this error: {}".format(r.status_code))
        except Exception as e:
            logger.error("{}".format(e))
            raise ValueError("{}".format(e))








































