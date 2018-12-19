from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
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
            return None
        ind_corner = ind_corner[0]
        self.dragged_ind = ind_corner
        self.dragged_hand = self.hands[ind_corner]
        self.dragged_offset = [event.xdata - self.dragged_hand.xy[0],
                               event.ydata - self.dragged_hand.xy[1]]

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


class MplPlotWidget(Canvas):
    def __init__(self, parent=None):
        super(MplPlotWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure(dpi=100)
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.plot = self.ax.plot([])[0]
        self.xmin = 0
        self.xmax = 1

    def plotSomeDataPoints(self, nmbpoints):
        x = np.linspace(0, 10, nmbpoints)
        y = np.cos(x)
        self.plot.set_data([x, y])
        self.draw()

    def setProperty(self, prop, val):
        if prop in ['xmin', 'xmax']:
            setattr(self, prop, val)
            self.ax.set_xlim(self.xmin, self.xmax)
            self.draw()
        else:
            super(MplPlotWidget, self).setProperty(prop, val)

    def set_xmax(self, xmax):
        self.xmax = xmax
        self.ax.set_xlim(self.xmin, self.xmax)
        self.draw()


class MplWidgetImport(Canvas):
    def __init__(self, parent=None):
        # Plot
        super(MplWidgetImport, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        # Image
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 cmap=plt.cm.binary_r)
        # Cropped area
        self.rect_hand = RectangleHandler(self, self.figure, self.ax)
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

    def on_press(self, event):
        # see: https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
        # Check
        if event.inaxes != self.ax:
            return None
        self.rect_hand.select_hand_at_point(event)
        self.rect_hand.prepare_for_drag()

    def on_motion(self, event):
        # Check
        if event.inaxes != self.ax:
            return None
        # Drag
        self.rect_hand.drag_to(event)

    def on_release(self, event):
        if self.rect_hand.is_dragging():
            self.rect_hand.finish_drag()
            self.rect_hand.unselect_hand()


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
        print('draw')
        if draw:
            self.draw()
        print('done')
