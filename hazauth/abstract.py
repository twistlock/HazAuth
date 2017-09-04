#!/usr/bin/env python


class AbsPlugin:
    """ Abstract plugin """

    def _commands(self):
        """ Get the list of commands for the current plugin.
        By default all public methods in the plugin implementation
        will be used as plugin commands. This method can be overriden
        in subclasses to customize the available command list """
        attrs = [attr for attr in dir(self) if not attr.startswith('_')]
        commands = {}
        for attr in attrs:
            method = getattr(self, attr)
            commands[attr] = method

        return commands
