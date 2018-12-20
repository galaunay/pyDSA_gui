import pyDSA as dsa
import numpy as np


class DSA(object):
    def __init__(self, ui):
        self.ui = ui
        self.current_ind = 0
        self.ims = None
        self.current_raw_im = None
        self.ims_cropped = None
        self.current_crop_lims = None
        self.current_cropped_im = None
        self.baseline_pt1 = None
        self.baseline_pt2 = None
        self.edge_detection_use_canny = True
        self.edge_detection_use_contour = False
        self.edges = None
        self.current_edge = None
        self.fits = None
        self.current_fit = None
        self.nmb_frames = None
        self.sizex = None
        self.sizey = None

    def import_image(self, filepath):
        self.ims = dsa.import_from_image(filepath, cache_infos=False)
        self.current_raw_im = self.ims
        self.nmb_frames = 1
        self.sizex = self.current_raw_im.shape[0]
        self.sizey = self.current_raw_im.shape[1]

    def import_video(self, filepath):
        self.ims = dsa.import_from_video(filepath, cache_infos=False)
        self.current_raw_im = self.ims[0]
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
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        new_pt1 = [pt1[0], sizey - pt1[1]]
        new_pt2 = [pt2[0], sizey - pt2[1]]
        self.ims.set_baseline(new_pt1, new_pt2)
        if self.ims_cropped is not None:
            self.ims_cropped.set_baseline(new_pt1, new_pt2)

    def get_current_edge(self, params):
        canny_args = params[0]
        canny_args.update(params[-1])
        contour_args = params[1]
        contour_args.update(params[-1])
        # canny edge
        if self.edge_detection_use_canny:
            edge = self.current_cropped_im.edge_detection(**canny_args)
        elif self.edge_detection_use_contour:
            edge = self.current_cropped_im.edge_detection_contour(**contour_args)
        else:
            raise Exception()
        edge = edge.xy.transpose()
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        edge[1] = sizey - edge[1]
        return edge
