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

from PyQt5.QtWidgets import QDialog, QFileDialog


def select_file(message="Open file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileName(dialog, message,
                                           filter=filetypes)
    return filepath


def select_new_file(message="New file", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getSaveFileName(dialog, message,
                                           filter=filetypes)
    return filepath


def select_files(message="Open files", filetypes=None):
    dialog = QDialog()
    filepath = QFileDialog.getOpenFileNames(dialog, message,
                                            filter=filetypes)
    return filepath
