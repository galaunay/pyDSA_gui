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
        t = str(timedelta(seconds=int(time.time()-self.t0)))
        text = f"{t}  {self.levels[level-1]}: {message}"
        self.logs.append(text)
        # Update log tab
        self.display_area.setTextColor(self.level_colors[level - 1])
        self.display_area.append(self.logs[-1])
        # Display in statu bar
        self.status_bar.showMessage(text)
