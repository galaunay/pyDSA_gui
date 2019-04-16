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


class Tab(object):

    def __init__(self, ui, app, dsa, log):
        self.app = app
        self.ui = ui
        self.dsa = dsa
        self.log = log
        self.initialized = False
        self.already_opened = False
        self._disable_frame_updater = False

    def enter_tab(self):
        pass

    def leave_tab(self):
        return True

    def enable_options(self):
        pass
