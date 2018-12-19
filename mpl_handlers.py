import matplotlib as mpl
import numpy as np


class RectangleHandler(object):
    def __init__(self, canvas, fig, ax):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.background = None
        self.lims = [[0, 0], [0, 0]]
        self.rect_color = 'r'
        self.rect = self.ax.plot([0], [0], color=self.rect_color, lw=.5)[0]
        self.hand_ratio = 1/500
        self.hand_size = 0
        self.hands = [mpl.patches.Rectangle([0, 0],
                                            self.hand_size, self.hand_size,
                                            color=self.rect_color,
                                            alpha=0.25)
                      for i in range(4)]
        ind_xs = [0, 1, 1, 0]
        ind_ys = [0, 0, 1, 1]
        for hand, ind_xlim, ind_ylim in zip(self.hands, ind_xs, ind_ys):
            hand.ind_xlim = ind_xlim
            hand.ind_ylim = ind_ylim
        for hand in self.hands:
            self.ax.add_patch(hand)
        self.dragged_hand = None
        self.dragged_offset = [0, 0]
        self.dragged_ind = None

    def update_lims(self, xlim1, xlim2, ylim1, ylim2):
        # update
        self.lims = [[xlim1, xlim2], [ylim1, ylim2]]
        self.ensure_lims_in_image()
        self.update_hand_size()
        self.update_rect()
        self.update_hands()

    def ensure_lims_in_image(self):
        sizex = abs(self.ax.viewLim.width)
        sizey = abs(self.ax.viewLim.height)
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

    def update_rect(self):
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        xs = [xlim1, xlim2, xlim2, xlim1, xlim1]
        ys = [ylim1, ylim1, ylim2, ylim2, ylim1]
        self.rect.set_data([xs, ys])

    def update_hand_size(self):
        sizex = abs(self.ax.viewLim.width)
        sizey = abs(self.ax.viewLim.height)
        self.hand_size = (self.hand_ratio*sizex*sizey)**.5
        if self.hand_size > np.min([sizex, sizey])/2:
            self.hand_size = int(np.min([sizex, sizey])/2) - 1
        for hand in self.hands:
            hand.set_width(self.hand_size)
            hand.set_height(self.hand_size)

    def update_hands(self):
        size = self.hand_size
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        xs = [xlim1, xlim2 - size, xlim2 - size, xlim1]
        ys = [ylim1, ylim1, ylim2 - size, ylim2 - size]
        for hand, xlim, ylim in zip(self.hands, xs, ys):
            hand.set_xy([xlim, ylim])

    def select_hand_at_point(self, event):
        ind_corner = np.argwhere([hand.contains(event)[0]
                                  for hand in self.hands])
        ind_corner = ind_corner.flatten()
        if len(ind_corner) == 0:
            return False
        ind_corner = ind_corner[0]
        self.dragged_ind = ind_corner
        self.dragged_hand = self.hands[ind_corner]
        self.dragged_offset = [event.xdata - self.dragged_hand.xy[0],
                               event.ydata - self.dragged_hand.xy[1]]
        return True

    def prepare_for_drag(self):
        for hand in self.hands:
            hand.set_animated(True)
        self.rect.set_animated(True)
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        for hand in self.hands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.rect)
        self.canvas.blit(self.ax.bbox)

    def drag_to(self, event):
        if self.dragged_hand is None:
            return None
        # Update lims
        new_xlim = event.xdata - self.dragged_offset[0]
        new_xlim += self.dragged_hand.ind_xlim*self.hand_size
        new_ylim = event.ydata - self.dragged_offset[1]
        new_ylim += self.dragged_hand.ind_ylim*self.hand_size
        self.lims[0][self.dragged_hand.ind_xlim] = new_xlim
        self.lims[1][self.dragged_hand.ind_ylim] = new_ylim
        self.ensure_lims_in_image()
        # Update rectangle
        self.update_rect()
        # Update handlers
        self.update_hands()
        # Redraw
        self.canvas.restore_region(self.background)
        for hand in self.hands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.rect)
        # blit just the redrawn area
        self.canvas.blit(self.ax.bbox)

    def unselect_hand(self):
        self.dragged_hand = None
        self.dragged_ind = None
        self.dragged_offset = None

    def finish_drag(self):
        for hand in self.hands:
            hand.set_animated(False)
        self.rect.set_animated(False)
        self.background = None

    def is_dragging(self):
        if self.dragged_hand is not None:
            return True
        else:
            return False


