"""OSO Hotwater Water Heater Module"""

from array import array
from numbers import Number
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

    async def turnOn(self, device: dict, fullUtilization: bool):
        """Turn device on
        
        Args:
            device (dict): Device to turn on.
            fullUtilization (bool): Fully utilize device.
        
        Returns:
            boolean: return True/False if turn on was successful.
        """

        final = False

        try:
            resp = await self.session.api.turnOn(device["device_id"], fullUtilization)
            if resp["original"] == 200:
                final = True
                await self.session.updateData()

        except Exception as e:
            await self.session.log.error(e)

        return final

    async def turnOff(self, device: dict, fullUtilization: bool):
        """Turn device off
        
        Args:
            device (dict): Device to turn off.
            fullUtilization (bool): Fully utilize device.
        
        Returns:
            boolean: return True/False if turn off was successful.
        """

        final = False

        try:
            resp = await self.session.api.turnOff(device["device_id"], fullUtilization)
            if resp["original"] == 200:
                final = True
                await self.session.updateData()

        except Exception as e:
            await self.session.log.error(e)

        return final

    async def setV40Min(self, device: dict, v40min: float):
        """Set V40 Min levels for device
        
        Args:
            device (dict): Device to turn off.
            v40Min (float): quantity of water at 40°C.
        
        Returns:
            boolean: return True/False if setting the V40Min was successful.
        """

        final = False

        try:
            resp = await self.session.api.setV40Min(device["device_id"], v40min)
            if resp["original"] == 200:
                final = True
                await self.session.updateData()

        except Exception as e:
            await self.session.log.error(e)

        return final

    async def setOptimizationMode(self, device: dict, option: Number, subOption: Number):
        """Set heater optimization mode
        
        Args:
            device (dict): Device to turn off.
            option (Number): heater optimization option.
            subOption (Number): heater optimization sub option.
        
        Returns:
            boolean: return True/False if setting the optimization mode was successful.
        """
        final = False

        try:
            resp = await self.session.api.setOptimizationMode(device["device_id"], optimizationOptions=option, optimizationSubOptions=subOption)
            if resp["original"] == 200:
                final = True
                await self.session.updateData()

        except Exception as e:
            await self.session.log.error(e)

        return final

    async def setProfile(self, device: dict, profile: array):
        """Set heater profile
        
        Args:
            device (dict): Device to set profile to.
            profile (array): array of temperatures for 24 hours (UTC).
        
        Returns:
            boolean: return True/False if setting the profile was successful.
        """
        final = False

        try:
            resp = await self.session.api.setProfile(device["device_id"], hours=profile)
            if resp["original"] == 200:
                final = True
                await self.session.updateData()

        except Exception as e:
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
            self.session.helper.deviceRecovered(device["device_id"])
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


