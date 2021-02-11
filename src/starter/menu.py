#!/usr/bin/env python


from __future__ import annotations
import os
import collections
from loguru import logger
# Own modules
from starter import utils


class Text_Menu:
    """
    Command prompt menu
    """
    def __init__(self, menu_name: str, heading: str) -> None:
        self.menu_name = menu_name
        self.heading = heading
    def wait_key(self) -> str:
        """
        Wait for a key press on the console and return it.
        Source: https://stackoverflow.com/a/34956791
        """
        result = None
        if os.name == 'nt':
            import msvcrt
            result = msvcrt.getch()
        else:
            import termios
            fd = sys.stdin.fileno()
            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            try:
                result = sys.stdin.read(1)
            except IOError:
                pass
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        if isinstance(result, bytes):
            result = str(result, encoding="utf-8").upper()
        return result
    def show_heading(self) -> None:
        """
        Renders the Heading of the menu in the logger at INFO level
        """
        for line in self.heading.split("\n"):
            logger.info(line)
    def show_separator(self) -> None:
        logger.info("\n" + "·" * 42)
    def show_options(self, options: collections.OrderedDict) -> None:
        """
        Renders a command prompt menu for each exrtacted traces file.
        Manages key input and acts accordingly
        """
        for key, text in options.items():
            logger.info(f"     ({key}) {text}")
        logger.info("")
    def show_reason(self, reason: str) -> None:
        logger.warning("\n" + utils.warn(reason))
    def show_comment(self, comment: str) -> None:
        logger.info(comment + "\n")
    def choose_from(self, options: collections.OrderedDict) -> str:
        self.show_options(options)
        choice = None
        choices = tuple(key.upper() for key in options.keys())
        logger.trace(f"{choices = }")
        while choice not in choices:
            try:
                if choice == False:
                    logger.trace(f"Empyting wait_key output")
                    _ = self.wait_key()
                    logger.trace(f"choice changing from False to None")
                    choice = None
                    continue
                else:
                    logger.trace(f"{choice = }")
                    logger.trace(f"Waiting for key")
                    choice = self.wait_key()
                    logger.trace(f"{choice = }")
            except UnicodeDecodeError:
                logger.trace("Handling UnicodeDecodeError, changing choice to False")
                choice = False
        return choice


if __name__ == "__main__":
    pass