class BaselineHandler(object):
    def __init__(self, canvas, fig, ax):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.background = None
        self.pt1 = None
        self.pt2 = None
        self.baseline_color = 'b'
        self.hand_ratio = 1/500
        self.hand_size = 0
        self.hands = [mpl.patches.Circle([0, 0],
                                         radius=self.hand_size/2,
                                         color=self.baseline_color,
                                         alpha=0.25)
                      for i in range(2)]
        for hand in self.hands:
            self.ax.add_patch(hand)
        self.line = self.ax.plot([0, 0], [0, 0],
                                 color=self.baseline_color,
                                 ls="-")[0]
        self.dragged_ind = None
        self.dragged_hand = None
        self.dragged_offset = [0, 0]

    def update_pts(self, pt1, pt2):
        # update
        self.pt1 = pt1
        self.pt2 = pt2
        self.update_hand_size()
        self.update_line()
        self.update_hands()

    def update_line(self):
        self.line.set_data([self.pt1[0], self.pt2[0]],
                           [self.pt1[1], self.pt2[1]])

    def update_hand_size(self):
        sizex = abs(self.ax.viewLim.width)
        sizey = abs(self.ax.viewLim.height)
        self.hand_size = (self.hand_ratio*sizex*sizey)**.5
        if self.hand_size > np.min([sizex, sizey])/2:
            self.hand_size = int(np.min([sizex, sizey])/2) - 1
        for hand in self.hands:
            hand.set_radius(self.hand_size/2)

    def update_hands(self):
        self.hands[0].set_center(self.pt1)
        self.hands[1].set_center(self.pt2)

    def select_hand_at_point(self, event):
        ind_sel = np.argwhere([hand.contains(event)[0]
                               for hand in self.hands])
        ind_sel = ind_sel.flatten()
        if len(ind_sel) == 0:
            return False
        ind_sel = ind_sel[0]
        self.dragged_ind = ind_sel
        self.dragged_hand = self.hands[ind_sel]
        center = self.dragged_hand.get_center()
        self.dragged_offset = [event.xdata - center[0],
                               event.ydata - center[1]]
        return True

    def prepare_for_drag(self):
        for hand in self.hands:
            hand.set_animated(True)
        self.line.set_animated(True)
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        for hand in self.hands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def drag_to(self, event):
        if self.dragged_hand is None:
            return None
        # Update lims
        new_x = event.xdata - self.dragged_offset[0]
        new_y = event.ydata - self.dragged_offset[1]
        if self.dragged_ind == 0:
            self.pt1 = [new_x, new_y]
        else:
            self.pt2 = [new_x, new_y]
        # Update line
        self.update_line()
        # Update handlers
        self.update_hands()
        # Redraw
        self.canvas.restore_region(self.background)
        for hand in self.hands:
            self.ax.draw_artist(hand)
        self.ax.draw_artist(self.line)
        # blit just the redrawn area
        self.canvas.blit(self.ax.bbox)

    def unselect_hand(self):
        self.dragged_hand = None
        self.dragged_ind = None
        self.dragged_offset = None

    def finish_drag(self):
        for hand in self.hands:
            hand.set_animated(False)
        self.line.set_animated(False)
        self.background = None

    def is_dragging(self):
        if self.dragged_hand is not None:
            return True
        else:
            return False
