# -*- coding: utf-8 -*-
# Copyright © 2011-2013 Binet Réseau
# See the LICENCE file for more informations

"""Common utilities for test cases"""

import kaoz.bot
import logging
import os
import sys

from .ircserver import IRCServerThread, logger as ircserver_logger

if sys.version_info < (3,):
    from ConfigParser import SafeConfigParser as ConfigParser
else:
    from configparser import ConfigParser

try:
    import unittest2 as unittest
except ImportError:
    import unittest


def get_local_conf_path():
    """Get the absolute path to local configuration file"""
    return os.path.join(os.path.dirname(__file__), 'kaoz.local.conf')

def get_local_conf():
    """Load local configuration"""
    path = get_local_conf_path()
    config = kaoz.bot.get_default_config()
    config.read(path)
    return config


def spawn_ircserver(config):
    """Spawn a local IRC server, with respect to given configuration"""
    server = config.get('irc', 'server')
    port = config.getint('irc', 'port')
    name = '%s.%d.localdomain' % (server, port)
    # TODO: SSL support
    thread = IRCServerThread((server, port), name)
    thread.start()
    return thread


def configure_logger(logger, loglevel):
    """Configure a logger to display messages at the specified loglevel"""
    if not isinstance(loglevel, int):
        num_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(num_loglevel, int):
            raise ValueError("Invalid log level: %s" % loglevel)
        loglevel = num_loglevel
    logger.setLevel(loglevel)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(
        "[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(log_handler)


def configure_ircserver_log(loglevel):
    """Configure logging of ircserver"""
    configure_logger(ircserver_logger, loglevel)
