#!/usr/bin/env python


from loguru import logger
import functools
import sys


logger = logger.opt(colors=True)
logger.opt = functools.partial(logger.opt, colors=True)
logger.remove()
logger.level("TRACE", color="<cyan>")
logger.level("DEBUG", color="<blue>")
logger.level("UNIMPORTANT", no=15, icon=logger.level("TRACE").icon, color="<normal>")
logger.__class__.unimportant = functools.partialmethod(logger.__class__.log, "UNIMPORTANT")
logger.level("PROCEDURE", no=18, icon=logger.level("INFO").icon, color="<normal>")
logger.__class__.procedure = functools.partialmethod(logger.__class__.log, "PROCEDURE")
logger.level("INFO", color="<normal>")
logger.level("SUCCESS", color="<normal>")
logger.level("IMPORTANT", no=27, icon=logger.level("WARNING").icon, color="<normal>")
logger.__class__.important = functools.partialmethod(logger.__class__.log, "IMPORTANT")
logger.level("WARNING", color="<normal>")
logger.level("ERROR", color="<normal>")
logger.level("CRITICAL", color="<normal>")
logger.add(sys.stdout, level="UNIMPORTANT", format="<level>{message}</level>")
