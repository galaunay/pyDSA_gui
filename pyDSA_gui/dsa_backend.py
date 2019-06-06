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


import cv2
import pyDSA_core as dsa
from IMTreatment.utils import make_unit
import numpy as np
from scipy import ndimage
import json
import os
import unum


class myJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, unum.Unum):
            return {"__unum.Unum__": [obj.asNumber(), obj.strUnit()]}
        if isinstance(obj, np.ndarray):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class myJSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook,
                                  *args, **kwargs)

    def object_hook(self, dct):
        if "__unum.Unum__" == list(dct.keys())[0]:
            unit = dct["__unum.Unum__"]
            return unit[0]*make_unit(unit[1][1:-1])
        return dct


class DSA(object):
    def __init__(self, app):
        self.app = app
        self.ui = app.ui
        self.log = app.log
        self.log.log('DSA backend: initializing backend', level=1)
        # Input
        self.input_type = None
        self.filepath = None
        # Computation control
        self.stop = False
        # Images
        self.default_image = dsa.Image()
        self.default_image.import_from_arrays(range(300), range(200),
                                              np.random.rand(300, 200)*255)
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None
        # precomp
        self.precomp_cache_params = None
        # Edges
        self.edge_detection_method = 'canny'
        self.edge_cache = []
        self.edge_cache_params = [None]*3
        self.edge_cache_method = None
        # Fit
        self.fit_method = 'ellipses'
        self.fits = None
        self.fit_cache = []
        self.fit_cache_params = [None]*3
        self.fit_cache_method = 'ellipses'
        # Plottable quantities
        self.plottable_quantity_cache = {}

    def is_initialized(self):
        return self.nmb_frames != 0

    def get_infofile(self):
        if self.input_type == "image":
            infofile_path = os.path.splitext(os.path.abspath(self.filepath[0]))[0]
            infofile_path += ".info"
        elif self.input_type == "images":
            path = self.filepath[0]
            infofile_path = os.path.dirname(os.path.abspath(path))
            infofile_path = os.path.join(infofile_path, "infofile.info")
        else:
            infofile_path = os.path.splitext(os.path.abspath(self.filepath))[0]
            infofile_path += ".info"
        return infofile_path

    def save_infofile(self):
        # get infos
        info = self.get_precomp_params()
        info.update({"infofile_maker": "pydsaqt5"})
        infofile_path = self.get_infofile()
        # make it serializable
        with open(infofile_path, 'w+') as f:
            json.dump(info, f, cls=myJSONEncoder)

    def read_infofile(self):
        infofile_path = self.get_infofile()
        # No file (yet)
        if not os.path.isfile(infofile_path):
            return None
        # get infos
        try:
            with open(infofile_path, 'r') as f:
                dic = json.load(f, cls=myJSONDecoder)
        except:
            self.log.log('Corrupted infofile, reinitializing...', level=2)
            os.remove(infofile_path)
            return None
        # check
        if not 'infofile_maker' in dic.keys():
            return None
        if not dic['infofile_maker'] == "pydsaqt5":
            return None
        # return
        return dic

    def check_cache(self):
        if self.is_precomp_params_changed() or self.is_edges_param_changed():
            self.reset_cache()
            self.edge_cache_params = self.get_edge_params()
            self.fit_cache_params = self.get_fit_params()
            self.precomp_cache_params = self.get_precomp_params()
            self.clear_plottable_quantity_cache()
            return True
        if self.is_fits_params_changed():
            self.reset_cache(edge=False)
            self.fit_cache_params = self.get_fit_params()
            self.clear_plottable_quantity_cache()
            return True
        return False

    def reset_cache(self, edge=True, fit=True):
        if self.nmb_frames is not None:
            if edge:
                self.edge_cache = [None]*self.nmb_frames
            if fit:
                self.fit_cache = [None]*self.nmb_frames
            self.clear_plottable_quantity_cache()
            self.fits = None

    def get_progressbar_hook(self, text_progress, text_finished):
        def hook(i, maxi):
            # base 0 to base 1
            i += 1
            # update progressbar
            self.ui.progressbar.setVisible(True)
            self.ui.progressbar.setMaximum(maxi)
            self.ui.progressbar.setValue(i)
            self.ui.cancelbutton.setVisible(True)
            # Add message to statusbar
            if text_progress != self.ui.statusbar.currentMessage():
                self.ui.statusbar.showMessage(text_progress,
                                              self.app.statusbar_delay)
                self.ui.statusbar.repaint()
            # Add to log when finished
            if i == maxi:
                self.ui.progressbar.setVisible(False)
                self.ui.cancelbutton.setVisible(False)
                self.log.log(text_finished, level=1)
                self.ui.statusbar.showMessage(text_finished,
                                              self.app.statusbar_delay)
        return hook

    def import_image(self, filepath):
        raise NotImplementedError

    def import_images(self, filepaths):
        raise NotImplementedError

    def import_video(self, filepath):
        raise NotImplementedError

    def is_valid_ind(self, ind):
        if self.nmb_frames == 0:
            return False
        if ind > self.nmb_frames or ind < 0:
            return False
        return True

    def get_dt(self):
        raise NotImplementedError

    def get_baseline_display_points(self, ind):
        precomp_params = self.get_precomp_params()
        lims = precomp_params['lims']
        dx = precomp_params['dx'].asNumber()
        baseline = self.get_current_precomp_im(ind).baseline
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
        raise NotImplementedError

    def get_precomp_params(self):
        return self.app.tab1.get_params()

    def is_precomp_params_changed(self):
        params = self.get_precomp_params()
        if self.precomp_cache_params is None:
            return True
        for d in ['dx', 'dt']:
            if params[d].strUnit() != self.precomp_cache_params[d].strUnit():
                return True
            elif params[d].asNumber() != self.precomp_cache_params[d].asNumber():
                return True
        for crop in ['lims', 'baseline_pts', 'cropt']:
            if np.any(params[crop] != self.precomp_cache_params[crop]):
                return True
        return False

    def get_current_precomp_im(self, ind):
        raise NotImplementedError

    def get_edge_params(self):
        return self.app.tab2.get_params()

    def is_edges_param_changed(self):
        params = self.get_edge_params()
        if self.edge_cache_method != self.edge_detection_method:
            return True
        for p1, p2 in zip(params, self.edge_cache_params):
            if p1 != p2:
                return True
        return False

    def get_current_edge(self, ind):
        raise NotImplementedError

    def get_current_edge_pts(self, ind):
        edge = self.get_current_edge(ind)
        if len(edge.xy) == 0:
            return [[], []]
        # Return edge pts
        pts = edge.xy.transpose().copy()
        precomp_params = self.get_precomp_params()
        lims = precomp_params['lims']
        dx = precomp_params['dx'].asNumber()
        deltax = lims[0][0]
        deltay = lims[1][1]
        pts[0] = pts[0]/dx - deltax
        pts[1] = deltay - pts[1]/dx
        return pts

    def get_fit_params(self):
        return self.app.tab3.get_params()

    def is_fits_params_changed(self):
        params = self.get_fit_params()
        if self.fit_cache_method != self.fit_method:
            return True
        for p1, p2 in zip(params, self.fit_cache_params):
            if p1 != p2:
                return True
        return False

    def get_current_fit(self, ind):
        raise NotImplementedError

    def get_current_fit_pts(self, ind):
        fit = self.get_current_fit(ind)
        if fit is None:
            return [[0], [0]], [[-999], [-999]]
        if fit.baseline is None:
            return [[0], [0]], [[-999], [-999]]
        pts = fit.get_fit_as_points()
        # Not fit here...
        if isinstance(pts, dsa.DropFit):
            return [[-999, -998], [-999, -998]], np.array([[-999], [-999]])
        # Get fit pts and center
        if self.fit_method in ['circle', 'ellipse']:
            if fit.fits is None:
                return [[-999, -998], [-999, -998]], np.array([[-999], [-999]])
            fit_center = fit.fits[0].copy()
        elif self.fit_method in ['wetting ridge']:
            fit_center = []
            for i in range(3):
                if fit.fits is None:
                    fit_center.append([np.nan, np.nan])
                else:
                    fit_center.append(fit.fits[i][0])
            fit_center = np.array(fit_center).transpose()
        else:
            fit_center = np.array([[-999], [-999]])
        # Return fit pts
        precomp_params = self.get_precomp_params()
        lims = precomp_params['lims']
        dx = precomp_params['dx'].asNumber()
        deltax = lims[0][0]
        deltay = lims[1][1]
        pts[0] = pts[0]/dx - deltax
        pts[1] = deltay - pts[1]/dx
        fit_center[0] = fit_center[0]/dx - deltax
        fit_center[1] = deltay - fit_center[1]/dx
        return pts, fit_center

    def get_current_ca(self, ind):
        # get the fit
        fit = self.get_current_fit(ind)
        if fit is None:
            return [[np.nan, np.nan], [np.nan, np.nan]]
        # No need to recompute contact angles
        if fit.thetas is None:
            try:
                fit.compute_contact_angle()
            except AttributeError:
                return [[np.nan, np.nan], [np.nan, np.nan]]
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
        precomp_params = self.get_precomp_params()
        dx = precomp_params['dx'].asNumber()
        lines = np.array(lines)/dx
        lims = precomp_params['lims']
        deltax = lims[0][0]
        deltay = lims[1][1]
        lines[:, 0] -= deltax
        lines[:, 1] = deltay - lines[:, 1]
        return lines

    def compute_fits(self):
        raise NotImplementedError

    def compute_cas(self, ind):
        raise NotImplementedError

    def get_run_params(self):
        return self.app.tab4.get_params()

    def get_plotable_quantity(self, quant, smooth=0):
        # fits should be computed already...
        if self.fits is None:
            self.log.log('Fit need to be computed first', level=3)
            return np.array([]), np.array([]), ""
        # check if already cached !
        cache_name = f"{quant}_smooth{smooth}"
        try:
            return self.plottable_quantity_cache[cache_name]
        except:
            pass
        # Get units
        precomp_params = self.get_precomp_params()
        dx = precomp_params['dx']
        dt = precomp_params['dt']
        ff, lf = precomp_params['cropt']
        unit_x = dx.strUnit()[1:-1]
        unit_t = dt.strUnit()[1:-1]
        dt = float(dt.asNumber())
        #
        run_params = self.get_run_params()
        N = run_params['N']
        # Get quantity
        try:
            if quant == 'Frame number':
                if self.nmb_frames == 1:
                    vals, unit = [0, 1], ""
                else:
                    vals, unit = np.arange(ff, ff + N*len(self.fits), N), ""
            elif quant == 'Time':
                vals, unit = self.fits.times, unit_t
            elif quant == 'Position (x, right)':
                _, pt2s = self.fits.get_drop_positions()
                vals, unit = pt2s[:, 0], unit_x
            elif quant == 'Position (x, left)':
                pt1s, _ = self.fits.get_drop_positions()
                vals, unit = pt1s[:, 0], unit_x
            elif quant == 'CL velocity (x, left)':
                pt1s, _ = self.fits.get_drop_positions()
                pt1s = pt1s[:, 0]
                vel = np.gradient(pt1s, self.fits.dt)
                vals, unit = vel, f"{unit_x}/{unit_t}"
            elif quant == 'CL velocity (x, right)':
                _, pt2s = self.fits.get_drop_positions()
                pt2s = pt2s[:, 0]
                vel = np.gradient(pt2s, self.fits.dt)
                vals, unit = vel, f"{unit_x}/{unit_t}"
            elif quant == 'Position (x, center)':
                xys = self.fits.get_drop_centers()
                vals, unit = xys[:, 0], unit_x
            elif quant == 'CA (right)':
                vals, unit = 180 - self.fits.get_contact_angles()[:, 1], "°"
            elif quant == 'CA (left)':
                vals, unit = self.fits.get_contact_angles()[:, 0], "°"
            elif quant == 'CA (mean)':
                thetas = self.fits.get_contact_angles()
                thetas[:, 1] = 180 - thetas[:, 1]
                vals, unit = np.mean(thetas, axis=1), "°"
            elif quant == 'Base radius':
                vals, unit = self.fits.get_base_diameters()/2, unit_x
            elif quant == 'Height':
                vals, unit = self.fits.get_drop_heights(), unit_x
            elif quant == 'Area':
                vals, unit = self.fits.get_drop_areas(), f'{unit_x}^2'
            elif quant == 'Volume':
                vals, unit = self.fits.get_drop_volumes(), f'{unit_x}^3'
            elif quant == 'Ridge height (left)':
                if self.fit_method == "wetting ridge":
                    vals = self.fits.get_ridge_height()[0]
                    unit = f'{unit_x}'
                else:
                    vals, unit = [], ""
            elif quant == 'Ridge height (right)':
                if self.fit_method == "wetting ridge":
                    vals = self.fits.get_ridge_height()[1]
                    unit = f'{unit_x}'
                else:
                    vals, unit = [], ""
            elif quant == 'Ridge height (mean)':
                if self.fit_method == "wetting ridge":
                    tps = self.fits.get_triple_points()
                    vals1 = tps[0][:, 1]
                    vals2 = tps[1][:, 1]
                    vals = (vals1 + vals2)/2
                    unit = f'{unit_x}'
                else:
                    vals, unit = [], ""
            elif quant == 'CA (TP, left)':
                if self.fit_method == "wetting ridge":
                    tps = self.fits.get_triple_pts_contact_angles()
                    vals, unit = tps[:, 0], f'{unit_x}'
                else:
                    vals, unit = [], ""
            elif quant == 'CA (TP, right)':
                if self.fit_method == "wetting ridge":
                    tps = self.fits.get_triple_pts_contact_angles()
                    vals, unit = 180 - tps[:, 1], f'{unit_x}'
                else:
                    vals, unit = [], ""
            elif quant == 'CA (TP, mean)':
                if self.fit_method == "wetting ridge":
                    tps = self.fits.get_triple_pts_contact_angles()
                    tps1 = tps[:, 0]
                    tps2 = 180 - tps[:, 1]
                    vals, unit = (tps1 + tps2)/2, f'{unit_x}'
                else:
                    vals, unit = [], ""
            else:
                self.log.log(f'Non-plotable quantity: {quant}', level=3)
                vals, unit = [], ""
        except:
            self.log.log_unknown_exception()
            vals, unit = [], ""
        # Smooth if asked
        if smooth != 0:
            nans = np.isnan(vals)
            if np.any(nans):
                inds = np.arange(len(vals))
                vals[nans] = np.interp(inds[nans], inds[~nans], vals[~nans])
            smoothed_vals = ndimage.gaussian_filter(vals, smooth,
                                                    mode='nearest')
            smoothed_vals[nans] = np.nan
            vals[nans] = np.nan
            vals_ori = vals
            vals = smoothed_vals
        else:
            vals_ori = [np.nan]*len(vals)
        # In case of only one frame, make sur the plot is stil visible
        if self.nmb_frames == 1:
            if len(vals) == 1:
                vals = np.concatenate((vals, vals))
                vals_ori = np.concatenate((vals_ori, vals_ori))
        # store computed values
        vals = np.asarray(vals)
        vals_ori = np.asarray(vals_ori)
        self.plottable_quantity_cache[cache_name] = vals, vals_ori, unit
        # return
        return vals, vals_ori, unit

    def clear_plottable_quantity_cache(self):
        self.plottable_quantity_cache = {}


