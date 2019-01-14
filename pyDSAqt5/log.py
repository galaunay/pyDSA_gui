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
import time


class Log(object):
    def __init__(self, display_area, status_bar, delay):
        self.logs = []
        self.delay = delay
        self.display_area = display_area
        self.status_bar = status_bar
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
        self.display_area.setTextColor(self.level_colors[level - 1])
        self.display_area.append(self.logs[-1])
        # Display in statu bar
        if level == 2:
            self.status_bar.showMessage(f"{message}", self.delay)
        elif level == 3:
            self.status_bar.showMessage(f"Error: {message}", self.delay)
