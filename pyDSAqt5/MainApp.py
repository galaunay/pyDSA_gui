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


from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,\
    QDialog
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np

from IMTreatment.utils import make_unit
import re
from .design import Ui_MainWindow
from .dsa_backend import DSA_hdd as DSA
from .log import Log


def select_file(message="Open file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileName(dialog, message,
                                           filter=filetypes)
    return filepath


def select_new_file(message="New file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getSaveFileName(dialog, message,
                                           filter=filetypes)
    return filepath


def select_files(message="Open files", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileNames(dialog, message,
                                            filter=filetypes)
    return filepath


class Tab(object):

    def __init__(self, ui, app, dsa, log):
        self.app = app
        self.ui = ui
        self.dsa = dsa
        self.log = log
        self.initialized = False
        self.already_opened = False

    def enter_tab(self):
        pass

    def leave_tab(self):
        return True

    def enable_options(self):
        pass


class TabImport(Tab):

    def __init__(self, ui, app, dsa, log):
        super().__init__(ui, app, dsa, log)

    def enter_tab(self):
        # Update the frame number
        self.ui.tab1_spinbox_frame.setValue(self.app.current_ind + 1)

    def leave_tab(self):
        # reset zoom
        self.ui.mplwidgetimport.reset_zoom()
        # Checks entries
        if not self.is_inputs_valid():
            return False
        # Ensure current image is in the selected range
        cropt = self.get_params('cropt')
        if self.app.current_ind > cropt[1] - 1:
            self.app.set_current_ind(cropt[1] - 1)
        elif self.app.current_ind < cropt[0] - 1:
            self.app.set_current_ind(cropt[0] - 1)
        # Save settings as infofile
        self.dsa.save_infofile()
        return True

    def enable_options(self):
        self.ui.tab1_crop_box.setEnabled(True)
        self.ui.tab1_scaling_box.setEnabled(True)
        self.ui.tab1_time_box.setEnabled(True)
        if self.dsa.input_type == "video":
            self.ui.tab1_dt_from_video.setVisible(True)
        else:
            self.ui.tab1_dt_from_video.setVisible(False)

    def is_inputs_valid(self):
        try:
            self.get_params('dt')
        except:
            self.log.log("Bad format for 'dt'", level=2)
            return False
        try:
            self.get_params('dx')
        except:
            self.log.log("Bad format for 'dx'", level=2)
            return False
        return True

    def enable_frame_sliders(self):
        self._disable_frame_updater = True
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(True)
            slide.setVisible(True)
            slide.setMinimum(1)
            slide.setMaximum(self.dsa.nmb_frames)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(True)
            spin.setVisible(True)
            spin.setMinimum(1)
            spin.setMaximum(self.dsa.nmb_frames)
        self.ui.tab1_frameslider_last.setValue(self.dsa.nmb_frames)
        self.ui.tab1_frameslider_first.setValue(0)
        self.ui.tab1_spinbox_frame.setValue(0)
        self._disable_frame_updater = False

    def disable_frame_sliders(self):
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(False)
            slide.setVisible(False)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(False)
            spin.setVisible(False)
        for text in [self.ui.tab1_label_frame,
                     self.ui.tab1_label_last,
                     self.ui.tab1_label_first]:
            text.setVisible(False)

    def enable_cropping(self):
        im = self.dsa.get_current_raw_im(self.app.current_ind)
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def enable_baseline(self):
        w, h = self.dsa.get_current_raw_im(self.app.current_ind).shape
        pt1 = [1/10*w, 2/3*h]
        pt2 = [9/10*w, 2/3*h]
        self.ui.mplwidgetimport.update_baseline(pt1, pt2)

    def import_image(self, toggle=None, filepath=None):
        if filepath is None:
            # Select image to import
            filepath = select_file('Open image')[0]
        # Import image
        self.app.current_ind = 0
        success = self.dsa.import_image(filepath)
        if success:
            # Disable frame sliders
            self.disable_frame_sliders()
            # Update image display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # De-init next tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()

    def import_images(self, toggle=None, filepath=None):
        # Select images to import
        if filepath is None:
            filepath = select_files('Open images')[0]
        # Check
        if len(filepath) == 0:
            return None
        # Import images
        success = self.dsa.import_images(filepath)
        if success:
            # Enable frame sliders
            self.enable_frame_sliders()
            # Update images display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # De-init other tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()

    def import_video(self, toggle=None, filepath=None):
        # Select video to import
        if filepath is None:
            filepath = select_file('Open video')[0]
        # Import video
        success = self.dsa.import_video(filepath)
        if success:
            # Enable frame sliders
            self.enable_frame_sliders()
            # Update video display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # Set the time interval from the video
            dt = self.dsa.get_dt()
            self.ui.tab1_set_dt_text.setText(f"{dt:.6f}")
            # De-init other tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()

    def update_from_infofile(self):
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        infos = self.dsa.read_infofile()
        if infos is None:
            return None
        # sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        # dt
        dt = str(infos['dt'].asNumber())
        self.ui.tab1_set_dt_text.setText(dt)
        # dx
        dx = f"{infos['dl']}{infos['dx'].strUnit()[1:-1]}"
        self.ui.tab1_set_scaling_text.setText(dx)
        if len(infos['scaling_pts']) > 0:
            self.ui.mplwidgetimport.update_scaling_pts(infos['scaling_pts'])
        # cropx and xropy
        xlim, ylim = infos['lims']
        ylim = sizey - ylim[::-1]
        self.ui.mplwidgetimport.update_crop_area(*xlim, *ylim)
        # baseline
        bpt1, bpt2 = infos['baseline_pts']
        bpt1[1] = sizey - bpt1[1]
        bpt2[1] = sizey - bpt2[1]
        self.ui.mplwidgetimport.update_baseline(bpt1, bpt2)
        # cropt
        self.ui.tab1_spinbox_first.setValue(infos['cropt'][0])
        self.ui.tab1_spinbox_last.setValue(infos['cropt'][1])
        self.ui.tab1_spinbox_frame.setValue(infos['cropt'][0])

    def set_current_frame(self, frame_number):
        if self._disable_frame_updater:
            return None
        self.app.current_ind = frame_number - 1
        im = self.dsa.get_current_raw_im(
            self.app.current_ind,
            thread_hook=self.ui.mplwidgetimport.update_image)

    def set_first_frame(self, frame_number):
        self.ui.tab1_spinbox_frame.setValue(frame_number)

    def set_last_frame(self, frame_number):
        self.ui.tab1_spinbox_frame.setValue(frame_number)

    def reset_crop(self):
        im = self.dsa.get_current_raw_im(self.app.current_ind)
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def dt_from_video(self, b):
        dt = self.dsa.get_dt()
        self.ui.tab1_set_dt_text.setText(f"{dt:.6f}")

    def set_scaling(self):
        self.ui.mplwidgetimport.is_scaling = True

    def remove_scaling(self):
        self.ui.mplwidgetimport.is_scaling = False
        self.ui.mplwidgetimport.scaling_hand.reset()

    def get_params(self, arg=None):
        dic = {}
        # dt and dt
        if arg is None or arg == 'dt':
            dt = float(self.ui.tab1_set_dt_text.text())*make_unit('s')
            dic['dt'] = dt
        if arg is None or arg == 'dx':
            scaling_pts = self.ui.mplwidgetimport.scaling_hand.pts
            dl_real = self.ui.mplwidgetimport.get_scale()
            dl_txt = self.ui.tab1_set_scaling_text.text()
            match = re.match(r'\s*([0-9.]+)\s*(.*)\s*', dl_txt)
            dl_txt = float(match.groups()[0])
            dl_unit = match.groups()[1]
            if dl_real is not None:
                dx = dl_txt/dl_real*make_unit(dl_unit)
            else:
                dx = make_unit('')
            dic['dx'] = dx
            dic['dl'] = dl_txt
            dic['scaling_pts'] = scaling_pts
        # cropx and cropy
        if arg is None or arg == 'lims':
            xlims, ylims = self.ui.mplwidgetimport.rect_hand.lims
            sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
            ylims = np.sort(sizey - ylims)
            lims = np.array([xlims, ylims])
            dic['lims'] = lims
        # baseline pts
        if arg is None or arg == 'baseline_pts':
            pt1 = self.ui.mplwidgetimport.baseline_hand.pt1
            pt2 = self.ui.mplwidgetimport.baseline_hand.pt2
            deltay = abs(self.ui.mplwidgetimport.ax.viewLim.height)
            base_pt1 = [pt1[0], deltay - pt1[1]]
            base_pt2 = [pt2[0], deltay - pt2[1]]
            dic['baseline_pts'] = [base_pt1, base_pt2]
        # cropt
        if arg is None or arg == 'cropt':
            first_frame = self.ui.tab1_frameslider_first.value()
            last_frame = self.ui.tab1_frameslider_last.value()
            dic['cropt'] = [first_frame, last_frame]
        # return
        if arg is None:
            return dic
        else:
            return dic[arg]


class TabEdges(Tab):

    def initialize(self):
        # enable slider if necessary
        if self.dsa.nmb_frames > 1:
            self.enable_frame_sliders()
        else:
            self.disable_frame_sliders()
        self.initialized = True

    def enter_tab(self):
        if not self.initialized:
            self.initialize()
        # Replot
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetdetect.update_image(im.values)
        pt1, pt2 = self.dsa.get_baseline_display_points(self.app.current_ind)
        self.ui.mplwidgetdetect.update_baseline(pt1, pt2)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setValue(self.app.current_ind + 1)
        self._disable_frame_updater = False
        # Update the first and last frames
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab2_frameslider.setMinimum(cropt[0])
        self.ui.tab2_frameslider.setMaximum(cropt[1])
        self.ui.tab2_spinbox.setMinimum(cropt[0])
        self.ui.tab2_spinbox.setMaximum(cropt[1])
        # update the detected edge
        self.update_edge()
        #
        self.already_opened = True
        self.ui.mplwidgetdetect.tab_opened = True

    def leave_tab(self):
        # reset zoom
        self.ui.mplwidgetdetect.reset_zoom()
        #
        return True

    def enable_options(self):
        self.ui.tab2_canny_box.setEnabled(True)
        self.ui.tab2_contour_box.setEnabled(True)
        self.ui.tab2_options_box.setEnabled(True)

    def set_current_frame(self, frame_number):
        if self._disable_frame_updater:
            return None
        self.app.set_current_ind(frame_number - 1)
        # update image
        params_precomp = self.app.tab1.get_params()
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetdetect.update_image(im.values)
        # update edge
        # TODO: replotting the edge markers for each frame take time,
        #       It may be a better idea to use imshow to display edges
        self.update_edge()

    def enable_frame_sliders(self):
        self._disable_frame_updater = True
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab2_frameslider.setMinimum(cropt[0])
        self.ui.tab2_frameslider.setMaximum(cropt[1])
        self.ui.tab2_spinbox.setMinimum(cropt[0])
        self.ui.tab2_spinbox.setMaximum(cropt[1])
        self.ui.tab2_frameslider.setEnabled(True)
        self.ui.tab2_spinbox.setEnabled(True)
        self.ui.tab2_frameslider.setValue(self.app.current_ind)
        self.ui.tab2_spinbox.setValue(self.app.current_ind)
        for widg in [self.ui.tab2_label_frame,
                     self.ui.tab2_spinbox,
                     self.ui.tab2_frameslider]:
            widg.setVisible(True)
        self._disable_frame_updater = False

    def disable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setEnabled(False)
        self.ui.tab2_spinbox.setEnabled(False)
        for widg in [self.ui.tab2_label_frame,
                     self.ui.tab2_spinbox,
                     self.ui.tab2_frameslider]:
            widg.setVisible(False)
        self._disable_frame_updater = False

    def get_params(self):
        canny = {'threshold1': self.ui.tab2_canny_threshold1.value(),
                 'threshold2': self.ui.tab2_canny_threshold2.value(),
                 'dilatation_steps': self.ui.tab2_canny_dilatation_steps.value(),
                 'smooth_size': self.ui.tab2_canny_smooth_size.value()}
        contour = {'level': self.ui.tab2_contour_level.value()/255}
        edges = 1
        if self.ui.tab2_nmb_edges_2.isChecked():
            edges = 2
        options = {'nmb_edges': edges,
                   'ignored_pixels': self.ui.tab2_ign_pixels.value(),
                   'size_ratio': self.ui.tab2_size_ratio.value()/100}
        return canny, contour, options

    def update_edge(self, draw=True):
        params = self.get_params()
        try:
            edge = self.dsa.get_current_edge_pts(self.app.current_ind)
        except:
            self.log.log_unknown_exception()
            return None
        self.ui.mplwidgetdetect.update_edge(edge)

    def toggle_canny(self, toggle):
        if toggle:
            self.dsa.edge_detection_method = 'canny'
            self.ui.tab2_contour_box.setChecked(False)
        else:
            if not self.ui.tab2_contour_box.isChecked():
                self.dsa.edge_detection_method = None
        self.update_edge()

    def toggle_contour(self, toggle):
        if toggle:
            self.dsa.edge_detection_method = 'contour'
            self.ui.tab2_canny_box.setChecked(False)
        else:
            if not self.ui.tab2_canny_box.isChecked():
                self.dsa.edge_detection_method = None
        self.update_edge()


class TabFits(Tab):

    def initialize(self):
        # enable slider if necessary
        if self.dsa.nmb_frames > 1:
            self.enable_frame_sliders()
        else:
            self.disable_frame_sliders()
        self.initialized = True

    def enter_tab(self):
        if not self.initialized:
            self.initialize()
        # Update the plot only if necessary
        params_precomp = self.app.tab1.get_params()
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetfit.update_image(im.values)
        pt1, pt2 = self.dsa.get_baseline_display_points(self.app.current_ind)
        self.ui.mplwidgetfit.update_baseline(pt1, pt2)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setValue(self.app.current_ind + 1)
        self._disable_frame_updater = False
        # update the edge fit and baseline
        self.update_fit()
        # update the 'ignore lower part' slider upper bound
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        self.ui.tab3_circle_ymin.setMaximum(sizey)
        self.ui.tab3_ellipse_ymin.setMaximum(sizey)
        self.ui.tab3_ellipses_ymin.setMaximum(sizey)
        #
        self.already_opened = True
        self.ui.mplwidgetfit.tab_opened = True

    def leave_tab(self):
        # reset zoom
        self.ui.mplwidgetfit.reset_zoom()
        #
        return True

    def enable_options(self):
        self.ui.tab3_circle_box.setEnabled(True)
        self.ui.tab3_ellipse_box.setEnabled(True)
        self.ui.tab3_ellipses_box.setEnabled(True)
        self.ui.tab3_polyline_box.setEnabled(True)
        self.ui.tab3_spline_box.setEnabled(True)

    def set_current_frame(self, frame_number):
        if self._disable_frame_updater:
            return None
        self.app.current_ind = frame_number - 1
        # update image
        precomp_params = self.app.tab1.get_params()
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetfit.update_image(im.values)
        # update fit
        self.update_fit()

    def enable_frame_sliders(self):
        self._disable_frame_updater = True
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab3_frameslider.setMinimum(cropt[0])
        self.ui.tab3_frameslider.setMaximum(cropt[1])
        self.ui.tab3_spinbox.setMinimum(cropt[0])
        self.ui.tab3_spinbox.setMaximum(cropt[1])
        self.ui.tab3_frameslider.setEnabled(True)
        self.ui.tab3_spinbox.setEnabled(True)
        self.ui.tab3_frameslider.setValue(self.app.current_ind)
        self.ui.tab3_spinbox.setValue(self.app.current_ind)
        for widg in [self.ui.tab3_label_frame,
                     self.ui.tab3_spinbox,
                     self.ui.tab3_frameslider]:
            widg.setVisible(True)
        self._disable_frame_updater = False

    def disable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setEnabled(False)
        self.ui.tab3_spinbox.setEnabled(False)
        for widg in [self.ui.tab3_label_frame,
                     self.ui.tab3_spinbox,
                     self.ui.tab3_frameslider]:
            widg.setVisible(False)
        self._disable_frame_updater = False

    def get_params(self):
        circle = {'triple_pts': [[0, self.ui.tab3_circle_ymin.value()]]*2}
        ellipse = {'triple_pts': [[0, self.ui.tab3_ellipse_ymin.value()]]*2}
        ellipses = {'triple_pts': [[0, self.ui.tab3_ellipses_ymin.value()]]*2}
        polyline = {'deg': self.ui.tab3_polyline_deg.value()}
        spline = {'k': self.ui.tab3_spline_deg.value(),
                  's': self.ui.tab3_spline_smooth.value()/100}
        return circle, ellipse, ellipses, polyline, spline

    def update_fit(self):
        params = self.get_params()
        try:
            fit, fit_center = self.dsa.get_current_fit_pts(self.app.current_ind)
        except:
            self.log.log_unknown_exception()
            return None
        try:
            cas = self.dsa.get_current_ca(self.app.current_ind)
        except:
            self.log.log_unknown_exception()
            return None
        self.ui.mplwidgetfit.update_fit_and_cas(fit, fit_center, cas)

    def _uncheck_others(self, box):
        checks = [b.setChecked(False)
                  for b in [self.ui.tab3_circle_box,
                            self.ui.tab3_ellipse_box,
                            self.ui.tab3_ellipses_box,
                            self.ui.tab3_polyline_box,
                            self.ui.tab3_spline_box]
                  if b != box and b.isChecked()]
        return checks

    def _update_fit_method(self):
        checks = np.array([box.isChecked()
                           for box in [self.ui.tab3_circle_box,
                                       self.ui.tab3_ellipse_box,
                                       self.ui.tab3_ellipses_box,
                                       self.ui.tab3_polyline_box,
                                       self.ui.tab3_spline_box]])
        if not np.any(checks):
            self.dsa.fit_method = None

    def toggle_circle(self, toggle):
        # TODO: send the fit methd as argument like the other parameters
        # TODO: DO the same for edge
        # TODO: Globally, be sure that the backend is just accessed trhough
        #       function call
        if toggle:
            self.dsa.fit_method = 'circle'
            self._uncheck_others(self.ui.tab3_circle_box)
        else:
            self._update_fit_method()
        self.update_fit()

    def toggle_ellipse(self, toggle):
        if toggle:
            self.dsa.fit_method = 'ellipse'
            self._uncheck_others(self.ui.tab3_ellipse_box)
        else:
            self._update_fit_method()
        self.update_fit()

    def toggle_ellipses(self, toggle):
        if toggle:
            self.dsa.fit_method = 'ellipses'
            self._uncheck_others(self.ui.tab3_ellipses_box)
        else:
            self._update_fit_method()
        self.update_fit()

    def toggle_polyline(self, toggle):
        if toggle:
            self.dsa.fit_method = 'polyline'
            self._uncheck_others(self.ui.tab3_polyline_box)
        else:
            self._update_fit_method()
        self.update_fit()

    def toggle_spline(self, toggle):
        if toggle:
            self.dsa.fit_method = 'spline'
            self._uncheck_others(self.ui.tab3_spline_box)
        else:
            self._update_fit_method()
        self.update_fit()


class TabAnalyze(Tab):

    def __init__(self, ui, app, dsa, log):
        super().__init__(ui, app, dsa, log)
        self.use_yaxis2 = False

    def initialize(self):
        # Add option to combo boxes
        # TODO: Centralize the accessible things to make it more
        #       convenient to add some
        for opts in ['Frame number', 'Time']:
            self.ui.tab4_combo_xaxis.insertItem(100, opts)
        for opts in ['CA (mean)', 'CA (left)', 'CA (right)', 'Base radius',
                     'CL velocity (x, left)', 'CL velocity (x, right)',
                     'Position (x, center)', 'Position (x, right)',
                     'Position (x, left)']:
            self.ui.tab4_combo_xaxis.insertItem(100, opts)
            self.ui.tab4_combo_yaxis.insertItem(100, opts)
            self.ui.tab4_combo_yaxis2.insertItem(100, opts)
        # Set defauts
        self.ui.tab4_combo_xaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis2.setCurrentIndex(3)
        self.initialized = True

    def enter_tab(self):
        # initialize if needed
        if not self.initialized:
            self.initialize()
        self.dsa.compute_fits()
        self.update_plot()

    def get_params(self, arg=None):
        dic = {}
        # number of frames
        if arg is None or arg == 'N':
            N = int(self.ui.tab4_set_N.value())
            dic['N'] = N
        return dic

    def compute(self):
        # Clean
        if self.already_opened:
            self.clean_plot()
        # compute edges for every frames !
        try:
            self.dsa.compute_edges()
        except:
            self.log.log_unknown_exception()
            return None
        # compute fits for every frames !
        try:
            self.dsa.compute_fits()
        except:
            self.log.log_unknown_exception()
            return None
        # Clear quantity cache
        self.dsa.clear_plottable_quantity_cache()
        #
        self.update_plot(replot=True, draw=True)
        self.already_opened = True

    def enable_options(self):
        self.ui.tab4_xaxis_box.setEnabled(True)
        self.ui.tab4_yaxis_box.setEnabled(True)
        self.ui.tab4_yaxis2_box.setEnabled(True)
        self.ui.tab4_local_values_box.setEnabled(True)
        self.ui.tab4_export_box.setEnabled(True)
        self.ui.tab4_run_box.setEnabled(True)
        if self.dsa.nmb_frames > 1:
            self.ui.tab4_run_box.setEnabled(True)
            # self.ui.tab4_set_N.setEnabled(True)
            precomp_params = self.app.tab1.get_params()
            ff, lf = precomp_params['cropt']
            self.ui.tab4_set_N.setValue(int((lf-ff)/50))
            self.ui.tab4_set_N.setMinimum(1)
            self.ui.tab4_set_N.setMaximum(self.dsa.nmb_frames)
        else:
            self.ui.tab4_run_box.setEnabled(False)
            # self.ui.tab4_set_N.setEnabled(False)

    def clean_plot(self):
        self.ui.mplwidgetanalyze.update_plots(
            [], [], [], [], [], xname="", yname="", y2name="",
            replot=False, draw=True)

    def update_plot(self, index=0, replot=False, draw=True):
        if not self.initialized:
            return None
        # get things to plot
        xaxis = self.ui.tab4_combo_xaxis.currentText()
        xsmooth = self.ui.tab4_smoothx.value()
        yaxis = self.ui.tab4_combo_yaxis.currentText()
        ysmooth = self.ui.tab4_smoothy.value()
        try:
            x, x_orig, unit_x = self.dsa.get_plotable_quantity(xaxis,
                                                               smooth=xsmooth)
        except:
            self.log.log_unknown_exception()
            x = []
            x_orig = []
            unit_x = ""
        try:
            y, y_orig, unit_y = self.dsa.get_plotable_quantity(yaxis,
                                                               smooth=ysmooth)
        except:
            self.log.log_unknown_exception()
            y = [np.nan]*len(x)
            y_orig = [np.nan]*len(x)
            unit_y = ""
        if self.use_yaxis2:
            yaxis2 = self.ui.tab4_combo_yaxis2.currentText()
            ysmooth2 = self.ui.tab4_smoothy2.value()
            try:
                y2, y2_orig, unit_y2 = self.dsa.get_plotable_quantity(
                    yaxis2,
                    smooth=ysmooth2)
            except:
                self.log.log_unknown_exception()
                y2 = [np.nan]*len(x)
                y2_orig = [np.nan]*len(x)
                unit_y2 = ""
        else:
            yaxis2 = ""
            y2 = [np.nan]*len(x)
            y2_orig = [np.nan]*len(x)
            unit_y2 = ""
        # Update local values labels
        self.ui.tab4_local_x_label.setText(f"{xaxis} [{unit_x}]")
        self.ui.tab4_local_y_label.setText(f"{yaxis} [{unit_y}]")
        if self.use_yaxis2:
            self.ui.tab4_local_y2_label.setEnabled(True)
            self.ui.tab4_local_y2_value.setEnabled(True)
            self.ui.tab4_local_y2_label.setText(f"{yaxis2} [{unit_y2}]")
        else:
            self.ui.tab4_local_y2_label.setEnabled(False)
            self.ui.tab4_local_y2_value.setEnabled(False)
            self.ui.tab4_local_y2_label.setText("None")
            self.ui.tab4_local_y2_value.setText("")
        # if no x
        if len(x) == 0:
            y = []
            y_orig = []
            y2 = []
            y2_orig = []
        # check length, just in case
        if len(x) != len(y):
            self.log.log('Incoherence in plottable quantities length:'
                         f'\n{xaxis} is {len(x)} and {yaxis} is {len(y)}',
                         level=3)
            if len(x) < len(y):
                x = [np.nan]*len(x)
                y = [np.nan]*len(x)
                y2 = [np.nan]*len(x)
            else:
                x = [np.nan]*len(y)
                y = [np.nan]*len(y)
                y2 = [np.nan]*len(y)
        # Names
        xname = f'{xaxis} [{unit_x}]'
        yname = f'{yaxis} [{unit_y}]'
        yname2 = f'{yaxis2} [{unit_y2}]'
        # Should the plots share the same ylims
        shared_names = ['Position', 'CL velocity', 'CA']
        sameylims = False
        for sname in shared_names:
            if yaxis.startswith(sname) and yaxis2.startswith(sname):
                sameylims = True
                break
        #
        self.ui.mplwidgetanalyze.update_plots(x, y, y2,
                                              y_orig, y2_orig,
                                              xname=xname,
                                              yname=yname,
                                              y2name=yname2,
                                              same_y_lims=sameylims,
                                              replot=replot,
                                              draw=draw)

    def toggle_axis2(self, toggle):
        self.use_yaxis2 = toggle
        self.update_plot()

    def export_as_csv(self, toggle):
        try:
            # get fiel to save to
            filepath = select_new_file("Save as")
            if len(filepath) == 0:
                return None
            filepath = filepath[0]
            if filepath[0] == "":
                return None
            # get data
            data = []
            headers = []
            for quant in self.app.plottable_quant:
                val, _, unit = self.dsa.get_plotable_quantity(quant, smooth=0)
                # check that length matches
                if len(data) > 0:
                    if len(data[0]) != len(val):
                        self.log.log(f"Quantity {quant} does not have the right"
                                     f" length ({len(val)} instead of"
                                     f" {len(data[0])})", level=3)
                        continue
                data.append(list(val))
                headers.append(f'{quant.replace(",", "")}'
                               f' [{unit.replace(",", "")}]')
            data = np.array(data, dtype=float).transpose()
            np.savetxt(filepath, data, delimiter=', ',
                       header=f"File: {self.dsa.filepath}\n"
                       f"Analysis date: {datetime.utcnow()}\n"
                       + ", ".join(headers))
            self.log.log(f"Save data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()


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
        # Variables
        self.current_ind = 0
        self.statusbar_delay = 2000
        self._disable_frame_updater = False
        self.plottable_quant = [
            'Frame number', 'Time', 'Position (x, right)',
            'CL velocity (x, left)', 'CL velocity (x, right)',
            'Position (x, left)', 'Position (x, center)',
            'CA (right)', 'CA (left)', 'CA (mean)', 'Base radius',
            'Height', 'Area', 'Volume']
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
        self.tab5 = Tab(self.ui, self, self.dsa, self.log)
        self.tabs = [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5]
        self.last_tab = 0
        # Including design.ui
        self.ui.setupUi(self)
        # Add missing links
        self.ui.mplwidgetanalyze.ui = self.ui
        # Initialize progressbar
        self.init_progressbar()
        # Always start from the first tab
        self.ui.tabWidget.setCurrentIndex(0)
        # Show it !
        self.show()

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
