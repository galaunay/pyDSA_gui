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


import matplotlib as mpl
import numpy as np
from pyDSA_core.baseline import Baseline


# Matplotlib 2.2 backward compatibility monkey patching
def set_center(self, xy):
    self.center = xy
    self.xy = xy
mpl.patches.Circle.set_center = set_center


class Handler(object):
    def __init__(self, canvas, fig, ax, color, hand_ratio):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.background = None
        self.color = color
        self.line = None
        self.create_line()
        self.hands = []
        self.minihands = []
        self.hand_ratio = hand_ratio
        self.hand_size = 0
        self.create_hands()
        for hand in self.hands + self.minihands:
            self.ax.add_patch(hand)
        self.dragged_hand = None
        self.dragged_offset = [0, 0]
        self.dragged_ind = None

    def create_line(self):
        self.line = self.ax.plot([0], [0], color=self.color, lw=.5)[0]

    def create_hands(self):
        raise Exception('Need to be defined !')

    def update_line(self):
        raise Exception('Need to be defined !')

    def update_hands(self):
        raise Exception('Need to be defined !')

    def update_from_event(self):
        raise Exception('Need to be defined !')

    def update_hand_size(self):
        sizex = abs(self.ax.viewLim.width)
        sizey = abs(self.ax.viewLim.height)
        self.hand_size = (self.hand_ratio*sizex*sizey)**.5
        if self.hand_size > np.min([sizex, sizey])/2:
            self.hand_size = int(np.min([sizex, sizey])/2) - 1
        for hand in self.hands:
            try:
                hand.set_width(self.hand_size)
                hand.set_height(self.hand_size)
            except:
                hand.set_radius(self.hand_size/2)
        for hand in self.minihands:
            try:
                hand.set_width(self.hand_size/10)
                hand.set_height(self.hand_size/10)
            except:
                hand.set_radius(self.hand_size/20)

    def select_hand_at_point(self, event):
        ind_sel = np.argwhere([hand.contains(event)[0]
                               for hand in self.hands])
        ind_sel = ind_sel.flatten()
        if len(ind_sel) == 0:
            return False
        ind_sel = ind_sel[0]
        self.dragged_ind = ind_sel
        self.dragged_hand = self.hands[ind_sel]
        try:
            pos = self.dragged_hand.xy
        except AttributeError:
            pos = self.dragged_hand.get_center()
        self.dragged_offset = [event.xdata - pos[0],
                               event.ydata - pos[1]]
        return True

    def prepare_for_drag(self):
        for hand in self.hands + self.minihands:
            hand.set_animated(True)
        self.line.set_animated(True)
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        for hand in self.hands + self.minihands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def drag_to(self, event, blit=True):
        if self.dragged_hand is None:
            return None
        # Update hands
        self.update_from_event(event)
        # Update line
        self.update_line()
        # Update handlers
        self.update_hands()
        # Redraw
        self.canvas.restore_region(self.background)
        for hand in self.hands + self.minihands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.line)
        # blit just the redrawn area
        if blit:
            self.canvas.blit(self.ax.bbox)

    def unselect_hand(self):
        self.dragged_hand = None
        self.dragged_ind = None
        self.dragged_offset = None

    def finish_drag(self):
        for hand in self.hands + self.minihands:
            hand.set_animated(False)
        self.line.set_animated(False)
        self.background = None

    def is_dragging(self):
        if self.dragged_hand is not None:
            return True
        else:
            return False


