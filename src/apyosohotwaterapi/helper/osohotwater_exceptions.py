"""OSO Hotwater exception class."""


class OSOHotwaterApiError(Exception):
    """Api error.

    Args:
        Exception (object): Exception object to invoke
    """


class OSOHotwaterReauthRequired(Exception):
    """Re-Authentication is required.

    Args:
        Exception (object): Exception object to invoke
    """


class OSOHotwaterUnknownConfiguration(Exception):
    """Unknown OSO Hotwater Configuration.

    Args:
        Exception (object): Exception object to invoke
    """


class NoSubscriptionKey(Exception):
    """No Subscription key exception.

    Args:
        Exception (object): Exception object to invoke
    """
