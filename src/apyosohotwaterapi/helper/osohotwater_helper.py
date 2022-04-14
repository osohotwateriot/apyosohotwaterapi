"""OSO Hotwater Helper code."""


class OSOHotwaterHelper:  # pylint: disable=too-few-public-methods
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
        if n_id in self.session.config.error_list:
            self.session.config.error_list.pop(n_id)