class RectangleHandler(Handler):
    def __init__(self, canvas, fig, ax):
        super().__init__(canvas, fig, ax, color='r', hand_ratio=1/500)
        self.lims = [[0, 0], [0, 0]]

    def create_hands(self):
        self.hands = [mpl.patches.Rectangle([0, 0],
                                            self.hand_size, self.hand_size,
                                            color=self.color,
                                            alpha=0.25)
                      for i in range(4)]
        ind_xs = [0, 1, 1, 0]
        ind_ys = [0, 0, 1, 1]
        for hand, ind_xlim, ind_ylim in zip(self.hands, ind_xs, ind_ys):
            hand.ind_xlim = ind_xlim
            hand.ind_ylim = ind_ylim

    def update_line(self):
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        xs = [xlim1, xlim2, xlim2, xlim1, xlim1]
        ys = [ylim1, ylim1, ylim2, ylim2, ylim1]
        self.line.set_data([xs, ys])

    def update_hands(self):
        size = self.hand_size
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        xs = [xlim1, xlim2 - size, xlim2 - size, xlim1]
        ys = [ylim1, ylim1, ylim2 - size, ylim2 - size]
        for hand, xlim, ylim in zip(self.hands, xs, ys):
            hand.set_xy([xlim, ylim])

    def update_from_event(self, event):
        new_xlim = event.xdata - self.dragged_offset[0]
        new_xlim += self.dragged_hand.ind_xlim*self.hand_size
        new_ylim = event.ydata - self.dragged_offset[1]
        new_ylim += self.dragged_hand.ind_ylim*self.hand_size
        self.lims[0][self.dragged_hand.ind_xlim] = new_xlim
        self.lims[1][self.dragged_hand.ind_ylim] = new_ylim
        self.ensure_lims_in_image()

    def update_lims(self, xlim1, xlim2, ylim1, ylim2):
        # update
        self.lims = [[xlim1, xlim2], [ylim1, ylim2]]
        self.ensure_lims_in_image()
        self.update_hand_size()
        self.update_line()
        self.update_hands()

    def ensure_lims_in_image(self):
        sizex = abs(self.ax.dataLim.width)
        sizey = abs(self.ax.dataLim.height)
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        # checks
        #    x
        if xlim1 < 0:
            xlim1 = 0
        if xlim2 > sizex:
            xlim2 = sizex
        if xlim2 < xlim1:
            xlim1 = xlim2
        #    y
        if ylim1 < 0:
            ylim1 = 0
        if ylim2 > sizey:
            ylim2 = sizey
        if ylim2 < ylim1:
            ylim1 = ylim2
        # Update
        self.lims = [[xlim1, xlim2], [ylim1, ylim2]]


class BaselineHandler(Handler):
    def __init__(self, canvas, fig, ax):
        super().__init__(canvas, fig, ax, color='b', hand_ratio=1/500)
        self.pt1 = None
        self.pt2 = None

    def create_hands(self):
        self.hands = [mpl.patches.Circle([0, 0],
                                         radius=self.hand_size/2,
                                         color=self.color,
                                         alpha=0.25)
                      for i in range(2)]

    def update_line(self):
        sizex = abs(self.ax.dataLim.width)
        pt1, pt2 = Baseline.get_baseline_from_points([self.pt1, self.pt2],
                                                     xmin=0,
                                                     xmax=sizex)
        self.line.set_data([pt1[0], pt2[0]], [pt1[1], pt2[1]])

    def update_hands(self):
        self.hands[0].set_center(self.pt1)
        self.hands[1].set_center(self.pt2)

    def update_from_event(self, event):
        new_x = event.xdata - self.dragged_offset[0]
        new_y = event.ydata - self.dragged_offset[1]
        if self.dragged_ind == 0:
            self.pt1 = [new_x, new_y]
        else:
            self.pt2 = [new_x, new_y]

    def update_pts(self, pt1, pt2):
        # update
        self.pt1 = pt1
        self.pt2 = pt2
        self.update_hand_size()
        self.update_line()
        self.update_hands()


