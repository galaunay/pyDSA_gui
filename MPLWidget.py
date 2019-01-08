from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pyDSA.baseline import Baseline

from mpl_handlers import BaselineHandler, RectangleHandler, ScalingHandler

colors = {'baseline': 'tab:blue',
          'crop_area': 'tab:red',
          'scaling': 'tab:green',
          'edge': 'tab:green',
          'fit': 'tab:orange',
          'ca': 'tab:blue',
          'plot1': 'tab:blue',
          'plot2': 'tab:red'}



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
        # Plot
        super(MplWidgetAnalyze, self).__init__(Figure())
        self.setParent(parent)
        self.figure = Figure(dpi=100, figsize=(200, 200))
        self.canvas = Canvas(self.figure)
        # self.ax = self.figure.add_axes([0.1, 0.1, 0.9, 0.9])
        self.ax = self.figure.subplots(1, 1)
        self.ax2 = self.ax.twinx()
        # plots
        self.plot1 = None
        self.plot2 = None
        # grid
        self.ax.grid()

    def update_plots(self, x, y, y2, xname, yname, y2name,
                     draw=True, replot=False):
        if replot or self.plot1 is None:
            self.ax.clear()
            self.ax2.clear()
            self.plot1 = self.ax.plot(x, y,
                                      color=colors['plot1'])[0]
            self.plot2 = self.ax2.plot(x, y2,
                                       color=colors['plot2'])[0]
            self.ax.grid()
        else:
            self.plot1.set_data(x, y)
            self.plot2.set_data(x, y2)
        # disable second axe if not needed
        if np.all(np.isnan(y2)):
            self.ax2.set_visible(False)
        else:
            self.ax2.set_visible(True)
        #
        self.ax.relim()
        self.ax.autoscale(True)
        self.ax.set_xlabel(xname)
        self.ax.set_ylabel(yname)
        self.ax2.relim()
        self.ax2.autoscale(True)
        self.ax2.set_xlabel(xname)
        self.ax2.set_ylabel(y2name)
        if draw:
            self.draw()
