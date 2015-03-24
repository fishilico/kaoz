# -*- coding: utf-8 -*-
# Copyright © 2011-2013 Binet Réseau
# See the LICENCE file for more informations

"""Do code coverage for the launch part of the bot"""

import coverage
import ctypes
import ctypes.util
import os
import os.path
import signal
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import kaoz.bot

from kaoz.tests.common import get_local_conf, get_local_conf_path
from kaoz.tests.ircserver import main as ircserver_main


def setup_die_if_parent_dies():
    """Setup a process so that it automatically dies when its parent dies

    Only supported on Linux
    """
    if sys.platform == 'linux':
        libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
        # PR_SET_PDEATHSIG = 1
        if libc.prctl(1, signal.SIGTERM) == -1:
            error = os.strerror(ctypes.get_errno())
            sys.stderr.write("Unable to set PDEATHSIG: %s\n" % error)


def fork_covered_subprocess(fct, arg):
    """Fork a new process to run the given function with one argument"""
    pid = os.fork()
    if pid != 0:
        return pid

    try:
        # Set-up coverage
        cov = coverage.coverage(auto_data=True)
        cov.start()

        # Automatically die if the parent goes wrong (unused safety)
        setup_die_if_parent_dies()

        # Run function
        fct(arg)
    except:
        traceback.print_exc()
    finally:
        os._exit(0)
        raise RuntimeError("Unable to exit cleanly")


def cover_launch_bot():
    """Spawn an irc server and a bot and run coverage on them"""
    # Retrieve configuration
    config = get_local_conf()
    configpath = get_local_conf_path()
    server = config.get('irc', 'server')
    port = config.getint('irc', 'port')

    # Launch an ircserver as a subprocess
    server_pid = fork_covered_subprocess(ircserver_main, [
        '--host', server,
        '--port', str(port),
        '--name', '%s.%d.localdomain' % (server, port),
    ])

    # Launch the bot
    bot_pid = fork_covered_subprocess(kaoz.bot.main,
                                      ['--config', configpath, '--logstd'])

    # Wait a little and kill both children
    time.sleep(5)
    os.kill(server_pid, signal.SIGINT)
    server_status = os.waitpid(server_pid, 0)[1]

    os.kill(bot_pid, signal.SIGTERM)
    bot_status = os.waitpid(bot_pid, 0)[1]

    if not os.WIFEXITED(server_status) or os.WEXITSTATUS(server_status) != 0:
        sys.stderr.write("Server exited with status %d\n" % server_status)
        return 1
    if not os.WIFSIGNALED(bot_status):
        sys.stderr.write("Bot exited with status %d\n" % bot_status)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(cover_launch_bot())
