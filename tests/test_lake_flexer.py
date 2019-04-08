#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 10:17:15 2019

@author: gtucker
"""

import os
import sys
import numpy as np
from landlab.io import write_esri_ascii
from landlab import RasterModelGrid

sys.path.append(os.path.abspath('..'))
from lakeflexer import LakeFlexer


def make_test_dem_with_line_load():
    """Make a 9x9 DEM with all elevation s at 10 m except a column down the
    middle where elevation is -10.0 m."""
    grid = RasterModelGrid((9, 9), xy_spacing=10000.0)
    dem = grid.add_zeros('node', 'topographic__elevation')
    dem[:] = 10.0
    dem[grid.x_of_node > 30000.0] = -10.0
    dem[grid.x_of_node > 40000.0] = 10.0
    return grid


def write_test_parameter_file(filename):
    f = open(filename, 'w')
    f.write('dem_filename: test_dem.asc\n')
    f.write('elastic_thickness: 10000.0\n')
    f.close()


def test_lake_flexer_with_line_load():
    
    dem_filename = 'test_dem.asc'
    param_filename = 'test_params.txt'
    
    test_grid = make_test_dem_with_line_load()
    write_esri_ascii(dem_filename, test_grid)
    write_test_parameter_file(param_filename)

    lf = LakeFlexer()
    lf.initialize(param_filename)
#    lf.run()
#    lf.finalize()
    
    # do the tests

    os.remove(dem_filename)
    os.remove(param_filename)
