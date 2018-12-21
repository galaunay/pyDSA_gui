import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog,\
    QDialog
from PyQt5 import QtWidgets, QtCore, QtGui
from design import Ui_MainWindow
import numpy as np

from dsa_backend import DSA
from log import Log


def select_file(message="Open file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileName(dialog, message,
                                           filter=filetypes)
    return filepath


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
        self.dsa = DSA(self)
        self.log = Log(self.ui.logarea, self.ui.statusbar)
        self._disable_frame_updater = False
        self.tab2_initialized = False
        self.tab3_initialized = False
        self.last_tab = 0

    def tab_changed(self, tab_nmb):
        # Do nothing if no imported images
        if self.dsa.ims is None:
            return None
        # Update dsa backend if last tab is import tab
        if self.last_tab == 0:
            self.dsa.update_crop_lims()
            self.dsa.update_baselines()
        # First tab
        if tab_nmb == 0:
            self.tab1_switch_to_tab()
        elif tab_nmb == 1:
            self.tab2_switch_to_tab()
        elif tab_nmb == 2:
            self.tab3_switch_to_tab()
        # Update last tab
        self.last_tab = tab_nmb

    # TAB 1
    def tab1_switch_to_tab(self):
        # Update the frame number
        self.ui.tab1_frameslider.setValue(self.dsa.current_ind + 1)
        self.ui.tab1_spinbox.setValue(self.dsa.current_ind + 1)

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

    def tab1_enable_baseline(self):
        w = self.dsa.current_raw_im.shape[0]
        h = self.dsa.current_raw_im.shape[1]
        pt1 = [1/10*w, 2/3*h]
        pt2 = [9/10*w, 2/3*h]
        self.ui.mplwidgetimport.update_baseline(pt1, pt2)

    def tab1_enable_scaling(self):
        self.ui.tab1_set_scaling_btn.setEnabled(True)
        self.ui.tab1_set_scaling_text.setEnabled(True)
        self.ui.tab1_remove_scaling_btn.setEnabled(True)

    def tab1_import_image(self):
        filepath = select_file('Open image')[0]
        try:
            self.dsa.import_image(filepath)
        except:
            self.log.log(f"Couldn't import image: {filepath}", level=3)
            return None
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable cropping sliders
        self.tab1_enable_cropping()
        # Enable baseline
        self.tab1_enable_baseline()
        # Enable scaling
        self.tab1_enable_scaling()

    def tab1_import_video(self):
        filepath = select_file('Open video')[0]
        try:
            self.dsa.import_video(filepath)
        except:
            self.log.log(f"Couldn't import video: {filepath}", level=3)
            return None
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values,
                                             replot=True)
        # Enable frame sliders
        self.tab1_enable_frame_sliders()
        # Enable cropping sliders
        self.tab1_enable_cropping()
        # Enable baseline
        self.tab1_enable_baseline()
        # Enable scaling
        self.tab1_enable_scaling()

    def tab1_set_current_frame(self, ind):
        self.dsa.set_current(ind - 1)
        self.ui.mplwidgetimport.update_image(self.dsa.current_raw_im.values)

    def tab1_reset_crop(self):
        crop_lims = [0, self.dsa.current_raw_im.shape[0],
                     0, self.dsa.current_raw_im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def tab1_set_scaling(self):
        self.ui.mplwidgetimport.is_scaling = True

    def tab1_remove_scaling(self):
        self.ui.mplwidgetimport.is_scaling = False
        self.ui.mplwidgetimport.scaling_hand.reset()

    # TAB 2
    def tab2_initialize(self):
        # enable slider if necessary
        if self.dsa.nmb_frames > 1:
            self.tab2_enable_frame_sliders()

    def tab2_switch_to_tab(self):
        draw = True
        if not self.tab2_initialized:
            self.tab2_initialize()
            draw = False
        # Replot the plot
        self.ui.mplwidgetdetect.update_image(
            self.dsa.current_cropped_im.values,
            replot=True, draw=draw)
        pt1, pt2 = self.dsa.get_baseline(cropped=True)
        self.ui.mplwidgetdetect.update_baseline(pt1, pt2, draw=draw)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setValue(self.dsa.current_ind + 1)
        self.ui.tab2_spinbox.setValue(self.dsa.current_ind + 1)
        self._disable_frame_updater = False
        # update the detected edge
        self.tab2_update_edge(draw=draw)
        #
        self.tab2_initialized = True

    def tab2_set_current_frame(self, ind):
        if self._disable_frame_updater:
            return None
        self.dsa.set_current(ind - 1)
        # update image
        self.ui.mplwidgetdetect.update_image(self.dsa.current_cropped_im.values,
                                             replot=False)
        # update edge
        # TODO: replotting the edge markersfor each frame take time,
        #       It may be a better idea to use imshow to display edges
        self.tab2_update_edge()

    def tab2_enable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setMinimum(1)
        self.ui.tab2_frameslider.setMaximum(self.dsa.nmb_frames)
        self.ui.tab2_spinbox.setMinimum(1)
        self.ui.tab2_spinbox.setMaximum(self.dsa.nmb_frames)
        self.ui.tab2_frameslider.setEnabled(True)
        self.ui.tab2_spinbox.setEnabled(True)
        self._disable_frame_updater = False

    def tab2_get_params(self):
        contour = {}
        options = {}
        canny = {'threshold1': self.ui.tab2_canny_threshold1.value(),
                 'threshold2': self.ui.tab2_canny_threshold2.value(),
                 'dilatation_steps': self.ui.tab2_canny_dilatation_steps.value(),
                 'smooth_size': self.ui.tab2_canny_smooth_size.value()}
        contour = {'level': self.ui.tab2_contour_level.value()/255,
                   'ignored_pixels': self.ui.tab2_ign_pixels.value(),
                   'size_ratio': self.ui.tab2_size_ratio.value()/100}
        if self.ui.tab2_nmb_edges_1.isChecked():
            edges = 1
        else:
            edges = 2
        options = {'nmb_edges': edges}
        return canny, contour, options

    def tab2_update_edge(self, draw=True):
        params = self.tab2_get_params()
        try:
            edge = self.dsa.get_current_edge(params)
        except Exception:
            self.log.log("Couldn't find a drop on the current frame",
                         level=2)
            edge = [[], []]
        self.ui.mplwidgetdetect.update_edge(edge, draw=draw)

    def tab2_toggle_canny(self, toggle):
        if toggle:
            self.dsa.edge_detection_method = 'canny'
            self.ui.tab2_contour_box.setChecked(False)
        else:
            if not self.ui.tab2_contour_box.isChecked():
                self.dsa.edge_detection_method = None
        self.tab2_update_edge()

    def tab2_toggle_contour(self, toggle):
        if toggle:
            self.dsa.edge_detection_method = 'contour'
            self.ui.tab2_canny_box.setChecked(False)
        else:
            if not self.ui.tab2_canny_box.isChecked():
                self.dsa.edge_detection_method = None
        self.tab2_update_edge()

    # TAB 3
    def tab3_initialize(self):
        # enable slider if necessary
        if self.dsa.nmb_frames > 1:
            self.tab3_enable_frame_sliders()

    def tab3_switch_to_tab(self):
        draw = True
        if not self.tab3_initialized:
            self.tab3_initialize()
            draw = False
        # Update the plot only if necessary
        self.dsa.update_crop_lims()
        self.ui.mplwidgetfit.update_image(
            self.dsa.current_cropped_im.values,
            replot=True, draw=draw)
        self.dsa.update_baselines()
        self.ui.mplwidgetfit.update_baseline(*self.dsa.get_baseline(),
                                             draw=draw)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setValue(self.dsa.current_ind + 1)
        self.ui.tab3_spinbox.setValue(self.dsa.current_ind + 1)
        self._disable_frame_updater = False
        # update the detected edge
        self.tab3_update_fit(draw=draw)
        # update the 'ignore lower part' slider upper bound
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        self.ui.tab3_circle_ymin.setMaximum(sizey)
        self.ui.tab3_ellipse_ymin.setMaximum(sizey)
        #
        self.tab3_initialized = True

    def tab3_set_current_frame(self, ind):
        if self._disable_frame_updater:
            return None
        self.dsa.set_current(ind - 1)
        # update image
        self.ui.mplwidgetfit.update_image(self.dsa.current_cropped_im.values,
                                          replot=False)
        # update fit
        self.tab3_update_fit()

    def tab3_enable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setMinimum(1)
        self.ui.tab3_frameslider.setMaximum(self.dsa.nmb_frames)
        self.ui.tab3_spinbox.setMinimum(1)
        self.ui.tab3_spinbox.setMaximum(self.dsa.nmb_frames)
        self.ui.tab3_frameslider.setEnabled(True)
        self.ui.tab3_spinbox.setEnabled(True)
        self._disable_frame_updater = False

    def tab3_get_params(self):
        circle = {'triple_pts': [[0, self.ui.tab3_circle_ymin.value()]]*2}
        ellipse = {'triple_pts': [[0, self.ui.tab3_ellipse_ymin.value()]]*2}
        polyline = {'deg': self.ui.tab3_polyline_deg.value()}
        spline = {'k': self.ui.tab3_spline_deg.value(),
                  's': self.ui.tab3_spline_smooth.value()/100}
        return circle, ellipse, polyline, spline

    def tab3_update_fit(self, draw=True):
        params = self.tab3_get_params()
        try:
            fit, fit_center = self.dsa.get_current_fit(params)
        except Exception:
            self.log.log("Couldn't find a fit for the current edge",
                         level=2)
            fit = [[], []]
            fit_center = [[], []]
        self.ui.mplwidgetfit.update_fit(fit, fit_center, draw=draw)

    def _tab3_uncheck_others(self, box):
        checks = [b.setChecked(False)
                  for b in [self.ui.tab3_circle_box,
                            self.ui.tab3_ellipse_box,
                            self.ui.tab3_polyline_box,
                            self.ui.tab3_spline_box]
                  if b != box and b.isChecked()]
        return checks

    def _tab3_update_fit_method(self):
        checks = np.array([box.isChecked()
                           for box in [self.ui.tab3_circle_box,
                                       self.ui.tab3_ellipse_box,
                                       self.ui.tab3_polyline_box,
                                       self.ui.tab3_spline_box]])
        # if not np.any(checks):
        #     self.dsa.fit_method = None

    def tab3_toggle_circle(self, toggle):
        if toggle:
            self.dsa.fit_method = 'circle'
            self._tab3_uncheck_others(self.ui.tab3_circle_box)
        else:
            self._tab3_update_fit_method()
        self.tab3_update_fit()

    def tab3_toggle_ellipse(self, toggle):
        if toggle:
            self.dsa.fit_method = 'ellipse'
            self._tab3_uncheck_others(self.ui.tab3_ellipse_box)
        else:
            self._tab3_update_fit_method()
        self.tab3_update_fit()

    def tab3_toggle_polyline(self, toggle):
        if toggle:
            self.dsa.fit_method = 'polyline'
            self._tab3_uncheck_others(self.ui.tab3_polyline_box)
        else:
            self._tab3_update_fit_method()
        self.tab3_update_fit()

    def tab3_toggle_spline(self, toggle):
        if toggle:
            self.dsa.fit_method = 'spline'
            self._tab3_uncheck_others(self.ui.tab3_spline_box)
        else:
            self._tab3_update_fit_method()
        self.tab3_update_fit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())
