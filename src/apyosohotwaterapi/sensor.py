"""OSO Hotwater Sensor Module."""

from .helper.const import OSOTOHA, sensor_commands


class OSOHotwaterSensor:
    """OSO Hotwater Sensor Code."""

    sensorType = "Sensor"
    hotwaterType = "Hotwater"
    hotwaterConnection = "HeaterConnection"

    async def getState(self, device: dict):
        """Get sensor state.

        Args:
            device (dict): Device to get state off.

        Returns:
            srt: State of device
        """
        state = None
        final = None

        try:
            data = self.session.data.sensors[device["device_id"]]
            if data["type"] == "":
                state = data[""]
                final = state
            elif data["type"] == "":
                final = data[""]
        except KeyError as e:
            await self.session.log.error(e)

        return final

    async def online(self, device: dict):
        """Get the online status of the Sensor.

        Args:
            device (dict): Device to get the state of.

        Returns:
            boolean: True/False if the device is online.
        """
        state = None
        final = False

        try:
            data = self.session.data.devices[device["device_id"]]
            state = data["connectionState"]["connectionState"]
            final = OSOTOHA[self.hotwaterType][self.hotwaterConnection].get(state, False)
        except KeyError as e:
            await self.session.log.error(e)

        return final


class Sensor(OSOHotwaterSensor):
    """Home Assistant sensor code.

    Args:
        OSOHotwaterSensor (object): OSO Hotwater sensor code.
    """

    def __init__(self, session: object = None):
        """Initialise sensor.

        Args:
            session (object, optional): session to interact with OSO Hotwater. Defaults no None.
        """
        self.session = session

    async def getSensor(self, device: dict):
        """Get updated sensor data.

        Args:
            device (dict): Device to update.

        Returns:
            dict: Updated device.
        """
        device.update({"online": await self.session.attr.onlineOffline(device["device_id"])})

        if device["online"]:
            self.session.helper.device_recovered(device["device_id"])
            dev_data = {}
            dev_data = {
                "haName": device["haName"],
                "haType": device["haType"],
                "osoHotwaterType": device["osoHotwaterType"],
                "device_id": device["device_id"],
                "device_type": device["device_type"],
                "device_name": device["device_name"],
                "available": await self.online(device)
            }

            if dev_data["osoHotwaterType"] in sensor_commands:
                code = sensor_commands.get(dev_data["osoHotwaterType"])
                dev_data.update(
                    {
                        "status": {"state": await eval(code)}
                    }
                )

            self.session.sensors.update({device["device_id"]: dev_data})
            return self.session.sensors[device["device_id"]]
        else:
            await self.session.log.error_check(
                device["device_id"], "ERROR", device["deviceData"]["online"]
            )
            return device
