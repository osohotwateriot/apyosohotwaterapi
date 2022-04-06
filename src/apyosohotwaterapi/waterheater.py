"""OSO Hotwater Water Heater Module"""

from sre_parse import State
from .helper.const import OSOTOHA

class OSOWaterHeater:
    """Water Heater Code
    
    Returns:
        object: Water Heater Object
    """

    hotwaterType = "Hotwater"

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
            final = OSOTOHA[self.hotwaterType]["HeaterState"].get(state, state)
        except KeyError as e:
            await self.session.log.error(e)

        return final

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


