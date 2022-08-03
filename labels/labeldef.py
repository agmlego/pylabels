# This file is part of pylabels, a Python library to create PDFs for printing
# labels.
# Copyright (C) 2012, 2013, 2014 Blair Bonnett
#
# pylabels is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pylabels is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pylabels.  If not, see <http://www.gnu.org/licenses/>.


import json
import os.path

from labels.specifications import Specification

# just some simple static constants
I2MM = 25.4
MM2P = 2.83465
SHEET_SIZES = {'letter': (8.5, 11), 'A4': (210, 297), 'A5': (148, 210)}


def build_label_def(jsonFilePath):
    """
    The basic purpose of this method is to load the JSON file specs
    and turn it into a dictionary of dictionaries where the label name
    is the key.  The dictionary that is the value should then contain
    all the necessary parameters to build a specification
    :param jsonFilePath:
    :return: a dictionary of label specs
    """
    with open(jsonFilePath, mode='r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        label_defs = {}
        for label in json_data['label']:
            label_defs[label['name']] = label
        return label_defs


# get the label definitions
LABEL_DEFS = build_label_def(os.path.join(
    os.path.dirname(__file__), 'labeldef.json'))


class AveryLabel(Specification):
    def __init__(self, label_name, **kwargs):
        # get our spec
        self.label_name = label_name
        data = LABEL_DEFS[label_name]
        # this gets the multiplier, if it is defined in inches
        # we multiply to get everything into mm
        multiplier = I2MM if data.pop('measurement') == 'in' else 1
        data.pop("name")
        # lets get the defaults out of the dictionary explicitly
        page_size = SHEET_SIZES[data.pop('page_size')]
        sheet_width = page_size[0] * multiplier
        sheet_height = page_size[1] * multiplier
        columns = data.pop('columns')
        rows = data.pop('rows')
        label_width = data.pop('label_width') * multiplier
        label_height = data.pop('label_height') * multiplier
        # now that we have popped all the required stuff out of the dictionary
        # we can just use defaults for the rest of the stuff
        # here is a list of things that dont get multiplied by the multiplier
        non_mult = ['corner_radius', 'padding_radius',
                    'background_image', 'background_filename']
        # holder for the transformed optional stuff
        opt_data = {}
        for k in data.keys():
            if k in non_mult or not (isinstance(data[k], (int, float))):
                opt_data[k] = data[k]
            else:
                opt_data[k] = data[k] * multiplier
        super().__init__(sheet_width=sheet_width, sheet_height=sheet_height, columns=columns, rows=rows,
                         label_height=label_height, label_width=label_width, **kwargs)
