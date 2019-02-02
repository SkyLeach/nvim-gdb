#!/usr/bin/env python3

"""
Run GDB in a pty.

This will allow to inject server commands not exposing them
to a user.
"""

import re
import json
import os

from BaseProxy import BaseProxy
import StreamFilter

class GdbProxy(BaseProxy):
    def __init__(self):
        super().__init__("GDB")
        self.last_src = None

    def ProcessInfoBreakpoints(self, response):
        # Gdb invokes a custom gdb command implemented in Python.
        # It itself is responsible for sending the processed result
        # to the correct address.

        # Select lines in the current file with enabled breakpoints.
        pattern = re.compile("([^:]+):(\d+)")
        breaks = {}
        for line in response.decode('utf-8').splitlines():
            try:
                fields = re.split("\s+", line)
                if fields[3] == 'y':    # Is enabled?
                    m = pattern.fullmatch(fields[-1])   # file.cpp:line
                    if (m and (self.last_src.endswith(m.group(1)) or self.last_src.endswith(os.path.realpath(m.group(1))))):
                        line = m.group(2)
                        brId = int(fields[0])
                        try:
                            breaks[line].append(brId)
                        except KeyError:
                            breaks[line] = [brId]
            except Exception as e:
                pass

        self.last_src = None
        return json.dumps(breaks).encode('utf-8')

    def FilterCommand(self, command):
        tokens = re.split(r'\s+', command.decode('utf-8'))
        if tokens[0] == 'info-breakpoints':
            self.last_src = tokens[1]
            self.set_filter(StreamFilter.StreamFilter(b"server nvim-gdb-", b"\n(gdb) "),
                            self.ProcessInfoBreakpoints)
            return b'server nvim-gdb-info-breakpoints\n'
        return command


if __name__ == '__main__':
    GdbProxy().run()
