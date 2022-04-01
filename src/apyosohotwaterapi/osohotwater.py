"""Start OSO Hotwater Session"""

import sys
import traceback
from os.path import expanduser
from typing import Optional

from aiohttp import ClientSession
from loguru import logger

from .session import OSOHotwaterSession
from .waterheater import WaterHeater

debug = []
home = expanduser("~")
logger.add(
    home + "/pyosohotwaterapi_debug.log", filter=lambda record: record["level"].name == "DEBUG"
)
logger.add(
    home + "/pyosohotwaterapi_info.log", filter=lambda record: record["level"].name == "INFO"
)
logger.add(
    home + "/pyosohotwaterapi_error.log", filter=lambda record: record["level"].name == "ERROR"
)

def exception_handler(exctype, value, tb):
    """Custom exception handler.

    Args:
        exctype ([type]): [description]
        value ([type]): [description]
        tb ([type]): [description]
    """
    last = len(traceback.extract_tb(tb)) - 1
    logger.error(
        f"-> \n"
        f"Error in {traceback.extract_tb(tb)[last].filename}\n"
        f"when running {traceback.extract_tb(tb)[last].name} function\n"
        f"on line {traceback.extract_tb(tb)[last].lineno} - "
        f"{traceback.extract_tb(tb)[last].line} \n"
        f"with vars {traceback.extract_tb(tb)[last].locals}"
    )
    traceback.print_exc(tb)


sys.excepthook = exception_handler

def trace_debug(frame, event, arg):
    """Trace functions.
    Args:
        frame (object): The current frame being debugged.
        event (str): The event type
        arg (dict): arguments in debug function..
    Returns:
        object: returns itself as per tracing docs
    """
    if "pyosohotwaterapi/" in str(frame):
        co = frame.f_code
        func_name = co.co_name
        func_line_no = frame.f_lineno
        if func_name in debug:
            if event == "call":
                func_filename = co.co_filename.rsplit("/", 1)
                caller = frame.f_back
                caller_line_no = caller.f_lineno
                caller_filename = caller.f_code.co_filename.rsplit("/", 1)

                logger.debug(
                    f"Call to {func_name} on line {func_line_no} "
                    f"of {func_filename[1]} from line {caller_line_no} "
                    f"of {caller_filename[1]}"
                )
            elif event == "return":
                logger.debug(f"returning {arg}")

        return trace_debug

class OSOHotwater(OSOHotwaterSession):
    """OSO Hotwater class
    
    Args:
        OSOHotwaterSession (object): Interact with OSO Hotwater
    """

    def __init__(
        self,
        subscriptionKey,
        websession: Optional[ClientSession] = None):

        super().__init__(subscriptionKey=subscriptionKey, websession=websession)
        self.session = self
        self.hotwater = WaterHeater(self.session)
        self.logger = logger
        if debug:
            sys.settrace(trace_debug)

    def setDebugging(self, debugger: list):
        """Set function to debug.

        Args:
            debugger (list): a list of functions to debug

        Returns:
            object: Returns traceback object.
        """
        global debug
        debug = debugger
        if debug:
            return sys.settrace(trace_debug)
        return sys.settrace(None)