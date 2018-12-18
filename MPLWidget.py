from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

class RectangleHandler(object):
    def __init__(self, fig, ax):
        self.fig = fig

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
        #
        super(MplWidgetImport, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        #
        self.data = np.random.rand(200, 300)
        self.im = self.ax.imshow(self.data,
                                 cmap=plt.cm.binary_r)
        # Cropped area
        self.background = None
        self.lims = [[0, 0], [0, 0]]
        self.crop_area_color = 'r'
        self.crop_area = self.ax.plot([0], [0],
                                      color=self.crop_area_color)[0]
        self.crop_handler_ratio = 1/100
        self.crop_handler_size = 0
        self.handlers = [mpl.patches.Rectangle([0, 0],
                                               self.crop_handler_size,
                                               self.crop_handler_size,
                                               color=self.crop_area_color,
                                               alpha=0.25)
                         for i in range(4)]
        for hand in self.handlers:
            self.ax.add_patch(hand)
        self.dragged_handler = None
        # clean stuff !
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
        self.lims = [[xlim1, xlim2], [ylim1, ylim2]]
        # Update rectangle
        xs = [xlim1, xlim2, xlim2, xlim1, xlim1]
        ys = [ylim1, ylim1, ylim2, ylim2, ylim1]
        self.crop_area.set_data([xs, ys])
        # Update handlers
        #    size
        self.crop_handler_size = (self.crop_handler_ratio
                                  * self.data.shape[0]
                                  * self.data.shape[1])**.5
        if self.crop_handler_size > np.min(self.data.shape)/2:
            self.crop_handler_size = int(np.min(self.data.shape)/2) - 1
        for hand in self.handlers:
            hand.set_width(self.crop_handler_size)
            hand.set_height(self.crop_handler_size)
        #    position
        size = self.crop_handler_size
        xs = [xlim1, xlim2 - size, xlim2 - size, xlim1]
        ys = [ylim1, ylim1, ylim2 - size, ylim2 - size]
        ind_xs = [0, 1, 1, 0]
        ind_ys = [0, 0, 1, 1]
        for hand, xlim, ylim, ind_xlim, ind_ylim in zip(self.handlers, xs, ys,
                                                        ind_xs, ind_ys):
            hand.set_xy([xlim, ylim])
            hand.ind_xlim = ind_xlim
            hand.ind_ylim = ind_ylim
        self.draw()

    def on_press(self, event):
        # see: https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
        if event.inaxes != self.ax:
            return None
        # check selected corner here
        ind_corner = np.argwhere([hand.contains(event)[0]
                                  for hand in self.handlers])
        ind_corner = ind_corner.flatten()
        if len(ind_corner) == 0:
            return None
        ind_corner = ind_corner[0]
        self.dragged_handler = self.handlers[ind_corner]
        self.dragged_offset = [event.xdata - self.dragged_handler.xy[0],
                               event.ydata - self.dragged_handler.xy[1]]
        #
        self.dragged_handler.set_animated(True)
        self.crop_area.set_animated(True)
        self.draw()
        self.background = self.copy_from_bbox(self.dragged_handler.axes.bbox)
        self.dragged_handler.axes.draw_artist(self.dragged_handler)
        self.blit(self.dragged_handler.axes.bbox)

    def on_motion(self, event):
        # Check
        if self.dragged_handler is None:
            return None
        if event.inaxes != self.ax:
            return None
        # Update handler
        new_xlim = event.xdata - self.dragged_offset[0]
        new_ylim = event.ydata - self.dragged_offset[1]
        self.dragged_handler.set_xy([new_xlim,
                                     new_ylim])
        # Update lims
        self.lims[0][self.dragged_handler.ind_xlim] = new_xlim
        self.lims[1][self.dragged_handler.ind_ylim] = new_ylim
        # Update rectangle
        (xlim1, xlim2), (ylim1, ylim2) = self.lims
        xs = [xlim1, xlim2, xlim2, xlim1, xlim1]
        ys = [ylim1, ylim1, ylim2, ylim2, ylim1]
        self.crop_area.set_data([xs, ys])
        # redraw
        self.restore_region(self.background)
        self.ax.draw_artist(self.dragged_handler)
        self.ax.draw_artist(self.crop_area)
        # blit just the redrawn area
        self.blit(self.dragged_handler.axes.bbox)

    def on_release(self, event):
        self.dragged_handler.set_animated(False)
        self.dragged_handler = None
        self.dragged_offset = None
        self.background = None
        self.figure.canvas.draw()






        # # draw everything but the selected rectangle and store the pixel buffer
        # canvas = self.point.figure.canvas
        # axes = self.point.axes
        # self.point.set_animated(True)
        # canvas.draw()
        # self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # # now redraw just the rectangle
        # axes.draw_artist(self.point)

        # # and blit just the redrawn area
        # canvas.blit(axes.bbox)
