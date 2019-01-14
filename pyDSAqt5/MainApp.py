import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,\
    QDialog
from PyQt5 import QtWidgets, QtCore
from .design import Ui_MainWindow
import numpy as np

from IMTreatment.utils import make_unit
import re
from .dsa_backend import DSA
from .log import Log


def select_file(message="Open file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileName(dialog, message,
                                           filter=filetypes)
    return filepath


def select_files(message="Open files", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileNames(dialog, message,
                                            filter=filetypes)
    return filepath


# TODO: Add slider for thresholds
# TODO: Add export data to csv
# TODO: Add export_as_script
# TODO: Add tests (QT5 tests ?)
#       - http://johnnado.com/pyqt-qtest-example/
#       - https://pypi.org/project/pytest-qt/
# TODO: Add circles fitting for ridge detection
# TODO: Add keybindings
# TODO: Add interactive vertical selector to analyze tab
# TODO: Make everything asynchroneous
# TODO: Make it executable
# TODO: Put it on pypi
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Variables
        self.statusbar_delay = 2000
        self._disable_frame_updater = False
        self.dsa = None
        # Add Progress bar to status bar
        self.ui.progressbar = QtWidgets.QProgressBar()
        self.ui.progressbar.setMaximumSize(QtCore.QSize(250, 16777215))
        self.ui.progressbar.setTextVisible(True)
        self.ui.progressbar.setFormat("%p%")
        self.ui.progressbar.setValue(0)
        self.ui.progressbar.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.ui.progressbar)
        # Initialize log
        self.log = Log(self.ui.logarea, self.ui.statusbar,
                       self.statusbar_delay)
        # Always start from the first tab
        self.ui.tabWidget.setCurrentIndex(0)
        # Tab-related variables
        self.tab1_filepath = ""
        self.tab2_initialized = False
        self.tab2_already_opened = False
        self.tab3_initialized = False
        self.tab3_already_opened = False
        self.tab4_initialized = False
        self.tab4_use_yaxis2 = False
        self.tab4_already_opened = False
        self.last_tab = 0
        # Show it !
        self.show()

    def enable_options(self):
        """ To run after importing at least an image"""
        # tab1
        self.ui.tab1_crop_box.setEnabled(True)
        self.ui.tab1_scaling_box.setEnabled(True)
        if self.dsa.nmb_frames > 1:
            self.ui.tab1_time_box.setEnabled(True)
        else:
            self.ui.tab1_time_box.setEnabled(False)
        # tab2
        self.ui.tab2_canny_box.setEnabled(True)
        self.ui.tab2_contour_box.setEnabled(True)
        self.ui.tab2_options_box.setEnabled(True)
        # tab3
        self.ui.tab3_circle_box.setEnabled(True)
        self.ui.tab3_ellipse_box.setEnabled(True)
        self.ui.tab3_polyline_box.setEnabled(True)
        self.ui.tab3_spline_box.setEnabled(True)
        # tab4
        if self.dsa.nmb_frames > 1:
            self.ui.tab4_xaxis_box.setEnabled(True)
            self.ui.tab4_yaxis_box.setEnabled(True)
            self.ui.tab4_yaxis2_box.setEnabled(True)
        else:
            self.ui.tab4_xaxis_box.setEnabled(False)
            self.ui.tab4_yaxis_box.setEnabled(False)
            self.ui.tab4_yaxis2_box.setEnabled(False)

    def tab_changed(self, tab_nmb):
        # Do nothing if no imported image yet
        if self.dsa is None:
            return None
        # Update precomputed images if the last tab is the import tab
        if self.last_tab == 0:
            if not self.tab1_check_inputs():
                self.ui.tabWidget.setCurrentIndex(0)
                return None
            self.tab1_leave_tab()
        # Do switch to tab
        if tab_nmb == 0:
            self.tab1_switch_to_tab()
        elif tab_nmb == 1:
            self.tab2_switch_to_tab()
        elif tab_nmb == 2:
            self.tab3_switch_to_tab()
        elif tab_nmb == 3:
            self.tab4_switch_to_tab()
        # Update the last tab
        self.last_tab = tab_nmb

    # TAB 1
    def tab1_switch_to_tab(self):
        # Update the frame number
        self.ui.tab1_frameslider.setValue(self.dsa.current_ind + 1)
        self.ui.tab1_spinbox_frame.setValue(self.dsa.current_ind + 1)

    def tab1_leave_tab(self):
        # Precompute images
        self.dsa.precompute_images(self.tab1_get_params())
        # Ensure current image is in the selected range
        cropt = self.dsa.precomp_old_params['cropt']
        if self.dsa.current_ind > cropt[1] - 1:
            self.dsa.set_current(cropt[1] - 1)
        elif self.dsa.current_ind < cropt[0] - 1:
            self.dsa.set_current(cropt[0] - 1)

    def tab1_check_inputs(self):
        try:
            dt = self.tab1_get_params('dt')
        except:
            self.log.log("Bad format for 'dt'",
                         level=2)
            return False
        try:
            dx = self.tab1_get_params('dx')
        except:
            self.log.log("Bad format for 'dx'",
                         level=2)
            return False
        return True

    def tab1_enable_frame_sliders(self):
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(True)
            slide.setMinimum(1)
            slide.setMaximum(self.dsa.nmb_frames)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(True)
            spin.setMinimum(1)
            spin.setMaximum(self.dsa.nmb_frames)
        self.ui.tab1_frameslider_last.setValue(self.dsa.nmb_frames)
        self.ui.tab1_spinbox_frame.setValue(0)

    def tab1_disable_frame_sliders(self):
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(False)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(False)

    def tab1_enable_cropping(self):
        im = self.dsa.get_current_raw_im()
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def tab1_enable_baseline(self):
        w, h = self.dsa.get_current_raw_im().shape
        pt1 = [1/10*w, 2/3*h]
        pt2 = [9/10*w, 2/3*h]
        self.ui.mplwidgetimport.update_baseline(pt1, pt2)

    def tab1_import_image(self):
        # Select image to import
        self.filepath_type = 'image'
        self.filepath = select_file('Open image')[0]
        # Import image
        self.dsa = DSA(self)
        try:
            self.dsa.import_image(self.filepath)
        except IOError:
            self.log.log(f"Cannot import '{self.filepath}': not a valid image",
                         level=3)
            return None
        # Update image display
        im = self.dsa.get_current_raw_im()
        self.ui.mplwidgetimport.update_image(im.values, replot=True)
        # Disable frame sliders
        self.tab1_disable_frame_sliders()
        # Enable cropping sliders
        self.tab1_enable_cropping()
        # Enable baseline
        self.tab1_enable_baseline()
        # Enable options
        self.enable_options()
        # De-init next tabs
        self.tab2_initialized = False
        self.tab3_initialized = False

    def tab1_import_images(self):
        # Select images to import
        self.filepath_type = 'images'
        self.filepath = select_files('Open images')[0]
        # Check
        if len(self.filepath) == 0:
            return None
        # Import images
        self.dsa = DSA(self)
        try:
            self.dsa.import_images(self.filepath)
        except IOError:
            self.log.log(f"Couldn't import selected files: {self.filepath}",
                         level=3)
            return None
        # Update images display
        im = self.dsa.get_current_raw_im()
        self.ui.mplwidgetimport.update_image(im.values, replot=True)
        # Enable frame sliders
        self.tab1_enable_frame_sliders()
        # Enable cropping sliders
        self.tab1_enable_cropping()
        # Enable baseline
        self.tab1_enable_baseline()
        # Enable options
        self.enable_options()
        # De-init other tabs
        self.tab2_initialized = False
        self.tab3_initialized = False

    def tab1_import_video(self):
        # Select video to import
        self.filepath_type = 'video'
        self.filepath = select_file('Open video')[0]
        # Import video
        self.dsa = DSA(self)
        try:
            self.dsa.import_video(self.filepath)
        except IOError:
            self.log.log(f"Couldn't import '{self.filepath}':"
                         " not a valid video", level=3)
            return None
        except ImportError:
            self.log.log(f"Couldn't import '{self.filepath}':", level=3)
            return None
        # Update video display
        im = self.dsa.get_current_raw_im()
        self.ui.mplwidgetimport.update_image(im.values, replot=True)
        # Enable frame sliders
        self.tab1_enable_frame_sliders()
        # Enable cropping sliders
        self.tab1_enable_cropping()
        # Enable baseline
        self.tab1_enable_baseline()
        # Enable options
        self.enable_options()
        # De-init other tabs
        self.tab2_initialized = False
        self.tab3_initialized = False

    def tab1_set_current_frame(self, ind):
        self.dsa.set_current(ind - 1)
        im = self.dsa.get_current_raw_im()
        self.ui.mplwidgetimport.update_image(im.values)

    def tab1_set_first_frame(self, ind):
        self.ui.tab1_spinbox_frame.setValue(ind)

    def tab1_set_last_frame(self, ind):
        self.ui.tab1_spinbox_frame.setValue(ind)

    def tab1_reset_crop(self):
        im = self.dsa.get_current_raw_im()
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def tab1_set_scaling(self):
        self.ui.mplwidgetimport.is_scaling = True

    def tab1_remove_scaling(self):
        self.ui.mplwidgetimport.is_scaling = False
        self.ui.mplwidgetimport.scaling_hand.reset()

    def tab1_get_params(self, arg=None):
        dic = {}
        # dt and dt
        if arg is None or arg == 'dt':
            dt = float(self.ui.tab1_set_dt_text.text())*make_unit('s')
            dic['dt'] = dt
        if arg is None or arg == 'dx':
            dx_real = self.ui.mplwidgetimport.get_scale()
            if dx_real is not None:
                dx_txt = self.ui.tab1_set_scaling_text.text()
                match = re.match(r'\s*([0-9.]+)\s*(.*)\s*', dx_txt)
                dx_txt = float(match.groups()[0])
                dx_unit = match.groups()[1]
                dx = dx_txt/dx_real*make_unit(dx_unit)
            else:
                dx = make_unit('')
            dic['dx'] = dx
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

    # TAB 2
    def tab2_initialize(self):
        # enable slider if necessary
        if self.dsa.nmb_frames > 1:
            self.tab2_enable_frame_sliders()
        else:
            self.tab2_disable_frame_sliders()

    def tab2_switch_to_tab(self):
        if not self.tab2_initialized:
            self.tab2_initialize()
        draw = True
        if not self.tab2_already_opened:
            draw = False
        # Replot
        im = self.dsa.get_current_precomp_im()
        self.ui.mplwidgetdetect.update_image(im.values, replot=True, draw=draw)
        pt1, pt2 = self.dsa.get_baseline_display_points()
        self.ui.mplwidgetdetect.update_baseline(pt1, pt2, draw=draw)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setValue(self.dsa.current_ind + 1)
        self._disable_frame_updater = False
        # Update the first and last frames
        cropt = self.dsa.precomp_old_params['cropt']
        self.ui.tab2_frameslider.setMinimum(cropt[0])
        self.ui.tab2_frameslider.setMaximum(cropt[1])
        self.ui.tab2_spinbox.setMinimum(cropt[0])
        self.ui.tab2_spinbox.setMaximum(cropt[1])
        # update the detected edge
        self.tab2_update_edge(draw=draw)
        #
        self.tab2_initialized = True
        self.tab2_already_opened = True

    def tab2_set_current_frame(self, ind):
        if self._disable_frame_updater:
            return None
        self.dsa.set_current(ind - 1)
        # update image
        im = self.dsa.get_current_precomp_im()
        self.ui.mplwidgetdetect.update_image(im.values, replot=False)
        # update edge
        # TODO: replotting the edge markers for each frame take time,
        #       It may be a better idea to use imshow to display edges
        self.tab2_update_edge()

    def tab2_enable_frame_sliders(self):
        self._disable_frame_updater = True
        cropt = self.dsa.precomp_old_params['cropt']
        self.ui.tab2_frameslider.setMinimum(cropt[0])
        self.ui.tab2_frameslider.setMaximum(cropt[1])
        self.ui.tab2_spinbox.setMinimum(cropt[0])
        self.ui.tab2_spinbox.setMaximum(cropt[1])
        self.ui.tab2_frameslider.setEnabled(True)
        self.ui.tab2_spinbox.setEnabled(True)
        self._disable_frame_updater = False

    def tab2_disable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab2_frameslider.setEnabled(False)
        self.ui.tab2_spinbox.setEnabled(False)
        self._disable_frame_updater = False

    def tab2_get_params(self):
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
        except:
            self.log.log('Unknown error during edge detection', level=3)
            return None
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
        else:
            self.tab3_disable_frame_sliders()

    def tab3_switch_to_tab(self):
        if not self.tab3_initialized:
            self.tab3_initialize()
        draw = True
        if not self.tab3_already_opened:
            draw = False
        # Update the plot only if necessary
        im = self.dsa.get_current_precomp_im()
        self.ui.mplwidgetfit.update_image(im.values, replot=True, draw=draw)
        pt1, pt2 = self.dsa.get_baseline_display_points()
        self.ui.mplwidgetfit.update_baseline(pt1, pt2, draw=draw)
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setValue(self.dsa.current_ind + 1)
        self._disable_frame_updater = False
        # update the edge fit and baseline
        self.tab3_update_fit(draw=draw)
        # update the 'ignore lower part' slider upper bound
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        self.ui.tab3_circle_ymin.setMaximum(sizey)
        self.ui.tab3_ellipse_ymin.setMaximum(sizey)
        #
        self.tab3_initialized = True
        self.tab3_already_opened = True

    def tab3_set_current_frame(self, ind):
        if self._disable_frame_updater:
            return None
        self.dsa.set_current(ind - 1)
        # update image
        im = self.dsa.get_current_precomp_im()
        self.ui.mplwidgetfit.update_image(im.values, replot=False)
        # update fit
        self.tab3_update_fit()

    def tab3_enable_frame_sliders(self):
        self._disable_frame_updater = True
        cropt = self.dsa.precomp_old_params['cropt']
        self.ui.tab3_frameslider.setMinimum(cropt[0])
        self.ui.tab3_frameslider.setMaximum(cropt[1])
        self.ui.tab3_spinbox.setMinimum(cropt[0])
        self.ui.tab3_spinbox.setMaximum(cropt[1])
        self.ui.tab3_frameslider.setEnabled(True)
        self.ui.tab3_spinbox.setEnabled(True)
        self._disable_frame_updater = False

    def tab3_disable_frame_sliders(self):
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setEnabled(False)
        self.ui.tab3_spinbox.setEnabled(False)
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
        except:
            self.log.log('Unknown error during edge fitting', level=3)
            return None
        self.ui.mplwidgetfit.update_fit(fit, fit_center, draw=draw)
        try:
            cas = self.dsa.get_current_ca()
        except:
            self.log.log('Unknown error during contact angle computation',
                         level=3)
            return None
        self.ui.mplwidgetfit.update_ca(cas, draw=draw)

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
        if not np.any(checks):
            self.dsa.fit_method = None

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

    # TAB4
    def tab4_initialize(self):
        if self.dsa.nmb_frames == 1:
            return None
        # Add option to combo boxes
        for opts in ['Frame number', 'Time']:
            self.ui.tab4_combo_xaxis.insertItem(100, opts)
        for opts in ['CA (mean)', 'CA (left)', 'CA (right)', 'Base radius',
                     'Position (x, center)', 'Position (x, right)',
                     'Position (x, left)']:
            self.ui.tab4_combo_xaxis.insertItem(100, opts)
            self.ui.tab4_combo_yaxis.insertItem(100, opts)
            self.ui.tab4_combo_yaxis2.insertItem(100, opts)
        # Set defauts
        self.ui.tab4_combo_xaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis2.setCurrentIndex(3)
        self.tab4_initialized = True

    def tab4_switch_to_tab(self):
        # initialize if needed
        if not self.tab4_initialized:
            self.tab4_initialize()
        # Do nothing if there is only one point...
        if self.dsa.nmb_frames <= 1:
            return None
        # Clean
        if self.tab4_already_opened:
            self.tab4_clean_plot()
        # compute edges for every frames !
        params = self.tab2_get_params()
        try:
            self.dsa.compute_edges(params)
        except:
            self.log.log('Unknown error during edges detection', level=3)
            return None
        # compute fits for every frames !
        params = self.tab3_get_params()
        try:
            self.dsa.compute_fits(params)
        except:
            self.log.log('Unknown error during edges fitting', level=3)
            return None
        # compute contact angles for every frames !
        try:
            self.dsa.compute_cas()
        except:
            self.log.log('Unknown error during contact angle computation',
                         level=3)
            return None
        #
        self.tab4_update_plot(0, replot=True)
        self.tab4_already_opened = True

    def tab4_clean_plot(self):
        self.ui.mplwidgetanalyze.update_plots([], [], [],
                                              xname="",
                                              yname="",
                                              y2name="",
                                              replot=False,
                                              draw=True)

    def tab4_update_plot(self, index, replot=False, draw=True):
        if not self.tab4_initialized:
            return None
        # get things to plot
        xaxis = self.ui.tab4_combo_xaxis.currentText()
        yaxis = self.ui.tab4_combo_yaxis.currentText()
        try:
            x, unit_x = self.dsa.get_plotable_quantity(xaxis)
        except:
            self.log.log(f"Unknown error while gathering '{xaxis}'",
                         level=3)
            x = []
            unit_x = ""
        try:
            y, unit_y = self.dsa.get_plotable_quantity(yaxis)
        except:
            self.log.log(f"Unknown error while gathering '{yaxis}'",
                         level=3)
            y = [np.nan]*len(x)
            unit_y = ""
        if self.tab4_use_yaxis2:
            yaxis2 = self.ui.tab4_combo_yaxis2.currentText()
            try:
                y2, unit_y2 = self.dsa.get_plotable_quantity(yaxis2)
            except:
                self.log.log(f"Unknown error while gathering '{yaxis2}'",
                             level=3)
                y2 = [np.nan]*len(x)
                unit_y2 = ""
        else:
            yaxis2 = ""
            y2 = [np.nan]*len(x)
            unit_y2 = ""
        # if no x
        if len(x) == 0:
            y = []
            y2 = []
        #
        # check length
        if len(x) != len(y):
            self.log.log('Incoherence in plottable quantities length:'
                         f'\n{xaxis} is {len(x)} and {yaxis} is {len(y)}',
                         level=3)
            if len(x) < len(y):
                y[0:len(x)]
            else:
                x[0:len(y)]
        # Names
        xname = f'{xaxis} [{unit_x}]'
        yname = f'{yaxis} [{unit_y}]'
        yname2 = f'{yaxis2} [{unit_y2}]'
        #
        self.ui.mplwidgetanalyze.update_plots(x, y, y2,
                                              xname=xname,
                                              yname=yname,
                                              y2name=yname2,
                                              replot=replot,
                                              draw=draw)

    def tab4_toggle_axis2(self, toggle):
        self.tab4_use_yaxis2 = toggle
        self.tab4_update_plot(index=0)

    # Menu
    def export_as_script(self):
        filepath = self.filepath
        params_im = self.tab1_get_params()
        params_edges = self.tab2_get_params()
        params_fit = self.tab3_get_params()
        raise Exception('Not implemented yet')


def run():
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