class DSA_mem(DSA):
    def __init__(self, app):
        super().__init__(app)
        # Ims
        self.ims = None
        # Precompute
        self.ims_precomp = None
        # Edges
        self.edges = None
        self.edges_old_params = None
        self.edges_old_method = self.edge_detection_method
        # Fit
        self.fits_old_params = None
        self.fits_old_method = self.fit_method

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
        self.input_type = 'video'
        self.filepath = filepath
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.ims[0].shape[0]
        self.sizey = self.ims[0].shape[1]
        return True

    def get_dt(self):
        return self.ims.dt

    def get_current_raw_im(self, ind):
        if self.ims is None:
            return self.default_image
        return self.ims[ind]

    def precompute_images(self):
        params = self.get_precomp_params()
        if self.ims_precomp is not None:
            if not self.is_precomp_params_changed():
                return None
        self.log.log('DSA backend: Preparing images for edge detection',
                     level=1)
        # store new parameters
        hook = self.get_progressbar_hook('Preparing images for edge detection',
                                         'Images ready for edge detection')
        # set baseline
        ims_precomp = self.ims.copy()
        try:
            base1, base2 = params['baseline_pts']
            ims_precomp.set_baseline(base1, base2)
        except:
            self.log.log_unknown_exception()
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
        self.precomp_cache_params = params
        # reset following edges and fits
        self.reset_cache()
        self.edges = None
        self.fits = None

    def get_current_precomp_im(self, ind):
        params = self.get_precomp_params()
        if self.ims_precomp is None or self.is_precomp_params_changed():
            self.precompute_images()
        cropt = params['cropt']
        if self.nmb_frames == 1:
            return self.ims_precomp[0]
        else:
            return self.ims_precomp[ind - cropt[0] + 1]

    def get_current_edge(self, ind):
        params = self.get_edge_params()
        params_precomp = self.app.tab1.get_params()
        im = self.get_current_precomp_im(ind)
        if self.edge_detection_method is None:
            return dsa.DropEdges([], im, None)
        # Reset cache if not valid anymore
        self.check_cache()
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

    def get_current_fit(self, ind):
        params = self.get_fit_params()
        # nothing to compute
        if self.fit_method is None:
            return dsa.DropFit(None, [None, None], [None, None])
        # Reset cache if not valid anymore
        self.check_cache()
        # Use cache if possible
        fit = self.fit_cache[ind]
        if fit is None:
            # Ensure the edge is computed
            edge_params = self.app.tab2.get_params()
            edge = self.get_current_edge(ind)
            if edge is None:
                return dsa.DropFit(edge.baseline, edge.x_bounds, edge.y_bounds)
            # log
            self.log.log('DSA backend: Computing fits for current image',
                         level=1)
            # Get params
            circle_args = params[0]
            ellipse_args = params[1]
            ellipses_args = params[2]
            polyline_args = params[3]
            spline_args = params[4]
            wr_args = params[5]
            try:
                if self.fit_method == 'circle':
                    fit = edge.fit_circle(**circle_args)
                elif self.fit_method == 'ellipse':
                    fit = edge.fit_ellipse(**ellipse_args)
                elif self.fit_method == 'ellipses':
                    fit = edge.fit_ellipses(**ellipses_args)
                elif self.fit_method == 'polyline':
                    fit = edge.fit_polyline(**polyline_args)
                elif self.fit_method == 'spline':
                    fit = edge.fit_spline(**spline_args)
                elif self.fit_method == 'wetting ridge':
                    # triple point estimate
                    miny = np.min(edge.xy[:, 1])
                    maxy = np.max(edge.xy[:, 1])
                    tp_y = miny + (maxy - miny)*wr_args['pos_estimate']
                    # get fitting
                    fit = edge.fit_circles([[0, tp_y], [0, tp_y]],
                                           sigma_max=wr_args['sigma'])
                else:
                    self.log.log("No fitting method selected", level=2)
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

    def is_edges_param_changed(self):
        params = self.get_edge_params()
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

    def compute_edges(self):
        params = self.get_edge_params()
        self.log.log('DSA backend: Computing edges for the image set', level=1)
        #
        if self.edge_detection_method is None:
            self.edges = None
            self.fits = None
            return None
        # precompute
        precomp_params = self.app.tab1.get_params()
        if self.ims_precomp is None:
            self.precompute_images()
        if self.is_precomp_params_changed():
            self.precompute_images()
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
        if not self.is_edges_param_changed():
            return None
        # Only use certains frames
        self.precompute_images()
        run_params = self.get_run_params()
        N = run_params['N']
        if N < 0:
            N = 1
        try:
            tmp_ims = self.ims_precomp.reduce_temporal_resolution(
                N, mean=False, inplace=False)
        except:
            tmp_ims = self.ims_precomp
            self.log.log_unknown_exception()
        # Edge detection
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

    def is_fits_params_changed(self):
        params = self.get_fit_params()
        # Get params
        circle_args = params[0]
        ellipse_args = params[1]
        ellipses_args = params[2]
        polyline_args = params[3]
        spline_args = params[4]
        wr_args = params[5]
        # Check if need to recompute
        new_args = {'circle': circle_args,
                    'ellipse': ellipse_args,
                    'ellipses': ellipses_args,
                    'polyline': polyline_args,
                    'spline': spline_args,
                    'wr': wr_args}[self.fit_method]
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

    def compute_fits(self):
        params = self.get_fit_params()
        self.log.log('DSA backend: fitting edges for the image set', level=1)
        # Check
        if self.edges is None:
            self.compute_edges()
            if self.edges is None:
                self.fits = None
                return None
        if self.fit_method is None:
            self.fits = None
            return None
        # Get params
        circle_args = params[0]
        ellipse_args = params[1]
        ellipses_args = params[2]
        polyline_args = params[3]
        spline_args = params[4]
        wr_args = params[5]
        new_args = {'circle': circle_args,
                    'ellipse': ellipse_args,
                    'ellipses': ellipses_args,
                    'polyline': polyline_args,
                    'spline': spline_args,
                    'wr': wr_args}[self.fit_method]
        new_params = {'method': self.fit_method,
                      'args': new_args}
        # Check if need to recompute
        if not self.is_fits_params_changed():
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
            elif self.fit_method == 'ellipses':
                fits = self.edges.fit_ellipses(iteration_hook=hook,
                                               **ellipses_args)
            elif self.fit_method == 'polyline':
                fits = self.edges.fit_polyline(iteration_hook=hook,
                                               **polyline_args)
            elif self.fit_method == 'spline':
                fits = self.edges.fit_spline(iteration_hook=hook,
                                             **spline_args)
            elif self.fit_method == 'wetting ridge':
                # get triple points from polyfit
                fits = self.edges.fit_polyline(deg=wr_args['deg'])
                fits.detect_triple_points()
                tps = zip(fits.get_triple_points())
                # get fitting
                fits = self.edges.fit_circles(tps, sigma_max=wr_args['sigma'])
            else:
                self.app.log.log('No fitting method selected', level=2)
                self.fits = None
                return None
        except:
            self.log.log_unknown_exception()
            self.fits = None
            return None
        # cas
        try:
            self.fits.compute_contact_angle(iteration_hook=hook)
        except:
            self.log.log_unknown_exception()
        # Store
        self.fits = fits
        self.fits_old_params = new_params
        self.fits_old_method = self.fit_method

    def compute_cas(self):
        pass


