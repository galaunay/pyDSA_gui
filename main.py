import sys
import pyDSA as dsa
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from design import Ui_MainWindow
import numpy as np


class DSA(object):
    def __init__(self, ui):
        self.ui = ui
        self.current_ind = 0
        self.ims = None
        self.current_raw_im = None
        self.ims_cropped = None
        self.current_crop_lims = None
        self.current_cropped_im = None
        self.edges = None
        self.current_edge = None
        self.fits = None
        self.current_fit = None
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None

    def import_image(self, filepath):
        self.ims = dsa.import_from_image(filepath, cache_infos=False)
        self.current_raw_im = self.ims
        self.nmb_frames = 1
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def import_video(self, filepath):
        self.ims = dsa.import_from_video(filepath, cache_infos=False)
        self.current_raw_im = self.ims[0]
        self.nmb_frames = len(self.ims)
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def set_current(self, ind):
        if self.nmb_frames == 1:
            return None
        self.current_ind = ind
        if self.ims is None:
            raise Exception()
        if ind > self.nmb_frames:
            raise Exception()
        self.current_raw_im = self.ims[ind]
        if self.ims_cropped is not None:
            self.current_cropped_im = self.ims_cropped[self.current_ind]

    def update_crop_lims(self):
        xlims, ylims = self.ui.mplwidgetimport.rect_hand.lims
        lims = np.array([xlims, ylims])
        if self.current_crop_lims is not None:
            if np.allclose(lims, self.current_crop_lims):
                return False
        self.current_crop_lims = lims
        self.ims_cropped = self.ims.crop(intervx=xlims, intervy=ylims,
                                         inplace=False)
        if self.nmb_frames == 1:
            self.current_cropped_im = self.ims_cropped
        else:
            self.current_cropped_im = self.ims_cropped.fields[self.current_ind]
        return True


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # # Add progress bar to status bar
        # self.ui.progressbar = QtWidgets.QProgressBar()
        # self.ui.progressbar.setMaximumSize(QtCore.QSize(150, 16777215))
        # self.ui.statusbar.addPermanentWidget(self.ui.progressbar)
        self.show()
        self.dsa = DSA(self.ui)
        self._disable_frame_updater = False
        self.tab2_initialized = False

    # TAB 1
    def tab1_enable_frame_sliders(self):
        self.ui.tab1_frameslider.setMinimum(1)
        self.ui.tab1_frameslider.setMaximum(self.dsa.nmb_frames)
        self.ui.tab1_spinbox.setMinimum(1)
        self.ui.tab1_spinbox.setMaximum(self.dsa.nmb_frames)
        self.ui.tab1_frameslider.setEnabled(True)
        self.ui.tab1_spinbox.setEnabled(True)

    def tab1_enable_cropping(self):
        self.ui.reset_crop.setEnabled(True)
        crop_lims = [0, self.dsa.current_raw_im.shape[0],
                     0, self.dsa.current_raw_im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def import_image(self):
        filepath = 'test.png'
        self.dsa.import_image(filepath)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable cropping sliders
        self.tab1_enable_cropping()

    def import_video(self):
        filepath = 'test.avi'
        self.dsa.import_video(filepath)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable frame sliders
        self.tab1_enable_frame_sliders()
        # Enable cropping sliders
        self.tab1_enable_cropping()

    def tab1_set_current_frame(self, ind):
        self.dsa.set_current(ind - 1)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values)

    def reset_crop(self):
        crop_lims = [0, self.dsa.current_raw_im.shape[0],
                     0, self.dsa.current_raw_im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def tab_changed(self, tab_nmb):
        if self.dsa.ims is None:
            return None
        if tab_nmb == 0:
            # Just to update
            self.ui.tab1_frameslider.setValue(self.dsa.current_ind + 1)
            self.ui.tab1_spinbox.setValue(self.dsa.current_ind + 1)
        if tab_nmb == 1:
            # Because of issue leading to massive slow down when
            # rendereing the second tab the first time...
            if self.tab2_initialized:
                draw = True
            else:
                draw = False
            updated = self.dsa.update_crop_lims()
            # enable slider if necessary
            if (not self.ui.tab2_frameslider.isEnabled()
                and self.dsa.nmb_frames > 1):
                self.tab2_enable_frame_sliders()
            # Update the plot only if necessary
            self.ui.mplwidgetdetect.update_image(
                self.dsa.current_cropped_im.values,
                replot=updated, draw=draw)
            self._disable_frame_updater = True
            self.ui.tab2_frameslider.setValue(self.dsa.current_ind + 1)
            self.ui.tab2_spinbox.setValue(self.dsa.current_ind + 1)
            self._disable_frame_updater = False
            self.tab2_initialized = True

    # TAB 2
    def tab2_set_current_frame(self, ind):
        if self._disable_frame_updater:
            return None
        self.dsa.set_current(ind - 1)
        self.ui.mplwidgetdetect.update_image(self.dsa.current_cropped_im.values,
                                             replot=False)

    def tab2_enable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setMinimum(1)
        self.ui.tab2_frameslider.setMaximum(self.dsa.nmb_frames)
        self.ui.tab2_spinbox.setMinimum(1)
        self.ui.tab2_spinbox.setMaximum(self.dsa.nmb_frames)
        self.ui.tab2_frameslider.setEnabled(True)
        self.ui.tab2_spinbox.setEnabled(True)
        self._disable_frame_updater = False


app = QApplication(sys.argv)
w = AppWindow()
import time
w.ui.tabWidget.setCurrentIndex(1)
w.ui.tabWidget.setCurrentIndex(0)
w.show()
# # TEMP
# w.import_video()
# # TEMP - End
sys.exit(app.exec_())
