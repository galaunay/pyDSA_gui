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

__author__ = "Gaby Launay"
__copyright__ = "Gaby Launay 2018-2019"
__credits__ = ""
__license__ = "GPL3"
__version__ = ""
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pyDSA.baseline import Baseline

from .mpl_handlers import BaselineHandler, RectangleHandler, ScalingHandler, \
    VerticalLineHandler

colors = {'baseline': 'tab:blue',
          'crop_area': 'tab:red',
          'scaling': 'tab:green',
          'edge': 'tab:green',
          'fit': 'tab:orange',
          'ca': 'tab:blue',
          'plot1': 'tab:blue',
          'plot2': 'tab:orange',
          'vertical line': 'tab:green'}



# class MplPlotWidget(Canvas):
#     def __init__(self, parent=None):
#         super(MplPlotWidget, self).__init__(Figure())

#         self.setParent(parent)
#         self.figure = Figure(dpi=100)
#         self.canvas = Canvas(self.figure)
#         self.ax = self.figure.add_subplot(111)
#         self.plot = self.ax.plot([])[0]
#         self.xmin = 0
#         self.xmax = 1

#     def plotSomeDataPoints(self, nmbpoints):
#         x = np.linspace(0, 10, nmbpoints)
#         y = np.cos(x)
#         self.plot.set_data([x, y])
#         self.draw()

#     def setProperty(self, prop, val):
#         if prop in ['xmin', 'xmax']:
#             setattr(self, prop, val)
#             self.ax.set_xlim(self.xmin, self.xmax)
#             self.draw()
#         else:
#             super(MplPlotWidget, self).setProperty(prop, val)

#     def set_xmax(self, xmax):
#         self.xmax = xmax
#         self.ax.set_xlim(self.xmin, self.xmax)
#         self.draw()