class ScalingHandler(Handler):
    def __init__(self, canvas, fig, ax):
        super().__init__(canvas, fig, ax, color='g', hand_ratio=1/500)
        self.pts = []

    def create_hands(self):
        for i in range(2):
            self.hands.append(mpl.patches.Circle([-1000, -1000],
                                                 radius=self.hand_size/2,
                                                 color=self.color,
                                                 alpha=0.25))
            self.minihands.append(mpl.patches.Circle([-1000, -1000],
                                                     radius=self.hand_size/20,
                                                     color=self.color,
                                                     alpha=1))

    def update_line(self):
        pass

    def update_hands(self):
        self.hands[0].set_center(self.pts[0])
        self.hands[1].set_center(self.pts[1])
        self.minihands[0].set_center(self.pts[0])
        self.minihands[1].set_center(self.pts[1])

    def update_from_event(self, event):
        new_x = event.xdata - self.dragged_offset[0]
        new_y = event.ydata - self.dragged_offset[1]
        self.pts[self.dragged_ind] = [new_x, new_y]

    def add_point(self, event):
        self.update_hand_size()
        pos = (event.xdata, event.ydata)
        if len(self.pts) == 0:
            hand = self.hands[0]
            minihand = self.minihands[0]
        elif len(self.pts) == 1:
            hand = self.hands[1]
            minihand = self.minihands[1]
        else:
            return None
        hand.set_center(pos)
        minihand.set_center(pos)
        self.pts.append(pos)

    def reset(self):
        self.pts = []
        for hand in self.hands + self.minihands:
            hand.set_center([-1000, -1000])
        self.canvas.draw()

    def get_scale(self):
        if len(self.pts) != 2:
            return None
        return ((self.pts[0][0] - self.pts[1][0])**2
                + (self.pts[0][1] - self.pts[1][1])**2)**.5

    def update_pts(self, pts):
        # update
        self.pts = pts
        self.update_hand_size()
        self.update_hands()


class VerticalLineHandler(Handler):
    def __init__(self, canvas, fig, ax, color):
        self.pt = [0, 0]
        super().__init__(canvas, fig, ax, color=color, hand_ratio=1/500)

    def create_line(self):
        self.line = self.ax.axvline(self.pt[0], color=self.color, lw=.5)

    def create_hands(self):
        self.update_hand_size()
        self.hands.append(mpl.patches.Circle(self.pt,
                                             radius=self.hand_size,
                                             color=self.color,
                                             alpha=0.25))

    def update_hand_size(self):
        self.hand_size = 2

    def update_line(self):
        ylims = self.ax.get_ylim()
        pt1 = [self.pt[0], ylims[0]]
        pt2 = [self.pt[0], ylims[1]]
        self.line.set_data([pt1[0], pt2[0]], [0, 1])

    def update_hands(self):
        self.hands[0].set_center(self.pt)
        xlims = self.ax.get_xlim()
        self.hands[0].set_radius((xlims[1] - xlims[0])*self.hand_size/100)

    def update_from_event(self, event):
        new_x = event.xdata
        new_y = event.ydata
        self.pt = [new_x, new_y]
        self.update_hands()
        self.update_upstream()

    def reset(self):
        self.pt = [0, 0]
        self.hands[0].set_center([-1000, -1000])
        self.canvas.draw()

    def update_line_pos(self, x):
        # update
        if x is None:
            return None
        if np.isnan(x):
            return None
        self.pt[0] = x
        self.pt[1] = np.mean(self.ax.get_ylim())
        self.update_hands()
        self.update_line()
        self.update_upstream()

    def update_upstream(self):
        """ Update the interface to reflect line modification"""
        # Get values at position
        self.canvas.parent.update_upstream()

    def prepare_for_drag(self):
        self.canvas.parent.indicator1.set_animated(True)
        self.canvas.parent.indicator2.set_animated(True)
        super(VerticalLineHandler, self).prepare_for_drag()
        self.canvas.parent.ax.draw_artist(self.canvas.parent.indicator1)
        self.canvas.parent.ax2.draw_artist(self.canvas.parent.indicator2)

    def drag_to(self, event):
        super(VerticalLineHandler, self).drag_to(event, blit=False)
        self.canvas.parent.ax.draw_artist(self.canvas.parent.indicator1)
        self.canvas.parent.ax2.draw_artist(self.canvas.parent.indicator2)
        # blit just the redrawn area
        self.canvas.blit(self.ax.bbox)

    def finish_drag(self):
        super(VerticalLineHandler, self).finish_drag()
        self.canvas.parent.indicator1.set_animated(False)
        self.canvas.parent.indicator2.set_animated(False)
