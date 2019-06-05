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
import numpy as np


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
        # Update the curent frame
        self._disable_frame_updater = True
        self.ui.tab3_frameslider.setValue(self.app.current_ind + 1)
        self._disable_frame_updater = False
        # Update the first and last frames
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab3_frameslider.setMinimum(cropt[0])
        self.ui.tab3_frameslider.setMaximum(cropt[1])
        self.ui.tab3_spinbox.setMinimum(cropt[0])
        self.ui.tab3_spinbox.setMaximum(cropt[1])
        # update the 'ignore lower part' slider upper bound
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        self.ui.tab3_circle_ymin.setMaximum(sizey)
        self.ui.tab3_ellipse_ymin.setMaximum(sizey)
        self.ui.tab3_ellipses_ymin.setMaximum(sizey)
        # update the edge fit
        self.update_fit(blit=False)
        # Update the baseline
        pt1, pt2 = self.dsa.get_baseline_display_points(self.app.current_ind)
        self.ui.mplwidgetfit.update_baseline(pt1, pt2, blit=False)
        # Update the plot only if necessary
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetfit.update_image(im.values, blit=True)
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
        self.ui.tab3_wetting_ridge_box.setEnabled(True)

    def set_current_frame(self, frame_number):
        self.app.current_ind = frame_number - 1
        if self._disable_frame_updater:
            return None
        # update image
        im = self.dsa.get_current_precomp_im(self.app.current_ind)
        self.ui.mplwidgetfit.update_image(im.values, blit=False)
        # update fit
        self.update_fit(blit=True)

    def enable_frame_sliders(self):
        # Preserve current ind
        current_ind = self.app.current_ind
        self._disable_frame_updater = True
        cropt = self.app.tab1.get_params('cropt')
        self.ui.tab3_frameslider.setMinimum(cropt[0])
        self.ui.tab3_frameslider.setMaximum(cropt[1])
        self.ui.tab3_spinbox.setMinimum(cropt[0])
        self.ui.tab3_spinbox.setMaximum(cropt[1])
        self.ui.tab3_frameslider.setEnabled(True)
        self.ui.tab3_spinbox.setEnabled(True)
        self.ui.tab3_frameslider.setValue(current_ind)
        self.ui.tab3_spinbox.setValue(current_ind)
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
        wr = {'pos_estimate': self.ui.tab3_wetting_ridge_pos_estimate.value()/100,
              'sigma': self.ui.tab3_wetting_ridge_sigma.value()/100}
        return circle, ellipse, ellipses, polyline, spline, wr

    def update_fit(self, blit=True):
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
        self.ui.mplwidgetfit.update_fit_and_cas(fit, fit_center, cas, blit=blit)

    def _uncheck_others(self, box):
        checks = [b.setChecked(False)
                  for b in [self.ui.tab3_circle_box,
                            self.ui.tab3_ellipse_box,
                            self.ui.tab3_ellipses_box,
                            self.ui.tab3_polyline_box,
                            self.ui.tab3_spline_box,
                            self.ui.tab3_wetting_ridge_box]
                  if b != box and b.isChecked()]
        return checks

    def _update_fit_method(self):
        checks = np.array([box.isChecked()
                           for box in [self.ui.tab3_circle_box,
                                       self.ui.tab3_ellipse_box,
                                       self.ui.tab3_ellipses_box,
                                       self.ui.tab3_polyline_box,
                                       self.ui.tab3_spline_box,
                                       self.ui.tab3_wetting_ridge_box]])
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

    def toggle_wetting_ridge(self, toggle):
        if toggle:
            self.dsa.fit_method = 'wetting ridge'
            self._uncheck_others(self.ui.tab3_wetting_ridge_box)
        else:
            self._update_fit_method()
        self.update_fit()