class MplWidgetImport(Canvas):
    def __init__(self, parent=None):
        # Plot
        super(MplWidgetImport, self).__init__(Figure())
        self.setParent(parent)
        self.parent = parent
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 cmap=plt.cm.binary_r)
        # Cropped area
        self.rect_hand = RectangleHandler(self, self.figure, self.ax)
        # Baseline
        self.baseline_hand = BaselineHandler(self, self.figure, self.ax)
        # Scaling
        self.is_scaling = False
        self.scaling_hand = ScalingHandler(self, self.figure, self.ax)
        # Clean stuff !
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticks([])
        self.ax.set_yticklabels([])
        # Connect event handlerd
        self.connect_press = self.mpl_connect('button_press_event',
                                              self.on_press)
        self.connect_release = self.mpl_connect('button_release_event',
                                                self.on_release)
        self.connect_motion = self.mpl_connect('motion_notify_event',
                                               self.on_motion)

    def update_image(self, im, replot=False):
        self.data = im.transpose()[::-1]
        if replot:
            self.im = self.ax.imshow(self.data,
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
        else:
            self.im.set_data(self.data)
        self.draw()

    def update_crop_area(self, xlim1, xlim2, ylim1, ylim2):
        self.rect_hand.update_lims(xlim1, xlim2,
                                   ylim1, ylim2)
        self.draw()

    def update_baseline(self, pt1, pt2):
        self.baseline_hand.update_pts(pt1, pt2)
        self.draw()

    def on_press(self, event):
        # see: https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
        # Check
        if event.inaxes != self.ax:
            return None
        #
        if self.scaling_hand.select_hand_at_point(event):
            self.scaling_hand.prepare_for_drag()
        # Add a new scaling point
        elif self.is_scaling and len(self.scaling_hand.pts) < 2:
            self.scaling_hand.add_point(event)
            self.draw()
        # On a crop handle
        elif self.rect_hand.select_hand_at_point(event):
            self.rect_hand.prepare_for_drag()
        # On a baseline handle
        elif self.baseline_hand.select_hand_at_point(event):
            self.baseline_hand.prepare_for_drag()

    def on_motion(self, event):
        # Check
        if event.inaxes != self.ax:
            return None
        #
        if self.scaling_hand.dragged_hand is not None:
            self.scaling_hand.drag_to(event)
        elif self.rect_hand.dragged_hand is not None:
            self.rect_hand.drag_to(event)
        elif self.baseline_hand.dragged_hand is not None:
            self.baseline_hand.drag_to(event)

    def on_release(self, event):
        if self.scaling_hand.is_dragging():
            self.scaling_hand.finish_drag()
            self.scaling_hand.unselect_hand()
        elif self.rect_hand.is_dragging():
            self.rect_hand.finish_drag()
            self.rect_hand.unselect_hand()
        elif self.baseline_hand.is_dragging():
            self.baseline_hand.finish_drag()
            self.baseline_hand.unselect_hand()

    def get_scale(self):
        return self.scaling_hand.get_scale()


class MplWidgetDetect(Canvas):
    def __init__(self, parent=None):
        # Plot
        super(MplWidgetDetect, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 cmap=plt.cm.binary_r)
        # baseline
        self.baseline = self.ax.plot([0, 0], [0, 0],
                                     color=colors['baseline'],
                                     lw=0.5,
                                     ls="-")[0]
        # edges
        self.edge = self.ax.plot([0], [0],
                                 color=colors['edge'],
                                 marker='o',
                                 ms=3,
                                 alpha=0.5,
                                 ls='none')[0]
        # Clean stuff !
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticks([])
        self.ax.set_yticklabels([])

    def update_image(self, im, replot=False, draw=True):
        self.data = im.transpose()[::-1]
        if replot:
            self.im = self.ax.imshow(self.data,
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
        else:
            self.im.set_data(self.data)
        if draw:
            self.draw()

    def update_baseline(self, pt1, pt2, draw=True):
        sizex = abs(self.ax.viewLim.width)
        pt1, pt2 = Baseline.get_baseline_from_points([pt1, pt2],
                                                     xmin=0, xmax=sizex)
        self.baseline.set_data([[pt1[0], pt2[0]],
                                [pt1[1], pt2[1]]])
        if draw:
            self.draw()

    def update_edge(self, edge, draw=True):
        self.edge.set_data(*edge)
        if draw:
            self.draw()


class MplWidgetFit(Canvas):
    def __init__(self, parent=None):
        # Plot
        super(MplWidgetFit, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 cmap=plt.cm.binary_r)
        # baseline
        self.baseline = self.ax.plot([0, 0], [0, 0],
                                     color=colors['baseline'],
                                     lw=0.5,
                                     ls="-")[0]
        # edges
        self.fit = self.ax.plot([0], [0],
                                color=colors['fit'],
                                ls='-')[0]
        self.fit_center = self.ax.plot([0], [0],
                                       color=colors['fit'],
                                       marker='o',
                                       ls='none')[0]
        # contact angles
        self.ca_r = self.ax.plot([], [],
                                 color=colors['ca'],
                                 marker='o',
                                 ms=3,
                                 ls='-')[0]
        self.ca_l = self.ax.plot([], [],
                                 color=colors['ca'],
                                 marker='o',
                                 ms=3,
                                 ls='-')[0]
        # Clean stuff !
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticks([])
        self.ax.set_yticklabels([])

    def update_image(self, im, replot=False, draw=True):
        self.data = im.transpose()[::-1]
        if replot:
            self.im = self.ax.imshow(self.data,
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
        else:
            self.im.set_data(self.data)
        if draw:
            self.draw()

    def update_baseline(self, pt1, pt2, draw=True):
        sizex = abs(self.ax.viewLim.width)
        pt1, pt2 = Baseline.get_baseline_from_points([pt1, pt2],
                                                     xmin=0, xmax=sizex)
        self.baseline.set_data([[pt1[0], pt2[0]],
                                [pt1[1], pt2[1]]])
        if draw:
            self.draw()

    def update_fit(self, fit, fit_center, draw=True):
        if fit_center is None:
            fit_center = [[0], [0]]
        self.fit.set_data(*fit)
        self.fit_center.set_data(fit_center)
        if draw:
            self.draw()

    def update_ca(self, cas, draw=True):
        ca1, ca2 = cas
        self.ca_r.set_data(*ca1)
        self.ca_l.set_data(*ca2)
        if draw:
            self.draw()


class MplWidgetAnalyze(Canvas):
    def __init__(self, parent=None):
        # Figure and axis
        super(MplWidgetAnalyze, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.subplots(1, 1)
        self.ax.yaxis.label.set_color(colors['plot1'])
        self.ax.tick_params(axis='y', colors=colors['plot1'])
        self.ax2 = self.ax.twinx()
        self.ax2.yaxis.label.set_color(colors['plot2'])
        self.ax2.tick_params(axis='y', colors=colors['plot2'])
        self.ax3 = self.ax.twinx()
        self.ax3.set_zorder(1)
        self.ax3.set_xticks([])
        self.ax3.set_yticks([])
        # plots
        self.current_x = []
        self.current_y = []
        self.current_y2 = []
        self.plot1 = None
        self.plot2 = None
        self.indicator1 = None
        self.indicator2 = None
        # Vertical line
        self.vertical_line = VerticalLineHandler(
            self,
            self.figure,
            self.ax3,
            color=colors['vertical line'])
        # Connect event handler
        self.connect_press = self.mpl_connect('button_press_event',
                                              self.on_press)
        self.connect_release = self.mpl_connect('button_release_event',
                                                self.on_release)
        self.connect_motion = self.mpl_connect('motion_notify_event',
                                               self.on_motion)
        # grid
        self.ax.grid()

    def on_press(self, event):
        # Check
        if event.inaxes != self.ax3:
            return None
        #
        if self.vertical_line.select_hand_at_point(event):
            self.vertical_line.prepare_for_drag()

    def on_motion(self, event):
        # Check
        if event.inaxes != self.ax3:
            return None
        #
        if self.vertical_line.dragged_hand is not None:
            self.vertical_line.drag_to(event)

    def on_release(self, event):
        if self.vertical_line.is_dragging():
            self.vertical_line.finish_drag()
            self.vertical_line.unselect_hand()

    def update_plots(self, x, y, y2, xname, yname, y2name,
                     draw=True, replot=False):
        # Because of issues with the vertical line hand...
        if draw:
            self.draw()
        # store
        self.current_x = x
        self.current_y = y
        self.current_y2 = y2
        # check
        if self.plot1 is None:
            replot = True
        # Completely replot is asked
        if replot:
            # Clean
            self.ax.clear()
            self.ax2.clear()
            # Plots
            self.plot1 = self.ax.plot(x, y,
                                      color=colors['plot1'])[0]
            self.plot2 = self.ax2.plot(x, y2,
                                       color=colors['plot2'])[0]
            self.indicator1 = self.ax.plot([], [], color=colors['plot1'],
                                           marker="o", ls='none')[0]
            self.indicator2 = self.ax2.plot([], [], color=colors['plot2'],
                                            marker="o", ls='none')[0]
            self.ax.grid()
        else:
            # Update plots
            self.plot1.set_data(x, y)
            self.plot2.set_data(x, y2)
        # Hide second axis if necessary
        is_y2 = np.logical_not(np.all(np.isnan(y2)))
        if is_y2:
            self.ax2.set_visible(True)
        else:
            self.ax2.set_visible(False)
        # Update limits
        self.update_lims(x, y, y2)
        # Update the vertical line position
        if len(x) > 1:
            self.vertical_line.update_line_pos((np.max(x) + np.min(x))/2)
        # Update labels
        self.ax.set_xlabel(xname)
        self.ax.set_ylabel(yname)
        if is_y2:
            self.ax2.set_ylabel(y2name)
        else:
            self.ax2.set_ylabel("")
        # Draw if asked
        if draw:
            self.draw()

    def update_lims(self, x, y, y2):
        # margin
        margin = 1/50
        # x
        if len(x) <= 1 or np.all(np.isnan(x)):
            x_min, x_max = -1, 1
        else:
            x_min, x_max = np.nanmin(x), np.nanmax(x)
        if np.any(np.isnan([x_min, x_max])):
            x_min = -1
            x_max = 1
        dx = x_max - x_min
        if dx == 0:
            dx = 0.1
        self.ax.set_xlim(x_min - dx*margin, x_max + dx*margin)
        # y
        if len(y) <= 1 or np.all(np.isnan(y)):
            y_min, y_max = -1, 1
        else:
            y_min, y_max = np.nanmin(y), np.nanmax(y)
        if np.any(np.isnan([y_min, y_max])):
            y_min = -1
            y_max = 1
        dy = y_max - y_min
        if dy == 0:
            dy = 0.1
        self.ax.set_ylim(y_min - dy*margin, y_max + dy*margin)
        # y2
        if len(y2) <= 1 or np.all(np.isnan(y2)):
            y2_min, y2_max = -1, 1
        else:
            y2_min, y2_max = np.nanmin(y2), np.nanmax(y2)
        if np.any(np.isnan([y2_min, y2_max])):
            y2_min = -1
            y2_max = 1
        dy2 = y2_max - y2_min
        if dy2 == 0:
            dy2 = 0.1
        self.ax2.set_ylim(y2_min - dy2*margin, y2_max + dy2*margin)
        # dummy ax3
        self.ax3.set_xlim(self.ax.get_xlim())
        self.ax3.set_ylim(self.ax.get_xlim())

    def update_upstream(self):
        """ Update the interface to reflect line modification"""
        # Get the position of the selected points
        xi = self.vertical_line.pt[0]
        x = self.current_x
        y = self.current_y
        y2 = self.current_y2
        yi = None
        y2i = None
        if len(self.current_x) != 0:
            indx = np.argwhere(self.current_x > xi)
            if len(indx) != 0:
                indx = indx[0]
                if len(indx) < 2:
                    indx = indx[0]
                    yi = self.linear_interp(x[indx - 1], x[indx],
                                            y[indx - 1], y[indx],
                                            xi)
                    y2i = self.linear_interp(x[indx - 1], x[indx],
                                             y2[indx - 1], y2[indx],
                                             xi)
        # Update the indicators
        if xi is not None and yi is not None:
            self.indicator1.set_data([xi], [yi])
        else:
            self.indicator1.set_data([], [])
        if xi is not None and y2i is not None:
            self.indicator2.set_data([xi], [y2i])
        else:
            self.indicator2.set_data([], [])
        # Update interface
        xi_t = ""
        if xi is not None:
            if not np.isnan(xi):
                xi_t = f"{xi:.4f}"
        self.ui.tab4_local_x_value.setText(xi_t)
        yi_t = ""
        if yi is not None:
            if not np.isnan(yi):
                yi_t = f"{yi:.4f}"
        self.ui.tab4_local_y_value.setText(yi_t)
        y2i_t = ""
        if y2i is not None:
            if not np.isnan(y2i):
                y2i_t = f"{y2i:.4f}"
        self.ui.tab4_local_y2_value.setText(y2i_t)

    @staticmethod
    def linear_interp(x1, x2, y1, y2, x):
        if x1 > x:
            return None
        if x > x2:
            return None
        y = (abs(x1 - x)*y2 + abs(x2 - x)*y1)/abs(x1 - x2)
        return y