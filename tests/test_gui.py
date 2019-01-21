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

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QApplication, QDialog
from pyDSAqt5.MainApp import AppWindow
import pytest
import time


class TestGui(object):

    def setup(self):
        self.app = QApplication([])
        self.w = AppWindow()
        self.ui = self.w.ui
        self.delay = 500

    def test_whole_process(self):
        QTest.qWait(self.delay)
        # Import video
        self.w.tab1_import_video(None, '../tests/test.avi')
        QTest.qWait(self.delay)
        # Goto edge tab
        self.ui.tabWidget.setCurrentIndex(1)
        QTest.qWait(self.delay)
        # Goto fit tab
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        # Goto analyze tab
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay*4)


# # TEMP
# pytest.main(['test_gui.py'])
# # TEMP - End



# class WholeProcessTest(QTest):
#     def test(self):
#         # Push OK with the left mouse button
#        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
#        QTest.mouseClick(okWidget, Qt.LeftButton)
#        self.assertEqual(self.form.jiggers, 36.0)
#        self.assertEqual(self.form.speedName, "&Karate Chop")



# class Test(unittest.TestCase):

#     #----------------------------------------------------------------------

#     #----------------------------------------------------------------------
#     def test_update_label_from_menu(self):
#         self.assertEqual(self.ui.label.text(), 'Empty')
#         self.menu.actions()[0].menu().actions()[0].trigger()
#         self.assertEqual(self.ui.label.text(), 'Updated label')

#     #----------------------------------------------------------------------
#     def test_update_label_from_shortcut(self):
#         self.assertEqual(self.ui.label.text(), 'Empty')
#         QTest.keyClicks(self.ui, 'U', Qt.ControlModifier)
#         print(self.ui.label.text())

#         QTest.keyPress(self.ui, 'U', Qt.ControlModifier)
#         print(self.ui.label.text())

#         QTest.keyPress(self.ui, Qt.Key_U, Qt.ControlModifier)
#         print(self.ui.label.text())

#         self.assertEqual(self.ui.label.text(), 'Updated label')
#         return

#     #----------------------------------------------------------------------
#     def tearDown(self):
#         pass
