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

from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np
from datetime import datetime


from .tab import Tab
from .files_helper import select_new_file


class TabData(Tab):

    def enter_tab(self):
        self.update_data_table()

    def update_data_table(self, *args, **kwargs):
        # get significative number
        sign_nmb = self.ui.tab5_significativ_numbers.value()
        # resize
        self.ui.tab5_DataTable.setColumnCount(len(self.app.plottable_quant))
        # Update headers
        self.ui.tab5_DataTable.setHorizontalHeaderLabels(self.app.plottable_quant)
        # check
        if self.dsa.fits is None:
            return None
        # Update table
        for n, quant in enumerate(self.app.plottable_quant):
            val, _, unit = self.dsa.get_plotable_quantity(quant, smooth=0)
            if n == 0:
                self.ui.tab5_DataTable.setRowCount(len(val))
            for m, item in enumerate(val):
                newitem = QTableWidgetItem(f"{item:.{sign_nmb}f}")
                self.ui.tab5_DataTable.setItem(m, n, newitem)
        # resize
        self.ui.tab5_DataTable.resizeColumnsToContents()
        self.ui.tab5_DataTable.resizeRowsToContents()

    def enable_options(self):
        self.ui.tab5_export_box.setEnabled(True)
        self.ui.tab5_number_format_box.setEnabled(True)

    def export_as_csv(self, toggle):
        try:
            # get fiel to save to
            filepath = select_new_file("Save as")
            extension = ".csv"
            if len(filepath) == 0:
                return None
            filepath = filepath[0]
            if filepath[0] == "":
                return None
            # Add extension
            if filepath[-len(extension):] != extension:
                filepath += extension
            # get data
            data = []
            headers = []
            for quant in self.app.plottable_quant:
                val, _, unit = self.dsa.get_plotable_quantity(quant, smooth=0)
                # check that length matches
                if len(data) > 0:
                    if len(data[0]) != len(val):
                        self.log.log(f"Quantity {quant} does not have the right"
                                     f" length ({len(val)} instead of"
                                     f" {len(data[0])})", level=3)
                        continue
                data.append(list(val))
                headers.append(f'{quant.replace(",", "")}'
                               f' [{unit.replace(",", "")}]')
            data = np.array(data, dtype=float).transpose()
            np.savetxt(filepath, data, delimiter=', ',
                       header=f"File: {self.dsa.filepath}\n"
                       f"Analysis date: {datetime.utcnow()}\n"
                       + ", ".join(headers))
            self.log.log(f"Save data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()
