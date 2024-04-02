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

    def _get_data_to_export(self):
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
        return data, headers

    def _get_edges_to_export(self):
        data = []
        headers = ["frame", "time", "x", "y"]
        for i in len(self.dsa.edges):
            pass
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
        return data, headers

    def _get_filepath_to_export(self, filepath, ext):
        # get fiel to save to
        if filepath is None:
            filepath, _ = select_new_file("Save as")
            if filepath == "":
                return None
        # Add extension
        if '.' not in filepath[-5:-1]:
            filepath += ext
        # Return
        return filepath

    def export_as_csv(self, toggle, filepath=None):
        try:
            # Get filepath
            filepath = self._get_filepath_to_export(filepath, ext=".csv")
            if filepath is None:
                return None
            # get and store data
            data, headers = self._get_data_to_export()
            date = datetime.now().strftime("%y-%m-%d %I:%M%p")
            np.savetxt(filepath, data, delimiter=', ',
                       header=f"File: {self.dsa.filepath}\n"
                       f"Analysis date: {date}\n"
                       + ", ".join(headers))
            self.log.log(f"Saved data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()

    def export_as_xlsx(self, toggle, filepath=None):
        import xlsxwriter
        try:
            # Get filepath
            filepath = self._get_filepath_to_export(filepath, ext=".xlsx")
            if filepath is None:
                return None
            # get and store data
            data, headers = self._get_data_to_export()
            date = datetime.now().strftime("%y-%m-%d %I:%M%p")
            wb = xlsxwriter.Workbook(filepath, {'nan_inf_to_errors': True})
            ws = wb.add_worksheet()
            # write headers
            ws.write('A1', "File")
            ws.write('A2', "Analysis date")
            ws.merge_range('B1:H1', f"{self.dsa.filepath}")
            ws.merge_range('B2:H2', f"{date}")
            ws.write_row(2, 0, headers)
            for i, row in enumerate(data):
                ws.write_row(i+3, 0, row)
            wb.close()
            self.log.log(f"Saved data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()

    def export_edges_as_csv(self, toggle, filepath=None):
        try:
            # Get filepath
            filepath = self._get_filepath_to_export(filepath, ext=".csv")
            if filepath is None:
                return None
            # get and store data
            data, headers = self._get_data_to_export()
            date = datetime.now().strftime("%y-%m-%d %I:%M%p")
            np.savetxt(filepath, data, delimiter=', ',
                       header=f"File: {self.dsa.filepath}\n"
                       f"Analysis date: {date}\n"
                       + ", ".join(headers))
            self.log.log(f"Saved data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()

    def export_edges_as_xlsx(self, toggle, filepath=None):
        import xlsxwriter
        try:
            # Get filepath
            filepath = self._get_filepath_to_export(filepath, ext=".xlsx")
            if filepath is None:
                return None
            # get and store data
            data, headers = self._get_data_to_export()
            date = datetime.now().strftime("%y-%m-%d %I:%M%p")
            wb = xlsxwriter.Workbook(filepath, {'nan_inf_to_errors': True})
            ws = wb.add_worksheet()
            # write headers
            ws.write('A1', "File")
            ws.write('A2', "Analysis date")
            ws.merge_range('B1:H1', f"{self.dsa.filepath}")
            ws.merge_range('B2:H2', f"{date}")
            ws.write_row(2, 0, headers)
            for i, row in enumerate(data):
                ws.write_row(i+3, 0, row)
            wb.close()
            self.log.log(f"Saved data in {filepath}", level=1)
        except:
            self.log.log_unknown_exception()
