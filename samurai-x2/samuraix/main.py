# Copyright (c) 2008-2009, samurai-x.org
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the samurai-x.org nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SAMURAI-X.ORG ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL SAMURAI-X.ORG  BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
    :mod:`samuraix.main` provides with a setuptools entrypoint for the
    `sx-wm` console script.
"""

import sys
import os
import imp
import traceback
import logging
import pkg_resources
from optparse import OptionParser
from tempfile import gettempdir

SXWM_USAGE = '''sx-wm [options] '''
DEFAULT_LOGFILE = os.path.join(gettempdir(), 'sx.lastrun.log')

class SamuraiLogger(logging.Logger):
    """
        The SamuraiLogger is a convenience :class:`logging.Logger` subclass
        with additional functionalities to log exceptions nicer.
    """
    def exception(self, exc):
        """
            Improved exception logger.

            :param exc: An Exception instance
        """
        type_, value, tb = sys.exc_info()
        formatted = '\n'.join(traceback.format_exception(type_, value, tb))
        self._log(logging.ERROR, formatted, (), {})

logging.setLoggerClass(SamuraiLogger)

log = logging.getLogger(__name__)

import samuraix
from .logformatter import FDFormatter

def configure_logging(options, file_level=logging.DEBUG, console_level=logging.DEBUG):
    """
        Set up the logging for the client.

        :param file_level: level of logging for files
        :param console_level: level of logging for the console
    """
    console = logging.StreamHandler()
    console.setLevel(console_level)
    formatter = FDFormatter('[%(asctime)s %(levelname)s %(name)s] %(message)s')
    console.setFormatter(formatter)
    # reset the handlers incase its a restart
    logging.getLogger('').handlers = []
    logging.getLogger('').addHandler(console)
    logging.root.setLevel(logging.DEBUG)
    lastlog = logging.FileHandler(options.logfile, 'w')
    lastlog.setLevel(file_level)
    formatter = logging.Formatter(
            '[%(asctime)s %(levelname)s %(name)s %(lineno)d] %(message)s')
    lastlog.setFormatter(formatter)
    logging.getLogger('').addHandler(lastlog)

    # parse logging levels string, format is:
    #   <logger_name>:<level_name>[,<logger_name2>:<level_name2>[,...]]
    # where logger_name is the name of a logger eg samuraix.main
    # and level_name is a name as described in the logging module
    # such as DEBUG/INFO/ERROR
    for setting in getattr(options, 'logging_levels', '').split(','):
        setting = setting.strip()
        if not setting:
            continue
        name, level = setting.split(':')
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))

    log.info('logging everything to %s' % options.logfile)

def load_config(config=None):
    """
        Sets :attr:`samuraix.config` to the desired configuration dictionary.
        If *config* is None, it will load :mod:`samuraix.defaultconfig`.
        If *config* is callable, it will call it and use the return value
        instead.
    """
    if config is None:
        from samuraix.defaultconfig import config
    if callable(config):
        config = config()
    samuraix.config = config

def load_user_config(configpath):
    """
        Tries to execute the Python configuration script. Returns
        its *config* member on success, None if there was an error
        reading the config file (e.g. if the file does not exist)

        :param configpath: The filename of the configuration script
                           we should try to load.

        :note: Yes, the configuration file is a Python script, yes,
               it is executed and yes, that's unsafe. Let's trust
               the user that he knows what he does.

    """
    configpath = os.path.normpath(os.path.expanduser(configpath))
    log.info('trying to import config from %s...' % configpath)
    try:
        fp, pathname, description = imp.find_module('config', [configpath])
    except ImportError:
        log.warning('%s/config.py not found - using default config' % configpath)
        return None
    mod = imp.load_module('config', fp, pathname, description)
    return getattr(mod, 'config')

def parse_options():
    """
        Parse the command line options and return them. The command-line
        arguments are ignored, since we aren't accepting any.
    """
    parser = OptionParser(SXWM_USAGE)
    parser.add_option('-c', '--config', dest='configpath',
            help='use samurai-x2 configuration from PATH (default: %default)', metavar='FILE',
            default='~/.samuraix/')

    parser.add_option('-f', '--logfile', dest='logfile',
            help='save the samurai-x2 log file to FILE', metavar='FILE',
            default=DEFAULT_LOGFILE)

    parser.add_option('', '--default-config', dest='print_default_config',
            help='print the default configuration to stdout',
            action='store_true',
            default=False)

    parser.add_option('-s', '--synchronous-check', dest='synchronous_check',
            help='turn on synchronous checks (useful for debugging)',
            action='store_true',
            default=False)

    parser.add_option('-l', '--logging', dest='logging_levels',
            help='set a logging handler to a specific debug level',
            default='',
    )

    options, args = parser.parse_args()
    return options


def run(app_func=None):
    setup_ooxcb()
    while samuraix.restarting:
        log.info('restart loop')
        samuraix.restarting = False
        run_app(app_func=app_func)


def restart():
    log.info('restart')
    samuraix.restarting = True
    samuraix.app.stop()

def setup_ooxcb():
    """
        configure all required mixins
    """
    import ooxcb.contrib.icccm
    import ooxcb.contrib.ewmh

    ooxcb.contrib.icccm.mixin()
    ooxcb.contrib.ewmh.mixin()

def run_app(app_func=None):
    """
        Run samurai-x. That's also the setuptools entrypoint for the `sx-wm`
        console script.

        First, it parses the options. If the user specified `--default-config`,
        it will just print the defaultconfig.py file and quit.
        If not, it configures the logging and loads the configuration.
        Then :attr:`samuraix.app` is set to an instance of *app_func*,
        or, if *app_func* is None, to an instance of
        :class:`samuraix.appl.App`.
        After that, :meth:`samuraix.appl.App.init` and
        :meth:`samuraix.appl.App.run` are called.

        :param app_func: A callable returning an application instance and
                         taking no arguments. If it is None,
                         :class:`samuraix.appl.App` will be used as fallback.

    """
    options = parse_options()
    if options.print_default_config: # just print samuraix.defaultconfig and quit.
        print pkg_resources.resource_string('samuraix', 'defaultconfig.py')
        return

    configure_logging(options)

    cfg = load_user_config(options.configpath)
    load_config(cfg)

    if app_func is None:
        from samuraix.appl import App
        app_func = App

    samuraix.app = app = app_func()
    app.synchronous_check = options.synchronous_check

    try:
        app.init()
        app.run()
    except Exception:
        import traceback
        log.error(traceback.format_exc())

