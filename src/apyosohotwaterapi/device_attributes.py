"""OSO Hotwater Device Attribute Module"""
from .helper.logger import Logger
from .helper.const import OSOTOHA

class OSOHotwaterAttributes:
    """Devcie Attributes Code."""

    hotwaterType = "Hotwater"
    hotwaterState = "HeaterState"
    hotwaterConnection = "HeaterConnection"
    hotwaterMode = "HeaterMode"
    hotwaterOptimizationMode = "HeaterOptimizationMode"
    hotwaterSubOptimizationMode = "HeaterSubOptimizationMode"

    def __init__(self, session: object = None):
        """Initialise attributes
        
        Args:
            session (object, optional): Session to interact with OSO Hotwater. Defaults to None.
        """
        self.session = session
        self.session.log = Logger()
        self.type = "Attribute"

    async def stateAttributes(self, device_id: str):
        """Get HS State Attributes.
        
        Args:
            device_id (str): The id of the device

        Returns:
            dict: Set of attributes
        """
        attr = {}

        if device_id in self.session.data.devices:
            attr.update({"available": (await self.onlineOffline(device_id))})
            attr.update({"power_load": (await self.getPowerConsumption(device_id))})
            attr.update({"volume": (await self.getVolume(device_id))})
            attr.update({"tapping_capacity_kWh": (await self.getTappingCapacitykWh(device_id))})
            attr.update({"capacity_mixed_water_40": (await self.getCapacityMixedWater40(device_id))})
            attr.update({"actual_load_kwh": (await self.getActualLoadKwh(device_id))})
            attr.update({"heater_state": (await self.getHeaterState(device_id))})
            attr.update({"heater_mode": (await self.getHeaterMode(device_id))})
            attr.update({"current_set_point": (await self.getCurrentSetPoint(device_id))})
            attr.update({"optimization_mode": (await self.getOptimizationMode(device_id))})
            attr.update({"sub_optimization_mode": (await self.getSubOptimizationMode(device_id))})
            attr.update({"v40_min": (await self.getV40Min(device_id))})
            attr.update({"profile": (await self.getProfile(device_id))})

        return attr

    async def onlineOffline(self, device_id: str):
        """Check if device is online.

        Args:
            device_id (str): The id of the device.

        Returns:
            boolean: True/False if device online.
        """
        state = None
        final = False

        try:
            data = self.session.data.devices[device_id]
            state = data["connectionState"]["connectionState"]
            final = OSOTOHA[self.hotwaterType][self.hotwaterConnection].get(state, False)
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getPowerConsumption(self, device_id: str):
        """Get heater power consumption.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The mode of the device.
        """
        consumption = None

        try:
            data = self.session.data.devices[device_id]
            consumption = data.get("powerConsumption", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return consumption

    async def getVolume(self, device_id: str):
        """Get heater volume.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The volume of the device.
        """
        volume = None

        try:
            data = self.session.data.devices[device_id]
            volume = data.get("volume", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return volume

    async def getTappingCapacitykWh(self, device_id: str):
        """Get tapping capacity in kWh.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The tapping capacity kWh.
        """
        capacity = None

        try:
            data = self.session.data.devices[device_id]
            capacity = data.get("data", {}).get("tappingCapacitykWh", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return capacity

    async def getCapacityMixedWater40(self, device_id: str):
        """Get capacity of water at 40 degrees.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The capacity of water at 40 degrees.
        """
        capacity = None

        try:
            data = self.session.data.devices[device_id]
            capacity = data.get("data", {}).get("capacityMixedWater40", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return capacity

    async def getActualLoadKwh(self, device_id: str):
        """Get load of heater in kW.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The actual load of the heater.
        """
        load = None

        try:
            data = self.session.data.devices[device_id]
            load = data.get("data", {}).get("actualLoadKwh", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return load

    async def getHeaterState(self, device_id: str):
        """Get state of heating.

        Args:
            device_id (str): The id of the device

        Returns:
            str: The state of the heater.
        """
        state = None
        final = None

        try:
            data = self.session.data.devices[device_id]
            state = data.get("control", {}).get("heater", 0)
            final = OSOTOHA[self.hotwaterType][self.hotwaterState].get(state, "OFF")
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getHeaterMode(self, device_id: str):
        """Get mode of heater.

        Args:
            device_id (str): The id of the device

        Returns:
            str: The mode of the heater.
        """
        state = None
        final = None

        try:
            data = self.session.data.devices[device_id]
            state = data.get("control", {}).get("heater", None)
            final = OSOTOHA[self.hotwaterType][self.hotwaterMode].get(state, "OFF")
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getCurrentSetPoint(self, device_id: str):
        """Get current setpoint of heater.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The current setpoint of the heater.
        """
        setPoint = None

        try:
            data = self.session.data.devices[device_id]
            setPoint = data.get("control", {}).get("currentSetPoint", 0)
        except KeyError as e:
            await self.session.log.error(e)

        return setPoint

    async def getOptimizationMode(self, device_id: str):
        """Get heater optimization mode.

        Args:
            device_id (str): The id of the device

        Returns:
            str: The optimization mode of the device.
        """
        mode = None
        final = None

        try:
            data = self.session.data.devices[device_id]
            mode = data["optimizationOption"]
            final = OSOTOHA[self.hotwaterType][self.hotwaterOptimizationMode].get(mode, mode)
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getSubOptimizationMode(self, device_id: str):
        """Get heater sub optimization mode.

        Args:
            device_id (str): The id of the device

        Returns:
            str: The sub optimization mode of the device.
        """
        mode = None
        final = None

        try:
            data = self.session.data.devices[device_id]
            mode = data["optimizationSubOption"]
            final = OSOTOHA[self.hotwaterType][self.hotwaterSubOptimizationMode].get(mode, mode)
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getV40Min(self, device_id: str):
        """Get v40 min level of the heater.

        Args:
            device_id (str): The id of the device

        Returns:
            float: The v40 min level of the device.
        """
        level = None

        try:
            data = self.session.data.devices[device_id]
            level = data["v40Min"]
        except KeyError as e:
            await self.session.log.error(e)

        return level

    async def getProfile(self, device_id: str):
        """Get the 24 hour profile of the heater. (UTC)

        Args:
            device_id (str): The id of the device

        Returns:
            float array: The 24 hour temperature profile of the device. (UTC)
        """
        level = None

        try:
            data = self.session.data.devices[device_id]
            level = data["v40Min"]
        except KeyError as e:
            await self.session.log.error(e)

        return level