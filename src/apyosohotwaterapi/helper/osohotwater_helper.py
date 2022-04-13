"""OSO Hotwater Helper code."""


class OSOHotwaterHelper:
    """OSO Hotwater helper class."""

    def __init__(self, session: object = None):
        """OSO Hotwater Helper.

        Args:
            session (object, optional): Interact with OSO Hotwater. Defaults to None.
        """
        self.session = session

    def device_recovered(self, n_id: str):
        """Register that device has recovered from being offline.

        Args:
            n_id (str): ID of the device
        """
        if n_id in self.session.config.errorList:
            self.session.config.errorList.pop(n_id)
