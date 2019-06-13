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
from PyQt5.QtWidgets import QApplication
from pyDSA_gui.MainApp import AppWindow
import pytest
import os
from os.path import join
import glob


class MockEvent(object):
    def __init__(self, x, y):
        self.xdata = x
        self.ydata = y


class TestGui(object):

    def setup(self):
        self.app = QApplication([])
        self.w = AppWindow(self.app)
        self.ui = self.w.ui
        self.delay = 100
        pwd = os.path.dirname(os.path.realpath(__file__))
        filelist = glob.glob(join(pwd, '*.info'))
        for filepath in filelist:
            os.remove(filepath)

    def test_whole_process(self):
        QTest.qWait(self.delay)

        #======================================================================
        # TAB 1
        #======================================================================
        # Import video
        pwd = os.path.dirname(os.path.realpath(__file__))
        self.w.tab1.import_file(None, [os.path.join(pwd, 'test.avi')])
        QTest.qWait(self.delay)
        # Crop in time
        self.ui.tab1_spinbox_first.setValue(50+92)
        QTest.qWait(self.delay)
        self.ui.tab1_spinbox_last.setValue(400)
        QTest.qWait(self.delay)
        self.ui.tab1_spinbox_frame.setValue(200)
        QTest.qWait(self.delay)
        # Crop in space
        self.ui.mplwidgetimport.update_crop_area(100, 1500, 50, 250)
        QTest.qWait(self.delay)
        # Set baseline
        self.ui.mplwidgetimport.update_baseline([100, 200], [1500, 200])
        QTest.qWait(self.delay)
        # Set scaling
        self.ui.mplwidgetimport.scaling_hand.add_point(MockEvent(500, 100))
        self.ui.mplwidgetimport.scaling_hand.add_point(MockEvent(643, 110))
        self.ui.mplwidgetimport.scaling_hand.add_point(MockEvent(674, 83))
        self.ui.tab1_set_scaling_text.setText('0.44mm')
        QTest.qWait(self.delay)
        # Set time sclaing
        self.ui.tab1_set_dt_text.setText('0.34')
        QTest.qWait(self.delay)

        #======================================================================
        # TAB 2
        #======================================================================
        # Goto edge tab
        self.ui.tabWidget.setCurrentIndex(1)
        QTest.qWait(self.delay)
        # COntour detection
        self.ui.tab2_contour_box.setChecked(True)
        QTest.qWait(self.delay)
        self.ui.tab2_contour_level.setValue(50)
        QTest.qWait(self.delay)
        # Canny detection
        self.ui.tab2_contour_box.setChecked(False)
        self.ui.tab2_canny_box.setChecked(True)
        self.ui.tab2_canny_dilatation_steps.setValue(0)
        self.ui.tab2_canny_threshold1.setValue(50)
        self.ui.tab2_canny_threshold2.setValue(200)
        self.ui.tab2_canny_smooth_size.setValue(1)
        QTest.qWait(self.delay)

        #======================================================================
        # TAB 3
        #======================================================================
        # Goto fit tab
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        # Test circle fit
        self.ui.tab3_circle_box.setChecked(True)
        QTest.qWait(self.delay)
        # Test ellipse fit
        self.ui.tab3_ellipse_box.setChecked(True)
        QTest.qWait(self.delay)
        # Test two ellipses fit
        self.ui.tab3_ellipses_box.setChecked(True)
        QTest.qWait(self.delay)
        # Test polyline fit
        self.ui.tab3_polyline_box.setChecked(True)
        self.ui.tab3_polyline_deg.setValue(7)
        QTest.qWait(self.delay)
        # Test spline fit
        self.ui.tab3_spline_box.setChecked(True)
        self.ui.tab3_spline_deg.setValue(3)
        QTest.qWait(self.delay)
        # Test wetting ridge fit
        self.ui.tab3_wetting_ridge_box.setChecked(True)
        QTest.qWait(self.delay)
        # Back to ellipse
        self.ui.tab3_ellipse_box.setChecked(True)
        QTest.qWait(self.delay)

        #======================================================================
        # TAB 4
        #======================================================================
        # Goto analyze tab
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay)
        # Set number of frames to take
        self.ui.tab4_set_N.setValue(10)
        QTest.qWait(self.delay)
        self.w.tab4.compute()
        QTest.qWait(self.delay)
        self.ui.tab4_yaxis2_box.setChecked(True)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_xaxis.setCurrentIndex(1)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis.setCurrentIndex(0)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis2.setCurrentIndex(3)
        QTest.qWait(self.delay)

        #==============================================================================
        # Quickly check that wetting ridge stuff has been added as well to tab4
        #==============================================================================
        # Goto fit tab
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        # Test wetting ridge fit
        self.ui.tab3_wetting_ridge_box.setChecked(True)
        QTest.qWait(self.delay)
        # Goto analyze tab
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis.setCurrentIndex(13)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis2.setCurrentIndex(12)
        QTest.qWait(self.delay)
        # Goto fit tab
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        # Test wetting ridge fit
        self.ui.tab3_ellipse_box.setChecked(True)
        QTest.qWait(self.delay)
        # Goto analyze tab
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay)

        #======================================================================
        # TAB 5
        #======================================================================
        # Goto data tab
        self.ui.tabWidget.setCurrentIndex(4)
        QTest.qWait(self.delay)
        # Set number of frames to take
        self.ui.tab5_significativ_numbers.setValue(10)
        QTest.qWait(self.delay)
        # Try exporting
        self.w.tab5.export_as_csv(None, filepath="./test.csv")
        self.w.tab5.export_as_xlsx(None, filepath="./test.xlsx")
        QTest.qWait(self.delay)
        os.remove("./test.csv")
        os.remove("./test.xlsx")


        #==============================================================================
        # Back to TAB 1 to import images
        #==============================================================================
        # Goto import tab
        self.ui.tabWidget.setCurrentIndex(0)
        QTest.qWait(self.delay)
        self.w.tab1.import_file(None,
                                [os.path.join(pwd, f'test{i+1}.png')
                                 for i in range(8)])

        #==============================================================================
        # Just chec if other tab are alright
        #==============================================================================
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tab2_contour_box.setChecked(True)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis.setCurrentIndex(6)
        QTest.qWait(self.delay)
        self.ui.tab4_yaxis2_box.setChecked(False)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(4)
        QTest.qWait(self.delay)

        #==============================================================================
        # Back to TAB 1 to import an image
        #==============================================================================
        # Goto import tab
        self.ui.tabWidget.setCurrentIndex(0)
        QTest.qWait(self.delay)
        self.w.tab1.import_file(None, [os.path.join(pwd, 'test1.png')])

        #==============================================================================
        # Just chec if other tab are alright
        #==============================================================================
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tab2_contour_box.setChecked(True)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(2)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(3)
        QTest.qWait(self.delay)
        self.ui.tab4_combo_yaxis.setCurrentIndex(6)
        QTest.qWait(self.delay)
        self.ui.tab4_yaxis2_box.setChecked(False)
        QTest.qWait(self.delay)
        self.ui.tabWidget.setCurrentIndex(4)
        QTest.qWait(self.delay)

        #==============================================================================
        # Say that it is done
        #==============================================================================
        print("Test finished successfully")

        # #==============================================================================
        # # Wait at the end
        # #==============================================================================
        # QTest.qWait(50000000)
        # #==============================================================================
        # # Clean
        # #==============================================================================
        # pwd = os.path.dirname(os.path.realpath(__file__))
        # filelist = glob.glob(join(pwd, '*.info'))
        # for filepath in filelist:
        #     os.remove(filepath)

if __name__ == "__main__":
    test = TestGui()
    test.setup()
    test.test_whole_process()

    # pytest.main(['test_gui.py'])