class DSA_hdd(DSA):

    def __init__(self, app):
        super().__init__(app)
        self.cached_current_raw_im = None
        self.cached_current_precomp_im = None
        self.cached_current_ind = None

    def reset_cache(self, edge=True, fit=True):
        super().reset_cache(edge=edge, fit=fit)
        self.cached_current_raw_im = None
        self.cached_current_precomp_im = None
        self.cached_current_ind = None

    def import_image(self, filepath, log=True):
        success = self.import_images([filepath], log=log)
        self.input_type = "image"
        return success

    def import_images(self, filepaths, log=True):
        self.log.log(f'DSA backend: Importing image set: {filepaths}', level=1)
        try:
            filepaths.sort()
            tmp_im = dsa.import_from_image(filepaths[0], dtype=np.uint8,
                                           cache_infos=False)
        except OSError:
            if log:
                self.log.log(f'Could not load images from first image: '
                             f'{filepaths[0]}', level=3)
            return None
        except:
            if log:
                self.log.log_unknown_exception()
            return None
        self.reset_cache()
        self.filepath = filepaths
        self.vid = filepaths
        self.input_type = 'images'
        self.ims = None
        self.nmb_frames = len(filepaths)
        self.sizex = tmp_im.shape[0]
        self.sizey = tmp_im.shape[1]
        return True

    def import_video(self, filepath, log=True):
        self.log.log(f'DSA backend: Importing video: {filepath}', level=1)
        try:
            vid = cv2.VideoCapture()
            vid.open(filepath)
            success, data = vid.read()
            if not success:
                raise OSError()
        except OSError:
            if log:
                self.log.log(f'Could not load video from: '
                             f'{filepath}', level=3)
            return None
        except:
            if log:
                self.log.log_unknown_exception()
            return None
        self.reset_cache()
        self.vid = vid
        self.input_type = 'video'
        self.filepath = filepath
        self.ims = None
        self.nmb_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.sizex = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.sizey = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.dt = 1
        return True

    def is_initialized(self):
        if self.nmb_frames is not None:
            return True
        return False

    def get_dt(self):
        if isinstance(self.vid, cv2.VideoCapture):
            return 1/float(self.vid.get(cv2.CAP_PROP_FPS))
        elif isinstance(self.vid, list):
            return self.dt
        else:
            self.log.log("Cannot get the value of dt...", level=3)
            return 1

    def get_current_raw_im(self, ind):
        if not self.is_valid_ind(ind):
            self.log.log(f"Couldn't get the asked frame number: {ind}", level=3)
            return self.default_image
        # check if can use the cached one
        if (self.cached_current_ind is not None
            and self.cached_current_raw_im is not None):
            if self.cached_current_ind == ind:
                return self.cached_current_raw_im
        # Import from hdd
        im = dsa.Image()
        if isinstance(self.vid, cv2.VideoCapture):
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, ind)
            try:
                success, data = self.vid.read()
            except OSError:
                self.log.log(f'Could not load video from: '
                             f'{self.filepath}', level=3)
                return self.default_image
            except:
                self.log.log_unknown_exception()
                return self.default_image
            if not success:
                self.log.log(f"Can't decode frame number {ind}", level=3)
                return self.default_image
            data = cv2.cvtColor(data, cv2.COLOR_RGB2GRAY)
            data = data.transpose()[:, ::-1]
            im.import_from_arrays(range(self.sizex), range(self.sizey),
                                  unit_x="", unit_y="",
                                  values=data, dtype=np.uint8,
                                  dontchecknans=True)
        elif isinstance(self.vid, list):
            try:
                im = dsa.import_from_image(self.vid[ind], cache_infos=False,
                                           dtype=np.uint8)
            except OSError:
                self.log.log(f'Could not load image from: '
                             f'{self.vid[ind]}', level=3)
                return self.default_image
            except:
                self.log.log_unknown_exception()
                return self.default_image
        else:
            self.log.log("Cannot get the current image... ", level=3)
            im = self.default_image
        # update the cache
        if self.cached_current_ind != ind:
            self.cached_current_precomp_im = None
            self.cached_current_ind = ind
        self.cached_current_raw_im = im
        # return
        return im

    def get_current_precomp_im(self, ind):
        # check if can use the cached one
        if (self.cached_current_ind is not None
            and self.cached_current_precomp_im is not None):
            if self.cached_current_ind == ind:
                return self.cached_current_precomp_im
        # import from hdd
        params = self.get_precomp_params()
        im_precomp = self.get_current_raw_im(ind).copy()
        # Baseline
        try:
            base1, base2 = params['baseline_pts']
            im_precomp.set_baseline(base1, base2)
        except:
            self.log.log_unknown_exception()
        # apply crop
        try:
            lims = params['lims']
            im_precomp.crop(intervx=lims[0], intervy=lims[1],
                            inplace=True)
        except:
            self.log.log_unknown_exception()
        # apply scaling
        try:
            im_precomp.scale(scalex=params['dx'],
                             scaley=params['dx'],
                             inplace=True)
        except:
            self.log.log_unknown_exception()
        # update the cache
        if self.cached_current_ind != ind:
            self.cached_current_raw_im = None
            self.cached_current_ind = ind
        self.cached_current_precomp_im = im_precomp
        # store
        return im_precomp

    def get_current_edge(self, ind):
        # Reset cache if not valid anymore
        self.check_cache()
        params = self.get_edge_params()
        im = self.get_current_precomp_im(ind)
        if self.edge_detection_method is None:
            return dsa.DropEdges([], im, None)
        # Use cache if possible
        edge = self.edge_cache[ind]
        if edge is None:
            # Get params
            canny_args = params[0].copy()
            canny_args.update(params[-1])
            contour_args = params[1].copy()
            contour_args.update(params[-1])
            # Edge detection
            try:
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
        return edge

    def get_current_fit(self, ind):
        # Reset cache if not valid anymore
        self.check_cache()
        params = self.get_fit_params()
        # nothing to compute
        if self.fit_method is None:
            return dsa.DropFit(None, [None, None], [None, None])
        # update cached params
        self.edge_cache_params = self.get_edge_params()
        self.fit_cache_params = self.get_fit_params()
        # Use cache if possible
        fit = self.fit_cache[ind]
        if fit is None:
            # Ensure the edge is computed
            edge = self.get_current_edge(ind)
            # Get params
            circle_args = params[0]
            ellipse_args = params[1]
            ellipses_args = params[2]
            polyline_args = params[3]
            spline_args = params[4]
            wr_args = params[5]
            try:
                if self.fit_method == 'circle':
                    fit = edge.fit_circle(**circle_args)
                elif self.fit_method == 'ellipse':
                    fit = edge.fit_ellipse(**ellipse_args)
                elif self.fit_method == 'ellipses':
                    fit = edge.fit_ellipses(**ellipses_args)
                elif self.fit_method == 'polyline':
                    fit = edge.fit_polyline(**polyline_args)
                elif self.fit_method == 'spline':
                    fit = edge.fit_spline(**spline_args)
                elif self.fit_method == 'wetting ridge':
                    # triple point estimate
                    miny = np.min(edge.xy[:, 1])
                    maxy = np.max(edge.xy[:, 1])
                    tp_y = miny + (maxy - miny)*wr_args['pos_estimate']
                    # get fitting
                    fit = edge.fit_circles([[0, tp_y], [0, tp_y]],
                                           sigma_max=wr_args['sigma'])
                else:
                    self.log.log("No fitting method selected", level=2)
                    return dsa.DropFit(edge.baseline, edge.x_bounds,
                                       edge.y_bounds)
            except Exception:
                self.log.log("Couldn't find a fit here...", level=2)
                fit = dsa.DropFit(edge.baseline, edge.x_bounds,
                                  edge.y_bounds)
            except:
                self.log.log_unknown_exception()
                fit = dsa.DropFit(edge.baseline, edge.x_bounds, edge.y_bounds)
            # contact angle
            try:
                fit.compute_contact_angle()
            except:
                pass
            # Update cache
            self.fit_cache[ind] = fit
            self.fit_cache_params = params
            self.fit_cache_method = self.fit_method
        return fit

    def compute_edges(self):
        pass

    def compute_fits(self):
        self.log.log('DSA backend: fitting edges for the image set', level=1)
        # Forbid the user to interact with th gui
        self.ui.tabWidget.setEnabled(False)
        # Just for safety...
        self.stop = False
        # checks
        if self.edge_detection_method is None:
            self.edges = None
            self.fits = None
            self.ui.tabWidget.setEnabled(True)
            return None
        # Get params
        precomp_params = self.app.tab1.get_params()
        run_params = self.get_run_params()
        N = run_params['N']
        dt = float(precomp_params['dt'].asNumber())
        ff, lf = precomp_params['cropt']
        im = self.get_current_precomp_im(0)
        hook = self.get_progressbar_hook('Computing', 'Computation done')
        fits = []
        ts = []
        # Compute
        if self.nmb_frames == 1:
            fits = [self.get_current_fit(0)]*2
            ts = [0, 1]
        else:
            for i, ind in enumerate(np.arange(ff, lf+1, N)):
                self.app.globalapp.processEvents()
                if self.stop:
                    fit = fits[-1]
                    fit.fits = None
                    fit.thetas = None
                else:
                    fit = self.get_current_fit(ind-1)
                fits.append(fit)
                ts.append(ind*dt)
                hook(i, int((lf - ff)/N))
        self.stop = False
        hook(99, 100)
        # Create dummy edges (necessary to create a fitting class...)
        class Dummy(object):
            pass
        edges = Dummy()
        edges.dt = dt
        edges.times = ts
        edges.unit_times = make_unit("s")
        edges.unit_x = make_unit("")
        edges.unit_y = make_unit("")
        edges.baseline = im.baseline
        # store
        if self.fit_method == 'circle':
            fits2 = dsa.temporalfits.TemporalCircleFits(fits, edges)
        elif self.fit_method == 'ellipse':
            fits2 = dsa.temporalfits.TemporalEllipseFits(fits, edges)
        elif self.fit_method == 'ellipses':
            fits2 = dsa.temporalfits.TemporalEllipsesFits(fits, edges)
        elif self.fit_method == 'polyline':
            fits2 = dsa.temporalfits.TemporalSplineFits(fits, edges)
        elif self.fit_method == 'spline':
            fits2 = dsa.temporalfits.TemporalSplineFits(fits, edges)
        elif self.fit_method == 'wetting ridge':
            fits2 = dsa.temporalfits.TemporalCirclesFits(fits, edges)
        else:
            self.app.log.log('No fitting method selected', level=2)
            fits2 = None
        self.fits = fits2
        self.ui.tabWidget.setEnabled(True)
