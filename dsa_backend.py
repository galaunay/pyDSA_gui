import pyDSA as dsa
import numpy as np
from pyDSA.helpers import get_ellipse_points


class DSA(object):
    def __init__(self, app):
        self.app = app
        self.ui = app.ui
        self.current_ind = 0
        # Images
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None
        self.ims = None
        self.current_raw_im = None
        # Crop
        self.ims_cropped = None
        self.current_crop_lims = None
        self.current_cropped_im = None
        # Baseline
        self.baseline_pt1 = None
        self.baseline_pt2 = None
        # Edges
        self.edge_detection_method = 'canny'
        self.edges = None
        self.current_edge = None
        self.edge_cache = []
        self.edge_cache_params = [None]*3
        self.edge_cache_method = None
        # Fit
        self.fit_method = 'ellipse'
        self.fits = None
        self.current_fit = None
        self.fit_cache = []
        self.fit_cache_params = [None]*3
        self.fit_cache_method = None
        # Cache

    def reset_cache(self, edge=True, fit=True):
        if self.nmb_frames is not None:
            if edge:
                self.edge_cache = [None]*self.nmb_frames
            if fit:
                self.fit_cache = [None]*self.nmb_frames

    def import_image(self, filepath):
        self.ims = dsa.import_from_image(filepath, cache_infos=False)
        self.current_raw_im = self.ims
        self.reset_cache()
        self.nmb_frames = 1
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def import_video(self, filepath):
        self.ims = dsa.import_from_video(filepath, cache_infos=False)
        self.current_raw_im = self.ims[0]
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def set_current(self, ind):
        if self.nmb_frames == 1:
            return None
        self.current_ind = ind
        if self.ims is None:
            raise Exception()
        if ind > self.nmb_frames:
            raise Exception()
        self.current_raw_im = self.ims[ind]
        if self.ims_cropped is not None:
            self.current_cropped_im = self.ims_cropped[self.current_ind]

    def update_crop_lims(self):
        xlims, ylims = self.ui.mplwidgetimport.rect_hand.lims
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        ylims = np.sort(sizey - ylims)
        lims = np.array([xlims, ylims])
        if self.current_crop_lims is not None:
            if np.allclose(lims, self.current_crop_lims):
                return False
        self.current_crop_lims = lims
        self.ims_cropped = self.ims.crop(intervx=xlims, intervy=ylims,
                                         inplace=False)
        if self.nmb_frames == 1:
            self.current_cropped_im = self.ims_cropped
        else:
            self.current_cropped_im = self.ims_cropped.fields[self.current_ind]
        # reset cache
        self.reset_cache()
        # return
        return True

    def update_baselines(self):
        pt1 = self.ui.mplwidgetimport.baseline_hand.pt1
        pt2 = self.ui.mplwidgetimport.baseline_hand.pt2
        if self.baseline_pt1 is not None:
            if (np.allclose(self.baseline_pt1, pt1) and
                np.allclose(self.baseline_pt2, pt2)):
                return False
        self.baseline_pt1 = pt1
        self.baseline_pt2 = pt2
        deltay = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        new_pt1 = [pt1[0], deltay - pt1[1]]
        new_pt2 = [pt2[0], deltay - pt2[1]]
        self.ims.set_baseline(new_pt1, new_pt2)
        if self.ims_cropped is not None:
            self.ims_cropped.set_baseline(new_pt1, new_pt2)
        # reset cache
        self.reset_cache()
        # return
        return True

    def get_baseline(self, cropped=False):
        pt1 = self.baseline_pt1.copy()
        pt2 = self.baseline_pt2.copy()
        if cropped:
            deltax = self.current_crop_lims[0][0]
            deltay = self.sizey - self.current_crop_lims[1][1]
            pt1[0] -= deltax
            pt2[0] -= deltax
            pt1[1] -= deltay
            pt2[1] -= deltay
        return pt1, pt2

    def get_current_edge(self, params):
        # Reset cache if not valid anymore
        if self.edge_cache_method != self.edge_detection_method:
            self.reset_cache()
        for p1, p2 in zip(params, self.edge_cache_params):
            if p1 != p2:
                self.reset_cache()
                break
        # Use cache if possible
        edge = self.edge_cache[self.current_ind]
        if self.edge_cache[self.current_ind] is None:
            # Get params
            canny_args = params[0].copy()
            canny_args.update(params[-1])
            contour_args = params[1].copy()
            contour_args.update(params[-1])
            # Edge detection
            if self.edge_detection_method == 'canny':
                edge = self.current_cropped_im.edge_detection(**canny_args)
            elif self.edge_detection_method == 'contour':
                edge = self.current_cropped_im.edge_detection_contour(**contour_args)
            else:
                raise Exception()
            # Update cache
            self.edge_cache[self.current_ind] = edge
            self.edge_cache_params = params
            self.edge_cache_method = self.edge_detection_method
        self.current_edge = edge
        # Return edge pts
        pts = edge.xy.transpose().copy()
        deltax = self.current_crop_lims[0][0]
        deltay = self.current_crop_lims[1][1]
        pts[0] = pts[0] - deltax
        pts[1] = deltay - pts[1]
        return pts

    def get_current_fit(self, params):
        # Reset cache if not valid anymre
        if self.fit_cache_method != self.fit_method:
            self.reset_cache()
        for p1, p2 in zip(params, self.fit_cache_params):
            if p1 != p2:
                self.reset_cache()
                break
        # Use cache if available
        fit = self.fit_cache[self.current_ind]
        # Ensure the edge is computed
        edge_params = self.app.tab2_get_params()
        self.get_current_edge(edge_params)
        if self.current_edge is None:
            return [[0], [0]], [[0], [0]]
        # Get params
        circle_args = params[0]
        ellipse_args = params[1]
        polyline_args = params[2]
        spline_args = params[3]
        # Fit
        if self.fit_method == 'circle':
            if fit is None:
                fit = self.current_edge.fit_circle(**circle_args)
            pts = fit.get_fit_as_points()
            fit_center = fit.fits[0].copy()
        elif self.fit_method == 'ellipse':
            if fit is None:
                fit = self.current_edge.fit_ellipse(**ellipse_args)
            pts = fit.get_fit_as_points()
            fit_center = fit.fits[0].copy()
        elif self.fit_method == 'polyline':
            if fit is None:
                fit = self.current_edge.fit_polyline(**polyline_args)
            pts = fit.get_fit_as_points()
            fit_center = [[-999], [-999]]
        elif self.fit_method == 'spline':
            if fit is None:
                fit = self.current_edge.fit_spline(**spline_args)
            pts = fit.get_fit_as_points()
            fit_center = [[-999], [-999]]
        else:
            self.app.log.log('please select a fitting method', level=1)
            return [[0], [0]], [[-999], [-999]]
        # Update cache
        self.fit_cache[self.current_ind] = fit
        self.fit_cache_params = params
        self.fit_cache_method = self.fit_method
        self.current_fit = fit
        # Return fit pts
        deltax = self.current_crop_lims[0][0]
        deltay = self.current_crop_lims[1][1]
        pts[0] = pts[0] - deltax
        pts[1] = deltay - pts[1]
        fit_center[0] = fit_center[0] - deltax
        fit_center[1] = deltay - fit_center[1]
        return pts, fit_center
