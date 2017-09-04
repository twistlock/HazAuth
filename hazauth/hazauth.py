#!/usr/bin/env python

import os
import sys

from pluginmanager import PluginManager


class HazAuth:
    """ Main command line interface """

    def __init__(self):
        """ Initialize the plugin manager """
        self.__pluginmanager = PluginManager()

    def _print_usage(self, should_list_plugins=False):
        print("Usage: {0} <plugin> <command> [<options>]".format(sys.argv[0]))

        if should_list_plugins:
            print("The following plugins are available:\n")
            self.__pluginmanager.help_all()

    def main(self, args):
        """ Validates user input and delegates to the plugin manager """

        if len(args) == 0:
            self._print_usage(should_list_plugins=True)
            return os.EX_USAGE

        elif len(args) == 1:
            self._print_usage()

            # Call the given plugin without command to print
            # the help of the plugin
            self.__pluginmanager.call(args[0], None, None)
            return os.EX_USAGE

        else:
            # Call the command in the given plugin with the
            # remaining arguments

            return self.__pluginmanager.call(args[0],
                                             args[1],
                                             args[2:])


if "__main__" == __name__:
    cli = HazAuth()
    return_code = cli.main(sys.argv[1:])

    if return_code:
        sys.exit(return_code)
    else:
        sys.exit(os.EX_UNAVAILABLE)
