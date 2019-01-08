from datetime import timedelta
from PyQt5 import QtGui
import time


class Log(object):
    def __init__(self, display_area, status_bar):
        self.logs = []
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
        # Update log tab
        self.display_area.setTextColor(self.level_colors[level - 1])
        self.display_area.append(self.logs[-1])
        # Display in statu bar
        if level == 2:
            self.status_bar.showMessage(f"{message}")
        elif level == 3:
            self.status_bar.showMessage(f"Error: {message}")
