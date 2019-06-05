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
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"


import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui

from .design import Ui_MainWindow
from .dsa_backend import DSA_hdd as DSA
from .log import Log
from .tab import Tab
from .tabimport import TabImport
from .tabedges import TabEdges
from .tabfits import TabFits
from .tabanalyze import TabAnalyze
from .tabdata import TabData


# TODO: Add export_as_script
# TODO: Add tests (QT5 tests ?)
#       - http://johnnado.com/pyqt-qtest-example/
#       - https://pypi.org/project/pytest-qt/
# TODO: Add circles fitting for ridge detection
# TODO: Add keybindings
# TODO: Make everything asynchroneous
class AppWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.globalapp = app
        # Properly set the icon
        script_path = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_path, "../icon/pyDSA_logo.eps")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        # Variables
        self.current_ind = 0
        self.statusbar_delay = 2000
        # Initialize log
        self.ui.logarea = None  # needed to be initialized for log
        self.ui.status_bar = None
        self.log = Log(self.ui, self.statusbar_delay)
        # Initialize dsa backend
        self.dsa = DSA(self)
        # Initialize tabs (need to be done before initializing design.py)
        self.tab1 = TabImport(self.ui, self, self.dsa, self.log)
        self.tab2 = TabEdges(self.ui, self, self.dsa, self.log)
        self.tab3 = TabFits(self.ui, self, self.dsa, self.log)
        self.tab4 = TabAnalyze(self.ui, self, self.dsa, self.log)
        self.tab5 = TabData(self.ui, self, self.dsa, self.log)
        self.tab6 = Tab(self.ui, self, self.dsa, self.log)
        self.tabs = [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5,
                     self.tab6]
        self.last_tab = 0
        # Including design.ui
        self.ui.setupUi(self)
        # Add missing links
        self.ui.mplwidgetanalyze.ui = self.ui
        self.ui.mplwidgetanalyze.app = self
        # Initialize progressbar
        self.init_progressbar()
        # Always start from the first tab
        self.ui.tabWidget.setCurrentIndex(0)
        # Show it !
        self.show()

    @property
    def plottable_quant(self):
        pq = ['Frame number', 'Time', 'Position (x, right)',
              'CL velocity (x, left)', 'CL velocity (x, right)',
              'Position (x, left)', 'Position (x, center)',
              'CA (right)', 'CA (left)', 'CA (mean)', 'Base radius',
              'Height', 'Area', 'Volume']
        if self.dsa.fit_method == 'wetting ridge':
            pq += ['Ridge height (left)', 'Ridge height (right)',
                   'CA (TP, left)', 'CA (TP, right)',
                   'CA (TP, mean)']
        return pq

    def init_progressbar(self):
        # Add Progress bar to status bar
        self.ui.progressbar = QtWidgets.QProgressBar()
        self.ui.progressbar.setMaximumSize(QtCore.QSize(250, 16777215))
        self.ui.progressbar.setTextVisible(True)
        self.ui.progressbar.setFormat("%p%")
        self.ui.progressbar.setValue(0)
        self.ui.progressbar.setVisible(False)
        self.ui.cancelbutton = QtWidgets.QPushButton()
        self.ui.cancelbutton.setText('Cancel')
        self.ui.cancelbutton.setVisible(False)
        self.ui.cancelbutton.clicked.connect(self.cancel_computation)
        self.ui.statusbar.addPermanentWidget(self.ui.cancelbutton)
        self.ui.statusbar.addPermanentWidget(self.ui.progressbar)

    def cancel_computation(self):
        self.dsa.stop = True

    def enable_options(self):
        """ To run after importing at least an image"""
        for tab in self.tabs:
            tab.enable_options()

    def change_tab(self, tab_nmb):
        # Do nothing if no imported image yet
        if not self.dsa.is_initialized():
            return None
        # Leave the current tab
        success = self.tabs[self.last_tab].leave_tab()
        if not success:
            self.ui.tabWidget.setCurrentIndex(self.last_tab)
            self.log.log('Something wrong happened during tab switching',
                         level=3)
            return None
        # enter the new tab
        self.tabs[tab_nmb].enter_tab()
        # Update last tab number
        self.last_tab = tab_nmb

    def set_current_ind(self, ind):
        if self.dsa.is_valid_ind(ind):
            self.current_ind = ind

    # Menu
    def export_as_script(self):
        params_im = self.tab1_get_params()
        params_edges = self.tab2_get_params()
        params_fit = self.tab3_get_params()
        raise Exception('Not implemented yet')


def run():
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = AppWindow(app)
    w.show()
    # exit()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
