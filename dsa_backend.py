import pyDSA as dsa
import numpy as np


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
        self.current_raw_im = None
        # Crop (time)
        self.nmb_cropped_frames = None
        self.first_frame = 1
        self.last_frame = None
        # Crop
        self.ims_cropped = None
        self.current_crop_lims = None
        self.current_cropped_im = None
        # Baseline
        self.baseline_pt1 = None
        self.baseline_pt2 = None
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
        self.ims = dsa.import_from_image(filepath, cache_infos=False)
        self.current_raw_im = self.ims
        self.reset_cache()
        self.nmb_frames = 1
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

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
        self.current_raw_im = self.ims[0]
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.last_frame = len(self.ims) - 1
        self.nmb_cropped_frames = self.nmb_frames
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def import_video(self, filepath):
        self.log.log(f'DSA backend: Importing video: {filepath}', level=1)
        hook = self.get_progressbar_hook('Importing video',
                                         'Video imported')
        self.ims = dsa.import_from_video(filepath, cache_infos=False,
                                         iteration_hook=hook)
        self.current_raw_im = self.ims[0]
        self.reset_cache()
        self.nmb_frames = len(self.ims)
        self.last_frame = len(self.ims) - 1
        self.nmb_cropped_frames = self.nmb_frames
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
        self.log.log('DSA backend: Updating cropping limits', level=1)
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
        self.log.log('DSA backend: Updating baselines', level=1)
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

    def update_frame_lims(self):
        first = self.ui.tab1_frameslider_first.value()
        last = self.ui.tab1_frameslider_last.value()
        self.nmb_cropped_frames = last - first
        self.first_frame = first
        self.last_frame = last

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
        if self.edge_detection_method is None:
            self.current_edge = None
            return [[], []]
        self.log.log('DSA backend: Computing edges for current image', level=1)
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
            try:
                if self.edge_detection_method == 'canny':
                    edge = self.current_cropped_im.edge_detection(**canny_args)
                elif self.edge_detection_method == 'contour':
                    edge = self.current_cropped_im.edge_detection_contour(**contour_args)
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
        self.current_edge = edge
        # Return edge pts
        pts = edge.xy.transpose().copy()
        deltax = self.current_crop_lims[0][0]
        deltay = self.current_crop_lims[1][1]
        pts[0] = pts[0] - deltax
        pts[1] = deltay - pts[1]
        return pts

    def get_current_fit(self, params):
        self.log.log('DSA backend: Computing fits for current image', level=1)
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
        deltax = self.current_crop_lims[0][0]
        deltay = self.current_crop_lims[1][1]
        lines[:, 0] -= deltax
        lines[:, 1] = deltay - lines[:, 1]
        return lines

    def get_plotable_quantity(self, quant):
        # fits should be computed already...
        if self.fits is None:
            self.log.log('Fit need to be computed first', level=3)
            return []
        #
        if quant == 'Frame number':
            return np.arange(self.first_frame, self.last_frame + 1, 1)
        elif quant == 'Time':
            return np.arange(self.first_frame, self.last_frame + 1, 1)*self.ims.dt
        elif quant == 'Position (x, right)':
            _, pt2s = self.fits.get_drop_positions()
            return pt2s[:, 0]
        elif quant == 'Position (x, left)':
            pt1s, _ = self.fits.get_drop_positions()
            return pt1s[:, 0]
        elif quant == 'Position (x, center)':
            xys = self.fits.get_drop_centers()
            return xys[:, 0]
        elif quant == 'CA (right)':
            return self.fits.get_contact_angles()[:, 0]
        elif quant == 'CA (left)':
            return 180 - self.fits.get_contact_angles()[:, 1]
        elif quant == 'CA (mean)':
            thetas = self.fits.get_contact_angles()
            thetas[:, 1] = 180 - thetas[:, 1]
            return np.mean(thetas, axis=1)
        elif quant == 'Base radius':
            return self.fits.get_base_diameters()
        elif quant == 'Height':
            return self.fits.get_drop_heights()
        elif quant == 'Area':
            return self.fits.get_drop_areas()
        elif quant == 'Volume':
            return self.fits.get_drop_volumes()
        else:
            raise Exception(f'Non-plottable quantity: {quant}')

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
        new_params = {'cropt': [self.first_frame + 0, self.last_frame + 0],
                      'cropx': self.current_crop_lims[0].copy(),
                      'cropy': self.current_crop_lims[1].copy(),
                      'detection_method': self.edge_detection_method,
                      'args': new_args[self.edge_detection_method]}
        need_recompute = False
        if self.edges_old_params is None or self.edges is None:
            need_recompute = True
        elif self.edges_old_params['detection_method'] != self.edge_detection_method:
            need_recompute = True
        else:
            for crop in ['cropt', 'cropx', 'cropy']:
                if np.any(new_params[crop] != self.edges_old_params[crop]):
                    need_recompute = True
                    break
            for key in new_params['args'].keys():
                if new_params['args'][key] != self.edges_old_params['args'][key]:
                    need_recompute = True
                    break
        if not need_recompute:
            return None
        else:
            self.edges_old_params = new_params
            self.fits = None
        # Only use the asked images
        tmp_ims = self.ims_cropped.crop(intervt=[self.first_frame - 1,
                                                 self.last_frame - 1],
                                        ind=True)
        # Edge detection
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
