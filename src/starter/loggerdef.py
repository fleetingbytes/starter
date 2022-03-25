#!/usr/bin/env python


from loguru import logger
import functools
import sys


logger = logger.opt(colors=True)
logger.opt = functools.partial(logger.opt, colors=True)
logger.remove()
logger.level("TRACE", color="<light-black>")
logger.level("DEBUG", color="<light-black>")
logger.level("UNIMPORTANT", no=15, icon=logger.level("TRACE").icon, color="<light-black>")
logger.__class__.unimportant = functools.partialmethod(logger.__class__.log, "UNIMPORTANT")
logger.level("PROCEDURE", no=18, icon=logger.level("INFO").icon, color="<cyan>")
logger.__class__.procedure = functools.partialmethod(logger.__class__.log, "PROCEDURE")
logger.level("INFO", color="<white>")
logger.level("SUCCESS", color="<green>")
logger.level("IMPORTANT", no=27, icon=logger.level("WARNING").icon, color="<yellow>")
logger.__class__.important = functools.partialmethod(logger.__class__.log, "IMPORTANT")
logger.level("WARNING", color="<light-magenta>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<RED>")
logger.add(sys.stdout, level="UNIMPORTANT", format="<level>{message}</level>")

