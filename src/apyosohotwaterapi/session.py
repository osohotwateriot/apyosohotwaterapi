"""OSO Hotwater Session Module"""
import asyncio
import copy
import operator
import time
import traceback
from datetime import datetime, timedelta

from aiohttp.web import HTTPException
from apyosohotwaterapi import API
from apyosohotwaterapi.helper.osohotwater_helper import OSOHotwaterHelper

from .device_attributes import OSOHotwaterAttributes
from .helper.const import OSOTOHA
from .helper.osohotwater_exceptions import (
    OSOHotwaterApiError,
    OSOHotwaterReauthRequired,
    OSOHotwaterUnknownConfiguration,
)
from .helper.logger import Logger
from .helper.map import Map

class OSOHotwaterSession:
    """OSO Hotwater Session Code
    
    Raises:
        HTTPException: HTTP error has occured

    Returns:
        object: Session object
    """

    def __init__(
        self, subscriptionKey: str, websession: object = None

    ):
        """Initialise the base variable values.
        Args:
            subscriptionKey (str, reqired): OSO Hotwater user subscription key.
            websession (object, optional): Websession for api calls. Defaults to None.
        """

        self.subscriptionKey = subscriptionKey

        self.helper = OSOHotwaterHelper(self)
        self.api = API(osohotwaterSession=self, websession=websession)
        self.attr = OSOHotwaterAttributes(self)
        self.log = Logger(self)
        self.updateLock = asyncio.Lock()
        self.config = Map(
            {
                "errorList": {},
                "file": False,
                "lastUpdated": datetime.now(),
                "scanInterval": timedelta(seconds=120),
                "sensors": False,
            }
        )
        self.data = Map(
            {
                "devices": {},
            }
        )
        self.devices = {}
        self.sensors = {}
        self.deviceList = {}

    async def updateInterval(self, new_interval: timedelta):
        """Update the scan interval.

        Args:
            new_interval (int): New interval for polling.
        """
        if type(new_interval) == int:
            new_interval = timedelta(seconds=new_interval)

        interval = new_interval
        if interval < timedelta(seconds=15):
            interval = timedelta(seconds=15)
        self.config.scanInterval = interval

    async def updateSubscriptionKey(self, subscriptionKey: str):
        """Update subscription key.

        Args:
            subscriptionKey (dict): The user subscription key.

        Returns:
            str: Subscription key
        """
        self.subscriptionKey = subscriptionKey

        return subscriptionKey

    async def updateData(self):
        """Get latest data for OSO Hotwater - rate limiting.

        Returns:
            boolean: True/False if update was successful
        """
        await self.updateLock.acquire()
        updated = False
        try:
            ep = self.config.lastUpdate + self.config.scanInterval
            if datetime.now() >= ep:
                await self.getDevices()
                updated = True
        finally:
            self.updateLock.release()

        return updated

    async def getDevices(self):
        """Get latest device list for the user
        
        Raises:
            HTTPException: HTTP error has occured updating the devices.

        Returns:
            boolean: True/False if update was successful.
        """
        get_devices_successful = False
        api_resp_d = None

        try:
            api_resp_d = await self.api.getDevices()
            if operator.contains(str(api_resp_d["original"]), "20") is False:
                raise HTTPException
            elif api_resp_d["parsed"] is None:
                raise OSOHotwaterApiError

            api_resp_p = api_resp_d["parsed"]
            tmpDevices = {}
            for aDevice in api_resp_p:
                tmpDevices.update({aDevice["deviceId"]: aDevice})

            if len(tmpDevices) > 0:
                self.data.devices = copy.deepcopy(tmpDevices)

            self.config.lastUpdate = datetime.now()
            get_devices_successful = True
        except (OSError, RuntimeError, OSOHotwaterApiError, ConnectionError, HTTPException):
            get_devices_successful = False

        return get_devices_successful

    async def startSession(self, config: dict = {}):
        """Setup the OSO Hotwater platform.

        Args:
            config (dict, optional): Configuration for Home Assistant to use. Defaults to {}.

        Raises:
            OSOHotwaterUnknownConfiguration: Unknown configuration identifed.
            OSOHotwaterReauthRequired: Subscription key has expired and a new one is required.

        Returns:
            list: List of devices
        """
        custom_component = False
        for file, line, w1, w2 in traceback.extract_stack():
            if "/custom_components/" in file:
                custom_component = True

        self.config.sensors = custom_component
        await self.updateInterval(
            config.get("options", {}).get("scan_interval", self.config.scanInterval)
        )
        
        if config != {}:
            if config["api_key"] is not None and not self.config.file:
                await self.updateSubscriptionKey(config["api_key"])
            elif not self.config.file:
                raise OSOHotwaterUnknownConfiguration

        try:
            await self.getDevices()
        except HTTPException:
            return HTTPException

        if self.data.devices == {}:
            raise OSOHotwaterReauthRequired

        return await self.createDevices()

    async def createDevices(self):
        """Create list of devices.

        Returns:
            list: List of devices
        """
        self.deviceList["sensor"] = []
        self.deviceList["water_heater"] = []
        
        for aDevice in self.data["devices"]:
            d = self.data.devices[aDevice]
            self.addList("water_heater", d)
            self.addList("sensor", d, haName=" Power Save", osoHotwaterType="POWER_SAVE")
            self.addList("sensor", d, haName=" Extra Energy", osoHotwaterType="EXTRA_ENERGY")
            self.addList("sensor", d, haName=" Power Load", osoHotwaterType="POWER_LOAD")
            self.addList("sensor", d, haName=" Volume", osoHotwaterType="VOLUME")
            self.addList("sensor", d, haName=" Tapping Capacity kWh", osoHotwaterType="TAPPING_CAPACITY_KWH")
            self.addList("sensor", d, haName=" Capacity Mixed Water 40", osoHotwaterType="CAPACITY_MIXED_WATER_40")
            self.addList("sensor", d, haName=" Heater State", osoHotwaterType="HEATER_STATE")
            self.addList("sensor", d, haName=" Heater Mode", osoHotwaterType="HEATER_MODE")
            self.addList("sensor", d, haName=" Optimization Mode", osoHotwaterType="OPTIMIZATION_MODE")
            self.addList("sensor", d, haName=" Sub Optimization Mode", osoHotwaterType="SUB_OPTIMIZATION_MODE")
            self.addList("sensor", d, haName=" V40 Min", osoHotwaterType="V40_MIN")
            self.addList("sensor", d, haName=" Profile", osoHotwaterType="PROFILE")

        return self.deviceList

    def addList(self, type: str, data: dict, **kwargs: dict):
        """Add entity to the list.

        Args:
            type (str): Type of entity
            data (dict): Information to create entity.

        Returns:
            dict: Entity.
        """
        formatted_data = {}
        display_name = data.get("deviceName", "Water Heater")
        connectionStatus = data.get("connectionState", {}).get("connectionState", "Unknown")
        online = OSOTOHA["Hotwater"]["HeaterConnection"].get(connectionStatus, False)

        try:
            formatted_data = {
                "device_id": data["deviceId"],
                "device_type": data.get("deviceType", "Unknown"),
                "device_name": display_name,
                "power_consumption": data.get("powerConsumption", 0),
                "volume": data.get("volume", 0),
                "online": online,
                "data": data.get("data", {}),
                "control": data.get("control", {}),
                "optimization_option": data.get("optimizationOption", ""),
                "optimization_suboption": data.get("optimizationSubOption", ""),
                "v40_min": data.get("v40Min", 0),
                "profile": data.get("profile", []),
                "haType": type,
                "haName": display_name
            }

            if kwargs.get("haName", "FALSE")[0] == " ":
                kwargs["haName"] = display_name + kwargs["haName"]
            else:
                formatted_data["haName"] = display_name
            formatted_data.update(kwargs)
        except KeyError as e:
            self.logger.error(e)

        self.deviceList[type].append(formatted_data)

    @staticmethod
    def epochTime(date_time: any, pattern: str, action: str):
        """date/time conversion to epoch.

        Args:
            date_time (any): epoch time or date and time to use.
            pattern (str): Pattern for converting to epoch.
            action (str): Convert from/to.

        Returns:
            any: Converted time.
        """
        if action == "to_epoch":
            pattern = "%d.%m.%Y %H:%M:%S"
            epochtime = int(time.mktime(time.strptime(str(date_time), pattern)))
            return epochtime
        elif action == "from_epoch":
            date = datetime.fromtimestamp(int(date_time)).strftime(pattern)
            return date