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


class TabAnalyze(Tab):

    def __init__(self, ui, app, dsa, log):
        super().__init__(ui, app, dsa, log)
        self.use_yaxis2 = False
        self._disable_plot_updater = False

    def initialize(self):
        # Set defauts for combo boxes
        self.ui.tab4_combo_xaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis.setCurrentIndex(0)
        self.ui.tab4_combo_yaxis2.setCurrentIndex(3)
        #
        self.initialized = True

    def update_combo_boxes(self):
        self._disable_plot_updater = True
        ind = self.ui.tab4_combo_xaxis.findText('Frame number')
        if ind == -1:
            for opts in ['Frame number', 'Time']:
                self.ui.tab4_combo_xaxis.insertItem(100, opts)
            for opts in ['CA (mean)', 'CA (left)', 'CA (right)', 'Base radius',
                         'CL velocity (x, left)', 'CL velocity (x, right)',
                         'Position (x, center)', 'Position (x, right)',
                         'Position (x, left)']:
                self.ui.tab4_combo_xaxis.insertItem(100, opts)
                self.ui.tab4_combo_yaxis.insertItem(100, opts)
                self.ui.tab4_combo_yaxis2.insertItem(100, opts)
        # Additional stuff for wetting ridge
        for opts in ['Ridge height (left)', 'Ridge height (right)',
                     'CA (TP, left)', 'CA (TP, right)',
                     'CA (TP, mean)']:
            if self.dsa.fit_method == "wetting ridge":
                if self.ui.tab4_combo_xaxis.findText(opts) == -1:
                    self.ui.tab4_combo_xaxis.insertItem(100, opts)
                    self.ui.tab4_combo_yaxis.insertItem(100, opts)
                    self.ui.tab4_combo_yaxis2.insertItem(100, opts)
            else:
                ind = self.ui.tab4_combo_xaxis.findText(opts)
                if ind != -1:
                    self.ui.tab4_combo_xaxis.removeItem(ind)
                    ind = self.ui.tab4_combo_yaxis.findText(opts)
                    self.ui.tab4_combo_yaxis.removeItem(ind)
                    self.ui.tab4_combo_yaxis2.removeItem(ind)
        # Maybe reinit the combo box positions
        for cb in [self.ui.tab4_combo_xaxis, self.ui.tab4_combo_yaxis,
                   self.ui.tab4_combo_yaxis2]:
            if cb.currentIndex() > cb.count():
                cb.setCurrentIndex(0)
        self._disable_plot_updater = False

    def enter_tab(self):
        # Update combo boxes
        self.update_combo_boxes()
        # initialize if needed
        if not self.initialized:
            self.initialize()
        # Compute fits
        self.dsa.compute_fits()
        # Enable data table
        self.ui.tabdata.setEnabled(True)
        # plot
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
            [], [], [], [], [], current_x=None,
            xname="", yname="", y2name="",
            replot=False, draw=True)

    def update_plot(self, index=0, replot=False, draw=True):
        if not self.initialized or self._disable_plot_updater:
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
        shared_names = ['Position', 'CL velocity', 'CA', 'Ridge height']
        sameylims = False
        for sname in shared_names:
            if yaxis.startswith(sname) and yaxis2.startswith(sname):
                sameylims = True
                break
        # Get current frame number
        fn, _, _ = self.dsa.get_plotable_quantity("Frame number")
        if len(fn) > 1:
            current_x = fn[np.argmin(abs(fn - (self.app.current_ind + 1)))]
        else:
            current_x = None
        # Update
        self.ui.mplwidgetanalyze.update_plots(x, y, y2,
                                              y_orig, y2_orig,
                                              current_x=current_x,
                                              xname=xname,
                                              yname=yname,
                                              y2name=yname2,
                                              same_y_lims=sameylims,
                                              replot=replot,
                                              draw=draw)

    def toggle_axis2(self, toggle):
        self.use_yaxis2 = toggle
        self.update_plot()
