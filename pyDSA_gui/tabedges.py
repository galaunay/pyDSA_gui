# -*- coding: utf-8 -*-
#!/usr/env python3

# Copyright (C) 2017 Gaby Launay

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

from .tab import Tab


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
        self.update_edge(blit=False)
        # Update the baseline
        pt1, pt2 = self.dsa.get_baseline_display_points(self.app.current_ind)
        self.ui.mplwidgetdetect.update_baseline(pt1, pt2, blit=False)
        # Replot Image
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetdetect.update_image(im.values, blit=True)
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
        self.app.set_current_ind(frame_number - 1)
        if self._disable_frame_updater:
            return None
        # update image
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetdetect.update_image(im.values, blit=False)
        # update edge
        self.update_edge(blit=True)

    def enable_frame_sliders(self):
        # Preserve current ind
        current_ind = self.app.current_ind
        self._disable_frame_updater = True
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab2_frameslider.setMinimum(cropt[0])
        self.ui.tab2_frameslider.setMaximum(cropt[1])
        self.ui.tab2_spinbox.setMinimum(cropt[0])
        self.ui.tab2_spinbox.setMaximum(cropt[1])
        self.ui.tab2_frameslider.setEnabled(True)
        self.ui.tab2_spinbox.setEnabled(True)
        self.ui.tab2_frameslider.setValue(current_ind)
        self.ui.tab2_spinbox.setValue(current_ind)
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

    def update_edge(self, blit=True):
        try:
            edge = self.dsa.get_current_edge_pts(self.app.current_ind)
        except:
            self.log.log_unknown_exception()
            return None
        self.ui.mplwidgetdetect.update_edge(edge, blit=blit)

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
