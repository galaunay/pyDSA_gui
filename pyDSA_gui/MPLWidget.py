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
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt4 import (
    NavigationToolbar2QT as MplNavigationBar)
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pyDSA_core.baseline import Baseline

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
          'figure_background': '#FAFAFA',
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


class MplToolBar(MplNavigationBar):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        # ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        # (None, None, None, None),
        # ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )


class MplCanvas(Canvas):
    def __init__(self, parent=None, fill=False):
        # Plot
        self.figure = Figure(dpi=100, figsize=(200, 200),
                             facecolor=colors['figure_background'])
        super(MplCanvas, self).__init__(self.figure)
        self.setParent(parent)
        self.parent = parent
        if fill:
            self.ax = self.figure.add_axes([0, 0, 1, 1])
        else:
            self.ax = self.figure.subplots(1, 1)


class MplWidget(QWidget):
    def __init__(self, *args, **kwargs):
        fill = kwargs.pop('fill')
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = MplCanvas(parent=self, fill=fill)
        self.toolbar = MplToolBar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)
        self.figure = self.canvas.figure
        self.ax = self.canvas.ax

    def reset_zoom(self):
        self.toolbar.home()


class MplWidgetImport(MplWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(fill=True, *args, **kwargs)
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 interpolation='None',
                                 cmap=plt.cm.binary_r)
        # add handlers
        # Cropped area
        self.rect_hand = RectangleHandler(self.canvas, self.figure, self.ax)
        # Baseline
        self.baseline_hand = BaselineHandler(self.canvas, self.figure, self.ax)
        # Scaling
        self.is_scaling = False
        self.scaling_hand = ScalingHandler(self.canvas, self.figure, self.ax)
        # Clean stuff !
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticks([])
        self.ax.set_yticklabels([])
        # Connect event handlerd
        self.connect_press = self.canvas.mpl_connect('button_press_event',
                                                     self.on_press)
        self.connect_release = self.canvas.mpl_connect('button_release_event',
                                                       self.on_release)
        self.connect_motion = self.canvas.mpl_connect('motion_notify_event',
                                                      self.on_motion)

    def update_image(self, im, replot=False):
        self.data = im.transpose()[::-1]
        if replot:
            self.im = self.ax.imshow(self.data,
                                     interpolation="None",
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
        else:
            self.im.set_data(self.data)
        self.canvas.draw()

    def update_crop_area(self, xlim1, xlim2, ylim1, ylim2):
        self.rect_hand.update_lims(xlim1, xlim2,
                                   ylim1, ylim2)
        self.canvas.draw()

    def update_baseline(self, pt1, pt2):
        self.baseline_hand.update_pts(pt1, pt2)
        self.canvas.draw()

    def update_scaling_pts(self, pts):
        self.scaling_hand.update_pts(pts)
        self.canvas.draw()

    def get_scale(self):
        return self.scaling_hand.get_scale()

    def on_press(self, event):
        # see: https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
        # Check
        if event.inaxes != self.ax:
            return None
        # toolbar want the focus !
        if self.toolbar._active is not None:
            return None
        # On a scaling handle
        if self.scaling_hand.select_hand_at_point(event):
            self.scaling_hand.prepare_for_drag()
        # Add a new scaling point
        elif self.is_scaling and len(self.scaling_hand.pts) < 2:
            self.scaling_hand.add_point(event)
            self.canvas.draw()
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


class MplWidgetDetect(MplWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(fill=True, *args, **kwargs)
        #
        self.axbackground = None
        self.need_replot = True
        self.tab_opened = False
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 interpolation="None",
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

    def update_image(self, im, blit=True):
        new_data = im.transpose()[::-1]
        if not np.all(new_data.shape == self.data.shape):
            self.need_replot = True
        self.data = new_data
        self.im.set_data(self.data)
        if blit:
            self.blit_it()

    def update_baseline(self, pt1, pt2, blit=True):
        sizex = abs(self.ax.viewLim.width)
        pt1, pt2 = Baseline.get_baseline_from_points([pt1, pt2],
                                                     xmin=-100*sizex,
                                                     xmax=100*sizex)
        self.baseline.set_data([[pt1[0], pt2[0]],
                                [pt1[1], pt2[1]]])
        if blit:
            self.blit_it()

    def update_edge(self, edge, blit=True):
        self.edge.set_data(*edge)
        if blit:
            self.blit_it()

    def blit_it(self):
        if not self.tab_opened:
            # If tab is not open, just redispay the data
            self.im = self.ax.imshow(self.data,
                                     interpolation='None',
                                     cmap=plt.cm.binary_r)
            return None
        if self.need_replot or self.axbackground is None:
            self.im = self.ax.imshow(self.data,
                                     interpolation='None',
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
            self.canvas.draw()
            self.axbackground = self.canvas.copy_from_bbox(self.ax.bbox)
            self.ax.draw_artist(self.edge)
            self.ax.draw_artist(self.baseline)
            self.need_replot = False
        else:
            self.canvas.restore_region(self.axbackground)
            self.ax.draw_artist(self.im)
            self.ax.draw_artist(self.edge)
            self.ax.draw_artist(self.baseline)
            self.canvas.blit(self.ax.bbox)


class MplWidgetFit(MplWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(fill=True, *args, **kwargs)
        #
        self.axbackground = None
        self.need_replot = True
        self.tab_opened = False
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 interpolation="None",
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

    def update_image(self, im, blit=True):
        new_data = im.transpose()[::-1]
        if not np.all(new_data.shape == self.data.shape):
            self.need_replot = True
        self.data = new_data
        self.im.set_data(self.data)
        if blit:
            self.blit_it()

    def update_baseline(self, pt1, pt2, blit=True):
        sizex = abs(self.ax.viewLim.width)
        pt1, pt2 = Baseline.get_baseline_from_points([pt1, pt2],
                                                     xmin=-100*sizex,
                                                     xmax=100*sizex)
        self.baseline.set_data([[pt1[0], pt2[0]],
                                [pt1[1], pt2[1]]])
        if blit:
            self.blit_it()

    def update_fit_and_cas(self, fit, fit_center, cas, blit=True):
        # fit
        if fit_center is None:
            fit_center = [[0], [0]]
        self.fit.set_data(*fit)
        self.fit_center.set_data(fit_center)
        # cas
        ca1, ca2 = cas
        self.ca_r.set_data(*ca1)
        self.ca_l.set_data(*ca2)
        if blit:
            self.blit_it()

    def blit_it(self):
        if not self.tab_opened:
            # If tab is not open, just redispay the data
            self.im = self.ax.imshow(self.data,
                                     interpolation='None',
                                     cmap=plt.cm.binary_r)
            return None
        if self.need_replot or self.axbackground is None:
            self.im = self.ax.imshow(self.data,
                                     interpolation="None",
                                     cmap=plt.cm.binary_r)
            # clean stuff !
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticks([])
            self.ax.set_yticklabels([])
            self.canvas.draw()
            self.axbackground = self.canvas.copy_from_bbox(self.ax.bbox)
            self.ax.draw_artist(self.baseline)
            self.ax.draw_artist(self.fit)
            self.ax.draw_artist(self.fit_center)
            self.ax.draw_artist(self.ca_r)
            self.ax.draw_artist(self.ca_l)
            self.need_replot = False
        else:
            self.canvas.restore_region(self.axbackground)
            self.ax.draw_artist(self.im)
            self.ax.draw_artist(self.baseline)
            self.ax.draw_artist(self.fit)
            self.ax.draw_artist(self.fit_center)
            self.ax.draw_artist(self.ca_r)
            self.ax.draw_artist(self.ca_l)
            self.canvas.blit(self.ax.bbox)


class MplWidgetAnalyze(MplWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(fill=False, *args, **kwargs)
        # Figure and axis
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
        self.current_xname = None
        self.current_y = []
        self.current_y2 = []
        self.plot1 = None
        self.plot2 = None
        self.plot1_orig = None  # In case we smooth the other one
        self.plot2_orig = None
        self.indicator1 = None
        self.indicator2 = None
        # Vertical line
        self.vertical_line = VerticalLineHandler(
            self.canvas,
            self.figure,
            self.ax3,
            color=colors['vertical line'])
        # Connect event handler
        self.connect_press = self.canvas.mpl_connect('button_press_event',
                                                     self.on_press)
        self.connect_release = self.canvas.mpl_connect('button_release_event',
                                                       self.on_release)
        self.connect_motion = self.canvas.mpl_connect('motion_notify_event',
                                                      self.on_motion)
        # grid
        self.ax.grid()

    def on_press(self, event):
        # Check
        if event.inaxes != self.ax3:
            return None
        # toolbar want the focus !
        if self.toolbar._active is not None:
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

    def update_plots(self, x, y, y2, y_orig, y2_orig, current_x,
                     xname, yname, y2name, same_y_lims=False,
                     draw=True, replot=False):
        # check
        if np.all(np.isnan(x)) and np.all(np.isnan(y)):
            x = []
            y = []
            y2 = []
            y_orig = []
            y2_orig = []
        # Because of issues with the vertical line hand...
        if draw:
            self.canvas.draw()
        # store
        self.current_x = x
        self.current_xname = xname
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
            self.plot1_orig = self.ax.plot(x, y_orig,
                                           color=colors['plot1'],
                                           alpha=0.2)[0]
            self.plot2_orig = self.ax2.plot(x, y2_orig,
                                            color=colors['plot2'],
                                            alpha=0.2)[0]
            self.indicator1 = self.ax.plot([], [], color=colors['plot1'],
                                           marker="o", ls='none')[0]
            self.indicator2 = self.ax2.plot([], [], color=colors['plot2'],
                                            marker="o", ls='none')[0]
            self.ax.grid()
        else:
            # Update plots
            self.plot1.set_data(x, y)
            self.plot2.set_data(x, y2)
            self.plot1_orig.set_data(x, y_orig)
            self.plot2_orig.set_data(x, y2_orig)
        # Hide second axis if necessary
        is_y2 = np.logical_not(np.all(np.isnan(y2)))
        if is_y2:
            self.ax2.set_visible(True)
        else:
            self.ax2.set_visible(False)
        # Update limits
        self.update_lims(x, y, y2, y_orig, y2_orig, samelims=same_y_lims)
        # Update the vertical line position
        try:
            if current_x is None and len(x) > 0:
                current_x = (np.nanmax(x) + np.nanmin(x))/2
            self.vertical_line.update_line_pos(current_x)
        except:
            self.log.log_unknown_exception()
        # Update labels
        self.ax.set_xlabel(xname)
        self.ax.set_ylabel(yname)
        if is_y2:
            self.ax2.set_ylabel(y2name)
        else:
            self.ax2.set_ylabel("")
        # Draw if asked
        if draw:
            self.canvas.draw()

    def update_lims(self, x, y, y2, y_orig, y2_orig, samelims=False):
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
        y = np.concatenate((y, y_orig))
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
        # y2
        y2 = np.concatenate((y2, y2_orig))
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
        # Set y lims
        if samelims:
            y_min = np.min([y_min, y2_min])
            y_max = np.max([y_max, y2_max])
            dy = np.max([dy, dy2])
            self.ax.set_ylim(y_min - dy*margin, y_max + dy*margin)
            self.ax2.set_ylim(y_min - dy*margin, y_max + dy*margin)
        else:
            self.ax.set_ylim(y_min - dy*margin, y_max + dy*margin)
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
            indxs = np.argwhere(np.logical_or(
                np.logical_and(self.current_x[1::] <= xi,
                               self.current_x[:-1] >= xi),
                np.logical_and(self.current_x[1::] >= xi,
                               self.current_x[:-1] <= xi))).flatten()
            yis = [self.linear_interp(x[indx], x[indx + 1],
                                      y[indx], y[indx + 1],
                                      xi)
                   for indx in indxs]
            y2is = [self.linear_interp(x[indx], x[indx + 1],
                                       y2[indx], y2[indx + 1],
                                       xi)
                    for indx in indxs]
            yis = np.asarray(yis)
            y2is = np.asarray(y2is)
            # only keep the one closest to the handler
            vl_pos = self.vertical_line.pt
            vl_pos = self.vertical_line.ax.transData.transform(vl_pos)
            if len(yis) > 0 and not np.all(np.isnan(yis)):
                yvl = self.ax.transData.inverted().transform(vl_pos)[1]
                tmpind = np.nanargmin(abs(yis - yvl))
                yi = yis[tmpind]
            if len(y2is) > 0 and not np.all(np.isnan(y2is)):
                yvl = self.ax2.transData.inverted().transform(vl_pos)[1]
                tmpind = np.nanargmin(abs(y2is - yvl))
                y2i = y2is[tmpind]
        #
        # Update the indicators
        if self.indicator1 is not None:
            if xi is not None and yi is not None:
                self.indicator1.set_data([xi], [yi])
            else:
                self.indicator1.set_data([], [])
        if self.indicator2 is not None:
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
        # Update the current indice
        current_x = self.vertical_line.pt[0]
        if not np.all(np.isnan(x)):
            fn, _, _ = self.app.dsa.get_plotable_quantity("Frame number")
            tmpind = np.nanargmin(abs(current_x - x))
            ind = fn[tmpind] - 1
            self.app.current_ind = ind

    @staticmethod
    def linear_interp(x1, x2, y1, y2, x):
        if x < x1 and x < x2:
            return None
        if x > x2 and x > x1:
            return None
        y = (abs(x1 - x)*y2 + abs(x2 - x)*y1)/abs(x1 - x2)
        return y
