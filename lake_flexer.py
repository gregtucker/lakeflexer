#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 10:17:01 2019

@author: gtucker
"""

from landlab import load_params
from landlab.io import read_esri_ascii


class LakeFlexer():
    """Calculate elastic lithosphere flexure for a (paleo)lake.

    Landlab-built model that takes a digital elevation model and a target
    water-surface elevation, and calculates flexure resulting from the load of
    the water.
    """

    def __init__(self, param_filename=None):
        
        if param_filename is None:
            self.initialized = False
        else:
            self.initialize(param_filename)

    def initialize(self, param_filename):
        
        params = load_params(param_filename)

        (grid, dem) = read_esri_ascii(params['dem_filename'])

        self.elastic_thickness = params['elastic_thickness']

        # (more to be added here)

        self.initialized = True
