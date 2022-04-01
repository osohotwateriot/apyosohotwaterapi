"""OSO Hotwater Water Heater Module"""

from .helper.const import OSOTOHA

class OSOWaterHeater:
    """Water Heater Code
    
    Returns:
        object: Water Heater Object
    """

    hotwaterType = "Hotwater"
    hotwaterState = "HeaterState"
    hotwaterConnection = "HeaterConnection"

    async def getHeaterState(self, device: dict):
        """Get water heater current mode.

        Args:
            device (dict): Device to get the mode for.

        Returns:
            str: Return mode.
        """
        state = None
        final = None

        try:
            device = self.session.data.devices[device["device_id"]]
            state = device["control"]["heater"]
            final = OSOTOHA[self.hotwaterType][self.hotwaterState].get(state, state)
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def getMinTemperature(self, device: dict):
        """Get heating minimum target temperature.

        Args:
            device (dict): Device to get min temp for.

        Returns:
            int: Minimum temperature
        """
        return OSOTOHA[self.hotwaterType]["DeviceConstants"]["minTemp"]

    async def getMaxTemperature(self, device: dict):
        """Get heating maximum target temperature.

        Args:
            device (dict): Device to get max temp for.

        Returns:
            int: Maximum temperature
        """
        return OSOTOHA[self.hotwaterType]["DeviceConstants"]["maxTemp"]

    async def getTargetTemperature(self, device: dict):
        """Get heating target temperature.

        Args:
            device (dict): Device to get target temperature for.

        Returns:
            str: Target temperature.
        """
        state = None

        try:
            device = self.session.data.devices[device["osoHotwaterID"]]
            state = float(device["control"].get("currentSetPoint", None))
        except (KeyError, TypeError) as e:
            await self.session.log.error(e)

        return state

    async def getConnectionState(self, device: dict):
        """Get connection state of the heater.

        Args:
            device (dict): Device to get connection state for.

        Returns:
            bool: Connection state.
        """
        state = False

        try:
            device = self.session.data.devices[device["device_id"]]
            state = device["online"]
        except KeyError as e:
            await self.session.log.error(e)

        return state

class WaterHeater(OSOWaterHeater):
    """Water heater class.

    Args:
        Hotwater (object): Hotwater class.
    """

    def __init__(self, session: object = None):
        """Initialise water heater.

        Args:
            session (object, optional): Session to interact with account. Defaults to None.
        """
        self.session = session

    async def getWaterHeater(self, device: dict):
        """Update water heater device.

        Args:
            device (dict): device to update.

        Returns:
            dict: Updated device.
        """
        device.update({ "online": await self.session.attr.onlineOffline(device["device_id"])})

        if(device["online"]):
            dev_data = {}
            dev_data = {
                "haName": device["haName"],
                "haType": device["haType"],
                "device_id": device["device_id"],
                "device_type": device["device_type"],
                "device_name": device["device_name"],
                "status": { "current_operation": await self.getHeaterState(device) },
                "attributes": await self.session.attr.stateAttributes(
                    device["device_id"]
                ),
            }

            self.session.devices.update({device["device_id"]: dev_data})
            return self.session.devices[device["device_id"]]
        else:
            await self.session.log.errorCheck(
                device["device_id"], "ERROR", device["online"]
            )
            return device


