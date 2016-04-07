""" The logging facility for our scripts """
###############################################################################
#Programmer: Orcan Ogetbil    orcan@nbcs.rutgers.edu                          #
#Date: 10/12/2010                                                             #
#Filename: rlogger.py                                                         #
#                                                                             #
#                                                                             #
#       Copyright 2010 Orcan Ogetbil                                          #
#                                                                             #
#    This program is free software; you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
###############################################################################

import sys
import logging
import logging.handlers

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': CYAN,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

class LogFile(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, logger, level=logging.DEBUG):
        self.logger = logger
        self.level = level

    def write(self, msg):
        """ Write to log """
        if self.level == logging.ERROR:
            self.logger.error(msg)
        elif self.level == logging.DEBUG:
            self.logger.debug(msg)
        else:
            self.logger.info(msg)

    def flush(self):
        """ Guess what this is doing :) """
        for handler in self.logger.handlers:
            handler.flush()

class ColoredFormatter(logging.Formatter):
    """ Make a nice color formatted output to stdout """
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        """ Define the color format """
        levelname = record.levelname
        msg = record.msg
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) \
                              + levelname + RESET_SEQ
            record.levelname = levelname_color
            msg_color = COLOR_SEQ % (30 + COLORS[levelname]) + msg + RESET_SEQ
            record.msg = msg_color
        return logging.Formatter.format(self, record)

def formatter_message(message, use_color = True):
    """ Replace the macros with their values """
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD",
                                                               BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


def init(filename, suspect, config, level, quiet):
    """ Initializes our loggers """
    my_logger = logging.getLogger(suspect)
    my_logger.propagate = False
    my_logger.setLevel(logging.DEBUG)

    # We have three handlers. One to stdout, one to the application specific
    # log file, one to the generic log file.

    plogfile = config.get("logs", "plainlog")
    phandler = logging.FileHandler(plogfile, "w")
    my_logger.addHandler(phandler)
    phandler.setLevel(level)

    if filename != "":
        formatter = logging.Formatter(
            "%(asctime)s - %(name)-13s - %(levelname)-8s - %(message)s")

        rfhandler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=int(config.get("logs", "maxBytes")),
            backupCount=int(config.get("logs", "backupCount"))
            )
        my_logger.addHandler(rfhandler)
        rfhandler.setFormatter(formatter)
        rfhandler.setLevel(logging.DEBUG) # make the logfile always most verbose

    if quiet == False:
        shandler = logging.StreamHandler()
        my_logger.addHandler(shandler)
        if level <= logging.DEBUG:
            fformat = "[%(levelname)-20s]  %(message)s $BOLD(%(filename)s:%(lineno)d)$RESET"
        else:
            fformat = "[%(levelname)-20s]  %(message)s"
        color_format = formatter_message(fformat, True)
        color_formatter = ColoredFormatter(color_format)
        shandler.setFormatter(color_formatter)
        shandler.setLevel(level)


    badlogger = logging.getLogger("yum.verbose.repoclosure")
    for handler in badlogger.handlers:
        badlogger.removeHandler(handler)

    # Also direct the stdout to the log
    sys.stdout = LogFile(my_logger, logging.DEBUG)
    sys.stderr = LogFile(my_logger, logging.ERROR)

