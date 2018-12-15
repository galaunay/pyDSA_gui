from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

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
        self.im = self.ax.imshow(np.random.rand(200, 300),
                                 cmap=plt.cm.binary_r)
        #
        self.crop_area_color = 'r'
        self.crop_area = self.ax.plot([0], [0],
                                      color=self.crop_area_color)[0]
        # clean stuff !
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticks([])
        self.ax.set_yticklabels([])

    def update_image(self, im):
        self.im.set_data(im.transpose()[::-1])
        self.im.set_clim(np.min(im), np.max(im))
        self.ax.axis('scaled')
        # self.ax.relim()
        self.draw()
        # import matplotlib as mpl
        # ax = mpl.axes.Axes()
        # ax.

    def update_crop_area(self, xlim1, xlim2, ylim1, ylim2):
        xs = [xlim1, xlim2, xlim2, xlim1, xlim1]
        ys = [ylim1, ylim1, ylim2, ylim2, ylim1]
        print(xs, ys)
        self.crop_area.set_data([xs, ys])
        self.draw()
