import sys
import pyDSA as dsa
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from design import Ui_MainWindow


class DSA(object):
    def __init__(self):
        self.ims = None
        self.current_raw_im = None
        self.crop_lims = None
        self.current_cropped_im = None
        self.current_edge = None
        self.current_fit = None
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None

    def import_image(self, filepath):
        self.ims = dsa.import_from_image(filepath, cache_infos=False)
        self.current_raw_im = self.ims
        self.nmb_frames = 1
        self.crop_lims = [0, self.current_raw_im.shape[0],
                          0, self.current_raw_im.shape[1]]
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def import_video(self, filepath):
        self.ims = dsa.import_from_video(filepath, cache_infos=False)
        self.current_raw_im = self.ims[0]
        self.nmb_frames = len(self.ims)
        self.crop_lims = [0, self.current_raw_im.shape[0],
                          0, self.current_raw_im.shape[1]]
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def set_current(self, ind):
        if self.ims is None:
            raise Exception()
        if ind > len(self.ims):
            raise Exception()
        self.current_raw_im = self.ims[ind]


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
        self.dsa = DSA()

    def enable_frame_sliders(self):
        self.ui.FrameSlider.setMinimum(1)
        self.ui.FrameSlider.setMaximum(self.dsa.nmb_frames)
        self.ui.FrameSpinBox.setMinimum(1)
        self.ui.FrameSpinBox.setMaximum(self.dsa.nmb_frames)
        self.ui.FrameSlider.setEnabled(True)
        self.ui.FrameSpinBox.setEnabled(True)

    def enable_cropping_sliders(self):
        self.ui.xlim1.setEnabled(True)
        self.ui.xlim1.setMaximum(self.dsa.sizex - 1)
        self.ui.xlim2.setEnabled(True)
        self.ui.xlim2.setMaximum(self.dsa.sizex - 1)
        self.ui.ylim1.setEnabled(True)
        self.ui.ylim1.setMaximum(self.dsa.sizey - 1)
        self.ui.ylim2.setEnabled(True)
        self.ui.ylim2.setMaximum(self.dsa.sizey - 1)
        self.ui.mplwidgetimport.update_crop_area(*self.dsa.crop_lims)

    def import_image(self):
        filepath = 'test.png'
        self.dsa.import_image(filepath)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable cropping sliders
        self.enable_cropping_sliders()

    def import_video(self):
        filepath = 'test.avi'
        self.dsa.import_video(filepath)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable frame sliders
        self.enable_frame_sliders()
        # Enable cropping sliders
        self.enable_cropping_sliders()

    def set_current_frame(self, ind):
        self.dsa.set_current(ind - 1)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values)

    def set_crop_xlim1(self, xlim1):
        self.dsa.crop_lims[0] = xlim1
        self.ui.mplwidgetimport.update_crop_area(*self.dsa.crop_lims)

    def set_crop_xlim2(self, xlim2):
        self.dsa.crop_lims[1] = self.dsa.current_raw_im.shape[0] - xlim2
        self.ui.mplwidgetimport.update_crop_area(*self.dsa.crop_lims)

    def set_crop_ylim1(self, ylim1):
        self.dsa.crop_lims[2] = ylim1
        self.ui.mplwidgetimport.update_crop_area(*self.dsa.crop_lims)

    def set_crop_ylim2(self, ylim2):
        self.dsa.crop_lims[3] = self.dsa.current_raw_im.shape[1] - ylim2
        self.ui.mplwidgetimport.update_crop_area(*self.dsa.crop_lims)


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
