# -*- coding: utf-8 -*-
#!/usr/env python3

# Copyright (C) 2018-2019 Gaby Launay

# Author: Gaby Launay  <gaby.launay@tutanota.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Gaby Launay"
__copyright__ = "Gaby Launay 2018-2019"
__credits__ = ""
__license__ = "GPL3"
__version__ = ""
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"


from datetime import timedelta
from PyQt5 import QtGui
import sys
import traceback
import time


# class catchAndLog(object):
#     """
#     Decorator that catches and log exceptions.
#     """

#     def __init__(self, log, filter=[], default_return=None):
#         """
#         Decorator that catches and log exceptions.

#         Parameters
#         ----------
#         log: Log instance
#             Log instance to communicate with
#         filter: list of Exception
#             Exception to ignore (log on a low level)
#         default_return: anything
#             Default return value for the function in case of Exception
#         """
#         self.log = log
#         self.filter = filter
#         self.default_return = default_return

#     def __call__(self, fun):
#         def wrapped(loc_self, *args):
#             print(f"args: {args}")
#             try:
#                 res = fun(loc_self, *args)
#                 return res
#             except:
#                 exc_info = sys.exc_info()
#                 exc = exc_info[0]
#                 if exc in self.filter:
#                     self.log_low(fun, exc_info)
#                 else:
#                     self.log_high(fun, exc_info)
#                 return self.default_return
#         return wrapped

#     def log_low(self, f, exc_info):
#         pass

#     def log_high(self, f, exc_info):
#         errmess = "".join(traceback.format_exception(*exc_info))
#         mess = f"Unknown error while running {f.__name__}:\n{errmess}"
#         self.log.log(mess, level=3)


class Log(object):
    def __init__(self, ui, delay=1):
        self.logs = []
        self.delay = delay
        self.ui = ui
        self.t0 = time.time()
        self.levels = ['Info', 'Warning', 'Error']
        self.level_colors = [QtGui.QColor(col)
                             for col in ['grey', 'orange', 'red']]

    def log(self, message, level):
        """
        Log a new message.

        Parameters
        ----------
        messages: string
           Message to log.

        level: int in [1, 2, 3]
           Level of the messages:
           1: just log to log tab
           2: log to log tab and display in minibar
           3: log in log tab and display in minibar in red !
        """
        t = str(timedelta(seconds=int(time.time()-self.t0)))
        text = f"{t}  {self.levels[level-1]}: {message}"
        self.logs.append(text)
        # Print in shell
        print(text)
        # Update log tab
        if self.ui.logarea is not None:
            self.ui.logarea.setTextColor(self.level_colors[level - 1])
            self.ui.logarea.append(self.logs[-1])
        # Display in statu bar
        if self.ui.status_bar is not None:
            short_mess = message.split('\n')[-1]
            if level == 2:
                self.ui.status_bar.showMessage(f"{short_mess}", self.delay)
            elif level == 3:
                self.ui.status_bar.showMessage(f"Error: {short_mess}",
                                               self.delay)

    def log_unknown_exception(self):
        # Get last exception
        exc_info = sys.exc_info()
        # log the error
        errmess = "Unknown error: " + str(exc_info[1])
        self.log(errmess, level=3)
        # print traceback
        trcmess = ' '*9 + "".join(traceback.format_exception(*exc_info))
        print(trcmess.replace('\n', '\n' + ' '*9))


if __name__ == "__main__":

    class LowError(Exception):
        pass

    class HighError(Exception):
        pass

    @catchAndLog(Log(None, None, 1), filter=[LowError], default_return=45)
    def foo(a, b):
        if a < 2:
            raise LowError('a is too small')
        if b < 2:
            raise HighError('b is too small')
        return a + b

    # try it
    print("")
    print("Alright")
    print(foo(3, 4))
    print("")
    print("Alright but return 45")
    print(foo(1, 5))
    print("")
    print("Not alright")
    print(foo(3, 1))
    print("")
    print("Not alright")
    print(foo("un", "deux"))
