import pyDSA as dsa
import re
import numpy as np
from IMTreatment.utils import make_unit


class DSA(object):
    def __init__(self, app):
        self.app = app
        self.ui = app.ui
        self.log = app.log
        self.log.log('DSA backend: initializing backend', level=1)
        self.current_ind = 0
        # Images
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None
        self.ims = None
        # Precompute
        self.precomp_old_params = None
        self.ims_precomp = None
        # Edges
        self.edge_detection_method = 'canny'
        self.current_edge = None
        self.edge_cache = []
        self.edge_cache_params = [None]*3
        self.edge_cache_method = None
        self.edges = None
        self.edges_old_params = None
        # Fit
        self.fit_method = 'ellipse'
        self.current_fit = None
        self.fit_cache = []
        self.fit_cache_params = [None]*3
        self.fit_cache_method = None
        self.fits = None
        self.fits_old_params = None

    def reset_cache(self, edge=True, fit=True):
        if self.nmb_frames is not None:
            if edge:
                self.edge_cache = [None]*self.nmb_frames
            if fit:
                self.fit_cache = [None]*self.nmb_frames

    def import_image(self, filepath):
        self.log.log(f'DSA backend: Importing image: {filepath}', level=1)
        self.ims = dsa.TemporalImages(cache_infos=False)
        self.ims.add_field(dsa.import_from_image(filepath, cache_infos=False),
                           copy=False)
        self.reset_cache()
        self.current_ind = 0
        self.nmb_frames = 1
        self.sizex = self.ims.shape[0]
        self.sizey = self.ims.shape[1]

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

    def import_images(self, filepaths):
        if len(filepaths) == 0:
            return None
        self.log.log(f'DSA backend: Importing image set: {filepaths}', level=1)
        self.ims = dsa.TemporalImages(filepath=None, cache_infos=False)
        filepaths.sort()
        import_hook = self.get_progressbar_hook('Importing image set',
                                                'Imported image set')
        for i, filepath in enumerate(filepaths):
            try:
                tmpim = dsa.import_from_image(filepath, cache_infos=False)
                self.ims.add_field(tmpim, time=i+1, unit_times="", copy=False)
                import_hook(i, len(filepaths))
            except IOError:
                self.log.log(f"Cannot import '{filepath}': not a valid image",
                             level=3)
                raise IOError()
        self.current_ind = 0
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.ims[0].shape[0]
        self.sizey = self.ims[0].shape[1]

    def import_video(self, filepath):
        self.log.log(f'DSA backend: Importing video: {filepath}', level=1)
        hook = self.get_progressbar_hook('Importing video',
                                         'Video imported')
        self.ims = dsa.import_from_video(filepath, cache_infos=False,
                                         iteration_hook=hook)
        self.current_ind = 0
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.sizex = self.ims[0].shape[0]
        self.sizey = self.ims[0].shape[1]

    def set_current(self, ind):
        if self.nmb_frames == 1:
            return None
        if self.ims is None:
            return None
        if ind > self.nmb_frames:
            return None
        self.current_ind = ind

    def get_baseline_display_points(self):
        lims = self.precomp_old_params['lims']
        dx = self.precomp_old_params['dx'].asNumber()
        baseline = self.get_current_precomp_im().baseline
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

    def get_current_raw_im(self):
        return self.ims[self.current_ind]

    def get_current_precomp_im(self):
        if self.ims_precomp is None:
            raise Exception()
        cropt = self.precomp_old_params['cropt']
        return self.ims_precomp[self.current_ind - cropt[0] + 1]

    def get_current_edge(self, params):
        if self.edge_detection_method is None:
            self.current_edge = None
            return [[], []]
        # Reset cache if not valid anymore
        if self.edge_cache_method != self.edge_detection_method:
            self.reset_cache()
        for p1, p2 in zip(params, self.edge_cache_params):
            if p1 != p2:
                self.reset_cache()
                break
        # Use cache if possible
        edge = self.edge_cache[self.current_ind]
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
                if self.edge_detection_method == 'canny':
                    im = self.get_current_precomp_im()
                    edge = im.edge_detection(**canny_args)
                elif self.edge_detection_method == 'contour':
                    im = self.get_current_precomp_im()
                    edge = im.edge_detection_contour(**contour_args)
                else:
                    raise Exception()
            except Exception:
                self.log.log("Couldn't find edges for the current frame",
                             level=2)
                self.current_edge = None
                return [[], []]
            # Update cache
            self.edge_cache[self.current_ind] = edge
            self.edge_cache_params = params
            self.edge_cache_method = self.edge_detection_method
        else:
            self.log.log('DSA backend: Using cached edges for current image',
                         level=1)
        self.current_edge = edge
        # Return edge pts
        pts = edge.xy.transpose().copy()
        lims = self.precomp_old_params['lims']
        dx = self.precomp_old_params['dx'].asNumber()
        deltax = lims[0][0]
        deltay = lims[1][1]
        pts[0] = pts[0]/dx - deltax
        pts[1] = deltay - pts[1]/dx
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
        if fit is None:
            self.log.log('DSA backend: Computing fits for current image',
                         level=1)
        else:
            self.log.log('DSA backend: Using cached fits for current image',
                         level=1)
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
            fit_center = np.array([[-999], [-999]])
        elif self.fit_method == 'spline':
            if fit is None:
                fit = self.current_edge.fit_spline(**spline_args)
            pts = fit.get_fit_as_points()
            fit_center = np.array([[-999], [-999]])
        else:
            return [[0], [0]], [[-999], [-999]]
        # Update cache
        self.fit_cache[self.current_ind] = fit
        self.fit_cache_params = params
        self.fit_cache_method = self.fit_method
        self.current_fit = fit
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

    def get_current_ca(self):
        if self.current_fit is None:
            return [[np.nan, np.nan], [np.nan, np.nan]]
        try:
            self.current_fit.compute_contact_angle()
        except:
            self.log.log('Failed to compute contact angles', level=2)
            return [[np.nan, np.nan], [np.nan, np.nan]]
        lines = self.current_fit._get_angle_display_lines()
        lines = lines[0:2]
        lines = np.array(lines)
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
            return []
        #
        dx = self.precomp_old_params['dx']
        dt = self.precomp_old_params['dt']
        ff, lf = self.precomp_old_params['cropt']
        unit_x = dx.strUnit()[1:-1]
        unit_t = dt.strUnit()[1:-1]
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
        elif quant == 'Position (x, center)':
            xys = self.fits.get_drop_centers()
            return xys[:, 0], unit_x
        elif quant == 'CA (right)':
            return self.fits.get_contact_angles()[:, 0], "°"
        elif quant == 'CA (left)':
            return 180 - self.fits.get_contact_angles()[:, 1], "°"
        elif quant == 'CA (mean)':
            thetas = self.fits.get_contact_angles()
            thetas[:, 1] = 180 - thetas[:, 1]
            return np.mean(thetas, axis=1), "°"
        elif quant == 'Base radius':
            return self.fits.get_base_diameters(), unit_x
        elif quant == 'Height':
            return self.fits.get_drop_heights(), unit_x
        elif quant == 'Area':
            return self.fits.get_drop_areas(), f'{unit_x}^2'
        elif quant == 'Volume':
            return self.fits.get_drop_volumes(), f'{unit_x}^3'
        else:
            raise Exception(f'Non-plotable quantity: {quant}')

    def precompute_images(self, params):
        self.log.log('DSA backend: Preparing images for edge detection',
                     level=1)
        need_recompute = False
        # Check if need to recompute
        if self.ims_precomp is None or self.precomp_old_params is None:
            need_recompute = True
        else:
            for d in ['dx', 'dt']:
                if params[d].strUnit() != self.precomp_old_params[d].strUnit():
                    need_recompute = True
                    break
                elif params[d].asNumber() != self.precomp_old_params[d].asNumber():
                    need_recompute = True
                    break
            for crop in ['lims', 'baseline_pts', 'cropt']:
                if np.any(params[crop] != self.precomp_old_params[crop]):
                    need_recompute = True
                    break
        if not need_recompute:
            return None
        # store new parameters
        self.precomp_old_params = params
        hook = self.get_progressbar_hook('Preparing images for edge detection',
                                         'Images ready for edge detection')
        # set baseline
        ims_precomp = self.ims.copy()
        base1, base2 = params['baseline_pts']
        ims_precomp.set_baseline(base1, base2)
        hook(0, 4)
        # apply crop
        lims = params['lims']
        limst = params['cropt']
        ims_precomp.crop(intervx=lims[0],
                         intervy=lims[1],
                         intervt=[limst[0] - 1, limst[1]],
                         inplace=True)
        hook(2, 4)
        # apply scaling
        ims_precomp.scale(scalex=params['dx'],
                          scaley=params['dx'],
                          scalet=params['dt'],
                          inplace=True)
        hook(3, 4)
        # store
        self.ims_precomp = ims_precomp
        # reset following edges and fits
        self.reset_cache()
        self.edges = None
        self.fits = None

    def compute_edges(self, params):
        self.log.log('DSA backend: Computing edges for the image set', level=1)
        # Get params
        canny_args = params[0].copy()
        canny_args.update(params[-1])
        contour_args = params[1].copy()
        contour_args.update(params[-1])
        # Check if need to recompute
        new_args = {'canny': canny_args,
                    'contour': contour_args}
        new_params = {'detection_method': self.edge_detection_method,
                      'args': new_args[self.edge_detection_method]}
        need_recompute = False
        if self.edges_old_params is None or self.edges is None:
            need_recompute = True
        elif self.edges_old_params['detection_method'] != self.edge_detection_method:
            need_recompute = True
        else:
            for key in new_params['args'].keys():
                if new_params['args'][key] != self.edges_old_params['args'][key]:
                    need_recompute = True
                    break
        if not need_recompute:
            return None
        # Store
        self.edges_old_params = new_params
        self.fits = None
        # Edge detection
        tmp_ims = self.ims_precomp
        hook = self.get_progressbar_hook('Detecting edges',
                                         'Detected edges')
        if self.edge_detection_method == 'canny':
            self.edges = tmp_ims.edge_detection(iteration_hook=hook,
                                                **canny_args)
        elif self.edge_detection_method == 'contour':
            self.edges = tmp_ims.edge_detection_contour(iteration_hook=hook,
                                                        **contour_args)
        else:
            raise Exception()

    def compute_fits(self, params):
        self.log.log('DSA backend: fitting edges for the image set', level=1)
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
        need_recompute = False
        if self.fits_old_params is None or self.fits is None:
            need_recompute = True
        elif new_params['method'] != self.fits_old_params['method']:
            need_recompute = True
        else:
            old_args = self.fits_old_params['args']
            for key in new_args.keys():
                if new_args[key] != old_args[key]:
                    need_recompute = True
                    break
        if not need_recompute:
            return None
        else:
            self.fits_old_params = new_params
        # Fit
        hook = self.get_progressbar_hook('Fitting edges',
                                         'Fitted edges')
        if self.fit_method == 'circle':
            self.fits = self.edges.fit_circle(iteration_hook=hook,
                                              **circle_args)
        elif self.fit_method == 'ellipse':
            self.fits = self.edges.fit_ellipse(iteration_hook=hook,
                                               **ellipse_args)
        elif self.fit_method == 'polyline':
            self.fits = self.edges.fit_polyline(iteration_hook=hook,
                                                **polyline_args)
        elif self.fit_method == 'spline':
            self.fits = self.edges.fit_spline(iteration_hook=hook,
                                              **spline_args)
        else:
            self.app.log.log('please select a fitting method', level=1)
            return [[0], [0]], [[-999], [-999]]

    def compute_cas(self):
        if self.fits.fits[0].thetas is None:
            hook = self.get_progressbar_hook('Computing contact angles',
                                             'Computed contact angles')
            self.fits.compute_contact_angle(iteration_hook=hook)
