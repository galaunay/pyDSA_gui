# -*- coding: utf-8 -*-
#!/usr/env python3

# Copyright (C) 2017 Gaby Launay

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

import numpy as np
from IMTreatment import make_unit
import re

from .tab import Tab
from .files_helper import select_files, select_file


class TabImport(Tab):

    def enter_tab(self):
        # Update the frame number
        self.ui.tab1_spinbox_frame.setValue(self.app.current_ind + 1)

    def leave_tab(self):
        # reset zoom
        self.ui.mplwidgetimport.reset_zoom()
        # Checks entries
        if not self.is_inputs_valid():
            return False
        # Ensure current image is in the selected range
        cropt = self.get_params('cropt')
        if self.app.current_ind > cropt[1] - 1:
            self.app.set_current_ind(cropt[1] - 1)
        elif self.app.current_ind < cropt[0] - 1:
            self.app.set_current_ind(cropt[0] - 1)
        # Save settings as infofile
        self.dsa.save_infofile()
        return True

    def enable_options(self):
        self.ui.tab1_crop_box.setEnabled(True)
        self.ui.tab1_scaling_box.setEnabled(True)
        self.ui.tab1_time_box.setEnabled(True)
        if self.dsa.input_type == "video":
            self.ui.tab1_dt_from_video.setVisible(True)
        else:
            self.ui.tab1_dt_from_video.setVisible(False)

    def is_inputs_valid(self):
        try:
            self.get_params('dt')
        except:
            self.log.log("Bad format for 'dt'", level=2)
            return False
        try:
            self.get_params('dx')
        except:
            self.log.log("Bad format for 'dx'", level=2)
            return False
        return True

    def enable_frame_sliders(self):
        self._disable_frame_updater = True
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(True)
            slide.setVisible(True)
            slide.setMinimum(1)
            slide.setMaximum(self.dsa.nmb_frames)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(True)
            spin.setVisible(True)
            spin.setMinimum(1)
            spin.setMaximum(self.dsa.nmb_frames)
        self.ui.tab1_frameslider_last.setValue(self.dsa.nmb_frames)
        self.ui.tab1_frameslider_first.setValue(0)
        self.ui.tab1_spinbox_frame.setValue(0)
        self._disable_frame_updater = False

    def disable_frame_sliders(self):
        for slide in [self.ui.tab1_frameslider,
                      self.ui.tab1_frameslider_first,
                      self.ui.tab1_frameslider_last]:
            slide.setEnabled(False)
            slide.setVisible(False)
        for spin in [self.ui.tab1_spinbox_frame,
                     self.ui.tab1_spinbox_first,
                     self.ui.tab1_spinbox_last]:
            spin.setEnabled(False)
            spin.setVisible(False)
        for text in [self.ui.tab1_label_frame,
                     self.ui.tab1_label_last,
                     self.ui.tab1_label_first]:
            text.setVisible(False)

    def enable_cropping(self):
        im = self.dsa.get_current_raw_im(self.app.current_ind)
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def enable_baseline(self):
        w, h = self.dsa.get_current_raw_im(self.app.current_ind).shape
        pt1 = [1/10*w, 2/3*h]
        pt2 = [9/10*w, 2/3*h]
        self.ui.mplwidgetimport.update_baseline(pt1, pt2)

    def import_file(self, toggle=None, filepath=None):
        # Ask for file path
        if filepath is None:
            filepath, typ = select_files('Open a file')
        # Checks
        if filepath is None:
            return None
        if len(filepath) == 0:
            return None
        # Images
        if len(filepath) > 1:
            success = self.import_images(filepath)
            return None
        else:
            filepath = filepath[0]
        # Image
        success = self.import_image(filepath, log=False)
        # Video
        if not success:
            success = self.import_video(filepath, log=False)
        # Something else
        if success:
            # disable data table
            self.ui.tabdata.setEnabled(False)
        else:
            self.log.log("Unrecognized file format", level=3)

        return success

    def import_image(self, filepath=None, log=True):
        if filepath is None:
            # Select image to import
            filepath = select_file('Open image')[0]
        # Import image
        self.app.current_ind = 0
        success = self.dsa.import_image(filepath, log=log)
        if success:
            # Disable frame sliders
            self.disable_frame_sliders()
            # Update image display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # De-init next tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()
        return success

    def import_images(self, filepath=None, log=True):
        # Select images to import
        if filepath is None:
            filepath = select_files('Open images')[0]
        # Check
        if len(filepath) == 0:
            return None
        # Import images
        success = self.dsa.import_images(filepath, log=log)
        if success:
            # Enable frame sliders
            self.enable_frame_sliders()
            # Update images display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # De-init other tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()
        return success

    def import_video(self, filepath=None, log=True):
        # Select video to import
        if filepath is None:
            filepath = select_file('Open video')[0]
        # Import video
        success = self.dsa.import_video(filepath, log=log)
        if success:
            # Enable frame sliders
            self.enable_frame_sliders()
            # Update video display
            im = self.dsa.get_current_raw_im(self.app.current_ind)
            self.ui.mplwidgetimport.update_image(im.values, replot=True)
            # Enable cropping sliders
            self.enable_cropping()
            # Enable baseline
            self.enable_baseline()
            # Enable options
            self.app.enable_options()
            # Set the time interval from the video
            dt = self.dsa.get_dt()
            self.ui.tab1_set_dt_text.setText(f"{dt:.6f}")
            # De-init other tabs
            self.app.tab2.initialized = False
            self.app.tab3.initialized = False
            # initilize stuff from infofile
            self.update_from_infofile()
        return success

    def update_from_infofile(self):
        sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        infos = self.dsa.read_infofile()
        if infos is None:
            return None
        # sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
        # dt
        dt = str(infos['dt'].asNumber())
        self.ui.tab1_set_dt_text.setText(dt)
        # dx
        dx = f"{infos['dl']}{infos['dx'].strUnit()[1:-1]}"
        self.ui.tab1_set_scaling_text.setText(dx)
        if len(infos['scaling_pts']) > 0:
            self.ui.mplwidgetimport.update_scaling_pts(infos['scaling_pts'])
        # cropx and xropy
        xlim, ylim = infos['lims']
        ylim = sizey - ylim[::-1]
        self.ui.mplwidgetimport.update_crop_area(*xlim, *ylim)
        # baseline
        bpt1, bpt2 = infos['baseline_pts']
        bpt1[1] = sizey - bpt1[1]
        bpt2[1] = sizey - bpt2[1]
        self.ui.mplwidgetimport.update_baseline(bpt1, bpt2)
        # cropt
        if self.dsa.input_type != "image":
            self.ui.tab1_spinbox_first.setValue(infos['cropt'][0])
            self.ui.tab1_spinbox_last.setValue(infos['cropt'][1])
            self.ui.tab1_spinbox_frame.setValue(infos['cropt'][0])

    def set_current_frame(self, frame_number):
        self.app.current_ind = frame_number - 1
        if self._disable_frame_updater:
            return None
        im = self.dsa.get_current_raw_im(self.app.current_ind)
        self.ui.mplwidgetimport.update_image(im.values)

    def set_first_frame(self, frame_number):
        self.ui.tab1_spinbox_frame.setValue(frame_number)

    def set_last_frame(self, frame_number):
        self.ui.tab1_spinbox_frame.setValue(frame_number)

    def zoom_to_area(self):
        xlims, ylims = self.ui.mplwidgetimport.rect_hand.lims
        self.ui.mplwidgetimport.toolbar.push_current()
        self.ui.mplwidgetimport.ax.set_xlim(*xlims)
        self.ui.mplwidgetimport.ax.set_ylim(*ylims[::-1])
        self.ui.mplwidgetimport.canvas.draw()

    def reset_crop(self):
        im = self.dsa.get_current_raw_im(self.app.current_ind)
        crop_lims = [0, im.shape[0], 0, im.shape[1]]
        self.ui.mplwidgetimport.update_crop_area(*crop_lims)

    def dt_from_video(self, b):
        dt = self.dsa.get_dt()
        self.ui.tab1_set_dt_text.setText(f"{dt:.6f}")

    def set_scaling(self):
        self.ui.mplwidgetimport.is_scaling = True

    def remove_scaling(self):
        self.ui.mplwidgetimport.is_scaling = False
        self.ui.mplwidgetimport.scaling_hand.reset()

    def get_params(self, arg=None):
        dic = {}
        # dt and dt
        if arg is None or arg == 'dt':
            dt = float(self.ui.tab1_set_dt_text.text())*make_unit('s')
            dic['dt'] = dt
        if arg is None or arg == 'dx':
            scaling_pts = self.ui.mplwidgetimport.scaling_hand.pts
            dl_real = self.ui.mplwidgetimport.get_scale()
            dl_txt = self.ui.tab1_set_scaling_text.text()
            match = re.match(r'\s*([0-9.]+)\s*(.*)\s*', dl_txt)
            dl_txt = float(match.groups()[0])
            dl_unit = match.groups()[1]
            if dl_real is not None:
                dx = dl_txt/dl_real*make_unit(dl_unit)
            else:
                dx = make_unit('')
            dic['dx'] = dx
            dic['dl'] = dl_txt
            dic['scaling_pts'] = scaling_pts
        # cropx and cropy
        if arg is None or arg == 'lims':
            xlims, ylims = self.ui.mplwidgetimport.rect_hand.lims
            sizey = abs(self.ui.mplwidgetimport.ax.viewLim.height)
            ylims = np.sort(sizey - ylims)
            lims = np.array([xlims, ylims])
            dic['lims'] = lims
        # baseline pts
        if arg is None or arg == 'baseline_pts':
            pt1 = self.ui.mplwidgetimport.baseline_hand.pt1
            pt2 = self.ui.mplwidgetimport.baseline_hand.pt2
            deltay = abs(self.ui.mplwidgetimport.ax.viewLim.height)
            base_pt1 = [pt1[0], deltay - pt1[1]]
            base_pt2 = [pt2[0], deltay - pt2[1]]
            dic['baseline_pts'] = [base_pt1, base_pt2]
        # cropt
        if arg is None or arg == 'cropt':
            first_frame = self.ui.tab1_frameslider_first.value()
            last_frame = self.ui.tab1_frameslider_last.value()
            dic['cropt'] = [first_frame, last_frame]
        # return
        if arg is None:
            return dic
        else:
            return dic[arg]
