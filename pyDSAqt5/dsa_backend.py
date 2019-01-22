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


import pyDSA as dsa
import numpy as np


class DSA(object):
    def __init__(self, app):
        self.app = app
        self.ui = app.ui
        self.log = app.log
        self.log.log('DSA backend: initializing backend', level=1)
        # Input
        self.input_type = None
        self.filepath = None
        # Images
        self.default_image = dsa.Image()
        self.default_image.import_from_arrays(range(300), range(200),
                                              np.random.rand(300, 200)*255)

        self.nmb_frames = None
        self.sizex = None
        self.sizey = None
        self.ims = None
        # Precompute
        self.precomp_old_params = None
        self.ims_precomp = None
        # Edges
        self.edge_detection_method = 'canny'
        self.edge_cache = []
        self.edge_cache_params = [None]*3
        self.edge_cache_method = None
        self.edges = None
        self.edges_old_params = None
        self.edges_old_method = self.edge_detection_method
        # Fit
        self.fit_method = 'ellipse'
        self.fit_cache = []
        self.fit_cache_params = [None]*3
        self.fit_cache_method = None
        self.fits = None
        self.fits_old_params = None
        self.fits_old_method = self.fit_method

    def is_initialized(self):
        return self.ims is not None

    def reset_cache(self, edge=True, fit=True):
        if self.nmb_frames is not None:
            if edge:
                self.edge_cache = [None]*self.nmb_frames
            if fit:
                self.fit_cache = [None]*self.nmb_frames

    def get_progressbar_hook(self, text_progress, text_finished):
        def hook(i, maxi):
            # base 0 to base 1
            i += 1
            # update progressbar
            self.ui.progressbar.setVisible(True)
            self.ui.progressbar.setMaximum(maxi)
            self.ui.progressbar.setValue(i)
            # Add message to statusbar
            if text_progress != self.ui.statusbar.currentMessage():
                self.ui.statusbar.showMessage(text_progress,
                                              self.app.statusbar_delay)
                self.ui.statusbar.repaint()
            # Add to log when finished
            if i == maxi:
                self.ui.progressbar.setVisible(False)
                self.log.log(text_finished, level=1)
                self.ui.statusbar.showMessage(text_finished,
                                              self.app.statusbar_delay)
        return hook

    def import_image(self, filepath):
        self.log.log(f'DSA backend: Importing image: {filepath}', level=1)
        ims = dsa.TemporalImages(cache_infos=False)
        try:
            ims.add_field(dsa.import_from_image(filepath, cache_infos=False),
                          copy=False)
        except IOError:
            self.log.log(f"Cannot import '{filepath}': not a valid image",
                         level=3)
            return False
        except:
            self.log.log_unknown_exception()
            return False
        self.ims = ims
        self.input_type = 'image'
        self.filepath = filepath
        self.reset_cache()
        self.nmb_frames = 1
        self.sizex = self.ims.shape[0]
        self.sizey = self.ims.shape[1]
        return True

    def import_images(self, filepaths):
        self.log.log(f'DSA backend: Importing image set: {filepaths}', level=1)
        ims = dsa.TemporalImages(filepath=None, cache_infos=False)
        filepaths.sort()
        import_hook = self.get_progressbar_hook('Importing image set',
                                                'Imported image set')
        try:
            for i, filepath in enumerate(filepaths):
                tmpim = dsa.import_from_image(filepath, cache_infos=False)
                ims.add_field(tmpim, time=i+1, unit_times="", copy=False)
                import_hook(i, len(filepaths))
        except IOError:
            self.log.log(f"Couldn't import selected files: {filepath}",
                         level=3)
            return False
        except:
            self.log.log_unknown_exception()
            return False
        self.ims = ims
        self.input_type = 'images'
        self.filepath = filepath
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.ims[0].shape[0]
        self.sizey = self.ims[0].shape[1]
        return True

    def import_video(self, filepath):
        self.log.log(f'DSA backend: Importing video: {filepath}', level=1)
        hook = self.get_progressbar_hook('Importing video',
                                         'Video imported')
        try:
            ims = dsa.import_from_video(filepath, cache_infos=False,
                                        iteration_hook=hook)
        except IOError:
            self.log.log(f"Couldn't import '{filepath}':"
                         " not a valid video", level=3)
            return False
        except ImportError:
            self.log.log(f"Couldn't import '{filepath}':", level=3)
            return False
        except:
            self.log.log_unknown_exception()
            return None
        self.ims = ims
        self.filepath_type = 'video'
        self.filepath = filepath
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.ims[0].shape[0]
        self.sizey = self.ims[0].shape[1]
        return True

    def is_valid_ind(self, ind):
        if self.ims is None:
            return False
        if ind > self.nmb_frames or ind < 0:
            return False
        return True

    def get_baseline_display_points(self, params, ind):
        lims = self.precomp_old_params['lims']
        dx = self.precomp_old_params['dx'].asNumber()
        baseline = self.get_current_precomp_im(params, ind).baseline
        pt1 = baseline.pt1.copy()
        pt2 = baseline.pt2.copy()
        # x
        deltax = lims[0][0]
        pt1[0] = pt1[0]/dx - deltax
        pt2[0] = pt2[0]/dx - deltax
        # y
        deltay = self.sizey + (lims[1][1] - self.sizey)
        pt1[1] = deltay - pt1[1]/dx
        pt2[1] = deltay - pt2[1]/dx
        return pt1, pt2

    def get_current_raw_im(self, ind):
        if self.ims is None:
            return self.default_image
        return self.ims[ind]

    def precompute_images(self, params):
        if self.ims_precomp is not None:
            if not self.is_precomp_params_changed(params):
                return None
        self.log.log('DSA backend: Preparing images for edge detection',
                     level=1)
        # store new parameters
        hook = self.get_progressbar_hook('Preparing images for edge detection',
                                         'Images ready for edge detection')
        # set baseline
        try:
            ims_precomp = self.ims.copy()
            base1, base2 = params['baseline_pts']
            ims_precomp.set_baseline(base1, base2)
        except:
            self.log.log_unknown_exception()
            ims_precomp = self.ims.copy()
        hook(0, 4)
        # apply crop
        try:
            lims = params['lims']
            limst = params['cropt']
            ims_precomp.crop(intervx=lims[0], intervy=lims[1],
                             intervt=[limst[0] - 1, limst[1]],
                             inplace=True)
        except:
            self.log.log_unknown_exception()
        hook(2, 4)
        # apply scaling
        try:
            ims_precomp.scale(scalex=params['dx'],
                              scaley=params['dx'],
                              scalet=params['dt'],
                              inplace=True)
        except:
            self.log.log_unknown_exception()
        hook(3, 4)
        # store
        self.ims_precomp = ims_precomp
        self.precomp_old_params = params
        # reset following edges and fits
        self.reset_cache()
        self.edges = None
        self.fits = None

    def is_precomp_params_changed(self, params):
        if self.precomp_old_params is None:
            return True
        for d in ['dx', 'dt']:
            if params[d].strUnit() != self.precomp_old_params[d].strUnit():
                return True
            elif params[d].asNumber() != self.precomp_old_params[d].asNumber():
                return True
        for crop in ['lims', 'baseline_pts', 'cropt']:
            if np.any(params[crop] != self.precomp_old_params[crop]):
                return True
        return False

    def get_current_precomp_im(self, params, ind):
        if self.ims_precomp is None or self.is_precomp_params_changed(params):
            self.precompute_images(params)
        cropt = params['cropt']
        return self.ims_precomp[ind - cropt[0] + 1]

    def is_edge_param_changed(self, params):
        if self.edge_cache_method != self.edge_detection_method:
            return True
        for p1, p2 in zip(params, self.edge_cache_params):
            if p1 != p2:
                return True
        return False

    def get_current_edge(self, params, ind):
        params_precomp = self.app.tab1.get_params()
        im = self.get_current_precomp_im(params_precomp, ind)
        if self.edge_detection_method is None:
            return dsa.DropEdges([], im, None)
        # Reset cache if not valid anymore
        if self.is_edge_param_changed(params):
            self.reset_cache()
        # Use cache if possible
        edge = self.edge_cache[ind]
        if edge is None:
            self.log.log('DSA backend: Computing edges for current image',
                         level=1)
            # Get params
            canny_args = params[0].copy()
            canny_args.update(params[-1])
            contour_args = params[1].copy()
            contour_args.update(params[-1])
            # Edge detection
            try:
                params_precomp = self.app.tab1.get_params()
                if self.edge_detection_method == 'canny':
                    edge = im.edge_detection(**canny_args)
                elif self.edge_detection_method == 'contour':
                    edge = im.edge_detection_contour(**contour_args)
                else:
                    self.log.log("No edge detection method selected",
                                 level=2)
                    return dsa.DropEdges([], im, None)
            except Exception:
                self.log.log("Couldn't find a drop here", level=2)
                return dsa.DropEdges([], im, None)
            except:
                self.log.log_unknown_exception()
                return dsa.DropEdges([], im, None)
            # Update cache
            self.edge_cache[ind] = edge
            self.edge_cache_params = params
            self.edge_cache_method = self.edge_detection_method
        else:
            self.log.log('DSA backend: Using cached edges for current image',
                         level=1)
        return edge

    def get_current_edge_pts(self, params, ind):
        edge = self.get_current_edge(params, ind)
        if len(edge.xy) == 0:
            return [[], []]
        # Return edge pts
        pts = edge.xy.transpose().copy()
        lims = self.precomp_old_params['lims']
        dx = self.precomp_old_params['dx'].asNumber()
        deltax = lims[0][0]
        deltay = lims[1][1]
        pts[0] = pts[0]/dx - deltax
        pts[1] = deltay - pts[1]/dx
        return pts

    def is_fit_params_changed(self, params):
        if self.fit_cache_method != self.fit_method:
            return True
        for p1, p2 in zip(params, self.fit_cache_params):
            if p1 != p2:
                return True
        return False

    def get_current_fit(self, params, ind):
        # Reset cache if not valid anymre
        if self.fit_method is None:
            return dsa.DropFit(None, [None, None], [None, None])
        # Reset cache if not valid anymore
        if self.is_fit_params_changed(params):
            self.reset_cache()
        # Use cache if possible
        fit = self.fit_cache[ind]
        if fit is None:
            # Ensure the edge is computed
            edge_params = self.app.tab2.get_params()
            edge = self.get_current_edge(edge_params, ind)
            if edge is None:
                return dsa.DropFit(edge.baseline, edge.x_bounds, edge.y_bounds)
            # log
            self.log.log('DSA backend: Computing fits for current image',
                         level=1)
            # Get params
            circle_args = params[0]
            ellipse_args = params[1]
            polyline_args = params[2]
            spline_args = params[3]
            try:
                if self.fit_method == 'circle':
                    fit = edge.fit_circle(**circle_args)
                elif self.fit_method == 'ellipse':
                    fit = edge.fit_ellipse(**ellipse_args)
                elif self.fit_method == 'polyline':
                    fit = edge.fit_polyline(**polyline_args)
                elif self.fit_method == 'spline':
                    fit = edge.fit_spline(**spline_args)
                else:
                    self.log.lof("No fitting method selected", level=2)
                    return dsa.DropFit(edge.baseline, edge.x_bounds,
                                       edge.y_bounds)
            except Exception:
                self.log.log("Couldn't find a fit here...", level=2)
                return dsa.DropFit(edge.baseline, edge.x_bounds,
                                   edge.y_bounds)
            except:
                self.log.log_unknown_exception()
                return dsa.DropFit(edge.baseline, edge.x_bounds, edge.y_bounds)
            # Update cache
            self.fit_cache[ind] = fit
            self.fit_cache_params = params
            self.fit_cache_method = self.fit_method
        else:
            self.log.log('DSA backend: Using cached fits for current image',
                         level=1)
        return fit

    def get_current_fit_pts(self, params, ind):
        fit = self.get_current_fit(params, ind)
        if fit.baseline is None:
            return [[0], [0]], [[-999], [-999]]
        # Get fit pts and center
        pts = fit.get_fit_as_points()
        if self.fit_method in ['circle', 'ellipse']:
            fit_center = fit.fits[0].copy()
        else:
            fit_center = np.array([[-999], [-999]])
        # Return fit pts
        lims = self.precomp_old_params['lims']
        dx = self.precomp_old_params['dx'].asNumber()
        deltax = lims[0][0]
        deltay = lims[1][1]
        pts[0] = pts[0]/dx - deltax
        pts[1] = deltay - pts[1]/dx
        fit_center[0] = fit_center[0]/dx - deltax
        fit_center[1] = deltay - fit_center[1]/dx
        return pts, fit_center

    def get_current_ca(self, ind):
        # get the fit
        fit_params = self.app.tab3.get_params()
        fit = self.get_current_fit(fit_params, ind)
        if fit is None:
            return [[np.nan, np.nan], [np.nan, np.nan]]
        # No need to recompute contact angles
        if fit.thetas is None:
            try:
                fit.compute_contact_angle()
            except:
                self.log.log_unknown_exception()
                return [[np.nan, np.nan], [np.nan, np.nan]]
        if fit.thetas is None:
            self.log.log("Couldn't compute contact angles "
                         "for the current image",
                         level=2)
            return [[np.nan, np.nan], [np.nan, np.nan]]
        # return angles
        lines = fit._get_angle_display_lines()
        lines = lines[0:2]
        dx = self.precomp_old_params['dx'].asNumber()
        lines = np.array(lines)/dx
        lims = self.precomp_old_params['lims']
        deltax = lims[0][0]
        deltay = lims[1][1]
        lines[:, 0] -= deltax
        lines[:, 1] = deltay - lines[:, 1]
        return lines

    def get_plotable_quantity(self, quant):
        # fits should be computed already...
        if self.fits is None:
            self.log.log('Fit need to be computed first', level=3)
            return [], ""
        #
        dx = self.precomp_old_params['dx']
        dt = self.precomp_old_params['dt']
        ff, lf = self.precomp_old_params['cropt']
        unit_x = dx.strUnit()[1:-1]
        unit_t = dt.strUnit()[1:-1]
        try:
            if quant == 'Frame number':
                return np.arange(ff, ff + len(self.ims_precomp), 1), ""
            elif quant == 'Time':
                return self.ims_precomp.times, unit_t
            elif quant == 'Position (x, right)':
                _, pt2s = self.fits.get_drop_positions()
                return pt2s[:, 0], unit_x
            elif quant == 'Position (x, left)':
                pt1s, _ = self.fits.get_drop_positions()
                return pt1s[:, 0], unit_x
            elif quant == 'CL velocity (x, left)':
                pt1s, _ = self.fits.get_drop_positions()
                pt1s = pt1s[:, 0]
                vel = np.gradient(pt1s, self.fits.dt)
                return vel, f"{unit_x}/{unit_t}"
            elif quant == 'CL velocity (x, right)':
                _, pt2s = self.fits.get_drop_positions()
                pt2s = pt2s[:, 0]
                vel = np.gradient(pt2s, self.fits.dt)
                return vel, f"{unit_x}/{unit_t}"
            elif quant == 'Position (x, center)':
                xys = self.fits.get_drop_centers()
                return xys[:, 0], unit_x
            elif quant == 'CA (right)':
                return self.fits.get_contact_angles()[:, 1], "°"
            elif quant == 'CA (left)':
                return 180 - self.fits.get_contact_angles()[:, 0], "°"
            elif quant == 'CA (mean)':
                thetas = self.fits.get_contact_angles()
                thetas[:, 1] = 180 - thetas[:, 1]
                return np.mean(thetas, axis=1), "°"
            elif quant == 'Base radius':
                return self.fits.get_base_diameters()/2, unit_x
            elif quant == 'Height':
                return self.fits.get_drop_heights(), unit_x
            elif quant == 'Area':
                return self.fits.get_drop_areas(), f'{unit_x}^2'
            elif quant == 'Volume':
                return self.fits.get_drop_volumes(), f'{unit_x}^3'
            else:
                self.log.log(f'Non-plotable quantity: {quant}', level=3)
                return [], ""
        except:
            self.log.log_unknown_exception()
            return [], ""

    def is_edges_param_changed(self, params):
        canny_args = params[0].copy()
        canny_args.update(params[-1])
        contour_args = params[1].copy()
        contour_args.update(params[-1])
        new_args = {'canny': canny_args,
                    'contour': contour_args}
        new_params = {'detection_method': self.edge_detection_method,
                      'args': new_args[self.edge_detection_method]}
        if self.edge_detection_method != self.edges_old_method:
            return True
        if self.edges_old_params is None or self.edges is None:
            return True
        elif (self.edges_old_params['detection_method']
              != self.edge_detection_method):
            return True
        else:
            for key in new_params['args'].keys():
                if (new_params['args'][key]
                    != self.edges_old_params['args'][key]):
                    return True
        return False

    def compute_edges(self, params):
        self.log.log('DSA backend: Computing edges for the image set', level=1)
        #
        if self.edge_detection_method is None:
            self.edges = None
            self.fits = None
            return None
        # precompute
        precomp_params = self.app.tab1.get_params()
        if self.ims_precomp is None:
            self.precompute_images(precomp_params)
        if self.is_precomp_params_changed(precomp_params):
            self.precompute_images(precomp_params)
        # Get params
        canny_args = params[0].copy()
        canny_args.update(params[-1])
        contour_args = params[1].copy()
        contour_args.update(params[-1])
        new_args = {'canny': canny_args,
                    'contour': contour_args}
        new_params = {'detection_method': self.edge_detection_method,
                      'args': new_args[self.edge_detection_method]}
        # Check if need to recompute
        if not self.is_edges_param_changed(params):
            return None
        # Edge detection
        self.precompute_images(self.app.tab1.get_params())
        tmp_ims = self.ims_precomp
        hook = self.get_progressbar_hook('Detecting edges', 'Detected edges')
        try:
            if self.edge_detection_method == 'canny':
                edges = tmp_ims.edge_detection(iteration_hook=hook,
                                               **canny_args)
            elif self.edge_detection_method == 'contour':
                edges = tmp_ims.edge_detection_contour(iteration_hook=hook,
                                                       **contour_args)
            else:
                self.log.log("No edge detection method selected", level=2)
                self.edges = None
                self.fits = None
                return None
        except Exception:
                self.log.log("No edges at all could be detected here", level=2)
                self.edges = None
                self.fits = None
                return None
        except:
            self.log.log_unknown_exception()
            self.edges = None
            self.fits = None
            return None
        # Store
        self.edges = edges
        self.edges_old_params = new_params
        self.edges_old_method = self.edge_detection_method
        self.fits = None

    def is_fits_param_changed(self, params):
        # Get params
        circle_args = params[0]
        ellipse_args = params[1]
        polyline_args = params[2]
        spline_args = params[3]
        # Check if need to recompute
        new_args = {'circle': circle_args,
                    'ellipse': ellipse_args,
                    'polyline': polyline_args,
                    'spline': spline_args}[self.fit_method]
        new_params = {'method': self.fit_method,
                      'args': new_args}
        if self.fit_method != self.fits_old_method:
            return True
        if self.fits_old_params is None or self.fits is None:
            return True
        elif new_params['method'] != self.fits_old_params['method']:
            return True
        else:
            old_args = self.fits_old_params['args']
            for key in new_args.keys():
                if new_args[key] != old_args[key]:
                    return True
        return False

    def compute_fits(self, params):
        self.log.log('DSA backend: fitting edges for the image set', level=1)
        # Check
        if self.edges is None:
            self.compute_edges(self.app.tab2.get_params())
            if self.edges is None:
                self.fits = None
                return None
        if self.fit_method is None:
            self.fits = None
            return None
        # Get params
        circle_args = params[0]
        ellipse_args = params[1]
        polyline_args = params[2]
        spline_args = params[3]
        new_args = {'circle': circle_args,
                    'ellipse': ellipse_args,
                    'polyline': polyline_args,
                    'spline': spline_args}[self.fit_method]
        new_params = {'method': self.fit_method,
                      'args': new_args}
        # Check if need to recompute
        if not self.is_fits_param_changed(params):
            return None
        # Fit
        hook = self.get_progressbar_hook('Fitting edges',
                                         'Fitted edges')
        try:
            if self.fit_method == 'circle':
                fits = self.edges.fit_circle(iteration_hook=hook,
                                             **circle_args)
            elif self.fit_method == 'ellipse':
                fits = self.edges.fit_ellipse(iteration_hook=hook,
                                              **ellipse_args)
            elif self.fit_method == 'polyline':
                fits = self.edges.fit_polyline(iteration_hook=hook,
                                               **polyline_args)
            elif self.fit_method == 'spline':
                fits = self.edges.fit_spline(iteration_hook=hook,
                                             **spline_args)
            else:
                self.app.log.log('No fitting method selected', level=2)
                self.fits = None
                return None
        except:
            self.log.log_unknown_exception()
            self.fits = None
            return None
        # Store
        self.fits = fits
        self.fits_old_params = new_params
        self.fits_old_method = self.fit_method

    def compute_cas(self):
        if self.fits is None:
            return None
        if self.fits.fits[0].thetas is None:
            hook = self.get_progressbar_hook('Computing contact angles',
                                             'Computed contact angles')
            try:
                self.fits.compute_contact_angle(iteration_hook=hook)
            except:
                self.log.log_unknown_exception()
