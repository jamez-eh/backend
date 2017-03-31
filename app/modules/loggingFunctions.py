#!/usr/bin/env python

"""
    Set up the logging
"""

import logging
import tempfile
import os


def initialize_logging():
    """
    Set up the screen and file logging.

    :return: The log filename
    """

    # set up DEBUG logging to file, INFO logging to STDERR
    log_file = os.path.join(tempfile.gettempdir(), 'ectyper.log')

    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=log_file,
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    return log_file
