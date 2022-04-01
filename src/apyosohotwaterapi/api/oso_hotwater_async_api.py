"""OSO Hotwater API Module."""

import operator
from typing import Optional
from numpy import full, number

import urllib3
from aiohttp import ClientResponse, ClientSession, web_exceptions

from ..helper.const import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN
from ..helper.osohotwater_exceptions import NoSubscriptionKey

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OSOHotwaterApiAsync:
    """OSO Hotwater API Code"""

    def __init__(
        self,
        osohotwaterSession=None,
        websession: Optional[ClientSession] = None):

        self.baseUrl = "https://osowh-apimanagement.azure-api.net/water-heater-api"
        self.urls = {
            "devices": self.baseUrl + "/1/Device/All",
            "tapping_capacity_kwh": self.baseUrl + "/1/Device/{0}/TappingCapacityKwh",
            "actual_load": self.baseUrl + "/1/Device/{0}/ActualLoad",
            "status": self.baseUrl + "/1/Device/{0}/Status",
            "metadata": self.baseUrl + "/1/Device/{0}/Metadata",
            "v40_min": self.baseUrl + "/1/Device/{0}/V40Min",
            "turn_on": self.baseUrl + "/1/Device/{0}/TurnOn?fullUtilizationParam={1}",
            "turn_off": self.baseUrl + "/1/Device/{0}/TurnOff?fullUtilizationParam={1}",
            "profile": self.baseUrl + "/1/Device/{0}/Profile",
            "optimization_mode": self.baseUrl + "/1/Device/{0}/OptimizationMode",
            "set_v40_min": self.baseUrl + "/1/Device/{0}/V40Min/{1}",
        }
        self.headers = {
            "content-type": "application/json",
            "Accept": "*/*"
        }
        self.timeout = 10
        self.json_return = {
            "original": "No response to OSO Hotwater API request",
            "parsed": "No response to OSO Hotwater API request",
        }
        self.session = osohotwaterSession
        self.websession = ClientSession() if websession is None else websession

    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make a request."""
        data = kwargs.get("data", None)

        if not self.session.subscriptionKey:
            raise NoSubscriptionKey
        
        self.headers.update(
            { "Ocp-Apim-Subscription-Key": self.session.subscriptionKey }
        )

        async with self.websession.request(
            method, url, headers=self.headers, data=data
        ) as resp:
            await resp.json(content_type=None)
            self.json_return.update({"original": resp.status})
            self.json_return.update({"parsed": await resp.json(content_type=None)})

        if operator.contains(str(resp.status), "20"):
            return True
        elif resp.status == HTTP_UNAUTHORIZED:
            self.session.logger.error(
                f"Subscription key not authorized when calling {url} - "
                f"HTTP status is - {resp.status}"
            )
        elif resp.status == HTTP_FORBIDDEN:
            self.session.logger.error(
                f"Subscription key not authorized when calling {url} - "
                f"HTTP status is - {resp.status}"
            )
        elif url is not None and resp.status is not None:
            self.session.logger.error(
                f"Something has gone wrong calling {url} - "
                f"HTTP status is - {resp.status}"
            )

    async def getDevices(self):
        """Call the get devices endpoint."""
        url = self.urls["devices"]
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def getTappingCapacityKwh(self, device_id: str):
        """Call the get tapping capacity kwh endpoint."""
        url = self.urls["tapping_capacity_kwh"].format(device_id)
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def getActualLoadKwh(self, device_id: str):
        """Call the get actual load endpoint."""
        url = self.urls["actual_load"].format(device_id)
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return
    
    async def getStatus(self, device_id: str):
        """Call the get status endpoint."""
        url = self.urls["status"].format(device_id)
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def getMetadata(self, device_id: str):
        """Call the get metadata endpoint."""
        url = self.urls["metadata"].format(device_id)
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def getV40Min(self, device_id: str):
        """Call the get V40 Min endpoint."""
        url = self.urls["v40_min"].format(device_id)
        try:
            await self.request("get", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def turnOn(self, device_id: str, full_utilization: bool):
        """Call the get V40 Min endpoint."""
        url = self.urls["turn_on"].format(device_id, full_utilization)
        try:
            await self.request("post", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def turnOff(self, device_id: str, full_utilization: bool):
        """Call the get V40 Min endpoint."""
        url = self.urls["turn_off"].format(device_id, full_utilization)
        try:
            await self.request("post", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def setProfile(self, device_id: str, **kwargs):
        """Call the get V40 Min endpoint."""
        jsc = (
            "{"
            + ",".join(
                ('"' + str(i) + '": ' '"' + str(t) + '" ' for i, t in kwargs.items())
            )
            + "}"
        )

        url = self.urls["profile"].format(device_id)
        try:
            await self.request("put", url, data=jsc)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def setOptimizationMode(self, device_id: str, **kwargs):
        """Call the get V40 Min endpoint."""
        jsc = (
            "{"
            + ",".join(
                ('"' + str(i) + '": ' '"' + str(t) + '" ' for i, t in kwargs.items())
            )
            + "}"
        )
        url = self.urls["optimization_mode"].format(device_id)
        try:
            await self.request("put", url, data=jsc)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def setV40Min(self, device_id: str, v40_min: number):
        """Call the get V40 Min endpoint."""
        url = self.urls["set_v40_min"].format(device_id, v40_min)
        try:
            await self.request("put", url)
        except (OSError, RuntimeError, ZeroDivisionError):
            await self.error()

        return self.json_return

    async def error(self):
        """An error has occurred iteracting with the OSO Hotwater API."""
        raise web_exceptions.HTTPError